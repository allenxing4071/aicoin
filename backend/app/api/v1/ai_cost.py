"""
AI成本管理API
"""
import logging
from typing import List, Optional, Dict
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.core.database import get_db
from app.api.v1.admin_db import get_current_user
from app.services.ai_cost_manager import get_cost_manager
from app.services.cloud_billing_sync import get_billing_sync
from app.models.intelligence_platform import IntelligencePlatform

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/models")
async def get_model_pricing(
    model_name: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    获取AI模型定价和统计信息（从实际配置的云平台读取）
    
    Args:
        model_name: 可选，指定模型名称
    
    Returns:
        模型列表及其统计信息
    """
    try:
        # 查询所有已配置的云平台
        stmt = select(IntelligencePlatform).where(IntelligencePlatform.enabled == True)
        result = await db.execute(stmt)
        platforms = result.scalars().all()
        
        # 转换为模型统计格式
        models_stats = []
        for platform in platforms:
            # 根据 platform_type 确定模型类型
            model_type = "intelligence"  # 默认类型
            if "search" in platform.platform_type.lower():
                model_type = "intelligence"
            elif "deep" in platform.platform_type.lower() or "analysis" in platform.platform_type.lower():
                model_type = "analysis"
            elif platform.provider == "deepseek":
                model_type = "decision"
            
            # 计算定价（根据实际使用情况估算）
            # 假设每次调用平均成本
            avg_cost_per_call = 0.01 if platform.total_calls > 0 else 0.001
            estimated_input_price = avg_cost_per_call * 1000  # 每M tokens
            estimated_output_price = avg_cost_per_call * 1500
            
            # 计算本月成本（简化：假设所有成本都是本月的）
            current_month_cost = platform.total_cost
            
            models_stats.append({
                "model_name": f"{platform.provider}_{platform.platform_type}",
                "display_name": platform.name,
                "provider": platform.provider,
                "type": model_type,
                "is_free": platform.total_cost == 0 and platform.total_calls > 0,
                "enabled": platform.enabled,
                "total_calls": platform.total_calls,
                "total_cost": platform.total_cost,
                "current_month_cost": current_month_cost,
                "monthly_budget": 0,  # 暂无预算限制
                "remaining_budget": 0,
                "usage_percentage": 0,
                "input_price": estimated_input_price,
                "output_price": estimated_output_price,
                "last_used_at": platform.last_health_check.isoformat() if platform.last_health_check else None,
                "success_rate": (platform.successful_calls / platform.total_calls * 100) if platform.total_calls > 0 else 0,
                "avg_response_time": platform.avg_response_time or 0,
            })
        
        # 如果指定了 model_name，过滤结果
        if model_name:
            models_stats = [m for m in models_stats if model_name.lower() in m["model_name"].lower()]
        
        return {
            "success": True,
            "data": models_stats,
            "count": len(models_stats)
        }
    except Exception as e:
        logger.error(f"获取模型定价失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/summary")
async def get_cost_summary(db: AsyncSession = Depends(get_db)):
    """
    获取成本总览（从实际配置的云平台计算）
    
    Returns:
        总成本、月成本、今日成本等汇总信息
    """
    try:
        # 查询所有已配置的云平台
        stmt = select(IntelligencePlatform)
        result = await db.execute(stmt)
        platforms = result.scalars().all()
        
        # 计算总成本
        total_cost = sum(p.total_cost for p in platforms)
        total_calls = sum(p.total_calls for p in platforms)
        
        # 简化：假设所有成本都是本月的（实际应该按时间过滤）
        month_cost = total_cost
        today_cost = 0  # 需要按日期过滤，暂时设为0
        
        # 统计启用的模型数量
        model_count = len([p for p in platforms if p.enabled])
        
        return {
            "success": True,
            "data": {
                "total_cost": total_cost,
                "month_cost": month_cost,
                "today_cost": today_cost,
                "total_calls": total_calls,
                "model_count": model_count
            }
        }
    except Exception as e:
        logger.error(f"获取成本摘要失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/usage-history")
async def get_usage_history(
    model_name: Optional[str] = None,
    days: int = Query(7, ge=1, le=90),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db)
):
    """
    获取使用历史记录
    
    Args:
        model_name: 可选，指定模型名称
        days: 查询最近N天，默认7天
        limit: 返回记录数，默认100
    
    Returns:
        使用历史记录列表
    """
    try:
        cost_manager = get_cost_manager(db)
        history = await cost_manager.get_usage_history(model_name, days, limit)
        
        return {
            "success": True,
            "data": history,
            "count": len(history)
        }
    except Exception as e:
        logger.error(f"获取使用历史失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/models/{model_name}/budget")
async def update_model_budget(
    model_name: str,
    budget: float = Query(..., ge=0),
    db: AsyncSession = Depends(get_db)
):
    """
    更新模型月度预算
    
    Args:
        model_name: 模型名称
        budget: 月度预算（元），0表示无限制
    
    Returns:
        更新结果
    """
    try:
        cost_manager = get_cost_manager(db)
        await cost_manager.update_monthly_budget(model_name, budget)
        
        return {
            "success": True,
            "message": f"已更新 {model_name} 的月度预算为 ¥{budget}"
        }
    except Exception as e:
        logger.error(f"更新预算失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/optimization-suggestions")
async def get_optimization_suggestions(db: AsyncSession = Depends(get_db)):
    """
    获取成本优化建议
    
    Returns:
        优化建议列表
    """
    try:
        cost_manager = get_cost_manager(db)
        suggestions = await cost_manager.get_cost_optimization_suggestions()
        
        return {
            "success": True,
            "data": suggestions,
            "count": len(suggestions)
        }
    except Exception as e:
        logger.error(f"获取优化建议失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/decision-interval-analysis")
async def get_decision_interval_analysis():
    """
    获取决策间隔成本分析
    
    Returns:
        不同决策间隔的成本对比
    """
    try:
        # 假设单次决策成本为 ¥1.047
        single_decision_cost = 1.047
        
        intervals = [
            {
                "name": "激进模式",
                "interval_seconds": 60,
                "interval_display": "1分钟",
                "daily_decisions": 1440,
                "daily_cost": round(1440 * single_decision_cost, 2),
                "monthly_cost": round(1440 * single_decision_cost * 30, 2),
                "recommended": False,
                "description": "高频交易，成本极高"
            },
            {
                "name": "标准模式",
                "interval_seconds": 300,
                "interval_display": "5分钟",
                "daily_decisions": 288,
                "daily_cost": round(288 * single_decision_cost, 2),
                "monthly_cost": round(288 * single_decision_cost * 30, 2),
                "recommended": False,
                "description": "中频交易，成本较高"
            },
            {
                "name": "平衡模式（当前）",
                "interval_seconds": 600,
                "interval_display": "10分钟",
                "daily_decisions": 144,
                "daily_cost": round(144 * single_decision_cost, 2),
                "monthly_cost": round(144 * single_decision_cost * 30, 2),
                "recommended": True,
                "description": "平衡性能与成本，推荐"
            },
            {
                "name": "保守模式",
                "interval_seconds": 900,
                "interval_display": "15分钟",
                "daily_decisions": 96,
                "daily_cost": round(96 * single_decision_cost, 2),
                "monthly_cost": round(96 * single_decision_cost * 30, 2),
                "recommended": True,
                "description": "低频交易，成本低"
            },
            {
                "name": "智能触发",
                "interval_seconds": 0,
                "interval_display": "事件驱动",
                "daily_decisions": 30,
                "daily_cost": round(30 * single_decision_cost, 2),
                "monthly_cost": round(30 * single_decision_cost * 30, 2),
                "recommended": True,
                "description": "只在关键时刻决策，成本最低"
            }
        ]
        
        # 计算节省比例（相对于激进模式）
        base_cost = intervals[0]["monthly_cost"]
        for interval in intervals:
            interval["savings_pct"] = round((1 - interval["monthly_cost"] / base_cost) * 100, 1)
            interval["savings_amount"] = round(base_cost - interval["monthly_cost"], 2)
        
        return {
            "success": True,
            "data": {
                "intervals": intervals,
                "current_interval": 600,
                "single_decision_cost": single_decision_cost,
                "note": "以上成本为预估值，实际成本取决于模型使用情况"
            }
        }
    except Exception as e:
        logger.error(f"获取决策间隔分析失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset-monthly-costs")
async def reset_monthly_costs(db: AsyncSession = Depends(get_db)):
    """
    重置月度成本（管理员功能，通常每月1号自动执行）
    
    Returns:
        重置结果
    """
    try:
        cost_manager = get_cost_manager(db)
        await cost_manager.reset_monthly_costs()
        
        return {
            "success": True,
            "message": "已重置所有模型的月度成本"
        }
    except Exception as e:
        logger.error(f"重置月度成本失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset-costs")
async def reset_platform_costs(
    db: AsyncSession = Depends(get_db),
    current_username: str = Depends(get_current_user)
):
    """
    重置所有平台成本为0
    
    ⚠️ 警告：这将清除所有历史成本数据！
    使用场景：
    1. 更新了价格表，想从头开始累积
    2. 测试环境清理数据
    3. 成本数据出现异常需要重置
    """
    try:
        # 管理员权限检查（通过 get_current_user 验证的用户都是管理员）
        logger.warning(f"⚠️  重置平台成本 (操作人: {current_username})")
        
        # 获取所有平台
        result = await db.execute(select(IntelligencePlatform))
        platforms = result.scalars().all()
        
        reset_count = 0
        old_total = 0.0
        
        for platform in platforms:
            old_total += platform.total_cost
            logger.info(f"   重置 {platform.name}: ¥{platform.total_cost:.4f} -> ¥0.00")
            platform.total_cost = 0.0
            platform.updated_at = datetime.utcnow()
            reset_count += 1
        
        await db.commit()
        
        logger.info(f"✅ 已重置 {reset_count} 个平台，清除总成本: ¥{old_total:.4f}")
        
        return {
            "success": True,
            "message": f"已重置 {reset_count} 个平台的成本",
            "data": {
                "reset_count": reset_count,
                "old_total_cost": old_total
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 重置成本失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/active-platforms")
async def get_active_platforms(db: AsyncSession = Depends(get_db)):
    """
    获取当前启用的智能平台列表
    
    Returns:
        启用的平台列表及其使用统计
    """
    try:
        # 查询所有启用的平台
        stmt = select(IntelligencePlatform).where(IntelligencePlatform.enabled == True)
        result = await db.execute(stmt)
        platforms = result.scalars().all()
        
        platform_list = []
        for platform in platforms:
            platform_list.append({
                "id": platform.id,
                "name": platform.name,
                "provider": platform.provider,
                "platform_type": platform.platform_type,
                "base_url": platform.base_url,
                "enabled": platform.enabled,
                "has_api_key": bool(platform.api_key and len(platform.api_key) > 0),
                "total_calls": platform.total_calls,
                "successful_calls": platform.successful_calls,
                "failed_calls": platform.failed_calls,
                "success_rate": round(platform.successful_calls / platform.total_calls * 100, 1) if platform.total_calls > 0 else 0,
                "total_cost": platform.total_cost,
                "health_status": platform.health_status or "unknown",
                "last_health_check": platform.last_health_check.isoformat() if platform.last_health_check else None
            })
        
        return {
            "success": True,
            "data": platform_list,
            "count": len(platform_list)
        }
    except Exception as e:
        logger.error(f"获取启用平台失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models-with-platforms")
async def get_models_with_platforms(db: AsyncSession = Depends(get_db)):
    """
    获取AI模型定价，并关联实际使用的云平台
    
    Returns:
        模型列表及其关联的云平台信息
    """
    try:
        # 获取模型统计
        cost_manager = get_cost_manager(db)
        models = await cost_manager.get_model_stats()
        
        # 获取启用的平台
        stmt = select(IntelligencePlatform).where(IntelligencePlatform.enabled == True)
        result = await db.execute(stmt)
        platforms = result.scalars().all()
        
        # 构建平台映射
        platform_map = {
            "qwen": [],
            "baidu": [],
            "tencent": [],
            "volcano": [],
            "deepseek": [],
            "openai": []
        }
        
        for platform in platforms:
            platform_info = {
                "name": platform.name,
                "provider": platform.provider,
                "type": platform.platform_type,
                "total_calls": platform.total_calls,
                "success_rate": round(platform.successful_calls / platform.total_calls * 100, 1) if platform.total_calls > 0 else 0,
                "total_cost": platform.total_cost
            }
            
            if platform.provider in platform_map:
                platform_map[platform.provider].append(platform_info)
        
        # 为每个模型关联对应的平台
        for model in models:
            model_provider = model.get("provider", "").lower()
            model["active_platforms"] = platform_map.get(model_provider, [])
            model["platform_count"] = len(model["active_platforms"])
        
        return {
            "success": True,
            "data": {
                "models": models,
                "platform_summary": {
                    provider: {
                        "count": len(platforms),
                        "total_calls": sum(p["total_calls"] for p in platforms),
                        "total_cost": sum(p["total_cost"] for p in platforms)
                    }
                    for provider, platforms in platform_map.items() if platforms
                }
            }
        }
    except Exception as e:
        logger.error(f"获取模型和平台关联信息失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sync-billing")
async def sync_cloud_billing(db: AsyncSession = Depends(get_db)):
    """
    从云平台同步真实账单数据
    
    从各大云平台（阿里云、百度云、腾讯云、火山引擎、DeepSeek）
    获取真实的使用费用并更新到数据库
    
    Returns:
        同步结果摘要
    """
    try:
        logger.info("🔄 开始同步云平台账单...")
        
        billing_sync = get_billing_sync()
        result = await billing_sync.sync_all_platforms(db)
        
        return {
            "success": True,
            "message": "账单同步完成",
            "data": result
        }
        
    except Exception as e:
        logger.error(f"❌ 账单同步失败: {e}")
        raise HTTPException(status_code=500, detail=f"账单同步失败: {str(e)}")

