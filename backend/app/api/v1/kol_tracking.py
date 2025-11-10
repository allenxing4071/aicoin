"""
KOL追踪API

提供KOL数据源管理和意见查询功能
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from pydantic import BaseModel
from datetime import datetime

from app.core.database import get_db
from app.models.kol import KOLSource, KOLOpinion

router = APIRouter(prefix="/kol", tags=["KOL追踪"])


# Pydantic模型
class KOLSourceCreate(BaseModel):
    name: str
    platform: str  # twitter/telegram
    channel_id: str
    influence_score: float = 0.0
    enabled: bool = True


class KOLSourceUpdate(BaseModel):
    name: Optional[str] = None
    platform: Optional[str] = None
    channel_id: Optional[str] = None
    influence_score: Optional[float] = None
    enabled: Optional[bool] = None


class KOLSourceResponse(BaseModel):
    id: int
    name: str
    platform: str
    channel_id: str
    influence_score: float
    accuracy_rate: float
    enabled: bool
    total_posts: int
    successful_predictions: int
    last_update: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class KOLOpinionResponse(BaseModel):
    id: int
    kol_id: int
    kol_name: str
    platform: str
    content: str
    sentiment: Optional[str]
    mentioned_coins: Optional[List[str]]
    confidence: Optional[float]
    post_url: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True


# API端点
@router.get("/sources", response_model=List[KOLSourceResponse])
async def get_kol_sources(
    platform: Optional[str] = None,
    enabled: Optional[bool] = None,
    db: AsyncSession = Depends(get_db)
):
    """获取KOL列表"""
    try:
        stmt = select(KOLSource)
        
        if platform:
            stmt = stmt.where(KOLSource.platform == platform)
        if enabled is not None:
            stmt = stmt.where(KOLSource.enabled == enabled)
        
        stmt = stmt.order_by(desc(KOLSource.influence_score))
        
        result = await db.execute(stmt)
        sources = result.scalars().all()
        
        return sources
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取KOL列表失败: {str(e)}")


@router.post("/sources", response_model=KOLSourceResponse)
async def create_kol_source(
    source: KOLSourceCreate,
    db: AsyncSession = Depends(get_db)
):
    """添加KOL"""
    try:
        # 检查是否已存在
        stmt = select(KOLSource).where(
            KOLSource.platform == source.platform,
            KOLSource.channel_id == source.channel_id
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()
        
        if existing:
            raise HTTPException(status_code=400, detail="该KOL已存在")
        
        # 创建新KOL
        db_source = KOLSource(**source.model_dump())
        db.add(db_source)
        await db.commit()
        await db.refresh(db_source)
        
        return db_source
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"添加KOL失败: {str(e)}")


@router.put("/sources/{source_id}", response_model=KOLSourceResponse)
async def update_kol_source(
    source_id: int,
    source: KOLSourceUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新KOL"""
    try:
        stmt = select(KOLSource).where(KOLSource.id == source_id)
        result = await db.execute(stmt)
        db_source = result.scalar_one_or_none()
        
        if not db_source:
            raise HTTPException(status_code=404, detail="KOL不存在")
        
        # 更新字段
        for key, value in source.model_dump(exclude_unset=True).items():
            setattr(db_source, key, value)
        
        await db.commit()
        await db.refresh(db_source)
        
        return db_source
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"更新KOL失败: {str(e)}")


@router.delete("/sources/{source_id}")
async def delete_kol_source(
    source_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除KOL"""
    try:
        stmt = select(KOLSource).where(KOLSource.id == source_id)
        result = await db.execute(stmt)
        db_source = result.scalar_one_or_none()
        
        if not db_source:
            raise HTTPException(status_code=404, detail="KOL不存在")
        
        await db.delete(db_source)
        await db.commit()
        
        return {"success": True, "message": "KOL已删除"}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"删除KOL失败: {str(e)}")


@router.get("/opinions")
async def get_kol_opinions(
    kol_id: Optional[int] = None,
    sentiment: Optional[str] = None,
    limit: int = Query(50, le=200),
    db: AsyncSession = Depends(get_db)
):
    """获取KOL意见列表"""
    try:
        stmt = select(KOLOpinion, KOLSource.name).join(
            KOLSource, KOLOpinion.kol_id == KOLSource.id
        )
        
        if kol_id:
            stmt = stmt.where(KOLOpinion.kol_id == kol_id)
        if sentiment:
            stmt = stmt.where(KOLOpinion.sentiment == sentiment)
        
        stmt = stmt.order_by(desc(KOLOpinion.created_at)).limit(limit)
        
        result = await db.execute(stmt)
        rows = result.all()
        
        opinions = [
            {
                "id": opinion.id,
                "kol_id": opinion.kol_id,
                "kol_name": kol_name,
                "platform": opinion.platform,
                "content": opinion.content,
                "sentiment": opinion.sentiment,
                "mentioned_coins": opinion.mentioned_coins,
                "confidence": opinion.confidence,
                "post_url": opinion.post_url,
                "created_at": opinion.created_at,
            }
            for opinion, kol_name in rows
        ]
        
        return {"success": True, "data": opinions}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取意见列表失败: {str(e)}")


@router.get("/statistics")
async def get_kol_statistics(db: AsyncSession = Depends(get_db)):
    """获取KOL统计数据"""
    try:
        # 总KOL数
        total_kols_stmt = select(func.count(KOLSource.id))
        total_kols = await db.scalar(total_kols_stmt) or 0
        
        # 启用的KOL数
        enabled_kols_stmt = select(func.count(KOLSource.id)).where(KOLSource.enabled == True)
        enabled_kols = await db.scalar(enabled_kols_stmt) or 0
        
        # 总意见数
        total_opinions_stmt = select(func.count(KOLOpinion.id))
        total_opinions = await db.scalar(total_opinions_stmt) or 0
        
        # 平均准确率
        avg_accuracy_stmt = select(func.avg(KOLSource.accuracy_rate))
        avg_accuracy = await db.scalar(avg_accuracy_stmt) or 0
        
        return {
            "success": True,
            "data": {
                "total_kols": total_kols,
                "enabled_kols": enabled_kols,
                "total_opinions": total_opinions,
                "avg_accuracy": float(avg_accuracy),
            }
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取统计数据失败: {str(e)}")

