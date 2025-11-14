"""
Debate API - 辩论系统接口
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, desc
from typing import List, Optional
from datetime import datetime, timedelta
import logging

from app.core.database import get_db
from app.models.debate import DebateHistory, DebateConfig, DebateStatistics
from app.schemas.debate import (
    DebateHistoryResponse,
    DebateHistoryListResponse,
    DebateConfigResponse,
    DebateConfigUpdate,
    DebateStatisticsResponse,
    DebateTriggerRequest,
    DebateTriggerResponse,
    DebateMemoryStats
)
from app.services.decision.debate_config import DebateConfigManager
from app.services.decision.debate_rate_limiter import DebateRateLimiter
from app.core.redis_client import get_redis_client

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/history", response_model=DebateHistoryListResponse)
async def get_debate_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    symbol: Optional[str] = None,
    recommendation: Optional[str] = None,
    db: AsyncSession = Depends(get_db)
):
    """
    获取辩论历史列表
    
    Args:
        skip: 跳过记录数
        limit: 返回记录数
        symbol: 筛选币种
        recommendation: 筛选推荐结果（BUY/SELL/HOLD）
    """
    try:
        # 构建查询
        query = select(DebateHistory)
        
        # 添加筛选条件
        conditions = []
        if symbol:
            conditions.append(DebateHistory.symbol == symbol)
        if recommendation:
            conditions.append(DebateHistory.final_recommendation == recommendation)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        # 获取总数
        count_query = select(func.count()).select_from(DebateHistory)
        if conditions:
            count_query = count_query.where(and_(*conditions))
        
        total_result = await db.execute(count_query)
        total = total_result.scalar()
        
        # 获取数据
        query = query.order_by(desc(DebateHistory.created_at)).offset(skip).limit(limit)
        result = await db.execute(query)
        debates = result.scalars().all()
        
        return DebateHistoryListResponse(
            total=total,
            items=[DebateHistoryResponse.model_validate(d) for d in debates]
        )
        
    except Exception as e:
        logger.error(f"获取辩论历史失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history/{debate_id}", response_model=DebateHistoryResponse)
async def get_debate_detail(
    debate_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取辩论详情"""
    try:
        stmt = select(DebateHistory).where(DebateHistory.id == debate_id)
        result = await db.execute(stmt)
        debate = result.scalars().first()
        
        if not debate:
            raise HTTPException(status_code=404, detail="辩论记录不存在")
        
        return DebateHistoryResponse.model_validate(debate)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取辩论详情失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/config", response_model=List[DebateConfigResponse])
async def get_debate_config(
    db: AsyncSession = Depends(get_db)
):
    """获取所有辩论配置"""
    try:
        stmt = select(DebateConfig)
        result = await db.execute(stmt)
        configs = result.scalars().all()
        
        return [DebateConfigResponse.model_validate(c) for c in configs]
        
    except Exception as e:
        logger.error(f"获取辩论配置失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/config/{config_key}")
async def update_debate_config(
    config_key: str,
    config_update: DebateConfigUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新辩论配置"""
    try:
        config_manager = DebateConfigManager(db)
        success = await config_manager.set_config(config_key, config_update.config_value)
        
        if not success:
            raise HTTPException(status_code=500, detail="更新配置失败")
        
        return {"success": True, "message": f"配置 {config_key} 已更新"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新辩论配置失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/statistics", response_model=List[DebateStatisticsResponse])
async def get_debate_statistics(
    days: int = Query(7, ge=1, le=90),
    db: AsyncSession = Depends(get_db)
):
    """
    获取辩论统计数据
    
    Args:
        days: 获取最近N天的统计
    """
    try:
        start_date = datetime.now() - timedelta(days=days)
        
        stmt = select(DebateStatistics).where(
            DebateStatistics.date >= start_date
        ).order_by(DebateStatistics.date)
        
        result = await db.execute(stmt)
        stats = result.scalars().all()
        
        return [DebateStatisticsResponse.model_validate(s) for s in stats]
        
    except Exception as e:
        logger.error(f"获取辩论统计失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/trigger", response_model=DebateTriggerResponse)
async def trigger_debate_manually(
    request: DebateTriggerRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    手动触发辩论（测试用）
    
    ⚠️  注意：这是管理员功能，会消耗 API 额度
    """
    try:
        # TODO: 实现手动触发辩论逻辑
        # 这需要初始化 DebateCoordinator 并执行辩论
        
        return DebateTriggerResponse(
            success=False,
            error="手动触发辩论功能暂未实现"
        )
        
    except Exception as e:
        logger.error(f"手动触发辩论失败: {e}", exc_info=True)
        return DebateTriggerResponse(
            success=False,
            error=str(e)
        )


@router.get("/memory/stats", response_model=DebateMemoryStats)
async def get_memory_stats():
    """获取辩论记忆统计"""
    try:
        # TODO: 实现记忆统计逻辑
        # 需要访问 DebateMemoryManager
        
        return DebateMemoryStats(
            bull_memory_count=0,
            bear_memory_count=0,
            manager_memory_count=0,
            total_memory_count=0
        )
        
    except Exception as e:
        logger.error(f"获取记忆统计失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/memory")
async def clear_debate_memory():
    """
    清空辩论记忆（危险操作）
    
    ⚠️  注意：这将删除所有辩论记忆，无法恢复
    """
    try:
        # TODO: 实现清空记忆逻辑
        # 需要访问 DebateMemoryManager
        
        return {
            "success": False,
            "message": "清空记忆功能暂未实现"
        }
        
    except Exception as e:
        logger.error(f"清空记忆失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rate-limit")
async def get_rate_limit_status():
    """获取限流状态"""
    try:
        redis_client = await get_redis_client()
        limiter = DebateRateLimiter(redis_client, daily_limit=100, hourly_limit=10)
        
        counts = await limiter.get_current_counts()
        
        return {
            "success": True,
            "data": counts
        }
        
    except Exception as e:
        logger.error(f"获取限流状态失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rate-limit/reset")
async def reset_rate_limit():
    """
    重置限流计数（管理员操作）
    
    ⚠️  注意：这将重置今日和当前小时的辩论计数
    """
    try:
        redis_client = await get_redis_client()
        limiter = DebateRateLimiter(redis_client, daily_limit=100, hourly_limit=10)
        
        await limiter.reset_counts()
        
        return {
            "success": True,
            "message": "限流计数已重置"
        }
        
    except Exception as e:
        logger.error(f"重置限流失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

