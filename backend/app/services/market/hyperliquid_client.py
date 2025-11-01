"""Hyperliquid API client - 简化版实现"""

import httpx
from typing import List, Dict, Any, Optional
from decimal import Decimal
from datetime import datetime
import logging
from app.core.config import settings

logger = logging.getLogger(__name__)


class HyperliquidClient:
    """Hyperliquid API客户端 (Testnet/Mainnet)"""
    
    def __init__(self, trading_service=None, use_mainnet_for_market_data: bool = True):
        self.base_url = settings.HYPERLIQUID_API_URL
        self.testnet = "testnet" in self.base_url.lower()  # 根据URL判断是否为testnet
        self.wallet_address = settings.HYPERLIQUID_WALLET_ADDRESS
        self.private_key = settings.HYPERLIQUID_PRIVATE_KEY
        self.client = httpx.AsyncClient(timeout=30.0)
        self._trading_service = trading_service  # 缓存trading service，避免重复初始化
        
        # 市场数据API：如果在testnet模式且use_mainnet_for_market_data=True，则使用mainnet获取市场数据
        # 这是因为testnet的交易对较少（例如没有XRP）
        if self.testnet and use_mainnet_for_market_data:
            self.market_data_url = "https://api.hyperliquid.xyz"
            logger.info(f"🌐 Using mainnet for market data (testnet has limited pairs)")
        else:
            self.market_data_url = self.base_url
            logger.info(f"🌐 Using {self.base_url} for market data")
    
    async def get_klines(
        self,
        symbol: str,
        interval: str = "1h",
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        获取K线数据
        
        注意: 这是模拟实现，实际需要对接Hyperliquid真实API
        """
        try:
            # 模拟数据 - 实际应该调用真实API
            logger.info(f"Fetching klines for {symbol}, interval={interval}, limit={limit}")
            
            # TODO: 实现真实的Hyperliquid API调用
            # 目前返回模拟数据用于测试
            return self._generate_mock_klines(symbol, interval, limit)
            
        except Exception as e:
            logger.error(f"Error fetching klines: {e}")
            raise
    
    async def get_orderbook(
        self,
        symbol: str,
        depth: int = 20
    ) -> Dict[str, Any]:
        """
        获取订单簿
        
        注意: 这是模拟实现
        """
        try:
            logger.info(f"Fetching orderbook for {symbol}, depth={depth}")
            
            # TODO: 实现真实的Hyperliquid API调用
            return self._generate_mock_orderbook(symbol, depth)
            
        except Exception as e:
            logger.error(f"Error fetching orderbook: {e}")
            raise
    
    async def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """获取实时价格 - 从Hyperliquid获取真实数据，包含24h涨跌幅"""
        try:
            logger.info(f"Fetching ticker for {symbol}")
            
            # 使用缓存的trading service，避免重复初始化
            if self._trading_service is None:
                from app.services.hyperliquid_trading import HyperliquidTradingService
                from app.core.redis_client import redis_client
                logger.warning("Trading service not provided, creating new instance (slow!)")
                self._trading_service = HyperliquidTradingService(redis_client, testnet=self.testnet)
                await self._trading_service.initialize()
            
            # 获取市场数据
            try:
                # 1. 获取当前价格（使用market_data_url，可能是mainnet）
                url = f"{self.market_data_url}/info"
                response = await self.client.post(url, json={"type": "allMids"})
                response.raise_for_status()
                data = response.json()
                
                # 查找对应symbol的价格（精确匹配）
                symbol_upper = symbol.upper()
                current_price = None
                
                # 直接查找（Hyperliquid使用大写symbol，如BTC, ETH等）
                logger.debug(f"Looking for {symbol_upper} in {len(data)} symbols")
                logger.debug(f"XRP in data: {'XRP' in data}, BTC in data: {'BTC' in data}")
                
                if symbol_upper in data:
                    current_price = float(data[symbol_upper])
                    logger.info(f"✅ Found {symbol_upper} price: {current_price}")
                else:
                    logger.error(f"❌ Symbol {symbol_upper} not found in market data")
                    # 打印所有包含字母的symbol（过滤掉@开头的）
                    letter_symbols = [s for s in data.keys() if not s.startswith('@') and not s[0].isdigit()]
                    logger.error(f"Available letter symbols: {sorted(letter_symbols)[:50]}")
                
                if current_price is None:
                    logger.warning(f"Symbol {symbol} not found in market data, using fallback")
                    return {
                        "symbol": symbol,
                        "price": "0.00",
                        "change_24h": "0.00",
                        "volume_24h": "0.00",
                        "timestamp": datetime.now().isoformat()
                    }
                
                # 2. 获取24小时K线数据来计算涨跌幅
                change_24h = "0.00"
                try:
                    # 获取24小时K线（1小时间隔，24根）
                    candles_response = await self.client.post(
                        url,
                        json={
                            "type": "candleSnapshot",
                            "req": {
                                "coin": symbol.upper(),
                                "interval": "1h",
                                "startTime": int((datetime.now().timestamp() - 86400) * 1000),  # 24小时前
                                "endTime": int(datetime.now().timestamp() * 1000)
                            }
                        }
                    )
                    if candles_response.status_code == 200:
                        candles_data = candles_response.json()
                        if candles_data and len(candles_data) > 0:
                            # 获取24小时前的开盘价
                            price_24h_ago = float(candles_data[0]['o'])  # 第一根K线的开盘价
                            # 计算涨跌幅
                            if price_24h_ago > 0:
                                change_pct = ((current_price - price_24h_ago) / price_24h_ago) * 100
                                change_24h = f"{change_pct:.2f}"
                                logger.info(f"{symbol}: 24h前价格={price_24h_ago}, 当前价格={current_price}, 涨跌幅={change_24h}%")
                except Exception as candle_error:
                    logger.warning(f"Failed to fetch 24h candles for {symbol}: {candle_error}")
                    # 如果获取K线失败，涨跌幅保持为0
                
                return {
                    "symbol": symbol,
                    "price": str(current_price),
                    "change_24h": change_24h,
                    "volume_24h": "0.00",  # TODO: 需要从API获取
                    "timestamp": datetime.now().isoformat()
                }
            except Exception as api_error:
                logger.error(f"❌ Error calling Hyperliquid API for {symbol}: {api_error}")
                logger.exception("Full traceback:")
                # 返回默认值而不是抛出异常
                return {
                    "symbol": symbol,
                    "price": "0.00",
                    "change_24h": "0.00",
                    "volume_24h": "0.00",
                    "timestamp": datetime.now().isoformat()
                }
            
        except Exception as e:
            logger.error(f"Error fetching ticker: {e}")
            raise
    
    async def get_account_balance(self) -> Dict[str, Any]:
        """获取账户余额 - 从Hyperliquid获取真实数据"""
        try:
            logger.info("Fetching account balance from Hyperliquid")
            
            # 使用缓存的trading service，避免重复初始化
            if self._trading_service is None:
                from app.services.hyperliquid_trading import HyperliquidTradingService
                from app.core.redis_client import redis_client
                logger.warning("Trading service not provided, creating new instance (slow!)")
                self._trading_service = HyperliquidTradingService(redis_client, testnet=self.testnet)
                await self._trading_service.initialize()
            
            account_state = await self._trading_service.get_account_state()
            margin_summary = account_state.get('marginSummary', {})
            
            return {
                "balance": str(margin_summary.get('accountValue', '0')),
                "equity": str(margin_summary.get('accountValue', '0')),
                "unrealized_pnl": str(margin_summary.get('totalNtlPos', '0')),
                "realized_pnl": "0.00"
            }
            
        except Exception as e:
            logger.error(f"Error fetching balance: {e}")
            raise
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """获取持仓 - 从Hyperliquid获取真实数据"""
        try:
            logger.info("Fetching positions from Hyperliquid")
            
            # 使用缓存的trading service，避免重复初始化
            if self._trading_service is None:
                from app.services.hyperliquid_trading import HyperliquidTradingService
                from app.core.redis_client import redis_client
                logger.warning("Trading service not provided, creating new instance (slow!)")
                self._trading_service = HyperliquidTradingService(redis_client, testnet=self.testnet)
                await self._trading_service.initialize()
            
            positions = await self._trading_service.get_positions()
            return positions
            
        except Exception as e:
            logger.error(f"Error fetching positions: {e}")
            raise
    
    async def place_order(
        self,
        symbol: str,
        side: str,
        size: Decimal,
        order_type: str = "MARKET",
        price: Optional[Decimal] = None
    ) -> Dict[str, Any]:
        """
        下单
        
        注意: 这是模拟实现，不会真实下单
        """
        try:
            logger.info(f"Placing order: {side} {size} {symbol} @ {order_type}")
            
            if not settings.TRADING_ENABLED:
                logger.warning("Trading is disabled, order not placed")
                return {
                    "success": False,
                    "reason": "Trading disabled",
                    "order_id": None
                }
            
            # TODO: 实现真实下单逻辑
            # 需要签名、发送到Hyperliquid API
            
            return {
                "success": True,
                "order_id": f"mock_order_{datetime.now().timestamp()}",
                "symbol": symbol,
                "side": side,
                "size": str(size),
                "type": order_type,
                "price": str(price) if price else None,
                "status": "FILLED"
            }
            
        except Exception as e:
            logger.error(f"Error placing order: {e}")
            raise
    
    def _generate_mock_klines(self, symbol: str, interval: str, limit: int) -> List[Dict]:
        """生成模拟K线数据"""
        base_price = 67500.0
        klines = []
        
        for i in range(limit):
            open_price = base_price + (i * 100)
            high_price = open_price + 200
            low_price = open_price - 100
            close_price = open_price + 50
            
            klines.append({
                "symbol": symbol,
                "interval": interval,
                "open_time": datetime.now().isoformat(),
                "close_time": datetime.now().isoformat(),
                "open": str(open_price),
                "high": str(high_price),
                "low": str(low_price),
                "close": str(close_price),
                "volume": "125.50"
            })
        
        return klines
    
    def _generate_mock_orderbook(self, symbol: str, depth: int) -> Dict:
        """生成模拟订单簿"""
        base_price = 67500.0
        
        bids = []
        asks = []
        
        for i in range(depth):
            bids.append({
                "price": str(base_price - (i * 10)),
                "size": str(10.0 + i)
            })
            asks.append({
                "price": str(base_price + (i * 10)),
                "size": str(8.0 + i)
            })
        
        return {
            "symbol": symbol,
            "bids": bids,
            "asks": asks,
            "timestamp": datetime.now().isoformat()
        }
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()


# Global instance
hyperliquid_client = HyperliquidClient()

