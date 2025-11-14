"""Account API endpoints"""

from fastapi import APIRouter, HTTPException, Depends, Query
import logging
import json
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.account import AccountInfo, PositionInfo
from app.schemas.admin import AccountSnapshotRecord
from app.models.account import AccountSnapshot
from app.services.market.hyperliquid_client import hyperliquid_client
from app.core.redis_client import redis_client
from app.core.database import get_db

router = APIRouter()
logger = logging.getLogger(__name__)

# 账户信息缓存配置
ACCOUNT_CACHE_KEY = "account:info"
ACCOUNT_CACHE_TTL = 2  # 缓存2秒，平衡实时性和性能


def get_trading_service():
    """获取全局的trading service"""
    from app.main import trading_service
    if trading_service is None:
        logger.error("❌ Trading service not initialized!")
        raise HTTPException(status_code=503, detail="Trading service not available")
    return trading_service


@router.get("/info", response_model=AccountInfo)
async def get_account_info(force_refresh: bool = False):
    """
    获取账户信息（带Redis缓存优化）
    
    Args:
        force_refresh: 是否强制刷新缓存
    
    Returns:
        账户信息(余额、持仓等)
    """
    try:
        # 1. 尝试从缓存获取（除非强制刷新）
        if not force_refresh:
            try:
                cached_json = await redis_client.get(ACCOUNT_CACHE_KEY)
                if cached_json:
                    logger.debug(f"✅ 账户信息命中缓存")
                    # Redis客户端的get方法已经解析JSON，直接返回dict
                    if isinstance(cached_json, str):
                        cached_data = json.loads(cached_json)
                    else:
                        cached_data = cached_json
                    return AccountInfo(**cached_data)
            except Exception as cache_err:
                logger.warning(f"缓存读取失败，从源获取: {cache_err}")
        
        # 2. 从Hyperliquid API获取最新数据
        service = get_trading_service()
        account_state = await service.get_account_state()
        
        # 3. 解析数据
        margin_summary = account_state.get('marginSummary', {})
        balance = str(margin_summary.get('accountValue', '0'))
        equity = str(margin_summary.get('accountValue', '0'))
        unrealized_pnl = str(margin_summary.get('totalNtlPos', '0'))
        
        asset_positions = account_state.get('assetPositions', [])
        positions = [PositionInfo(**p) for p in asset_positions] if asset_positions else []
        
        account_info = AccountInfo(
            balance=balance,
            equity=equity,
            unrealized_pnl=unrealized_pnl,
            realized_pnl='0',
            positions=positions
        )
        
        # 4. 写入缓存（使用json()方法避免Decimal序列化问题）
        try:
            # 使用Pydantic的json()方法，它会正确处理Decimal类型
            account_json_str = account_info.json()
            await redis_client.set(
                ACCOUNT_CACHE_KEY,
                json.loads(account_json_str),  # 转为dict存储
                expire=ACCOUNT_CACHE_TTL
            )
            logger.debug(f"💾 账户信息已缓存 {ACCOUNT_CACHE_TTL}秒")
        except Exception as cache_err:
            logger.warning(f"缓存写入失败: {cache_err}")
        
        return account_info
        
    except Exception as e:
        logger.error(f"Error fetching account info: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/positions", response_model=list[PositionInfo])
async def get_positions():
    """
    获取持仓列表
    
    Returns:
        持仓列表
    """
    try:
        service = get_trading_service()
        account_state = await service.get_account_state()
        asset_positions = account_state.get('assetPositions', [])
        return [PositionInfo(**p) for p in asset_positions] if asset_positions else []
        
    except Exception as e:
        logger.error(f"Error fetching positions: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/value")
async def get_account_value():
    """
    获取账户价值
    
    Returns:
        账户价值信息
    """
    try:
        client = get_hyperliquid_client()
        balance_data = await client.get_account_balance()
        
        return {
            "success": True,
            "total_value": float(balance_data.get('equity', '0')),
            "cash": float(balance_data.get('balance', '0')),
            "unrealized_pnl": float(balance_data.get('unrealized_pnl', '0'))
        }
        
    except Exception as e:
        logger.error(f"Error fetching account value: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/snapshots", response_model=List[AccountSnapshotRecord])
async def get_account_snapshots(
    hours: int = Query(default=72, ge=1, le=720, description="查询多少小时的历史数据"),
    limit: int = Query(default=500, ge=10, le=1000, description="返回的数据点数量"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取账户快照历史数据
    
    Args:
        hours: 查询多少小时的历史数据（默认72小时）
        limit: 返回的数据点数量（默认500）
        db: 数据库会话
        
    Returns:
        账户快照列表，按时间倒序排列
    """
    try:
        # 计算起始时间
        start_time = datetime.utcnow() - timedelta(hours=hours)
        
        # 查询数据库
        query = (
            select(AccountSnapshot)
            .where(AccountSnapshot.timestamp >= start_time)
            .order_by(desc(AccountSnapshot.timestamp))
            .limit(limit)
        )
        
        result = await db.execute(query)
        snapshots = result.scalars().all()
        
        # 转换为响应模型
        snapshot_records = [AccountSnapshotRecord.model_validate(s) for s in snapshots]
        
        logger.info(f"✅ 返回 {len(snapshot_records)} 条账户快照记录（最近 {hours} 小时）")
        return snapshot_records
        
    except Exception as e:
        logger.error(f"Error fetching account snapshots: {e}")
        raise HTTPException(status_code=500, detail=str(e))

