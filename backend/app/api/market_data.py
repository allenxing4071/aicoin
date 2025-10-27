"""
实时行情数据 API
提供价格、K线、订单簿等市场数据
"""

from fastapi import APIRouter, Depends, HTTPException
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

from app.services.hyperliquid_market_data import HyperliquidMarketData
from app.websocket.manager import websocket_manager

logger = logging.getLogger(__name__)

router = APIRouter()

# 全局市场数据服务实例
market_data_service: Optional[HyperliquidMarketData] = None

def get_market_data_service() -> HyperliquidMarketData:
    """获取市场数据服务实例"""
    global market_data_service
    if market_data_service is None:
        # 如果服务未初始化，尝试手动初始化
        try:
            from app.core.redis_client import redis_client
            import asyncio
            
            async def init_service():
                await redis_client.connect()
                service = HyperliquidMarketData(redis_client, testnet=True)
                await service.start()
                return service
            
            # 在事件循环中运行初始化
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # 如果事件循环正在运行，使用新的事件循环
                    import concurrent.futures
                    import threading
                    
                    def run_in_new_loop():
                        new_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(new_loop)
                        try:
                            return new_loop.run_until_complete(init_service())
                        finally:
                            new_loop.close()
                    
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        future = executor.submit(run_in_new_loop)
                        market_data_service = future.result()
                else:
                    market_data_service = asyncio.run(init_service())
            except RuntimeError:
                # 如果没有事件循环，创建新的
                market_data_service = asyncio.run(init_service())
            
            logger.info("Market data service initialized on demand")
        except Exception as e:
            logger.error(f"Failed to initialize market data service: {e}")
            raise HTTPException(status_code=503, detail="Market data service not initialized")
    
    return market_data_service

def set_market_data_service(service: HyperliquidMarketData):
    """设置市场数据服务实例"""
    global market_data_service
    market_data_service = service

@router.get("/prices")
async def get_all_prices(service: HyperliquidMarketData = Depends(get_market_data_service)):
    """获取所有币种的最新价格"""
    try:
        prices = await service.get_all_cached_prices()
        return {
            "success": True,
            "data": prices,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Failed to get prices: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch prices")

@router.get("/prices/{symbol}")
async def get_price(symbol: str, service: HyperliquidMarketData = Depends(get_market_data_service)):
    """获取特定币种的最新价格"""
    try:
        symbol = symbol.upper()
        price_data = await service.get_cached_price(symbol)
        
        if price_data:
            return {
                "success": True,
                "data": price_data,
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail=f"Price data not found for {symbol}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch price")

@router.get("/klines/{symbol}")
async def get_klines(
    symbol: str, 
    interval: str = "1m",
    limit: int = 100,
    service: HyperliquidMarketData = Depends(get_market_data_service)
):
    """获取K线数据"""
    try:
        symbol = symbol.upper()
        klines = await service.get_cached_klines(symbol, interval)
        
        if klines:
            # 限制返回数量
            if limit > 0:
                klines = klines[-limit:]
            
            return {
                "success": True,
                "data": {
                    "symbol": symbol,
                    "interval": interval,
                    "klines": klines,
                    "count": len(klines)
                },
                "timestamp": datetime.now().isoformat()
            }
        else:
            raise HTTPException(status_code=404, detail=f"Kline data not found for {symbol}")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get klines for {symbol}: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch klines")

@router.get("/ticker")
async def get_ticker(service: HyperliquidMarketData = Depends(get_market_data_service)):
    """获取价格Ticker数据 (用于前端价格栏)"""
    try:
        prices = await service.get_all_cached_prices()
        
        # 格式化为前端需要的格式
        ticker_data = []
        for symbol, price_data in prices.items():
            ticker_data.append({
                "symbol": symbol,
                "price": price_data.get('price', 0),
                "change": 0,  # 暂时设为0，后续可以计算24h变化
                "changePercent": 0,
                "volume": 0,  # 暂时设为0
                "timestamp": price_data.get('timestamp')
            })
        
        return {
            "success": True,
            "data": ticker_data,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get ticker data: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch ticker data")

@router.get("/market/status")
async def get_market_status(service: HyperliquidMarketData = Depends(get_market_data_service)):
    """获取市场状态"""
    try:
        prices = await service.get_all_cached_prices()
        
        return {
            "success": True,
            "data": {
                "market_status": "open",
                "supported_symbols": service.symbols,
                "active_symbols": list(prices.keys()),
                "websocket_connections": websocket_manager.get_connection_count(),
                "last_update": datetime.now().isoformat()
            },
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to get market status: {e}")
        raise HTTPException(status_code=500, detail="Failed to fetch market status")

@router.post("/market/refresh")
async def refresh_market_data(service: HyperliquidMarketData = Depends(get_market_data_service)):
    """手动刷新市场数据"""
    try:
        # 触发数据刷新
        import asyncio
        asyncio.create_task(service._update_prices_periodically())
        
        return {
            "success": True,
            "message": "Market data refresh triggered",
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Failed to refresh market data: {e}")
        raise HTTPException(status_code=500, detail="Failed to refresh market data")
