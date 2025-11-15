"""
Prompt管理API v2 - 数据库版本
包含CRUD、热重载、性能查询、版本回滚、DeepSeek优化、A/B测试、风险指标
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any, Optional
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, desc
from datetime import datetime
import logging

from app.core.database import get_db
from app.api.v1.admin.auth import verify_admin_token
from app.models.prompt_template import (
    PromptTemplate, PromptTemplateVersion,
    PromptPerformance, PromptABTest
)
from app.services.decision.prompt_manager_db import get_global_prompt_manager_db, reload_global_templates_db
from app.services.decision.prompt_redis_subscriber import publish_prompt_reload
from app.services.quantitative.risk_metrics import PromptRiskMetrics
from app.services.quantitative.ab_test import PromptABTestFramework
from app.services.quantitative.overfitting_detector import PromptOverfittingDetector
from app.core.redis_client import redis_client

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/prompts/v2", tags=["prompts-v2"])


# ===== Pydantic Models =====

class PromptTemplateInfo(BaseModel):
    id: int
    name: str
    category: str
    permission_level: Optional[str]
    content: str
    version: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class PromptTemplateCreate(BaseModel):
    name: str
    category: str
    permission_level: Optional[str] = None
    content: str


class PromptTemplateUpdate(BaseModel):
    content: str
    change_summary: Optional[str] = None


class PromptOptimizeRequest(BaseModel):
    template_id: int
    optimization_goal: str = "提高决策准确率，降低误判风险"


class PromptGenerateRequest(BaseModel):
    name: str
    category: str
    permission_level: Optional[str] = None
    requirement: str


class ABTestCreate(BaseModel):
    test_name: str
    prompt_a_id: int
    prompt_b_id: int
    traffic_split: float = 0.5
    duration_days: int = 7


# ===== CRUD API =====

@router.get("/", response_model=List[PromptTemplateInfo])
async def list_prompts(
    category: Optional[str] = None,
    permission_level: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _: Dict = Depends(verify_admin_token)
):
    """列出所有Prompt模板"""
    try:
        query = select(PromptTemplate).where(PromptTemplate.is_active == True)
        
        if category:
            query = query.where(PromptTemplate.category == category)
        if permission_level:
            query = query.where(PromptTemplate.permission_level == permission_level)
        
        result = await db.execute(query)
        templates = result.scalars().all()
        
        return [PromptTemplateInfo(**t.__dict__) for t in templates]
    
    except Exception as e:
        logger.error(f"列出Prompt失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{template_id}", response_model=PromptTemplateInfo)
async def get_prompt(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    _: Dict = Depends(verify_admin_token)
):
    """获取单个Prompt模板"""
    template = await db.get(PromptTemplate, template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Prompt不存在")
    
    return PromptTemplateInfo(**template.__dict__)


@router.post("/", response_model=PromptTemplateInfo, status_code=201)
async def create_prompt(
    data: PromptTemplateCreate,
    db: AsyncSession = Depends(get_db),
    user: Dict = Depends(verify_admin_token)
):
    """创建新Prompt模板"""
    try:
        # 创建模板
        template = PromptTemplate(
            name=data.name,
            category=data.category,
            permission_level=data.permission_level,
            content=data.content,
            version=1,
            is_active=True,
            created_by=user.get("id")
        )
        
        db.add(template)
        await db.flush()
        
        # 创建版本历史
        version = PromptTemplateVersion(
            template_id=template.id,
            version=1,
            content=data.content,
            change_summary="初始版本",
            created_by=user.get("id")
        )
        
        db.add(version)
        await db.commit()
        await db.refresh(template)
        
        # 发布重载消息
        await publish_prompt_reload(redis_client, data.category)
        
        logger.info(f"✅ 创建Prompt: {data.category}/{data.name}")
        
        return PromptTemplateInfo(**template.__dict__)
    
    except Exception as e:
        await db.rollback()
        logger.error(f"创建Prompt失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{template_id}", response_model=PromptTemplateInfo)
async def update_prompt(
    template_id: int,
    data: PromptTemplateUpdate,
    db: AsyncSession = Depends(get_db),
    user: Dict = Depends(verify_admin_token)
):
    """更新Prompt模板（创建新版本）"""
    try:
        template = await db.get(PromptTemplate, template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Prompt不存在")
        
        # 更新内容和版本号
        template.content = data.content
        template.version += 1
        template.updated_at = datetime.now()
        
        # 创建版本历史
        version = PromptTemplateVersion(
            template_id=template.id,
            version=template.version,
            content=data.content,
            change_summary=data.change_summary or f"版本{template.version}更新",
            created_by=user.get("id")
        )
        
        db.add(version)
        await db.commit()
        await db.refresh(template)
        
        # 发布重载消息
        await publish_prompt_reload(redis_client, template.category)
        
        logger.info(f"✅ 更新Prompt: {template.category}/{template.name} v{template.version}")
        
        return PromptTemplateInfo(**template.__dict__)
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"更新Prompt失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/generate-level-prompts")
async def generate_level_prompts(
    db: AsyncSession = Depends(get_db),
    _: Dict = Depends(verify_admin_token)
):
    """为 L0-L5 权限等级自动生成中文决策 Prompt"""
    try:
        level_configs = {
            "L0": {
                "name": "decision_l0_conservative",
                "description": "极度保守型",
                "content": """你是一个极度保守的加密货币交易决策助手。

## 核心原则
- **风险第一**：绝对避免任何高风险操作
- **资金安全**：保护本金是首要任务
- **稳健收益**：宁可错过机会，不可冒险亏损

## 决策流程
1. 分析市场数据：{{ market_data }}
2. 评估技术指标（重点关注风险信号）
3. 严格风险控制检查
4. 给出明确的交易建议

## 交易限制
- 最大仓位：5%
- 最大杠杆：1x（不使用杠杆）
- 置信度阈值：≥ 0.9（极高置信度才交易）
- 每日最大交易次数：1次

## 风险控制
- 严格止损：2%
- 避免追涨杀跌
- 只在明确的趋势中交易
- 遇到不确定性立即持有或退出

## 输出格式
请以 JSON 格式输出决策结果：
{{
    "action": "买入/卖出/持有",
    "confidence": 0.0-1.0,
    "reasoning": "详细的决策理由",
    "risk_level": "极低",
    "position_size": "建议仓位大小（百分比）",
    "stop_loss": "止损价格",
    "take_profit": "止盈价格"
}}"""
            },
            "L1": {
                "name": "decision_l1_stable",
                "description": "保守稳健型",
                "content": """你是一个保守稳健的加密货币交易决策助手。

## 核心原则
- **稳健为主**：优先考虑风险控制
- **适度进取**：在安全的前提下追求收益
- **长期视角**：关注长期稳定增长

## 决策流程
1. 分析市场数据：{{ market_data }}
2. 评估技术指标和市场情绪
3. 风险收益比分析
4. 给出明确的交易建议

## 交易限制
- 最大仓位：10%
- 最大杠杆：2x
- 置信度阈值：≥ 0.8
- 每日最大交易次数：2次

## 风险控制
- 止损：3%
- 分批建仓
- 避免高波动时段
- 保持适度的现金储备

## 输出格式
请以 JSON 格式输出决策结果：
{{
    "action": "买入/卖出/持有",
    "confidence": 0.0-1.0,
    "reasoning": "详细的决策理由",
    "risk_level": "低",
    "position_size": "建议仓位大小（百分比）",
    "stop_loss": "止损价格",
    "take_profit": "止盈价格"
}}"""
            },
            "L2": {
                "name": "decision_l2_balanced",
                "description": "平衡型",
                "content": """你是一个平衡型的加密货币交易决策助手。

## 核心原则
- **风险收益平衡**：在风险和收益之间寻找最佳平衡
- **灵活应对**：根据市场情况调整策略
- **理性决策**：基于数据和分析做出决策

## 决策流程
1. 分析市场数据：{{ market_data }}
2. 综合评估技术指标、情绪和基本面
3. 风险收益比权衡
4. 给出明确的交易建议

## 交易限制
- 最大仓位：20%
- 最大杠杆：3x
- 置信度阈值：≥ 0.7
- 每日最大交易次数：3次

## 风险控制
- 止损：5%
- 动态仓位管理
- 趋势跟随 + 逆势调整
- 保持合理的风险敞口

## 输出格式
请以 JSON 格式输出决策结果：
{{
    "action": "买入/卖出/持有",
    "confidence": 0.0-1.0,
    "reasoning": "详细的决策理由",
    "risk_level": "中",
    "position_size": "建议仓位大小（百分比）",
    "stop_loss": "止损价格",
    "take_profit": "止盈价格"
}}"""
            },
            "L3": {
                "name": "decision_l3_aggressive",
                "description": "积极进取型",
                "content": """你是一个积极进取的加密货币交易决策助手。

## 核心原则
- **积极进取**：主动寻找交易机会
- **高收益目标**：追求更高的投资回报
- **风险可控**：在可承受范围内承担风险

## 决策流程
1. 分析市场数据：{{ market_data }}
2. 识别高潜力交易机会
3. 评估风险收益比
4. 给出明确的交易建议

## 交易限制
- 最大仓位：30%
- 最大杠杆：5x
- 置信度阈值：≥ 0.65
- 每日最大交易次数：5次

## 风险控制
- 止损：7%
- 积极的仓位管理
- 趋势加仓策略
- 快速止盈止损

## 输出格式
请以 JSON 格式输出决策结果：
{{
    "action": "买入/卖出/持有",
    "confidence": 0.0-1.0,
    "reasoning": "详细的决策理由",
    "risk_level": "中高",
    "position_size": "建议仓位大小（百分比）",
    "stop_loss": "止损价格",
    "take_profit": "止盈价格"
}}"""
            },
            "L4": {
                "name": "decision_l4_high_risk",
                "description": "高风险型",
                "content": """你是一个高风险偏好的加密货币交易决策助手。

## 核心原则
- **高风险高收益**：追求最大化收益
- **果断决策**：快速识别并抓住机会
- **灵活应变**：根据市场快速调整策略

## 决策流程
1. 分析市场数据：{{ market_data }}
2. 识别高波动交易机会
3. 快速评估和执行
4. 给出明确的交易建议

## 交易限制
- 最大仓位：50%
- 最大杠杆：10x
- 置信度阈值：≥ 0.6
- 每日最大交易次数：10次

## 风险控制
- 止损：10%
- 高频交易策略
- 波段操作
- 快进快出

## 输出格式
请以 JSON 格式输出决策结果：
{{
    "action": "买入/卖出/持有",
    "confidence": 0.0-1.0,
    "reasoning": "详细的决策理由",
    "risk_level": "高",
    "position_size": "建议仓位大小（百分比）",
    "stop_loss": "止损价格",
    "take_profit": "止盈价格"
}}"""
            },
            "L5": {
                "name": "decision_l5_extreme",
                "description": "极限激进型",
                "content": """你是一个极限激进的加密货币交易决策助手。

## 核心原则
- **极限收益**：追求最大可能的收益
- **高度激进**：敢于承担极高风险
- **快速反应**：毫秒级决策和执行

## 决策流程
1. 分析市场数据：{{ market_data }}
2. 识别所有可能的交易机会
3. 快速执行
4. 给出明确的交易建议

## 交易限制
- 最大仓位：100%（满仓）
- 最大杠杆：20x
- 置信度阈值：≥ 0.5
- 每日最大交易次数：无限制

## 风险控制
- 止损：15%
- 极高频交易
- 追涨杀跌策略
- 全仓操作

## ⚠️ 风险警告
此等级风险极高，可能导致重大损失！仅适合经验丰富的交易者。

## 输出格式
请以 JSON 格式输出决策结果：
{{
    "action": "买入/卖出/持有",
    "confidence": 0.0-1.0,
    "reasoning": "详细的决策理由",
    "risk_level": "极高",
    "position_size": "建议仓位大小（百分比）",
    "stop_loss": "止损价格",
    "take_profit": "止盈价格"
}}"""
            }
        }
        
        generated_count = 0
        
        for level, config in level_configs.items():
            # 检查是否已存在
            existing_query = select(PromptTemplate).where(
                PromptTemplate.name == config["name"],
                PromptTemplate.is_active == True
            )
            existing_result = await db.execute(existing_query)
            existing_template = existing_result.scalar_one_or_none()
            
            if existing_template:
                # 更新现有模板
                existing_template.content = config["content"]
                existing_template.version += 1
                existing_template.updated_at = datetime.now()
                
                # 创建版本记录
                version = PromptTemplateVersion(
                    template_id=existing_template.id,
                    version=existing_template.version,
                    content=config["content"],
                    change_summary=f"热重载：自动更新 {level} {config['description']}决策 Prompt"
                )
                db.add(version)
                
                logger.info(f"✅ 更新 {level} 决策 Prompt (ID: {existing_template.id})")
            else:
                # 创建新模板
                new_template = PromptTemplate(
                    name=config["name"],
                    category="decision",
                    permission_level=level,
                    content=config["content"],
                    version=1,
                    is_active=True
                )
                db.add(new_template)
                await db.flush()  # 获取 ID
                
                # 创建初始版本记录
                version = PromptTemplateVersion(
                    template_id=new_template.id,
                    version=1,
                    content=config["content"],
                    change_summary=f"热重载：创建 {level} {config['description']}决策 Prompt"
                )
                db.add(version)
                
                logger.info(f"✅ 创建 {level} 决策 Prompt (ID: {new_template.id})")
            
            generated_count += 1
        
        await db.commit()
        
        logger.info(f"🎉 成功生成/更新 {generated_count} 个决策 Prompt")
        
        return {
            "success": True,
            "generated_count": generated_count,
            "message": f"成功生成/更新 {generated_count} 个决策 Prompt (L0-L5)"
        }
    
    except Exception as e:
        await db.rollback()
        logger.error(f"生成决策 Prompt 失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reload")
async def reload_prompts(
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    _: Dict = Depends(verify_admin_token)
):
    """热重载Prompt"""
    try:
        await reload_global_templates_db(db, category)
        await publish_prompt_reload(redis_client, category)
        
        message = f"已重载 {category or '所有'} Prompt"
        logger.info(f"🔄 {message}")
        
        return {"success": True, "message": message}
    
    except Exception as e:
        logger.error(f"重载Prompt失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== 版本管理 API =====

@router.get("/{template_id}/versions")
async def list_versions(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    _: Dict = Depends(verify_admin_token)
):
    """列出Prompt的所有版本"""
    query = select(PromptTemplateVersion).where(
        PromptTemplateVersion.template_id == template_id
    ).order_by(desc(PromptTemplateVersion.version))
    
    result = await db.execute(query)
    versions = result.scalars().all()
    
    return [
        {
            "id": v.id,
            "version": v.version,
            "content": v.content,
            "change_summary": v.change_summary,
            "created_at": v.created_at
        }
        for v in versions
    ]


@router.post("/{template_id}/rollback/{version}")
async def rollback_version(
    template_id: int,
    version: int,
    db: AsyncSession = Depends(get_db),
    user: Dict = Depends(verify_admin_token)
):
    """回滚到指定版本"""
    try:
        # 获取目标版本
        query = select(PromptTemplateVersion).where(
            PromptTemplateVersion.template_id == template_id,
            PromptTemplateVersion.version == version
        )
        result = await db.execute(query)
        target_version = result.scalar_one_or_none()
        
        if not target_version:
            raise HTTPException(status_code=404, detail="版本不存在")
        
        # 更新模板
        template = await db.get(PromptTemplate, template_id)
        template.content = target_version.content
        template.version += 1  # 创建新版本
        template.updated_at = datetime.now()
        
        # 创建新版本记录
        new_version = PromptTemplateVersion(
            template_id=template.id,
            version=template.version,
            content=target_version.content,
            change_summary=f"回滚到版本{version}",
            created_by=user.get("id")
        )
        
        db.add(new_version)
        await db.commit()
        
        # 发布重载消息
        await publish_prompt_reload(redis_client, template.category)
        
        logger.info(f"✅ 回滚Prompt {template_id} 到版本{version}")
        
        return {"success": True, "message": f"已回滚到版本{version}"}
    
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        logger.error(f"回滚失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== DeepSeek优化 API =====

@router.post("/generate")
async def generate_with_deepseek(
    request: PromptGenerateRequest,
    _: Dict = Depends(verify_admin_token)
):
    """使用DeepSeek根据需求生成Prompt"""
    try:
        # TODO: 集成DeepSeek API
        # 这里简化为示例，根据类别和需求生成模板
        
        category_templates = {
            "decision": """你是一个专业的加密货币交易决策助手。

## 核心目标
{requirement}

## 决策流程
1. 分析市场数据：{{ market_data }}
2. 评估技术指标
3. 考虑风险因素
4. 给出明确的交易建议（买入/卖出/持有）

## 风险控制
- 严格遵守止损策略
- 控制仓位大小
- 避免过度交易

## 输出格式
请以 JSON 格式输出决策结果：
{{
    "action": "买入/卖出/持有",
    "confidence": 0.0-1.0,
    "reasoning": "决策理由",
    "risk_level": "低/中/高"
}}""",
            
            "debate": """你是一个{name}，参与加密货币投资决策的辩论。

## 角色定位
{requirement}

## 辩论要点
1. 提出明确的观点和论据
2. 使用市场数据和技术分析支持你的论点
3. 反驳对方的观点
4. 保持专业和客观

## 数据来源
- 市场数据：{{ market_data }}
- 情报报告：{{ intelligence_report }}

## 输出要求
以对话式风格提出你的论点，直接回应对方的观点，并有效地进行辩论。""",
            
            "intelligence": """你是一个加密货币情报分析专家。

## 分析目标
{requirement}

## 情报来源
- 链上数据
- 社交媒体情绪
- 新闻事件
- 大户动向

## 分析维度
1. 市场情绪分析
2. 资金流向追踪
3. 重大事件影响
4. 风险预警

## 输出格式
提供结构化的情报报告，包括：
- 关键发现
- 风险提示
- 投资建议"""
        }
        
        # 根据类别选择模板
        template = category_templates.get(request.category, category_templates["decision"])
        
        # 替换变量
        generated_content = template.format(
            requirement=request.requirement,
            name=request.name
        )
        
        return {
            "generated_content": generated_content,
            "category": request.category,
            "permission_level": request.permission_level
        }
    
    except Exception as e:
        logger.error(f"DeepSeek生成失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/optimize")
async def optimize_with_deepseek(
    request: PromptOptimizeRequest,
    db: AsyncSession = Depends(get_db),
    _: Dict = Depends(verify_admin_token)
):
    """使用DeepSeek优化Prompt"""
    try:
        template = await db.get(PromptTemplate, request.template_id)
        if not template:
            raise HTTPException(status_code=404, detail="Prompt不存在")
        
        # TODO: 集成DeepSeek API
        # 这里简化为示例
        optimized_content = f"{template.content}\n\n# DeepSeek优化建议：\n# 1. 增强风险控制逻辑\n# 2. 补充市场情绪分析\n# 3. 优化决策流程"
        
        return {
            "original_content": template.content,
            "optimized_content": optimized_content,
            "improvement_points": [
                "增强风险控制逻辑",
                "补充市场情绪分析",
                "优化决策流程"
            ]
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"DeepSeek优化失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== 风险指标 API =====

@router.get("/{template_id}/risk-metrics")
async def get_risk_metrics(
    template_id: int,
    db: AsyncSession = Depends(get_db),
    _: Dict = Depends(verify_admin_token)
):
    """获取Prompt的风险指标"""
    try:
        # 查询性能记录
        query = select(PromptPerformance).where(
            PromptPerformance.template_id == template_id
        )
        result = await db.execute(query)
        performance = result.scalar_one_or_none()
        
        if not performance:
            return {"message": "暂无性能数据"}
        
        return {
            "template_id": template_id,
            "total_decisions": performance.total_decisions,
            "win_rate": float(performance.win_rate) if performance.win_rate else 0,
            "total_pnl": float(performance.total_pnl) if performance.total_pnl else 0,
            "sharpe_ratio": float(performance.sharpe_ratio) if performance.sharpe_ratio else None,
            "sortino_ratio": float(performance.sortino_ratio) if performance.sortino_ratio else None,
            "max_drawdown": float(performance.max_drawdown) if performance.max_drawdown else None,
            "calmar_ratio": float(performance.calmar_ratio) if performance.calmar_ratio else None,
            "var_95": float(performance.var_95) if performance.var_95 else None,
            "cvar_95": float(performance.cvar_95) if performance.cvar_95 else None
        }
    
    except Exception as e:
        logger.error(f"获取风险指标失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ===== A/B测试 API =====

@router.post("/ab-tests", status_code=201)
async def create_ab_test(
    data: ABTestCreate,
    db: AsyncSession = Depends(get_db),
    user: Dict = Depends(verify_admin_token)
):
    """创建A/B测试"""
    try:
        ab_framework = PromptABTestFramework(db)
        test = await ab_framework.create_ab_test(
            test_name=data.test_name,
            prompt_a_id=data.prompt_a_id,
            prompt_b_id=data.prompt_b_id,
            traffic_split=data.traffic_split,
            duration_days=data.duration_days,
            created_by=user.get("id")
        )
        
        return {
            "id": test.id,
            "test_name": test.test_name,
            "status": test.status,
            "start_time": test.start_time
        }
    
    except Exception as e:
        logger.error(f"创建A/B测试失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ab-tests/{test_id}")
async def get_ab_test(
    test_id: int,
    db: AsyncSession = Depends(get_db),
    _: Dict = Depends(verify_admin_token)
):
    """获取A/B测试结果"""
    test = await db.get(PromptABTest, test_id)
    if not test:
        raise HTTPException(status_code=404, detail="测试不存在")
    
    return {
        "id": test.id,
        "test_name": test.test_name,
        "status": test.status,
        "prompt_a_id": test.prompt_a_id,
        "prompt_b_id": test.prompt_b_id,
        "a_stats": {
            "total_decisions": test.a_total_decisions,
            "win_rate": float(test.a_win_rate) if test.a_win_rate else 0,
            "total_pnl": float(test.a_total_pnl) if test.a_total_pnl else 0
        },
        "b_stats": {
            "total_decisions": test.b_total_decisions,
            "win_rate": float(test.b_win_rate) if test.b_win_rate else 0,
            "total_pnl": float(test.b_total_pnl) if test.b_total_pnl else 0
        },
        "p_value": float(test.p_value) if test.p_value else None,
        "is_significant": test.is_significant,
        "winner": test.winner,
        "conclusion": test.conclusion
    }


@router.post("/ab-tests/{test_id}/stop")
async def stop_ab_test(
    test_id: int,
    db: AsyncSession = Depends(get_db),
    _: Dict = Depends(verify_admin_token)
):
    """停止A/B测试"""
    try:
        ab_framework = PromptABTestFramework(db)
        test = await ab_framework.stop_test(test_id)
        
        return {
            "success": True,
            "winner": test.winner,
            "conclusion": test.conclusion
        }
    
    except Exception as e:
        logger.error(f"停止A/B测试失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))

