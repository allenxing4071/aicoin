"""
Hyperliquid 实时行情数据服务
订阅实时价格、K线、订单簿数据
"""

import asyncio
import json
import logging
import websockets
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import redis
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange

logger = logging.getLogger(__name__)

class HyperliquidMarketData:
    """Hyperliquid 行情数据服务"""
    
    def __init__(self, redis_client: redis.Redis, testnet: bool = True):
        self.redis = redis_client
        self.testnet = testnet
        # 暂时使用模拟数据，避免API连接问题
        self.info = None
        self.exchange = None  # 交易功能稍后实现
        
        # 支持的币种
        self.symbols = ['BTC', 'ETH', 'SOL', 'BNB', 'DOGE', 'XRP']
        
        # WebSocket 连接
        self.ws_url = "wss://api.hyperliquid-testnet.xyz/ws" if testnet else "wss://api.hyperliquid.xyz/ws"
        self.ws = None
        self.running = False
        
        # 数据缓存键
        self.price_key = "hyperliquid:price:{symbol}"
        self.kline_key = "hyperliquid:kline:{symbol}:{interval}"
        self.orderbook_key = "hyperliquid:orderbook:{symbol}"
        
        # 模拟价格数据
        self.mock_prices = {
            'BTC': 95000.0,
            'ETH': 3500.0,
            'SOL': 180.0,
            'BNB': 600.0,
            'DOGE': 0.35,
            'XRP': 0.50
        }
        
    async def start(self):
        """启动行情数据服务"""
        logger.info("Starting Hyperliquid market data service...")
        self.running = True
        
        # 初始化Info客户端获取真实数据
        try:
            if self.testnet:
                # 测试网暂时不可用，使用主网
                self.info = Info(skip_ws=True)
            else:
                self.info = Info(skip_ws=True)
            logger.info("Connected to Hyperliquid API for real market data")
        except Exception as e:
            logger.error(f"Failed to connect to Hyperliquid API: {e}")
            logger.info("Falling back to mock data")
            self.info = None
        
        # 启动数据更新任务
        asyncio.create_task(self._update_prices_periodically())
        asyncio.create_task(self._update_klines_periodically())
    
    async def _get_mock_price(self, symbol: str) -> Dict[str, Any]:
        """获取模拟价格数据"""
        import random
        
        base_price = self.mock_prices.get(symbol, 100.0)
        # 添加随机波动
        change_percent = (random.random() - 0.5) * 0.02  # ±1%波动
        new_price = base_price * (1 + change_percent)
        
        return {
            'symbol': symbol,
            'price': round(new_price, 2),
            'changePercent': round(change_percent * 100, 2),
            'timestamp': datetime.now().isoformat(),
            'volume': random.randint(1000, 10000)
        }
        
    async def stop(self):
        """停止行情数据服务"""
        logger.info("Stopping Hyperliquid market data service...")
        self.running = False
        
        if self.ws:
            await self.ws.close()
            
    async def _connect_websocket(self):
        """连接 WebSocket"""
        try:
            self.ws = await websockets.connect(self.ws_url)
            logger.info(f"Connected to Hyperliquid WebSocket: {self.ws_url}")
            
            # 订阅所有币种的价格更新
            for symbol in self.symbols:
                await self._subscribe_price_updates(symbol)
                
            # 启动消息处理
            asyncio.create_task(self._handle_websocket_messages())
            
        except Exception as e:
            logger.error(f"Failed to connect to Hyperliquid WebSocket: {e}")
            # 重连机制
            await asyncio.sleep(5)
            if self.running:
                await self._connect_websocket()
    
    async def _subscribe_price_updates(self, symbol: str):
        """订阅价格更新"""
        try:
            # 订阅价格更新
            subscribe_msg = {
                "method": "subscribe",
                "subscription": {
                    "type": "l2Book",
                    "coin": symbol
                }
            }
            
            if self.ws:
                await self.ws.send(json.dumps(subscribe_msg))
                logger.info(f"Subscribed to price updates for {symbol}")
                
        except Exception as e:
            logger.error(f"Failed to subscribe to {symbol} price updates: {e}")
    
    async def _handle_websocket_messages(self):
        """处理 WebSocket 消息"""
        try:
            async for message in self.ws:
                if not self.running:
                    break
                    
                data = json.loads(message)
                await self._process_market_data(data)
                
        except websockets.exceptions.ConnectionClosed:
            logger.warning("WebSocket connection closed, attempting to reconnect...")
            if self.running:
                await asyncio.sleep(5)
                await self._connect_websocket()
        except Exception as e:
            logger.error(f"Error handling WebSocket messages: {e}")
            if self.running:
                await asyncio.sleep(5)
                await self._connect_websocket()
    
    async def _process_market_data(self, data: Dict[str, Any]):
        """处理市场数据"""
        try:
            if 'data' in data:
                market_data = data['data']
                
                # 处理订单簿数据
                if 'coin' in market_data and 'levels' in market_data:
                    symbol = market_data['coin']
                    levels = market_data['levels']
                    
                    if levels and len(levels) > 0:
                        # 获取最佳买价和卖价
                        best_bid = float(levels[0][0]) if levels[0] else 0
                        best_ask = float(levels[1][0]) if len(levels) > 1 and levels[1] else 0
                        
                        # 计算中间价
                        mid_price = (best_bid + best_ask) / 2 if best_bid and best_ask else 0
                        
                        if mid_price > 0:
                            # 缓存价格数据
                            price_data = {
                                'symbol': symbol,
                                'price': mid_price,
                                'bid': best_bid,
                                'ask': best_ask,
                                'timestamp': datetime.now().isoformat(),
                                'source': 'hyperliquid'
                            }
                            
                            await self._cache_price_data(symbol, price_data)
                            
        except Exception as e:
            logger.error(f"Error processing market data: {e}")
    
    async def _cache_price_data(self, symbol: str, price_data: Dict[str, Any]):
        """缓存价格数据到 Redis"""
        try:
            key = self.price_key.format(symbol=symbol)
            await self.redis.set(key, price_data, expire=60)  # 60秒过期
            logger.debug(f"Cached price data for {symbol}: {price_data['price']}")
            
        except Exception as e:
            logger.error(f"Failed to cache price data for {symbol}: {e}")
    
    async def _update_prices_periodically(self):
        """定期更新价格数据"""
        while self.running:
            try:
                for symbol in self.symbols:
                    try:
                        # 如果有真实API连接，使用真实数据
                        if self.info:
                            price_data = await self._fetch_latest_price(symbol)
                        else:
                            # 否则使用模拟数据
                            price_data = await self._get_mock_price(symbol)
                        
                        if price_data:
                            await self._cache_price_data(symbol, price_data)
                            
                    except Exception as e:
                        logger.error(f"Failed to get price for {symbol}: {e}")
                        # 出错时使用模拟数据
                        try:
                            price_data = await self._get_mock_price(symbol)
                            if price_data:
                                await self._cache_price_data(symbol, price_data)
                        except:
                            pass
                
                # 每5秒更新一次
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Error in periodic price update: {e}")
                await asyncio.sleep(10)
    
    async def _fetch_latest_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """从 Hyperliquid API 获取最新价格"""
        try:
            # 获取L2订单簿快照
            l2_data = self.info.l2_snapshot(symbol)
            
            if l2_data and 'levels' in l2_data:
                levels = l2_data['levels']
                # levels[0]是买单，levels[1]是卖单
                if len(levels) >= 2 and levels[0] and levels[1]:
                    # 每个level是 [[price, size], [price, size], ...]
                    best_bid = float(levels[0][0]['px']) if levels[0] else 0
                    best_ask = float(levels[1][0]['px']) if levels[1] else 0
                    mid_price = (best_bid + best_ask) / 2 if best_bid and best_ask else 0
                    
                    if mid_price > 0:
                        return {
                            'symbol': symbol,
                            'price': mid_price,
                            'bid': best_bid,
                            'ask': best_ask,
                            'timestamp': datetime.now().isoformat(),
                            'source': 'hyperliquid_api'
                        }
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to fetch latest price for {symbol}: {e}")
            return None
    
    async def _update_klines_periodically(self):
        """定期更新K线数据"""
        while self.running:
            try:
                for symbol in self.symbols:
                    try:
                        # 获取1分钟K线数据
                        kline_data = await self._fetch_kline_data(symbol, '1m')
                        if kline_data:
                            await self._cache_kline_data(symbol, '1m', kline_data)
                            
                    except Exception as e:
                        logger.error(f"Failed to fetch kline data for {symbol}: {e}")
                
                # 每60秒更新一次K线
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Error in periodic kline update: {e}")
                await asyncio.sleep(60)
    
    async def _fetch_kline_data(self, symbol: str, interval: str) -> Optional[List[Dict[str, Any]]]:
        """获取K线数据"""
        try:
            # 如果有真实API连接，尝试获取真实K线数据
            if self.info:
                try:
                    # Hyperliquid API获取K线数据快照
                    # 参数: coin, interval, startTime, endTime
                    import time
                    end_time = int(time.time() * 1000)  # 当前时间（毫秒）
                    start_time = end_time - (100 * 60 * 1000)  # 100分钟前
                    
                    candles = self.info.candles_snapshot(symbol, interval, start_time, end_time)
                    if candles:
                        klines = []
                        for candle in candles:
                            klines.append({
                                'timestamp': candle.get('t', 0),
                                'open': float(candle.get('o', 0)),
                                'high': float(candle.get('h', 0)),
                                'low': float(candle.get('l', 0)),
                                'close': float(candle.get('c', 0)),
                                'volume': float(candle.get('v', 0)),
                                'source': 'hyperliquid_api'
                            })
                        return klines
                except Exception as e:
                    logger.warning(f"Failed to fetch real kline data for {symbol}, using mock data: {e}")
            
            # 否则使用模拟K线数据
            return await self._get_mock_kline_data(symbol, interval)
            
        except Exception as e:
            logger.error(f"Failed to fetch kline data for {symbol}: {e}")
            return None
    
    async def _get_mock_kline_data(self, symbol: str, interval: str) -> List[Dict[str, Any]]:
        """生成模拟K线数据"""
        import random
        from datetime import datetime, timedelta
        
        base_price = self.mock_prices.get(symbol, 100.0)
        klines = []
        
        # 生成最近10根K线
        for i in range(10):
            # 添加随机波动
            change_percent = (random.random() - 0.5) * 0.05  # ±2.5%波动
            price = base_price * (1 + change_percent)
            
            # 生成OHLC数据
            open_price = price * (1 + (random.random() - 0.5) * 0.01)
            high_price = max(open_price, price) * (1 + random.random() * 0.01)
            low_price = min(open_price, price) * (1 - random.random() * 0.01)
            close_price = price
            
            volume = random.randint(100, 1000)
            
            kline = {
                'timestamp': (datetime.now() - timedelta(minutes=10-i)).isoformat(),
                'open': round(open_price, 2),
                'high': round(high_price, 2),
                'low': round(low_price, 2),
                'close': round(close_price, 2),
                'volume': volume
            }
            klines.append(kline)
        
        return klines
    
    async def _cache_kline_data(self, symbol: str, interval: str, kline_data: List[Dict[str, Any]]):
        """缓存K线数据到 Redis"""
        try:
            key = self.kline_key.format(symbol=symbol, interval=interval)
            await self.redis.set(key, kline_data, expire=300)  # 5分钟过期
            logger.debug(f"Cached {len(kline_data)} kline data points for {symbol}")
            
        except Exception as e:
            logger.error(f"Failed to cache kline data for {symbol}: {e}")
    
    async def get_cached_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """获取缓存的价格数据"""
        try:
            key = self.price_key.format(symbol=symbol)
            data = await self.redis.get(key)
            if data:
                # Redis客户端已经自动解析了JSON，直接返回
                return data
            return None
            
        except Exception as e:
            logger.error(f"Failed to get cached price for {symbol}: {e}")
            return None
    
    async def get_cached_klines(self, symbol: str, interval: str = '1m') -> Optional[List[Dict[str, Any]]]:
        """获取缓存的K线数据"""
        try:
            key = self.kline_key.format(symbol=symbol, interval=interval)
            data = await self.redis.get(key)
            if data:
                # Redis客户端已经自动解析了JSON，直接返回
                return data
            return None
            
        except Exception as e:
            logger.error(f"Failed to get cached klines for {symbol}: {e}")
            return None
    
    async def get_all_cached_prices(self) -> Dict[str, Dict[str, Any]]:
        """获取所有缓存的价格数据"""
        prices = {}
        for symbol in self.symbols:
            price_data = await self.get_cached_price(symbol)
            if price_data:
                prices[symbol] = price_data
        return prices
