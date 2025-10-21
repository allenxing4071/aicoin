"""Market data API endpoints"""

from fastapi import APIRouter, HTTPException
from typing import List
from decimal import Decimal
import logging

from app.schemas.market import KlineData, OrderbookData, TickerData
from app.services.market.hyperliquid_client import hyperliquid_client

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/kline/{symbol}", response_model=List[KlineData])
async def get_kline(
    symbol: str,
    interval: str = "1h",
    limit: int = 100
):
    """
    获取K线数据
    
    Args:
        symbol: 交易品种
        interval: K线周期 (1m, 5m, 1h, 4h, 1d)
        limit: 返回数量
        
    Returns:
        K线数据列表
    """
    try:
        klines = await hyperliquid_client.get_klines(symbol, interval, limit)
        return [KlineData(**k) for k in klines]
        
    except Exception as e:
        logger.error(f"Error fetching klines: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/orderbook/{symbol}", response_model=OrderbookData)
async def get_orderbook(
    symbol: str,
    depth: int = 20
):
    """
    获取订单簿
    
    Args:
        symbol: 交易品种
        depth: 深度档位
        
    Returns:
        订单簿数据
    """
    try:
        orderbook = await hyperliquid_client.get_orderbook(symbol, depth)
        return OrderbookData(**orderbook)
        
    except Exception as e:
        logger.error(f"Error fetching orderbook: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/ticker/{symbol}", response_model=TickerData)
async def get_ticker(symbol: str):
    """
    获取实时价格
    
    Args:
        symbol: 交易品种
        
    Returns:
        实时价格数据
    """
    try:
        ticker = await hyperliquid_client.get_ticker(symbol)
        return TickerData(**ticker)
        
    except Exception as e:
        logger.error(f"Error fetching ticker: {e}")
        raise HTTPException(status_code=500, detail=str(e))

