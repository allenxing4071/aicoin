"""Hyperliquid交易执行服务"""

import asyncio
import json
from datetime import datetime
from typing import Dict, List, Optional, Any
from decimal import Decimal
from loguru import logger
from eth_account import Account

from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants

from app.core.config import settings
from app.core.redis_client import RedisClient


class HyperliquidTradingService:
    """Hyperliquid交易服务"""
    
    def __init__(self, redis_client: RedisClient, testnet: bool = True):
        self.redis_client = redis_client
        self.testnet = testnet
        self.info = None
        self.exchange = None
        self.wallet_address = None
        self.private_key = None
        self.is_initialized = False
        
        # 支持的交易对
        self.symbols = ["BTC", "ETH", "SOL", "BNB", "DOGE", "XRP"]
        
        # 交易配置
        self.max_position_size = Decimal("1000")  # 最大持仓金额
        self.max_daily_trades = 100  # 每日最大交易次数
        self.risk_limit_per_trade = Decimal("100")  # 每笔交易风险限额
        
        # 交易统计
        self.daily_trades_count = 0
        self.daily_pnl = Decimal("0")
        self.total_trades = 0
        
    async def initialize(self):
        """初始化交易服务"""
        try:
            logger.info("Initializing Hyperliquid trading service...")
            
            # 初始化Info客户端
            # Hyperliquid SDK会自动使用正确的API端点
            self.info = Info(skip_ws=True)
            
            # 获取钱包地址和私钥（从环境变量）
            self.wallet_address = settings.HYPERLIQUID_WALLET_ADDRESS
            self.private_key = settings.HYPERLIQUID_PRIVATE_KEY
            
            if not self.wallet_address or not self.private_key:
                logger.warning("Hyperliquid wallet credentials not configured, using mock mode")
                self.is_initialized = False
                return
            
            # 初始化Exchange客户端
            # 从私钥创建LocalAccount对象
            wallet = Account.from_key(self.private_key)
            
            # 根据testnet参数选择API端点
            if self.testnet:
                base_url = constants.TESTNET_API_URL
            else:
                base_url = constants.MAINNET_API_URL
            
            self.exchange = Exchange(
                wallet=wallet,
                base_url=base_url
            )
            
            # 验证连接
            await self._verify_connection()
            
            self.is_initialized = True
            logger.info("Hyperliquid trading service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Hyperliquid trading service: {e}")
            self.is_initialized = False
    
    async def _verify_connection(self):
        """验证连接"""
        try:
            # 获取用户状态
            user_state = self.info.user_state(self.wallet_address)
            logger.info(f"Connected to Hyperliquid, wallet: {self.wallet_address}")
            logger.info(f"User state: {user_state}")
        except Exception as e:
            logger.error(f"Failed to verify Hyperliquid connection: {e}")
            raise
    
    async def get_account_info(self) -> Dict[str, Any]:
        """获取账户信息"""
        try:
            if not self.is_initialized:
                return await self._get_mock_account_info()
            
            user_state = self.info.user_state(self.wallet_address)
            
            return {
                "wallet_address": self.wallet_address,
                "total_collateral": user_state.get("totalCollateral", 0),
                "free_collateral": user_state.get("freeCollateral", 0),
                "positions": user_state.get("assetPositions", []),
                "open_orders": user_state.get("openOrders", []),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get account info: {e}")
            return await self._get_mock_account_info()
    
    async def _get_mock_account_info(self) -> Dict[str, Any]:
        """获取模拟账户信息"""
        return {
            "wallet_address": "mock_wallet_address",
            "total_collateral": 10000.0,
            "free_collateral": 5000.0,
            "positions": [
                {
                    "position": {"coin": "BTC", "szi": "0.1", "entryPx": "95000"},
                    "unrealizedPnl": "500.0"
                }
            ],
            "open_orders": [],
            "timestamp": datetime.now().isoformat(),
            "mock": True
        }
    
    async def get_positions(self) -> List[Dict[str, Any]]:
        """获取当前持仓"""
        try:
            account_info = await self.get_account_info()
            positions = account_info.get("positions", [])
            
            formatted_positions = []
            for pos in positions:
                position_data = pos.get("position", {})
                formatted_positions.append({
                    "symbol": position_data.get("coin", ""),
                    "size": float(position_data.get("szi", 0)),
                    "entry_price": float(position_data.get("entryPx", 0)),
                    "unrealized_pnl": float(pos.get("unrealizedPnl", 0)),
                    "side": "long" if float(position_data.get("szi", 0)) > 0 else "short"
                })
            
            return formatted_positions
            
        except Exception as e:
            logger.error(f"Failed to get positions: {e}")
            return []
    
    async def place_order(
        self,
        symbol: str,
        side: str,
        size: float,
        price: Optional[float] = None,
        order_type: str = "market"
    ) -> Dict[str, Any]:
        """下单"""
        try:
            if not self.is_initialized:
                return await self._place_mock_order(symbol, side, size, price, order_type)
            
            # 风险检查
            if not await self._risk_check(symbol, side, size):
                return {
                    "success": False,
                    "error": "Risk check failed",
                    "order_id": None
                }
            
            # 构建订单请求
            is_buy = side.lower() == "buy"
            
            # 提交订单
            if order_type.lower() == "market":
                result = self.exchange.market_open(symbol, is_buy, size)
            else:
                result = self.exchange.limit_order(symbol, is_buy, size, price)
            
            if result.get("status") == "ok":
                order_id = result.get("response", {}).get("data", {}).get("statuses", [{}])[0].get("resting", {}).get("oid")
                
                # 记录交易
                await self._record_trade(symbol, side, size, price, order_id)
                
                return {
                    "success": True,
                    "order_id": order_id,
                    "symbol": symbol,
                    "side": side,
                    "size": size,
                    "price": price,
                    "timestamp": datetime.now().isoformat()
                }
            else:
                return {
                    "success": False,
                    "error": result.get("response", {}).get("error", "Unknown error"),
                    "order_id": None
                }
                
        except Exception as e:
            logger.error(f"Failed to place order: {e}")
            return {
                "success": False,
                "error": str(e),
                "order_id": None
            }
    
    async def _place_mock_order(
        self,
        symbol: str,
        side: str,
        size: float,
        price: Optional[float],
        order_type: str
    ) -> Dict[str, Any]:
        """模拟下单"""
        order_id = f"mock_order_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # 模拟订单执行
        await asyncio.sleep(0.1)  # 模拟网络延迟
        
        logger.info(f"Mock order placed: {symbol} {side} {size} @ {price}")
        
        return {
            "success": True,
            "order_id": order_id,
            "symbol": symbol,
            "side": side,
            "size": size,
            "price": price or 0,
            "timestamp": datetime.now().isoformat(),
            "mock": True
        }
    
    async def _risk_check(self, symbol: str, side: str, size: float) -> bool:
        """风险检查"""
        try:
            # 检查每日交易次数
            if self.daily_trades_count >= self.max_daily_trades:
                logger.warning("Daily trade limit exceeded")
                return False
            
            # 检查单笔交易风险
            if size > self.risk_limit_per_trade:
                logger.warning(f"Trade size {size} exceeds risk limit {self.risk_limit_per_trade}")
                return False
            
            # 检查持仓限制
            positions = await self.get_positions()
            total_exposure = sum(abs(pos["size"]) for pos in positions)
            if total_exposure + size > self.max_position_size:
                logger.warning("Position size limit exceeded")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Risk check failed: {e}")
            return False
    
    async def _record_trade(self, symbol: str, side: str, size: float, price: Optional[float], order_id: str):
        """记录交易"""
        try:
            trade_data = {
                "order_id": order_id,
                "symbol": symbol,
                "side": side,
                "size": size,
                "price": price,
                "timestamp": datetime.now().isoformat(),
                "pnl": 0.0  # 初始PnL为0
            }
            
            # 存储到Redis
            await self.redis_client.set(f"trade:{order_id}", trade_data, expire=86400)
            
            # 更新统计
            self.daily_trades_count += 1
            self.total_trades += 1
            
            logger.info(f"Trade recorded: {order_id}")
            
        except Exception as e:
            logger.error(f"Failed to record trade: {e}")
    
    async def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """取消订单"""
        try:
            if not self.is_initialized:
                return await self._cancel_mock_order(order_id)
            
            result = self.exchange.cancel(symbol="BTC", oid=order_id)
            
            if result.get("status") == "ok":
                return {
                    "success": True,
                    "order_id": order_id,
                    "message": "Order cancelled successfully"
                }
            else:
                return {
                    "success": False,
                    "error": result.get("response", {}).get("error", "Unknown error")
                }
                
        except Exception as e:
            logger.error(f"Failed to cancel order: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _cancel_mock_order(self, order_id: str) -> Dict[str, Any]:
        """模拟取消订单"""
        logger.info(f"Mock order cancelled: {order_id}")
        return {
            "success": True,
            "order_id": order_id,
            "message": "Order cancelled successfully",
            "mock": True
        }
    
    async def get_order_status(self, order_id: str) -> Dict[str, Any]:
        """获取订单状态"""
        try:
            if not self.is_initialized:
                return await self._get_mock_order_status(order_id)
            
            # 从Redis获取交易记录
            trade_data = await self.redis_client.get(f"trade:{order_id}")
            if trade_data:
                return {
                    "success": True,
                    "order_id": order_id,
                    "status": "filled",
                    "data": trade_data
                }
            else:
                return {
                    "success": False,
                    "error": "Order not found"
                }
                
        except Exception as e:
            logger.error(f"Failed to get order status: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def _get_mock_order_status(self, order_id: str) -> Dict[str, Any]:
        """获取模拟订单状态"""
        return {
            "success": True,
            "order_id": order_id,
            "status": "filled",
            "data": {
                "order_id": order_id,
                "symbol": "BTC",
                "side": "buy",
                "size": 0.1,
                "price": 95000.0,
                "timestamp": datetime.now().isoformat(),
                "mock": True
            }
        }
    
    async def get_trading_stats(self) -> Dict[str, Any]:
        """获取交易统计"""
        return {
            "daily_trades_count": self.daily_trades_count,
            "daily_pnl": float(self.daily_pnl),
            "total_trades": self.total_trades,
            "max_position_size": float(self.max_position_size),
            "max_daily_trades": self.max_daily_trades,
            "risk_limit_per_trade": float(self.risk_limit_per_trade),
            "timestamp": datetime.now().isoformat()
        }
    
    async def stop(self):
        """停止服务"""
        logger.info("Stopping Hyperliquid trading service...")
        # 清理资源
        self.is_initialized = False
        logger.info("Hyperliquid trading service stopped")
