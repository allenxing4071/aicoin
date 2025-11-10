"""Platform Budget Management API

管理AI平台的预算设置和告警
"""

from typing import Dict, Any, List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from pydantic import BaseModel

from app.core.database import get_db
from app.models.intelligence_platform import IntelligencePlatform

router = APIRouter()


class BudgetUpdate(BaseModel):
    """预算更新请求"""
    monthly_budget: float
    alert_threshold: float = 80.0  # 默认80%告警


class GlobalBudgetUpdate(BaseModel):
    """全局预算设置"""
    total_budget: float
    alert_threshold: float = 80.0


@router.get("/budget/summary")
async def get_budget_summary(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """获取预算使用总览"""
    result = await db.execute(select(IntelligencePlatform))
    platforms = result.scalars().all()
    
    total_budget = 0.0
    total_used = 0.0
    platforms_data = []
    
    for platform in platforms:
        config = platform.config_json or {}
        monthly_budget = config.get('monthly_budget', 0.0)
        total_budget += monthly_budget
        total_used += platform.total_cost
        
        platforms_data.append({
            "id": platform.id,
            "name": platform.name,
            "provider": platform.provider,
            "monthly_budget": monthly_budget,
            "current_cost": platform.total_cost,
            "usage_percentage": (platform.total_cost / monthly_budget * 100) if monthly_budget > 0 else 0,
            "alert_threshold": config.get('alert_threshold', 80.0),
        })
    
    return {
        "success": True,
        "data": {
            "total_budget": total_budget,
            "total_used": total_used,
            "budget_usage": (total_used / total_budget * 100) if total_budget > 0 else 0,
            "platforms": platforms_data,
        }
    }


@router.put("/platforms/{platform_id}/budget")
async def update_platform_budget(
    platform_id: int,
    budget: BudgetUpdate,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """更新单个平台的预算"""
    result = await db.execute(
        select(IntelligencePlatform).where(IntelligencePlatform.id == platform_id)
    )
    platform = result.scalar_one_or_none()
    
    if not platform:
        raise HTTPException(status_code=404, detail="平台不存在")
    
    # 更新config_json中的预算信息
    # 注意：需要创建新的dict对象，否则SQLAlchemy不会检测到JSON字段的变化
    config = dict(platform.config_json or {})
    config['monthly_budget'] = budget.monthly_budget
    config['alert_threshold'] = budget.alert_threshold
    
    # 使用flag_modified来标记JSON字段已修改
    from sqlalchemy.orm.attributes import flag_modified
    platform.config_json = config
    flag_modified(platform, 'config_json')
    
    await db.commit()
    await db.refresh(platform)
    
    # 验证保存是否成功
    print(f"✅ 预算保存成功: {platform.name} - 月度预算: ¥{budget.monthly_budget}, 告警阈值: {budget.alert_threshold}%")
    print(f"   当前config_json: {platform.config_json}")
    
    return {
        "success": True,
        "message": f"已更新 {platform.name} 的预算设置",
        "data": {
            "platform_id": platform_id,
            "platform_name": platform.name,
            "monthly_budget": budget.monthly_budget,
            "alert_threshold": budget.alert_threshold,
            "config_json": platform.config_json,
        }
    }


@router.get("/budget/alerts")
async def get_budget_alerts(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """获取预算告警列表"""
    result = await db.execute(select(IntelligencePlatform))
    platforms = result.scalars().all()
    
    alerts = []
    
    for platform in platforms:
        config = platform.config_json or {}
        monthly_budget = config.get('monthly_budget', 0.0)
        alert_threshold = config.get('alert_threshold', 80.0)
        
        if monthly_budget > 0:
            usage_percentage = (platform.total_cost / monthly_budget) * 100
            
            if usage_percentage >= 100:
                alerts.append({
                    "level": "critical",
                    "platform_id": platform.id,
                    "platform_name": platform.name,
                    "message": f"{platform.name} 已超出月度预算",
                    "usage_percentage": usage_percentage,
                    "budget": monthly_budget,
                    "used": platform.total_cost,
                })
            elif usage_percentage >= alert_threshold:
                alerts.append({
                    "level": "warning",
                    "platform_id": platform.id,
                    "platform_name": platform.name,
                    "message": f"{platform.name} 预算使用率已达 {usage_percentage:.1f}%",
                    "usage_percentage": usage_percentage,
                    "budget": monthly_budget,
                    "used": platform.total_cost,
                })
    
    return {
        "success": True,
        "data": {
            "alerts": alerts,
            "total_alerts": len(alerts),
            "critical_count": len([a for a in alerts if a['level'] == 'critical']),
            "warning_count": len([a for a in alerts if a['level'] == 'warning']),
        }
    }


@router.post("/budget/check")
async def check_budget_status(
    platform_id: int,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """检查特定平台的预算状态"""
    result = await db.execute(
        select(IntelligencePlatform).where(IntelligencePlatform.id == platform_id)
    )
    platform = result.scalar_one_or_none()
    
    if not platform:
        raise HTTPException(status_code=404, detail="平台不存在")
    
    config = platform.config_json or {}
    monthly_budget = config.get('monthly_budget', 0.0)
    alert_threshold = config.get('alert_threshold', 80.0)
    
    if monthly_budget == 0:
        return {
            "success": True,
            "data": {
                "has_budget": False,
                "message": "未设置预算",
            }
        }
    
    usage_percentage = (platform.total_cost / monthly_budget) * 100
    remaining = monthly_budget - platform.total_cost
    
    status = "normal"
    if usage_percentage >= 100:
        status = "exceeded"
    elif usage_percentage >= alert_threshold:
        status = "warning"
    
    return {
        "success": True,
        "data": {
            "has_budget": True,
            "status": status,
            "monthly_budget": monthly_budget,
            "current_cost": platform.total_cost,
            "remaining": remaining,
            "usage_percentage": usage_percentage,
            "alert_threshold": alert_threshold,
            "should_alert": usage_percentage >= alert_threshold,
            "should_disable": usage_percentage >= 100,
        }
    }

