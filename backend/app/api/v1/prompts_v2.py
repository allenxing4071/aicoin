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

