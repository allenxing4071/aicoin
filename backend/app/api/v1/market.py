"""Market data API endpoints"""

from fastapi import APIRouter, HTTPException
from typing import List
from decimal import Decimal
import logging
import json

from app.schemas.market import KlineData, OrderbookData, TickerData
from app.services.market.hyperliquid_client import hyperliquid_client
from app.core.redis_client import redis_client

router = APIRouter()
logger = logging.getLogger(__name__)

# 市场数据缓存配置
TICKERS_CACHE_KEY = "market:tickers:all"
TICKERS_CACHE_TTL = 1  # 缓存1秒，高频调用优化


def get_market_data_service():
    """获取全局的market data service"""
    from app.main import market_data_service
    if market_data_service is None:
        logger.error("❌ Market data service not initialized!")
        raise HTTPException(status_code=503, detail="Market data service not available")
    return market_data_service


@router.get("/klines", response_model=List[KlineData])
async def get_klines_query(
    symbol: str,
    interval: str = "1h",
    limit: int = 100
):
    """
    获取K线数据（查询参数版本）
    
    Args:
        symbol: 交易品种 (如: BTCUSDT, BTC, ETH)
        interval: K线周期 (1m, 5m, 1h, 4h, 1d)
        limit: 返回数量
        
    Returns:
        K线数据列表
    """
    try:
        # 处理symbol格式：BTCUSDT -> BTC
        if symbol.endswith('USDT'):
            symbol = symbol[:-4]
        
        service = get_market_data_service()
        klines = await service.get_klines(symbol, interval, limit)
        return [KlineData(**k) for k in klines]
        
    except Exception as e:
        logger.error(f"Error fetching klines for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kline/{symbol}", response_model=List[KlineData])
async def get_kline(
    symbol: str,
    interval: str = "1h",
    limit: int = 100
):
    """
    获取K线数据（路径参数版本）
    
    Args:
        symbol: 交易品种
        interval: K线周期 (1m, 5m, 1h, 4h, 1d)
        limit: 返回数量
        
    Returns:
        K线数据列表
    """
    try:
        service = get_market_data_service()
        klines = await service.get_klines(symbol, interval, limit)
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
        service = get_market_data_service()
        orderbook = await service.get_orderbook(symbol, depth)
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
        service = get_market_data_service()
        ticker = await service.get_ticker(symbol)
        return TickerData(**ticker)
        
    except Exception as e:
        logger.error(f"Error fetching ticker: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/tickers", response_model=List[TickerData])
async def get_all_tickers(force_refresh: bool = False):
    """
    获取所有交易对的实时价格（带Redis缓存优化）
    
    Args:
        force_refresh: 是否强制刷新缓存
    
    Returns:
        所有交易对的实时价格列表
    """
    try:
        # 1. 尝试从缓存获取（除非强制刷新）
        if not force_refresh:
            try:
                cached_data = await redis_client.get(TICKERS_CACHE_KEY)
                if cached_data:
                    logger.debug(f"✅ 行情数据命中缓存")
                    return [TickerData(**t) for t in cached_data]
            except Exception as cache_err:
                logger.warning(f"缓存读取失败: {cache_err}")
        
        # 2. 从市场服务获取最新数据
        symbols = ["BTC", "ETH", "SOL", "BNB", "DOGE", "XRP"]
        service = get_market_data_service()
        tickers = []
        
        for symbol in symbols:
            try:
                ticker = await service.get_ticker(symbol)
                tickers.append(TickerData(**ticker))
            except Exception as e:
                logger.warning(f"Error fetching ticker for {symbol}: {e}")
                continue
        
        # 3. 写入缓存
        if tickers:
            try:
                await redis_client.set(
                    TICKERS_CACHE_KEY,
                    [t.dict() for t in tickers],
                    expire=TICKERS_CACHE_TTL
                )
                logger.debug(f"💾 行情数据已缓存 {TICKERS_CACHE_TTL}秒")
            except Exception as cache_err:
                logger.warning(f"缓存写入失败: {cache_err}")
        
        return tickers
        
    except Exception as e:
        logger.error(f"Error fetching all tickers: {e}")
        raise HTTPException(status_code=500, detail=str(e))

