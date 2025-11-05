"""Intelligence Platforms API - 情报平台管理API"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any
from datetime import datetime

from app.core.database import get_db
from app.models.intelligence_platform import IntelligencePlatform
from pydantic import BaseModel

router = APIRouter()


class PlatformCreate(BaseModel):
    """创建平台请求"""
    name: str
    provider: str  # baidu/tencent/volcano/aws
    platform_type: str  # qwen_search/qwen_deep/free
    api_key: str | None = None
    base_url: str
    enabled: bool = True
    config_json: Dict[str, Any] | None = None


class PlatformUpdate(BaseModel):
    """更新平台请求"""
    name: str | None = None
    api_key: str | None = None
    enabled: bool | None = None
    config_json: Dict[str, Any] | None = None


@router.get("/platforms")
async def list_platforms(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """列出所有情报平台"""
    result = await db.execute(select(IntelligencePlatform))
    platforms = result.scalars().all()
    
    return {
        "platforms": [p.to_dict() for p in platforms],
        "total": len(platforms)
    }


@router.post("/platforms")
async def create_platform(
    platform: PlatformCreate,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """添加新平台"""
    new_platform = IntelligencePlatform(
        name=platform.name,
        provider=platform.provider,
        platform_type=platform.platform_type,
        api_key=platform.api_key,
        base_url=platform.base_url,
        enabled=platform.enabled,
        config_json=platform.config_json
    )
    
    db.add(new_platform)
    await db.commit()
    await db.refresh(new_platform)
    
    return {"platform": new_platform.to_dict()}


@router.patch("/platforms/{platform_id}")
async def update_platform(
    platform_id: int,
    update: PlatformUpdate,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """更新平台配置"""
    result = await db.execute(
        select(IntelligencePlatform).where(IntelligencePlatform.id == platform_id)
    )
    platform = result.scalar_one_or_none()
    
    if not platform:
        raise HTTPException(status_code=404, detail="平台不存在")
    
    if update.name is not None:
        platform.name = update.name
    if update.api_key is not None:
        platform.api_key = update.api_key
    if update.enabled is not None:
        platform.enabled = update.enabled
    if update.config_json is not None:
        platform.config_json = update.config_json
    
    platform.updated_at = datetime.utcnow()
    
    await db.commit()
    await db.refresh(platform)
    
    return {"platform": platform.to_dict()}


@router.delete("/platforms/{platform_id}")
async def delete_platform(
    platform_id: int,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, str]:
    """删除平台"""
    result = await db.execute(
        select(IntelligencePlatform).where(IntelligencePlatform.id == platform_id)
    )
    platform = result.scalar_one_or_none()
    
    if not platform:
        raise HTTPException(status_code=404, detail="平台不存在")
    
    await db.delete(platform)
    await db.commit()
    
    return {"message": "平台已删除"}


@router.get("/platforms/{platform_id}/health")
async def check_platform_health(
    platform_id: int,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """健康检查"""
    result = await db.execute(
        select(IntelligencePlatform).where(IntelligencePlatform.id == platform_id)
    )
    platform = result.scalar_one_or_none()
    
    if not platform:
        raise HTTPException(status_code=404, detail="平台不存在")
    
    # TODO: 实际健康检查
    is_healthy = platform.enabled
    
    platform.last_health_check = datetime.utcnow()
    platform.health_status = "healthy" if is_healthy else "unhealthy"
    
    await db.commit()
    
    return {
        "platform_id": platform_id,
        "health_status": platform.health_status,
        "last_check": platform.last_health_check.isoformat()
    }


@router.get("/platforms/stats")
async def get_platforms_stats(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """获取平台统计信息"""
    result = await db.execute(select(IntelligencePlatform))
    platforms = result.scalars().all()
    
    total_calls = sum(p.total_calls for p in platforms)
    total_cost = sum(p.total_cost for p in platforms)
    
    return {
        "total_platforms": len(platforms),
        "enabled_platforms": sum(1 for p in platforms if p.enabled),
        "total_calls": total_calls,
        "total_cost": total_cost,
        "by_provider": {
            p.provider: {
                "calls": p.total_calls,
                "success_rate": p.successful_calls / p.total_calls if p.total_calls > 0 else 0,
                "cost": p.total_cost
            }
            for p in platforms
        }
    }

