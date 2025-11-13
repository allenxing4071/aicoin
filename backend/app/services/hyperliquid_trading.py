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
        self.vault_address = None  # 主钱包地址(资金所在地)
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
            
            # 如果设置了vault_address,使用API wallet代理交易
            self.vault_address = getattr(settings, 'HYPERLIQUID_VAULT_ADDRESS', None)
            
            if self.vault_address:
                # Agent模式: API钱包代表主钱包交易
                self.exchange = Exchange(
                    wallet=wallet,
                    base_url=base_url,
                    vault_address=self.vault_address
                )
                logger.info(f"Using Agent mode: API wallet {self.wallet_address} for vault {self.vault_address}")
            else:
                # 直接模式: 使用钱包本身交易
                self.exchange = Exchange(
                    wallet=wallet,
                    base_url=base_url
                )
                logger.info(f"Using Direct mode: wallet {self.wallet_address}")
            
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
            # 在Agent模式下查询vault地址,否则查询wallet地址
            query_address = self.vault_address if self.vault_address else self.wallet_address
            user_state = self.info.user_state(query_address)
            logger.info(f"Connected to Hyperliquid, wallet: {self.wallet_address}, vault: {self.vault_address}")
            logger.info(f"User state: {user_state}")
        except Exception as e:
            logger.error(f"Failed to verify Hyperliquid connection: {e}")
            raise
    
    async def get_account_info(self) -> Dict[str, Any]:
        """获取账户信息"""
        try:
            if not self.is_initialized:
                return await self._get_mock_account_info()
            
            # 在Agent模式下查询vault地址,否则查询wallet地址
            query_address = self.vault_address if self.vault_address else self.wallet_address
            user_state = self.info.user_state(query_address)
            
            return {
                "wallet_address": query_address,
                "total_collateral": user_state.get("totalCollateral", 0),
                "free_collateral": user_state.get("freeCollateral", 0),
                "positions": user_state.get("assetPositions", []),
                "open_orders": user_state.get("openOrders", []),
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get account info: {e}")
            return await self._get_mock_account_info()
    
    async def get_account_state(self) -> Dict[str, Any]:
        """获取账户状态（用于AI决策）"""
        try:
            if not self.is_initialized:
                return {
                    "marginSummary": {
                        "accountValue": "100.0",
                        "totalNtlPos": "0.0",
                        "totalRawUsd": "100.0",
                        "totalMarginUsed": "0.0"
                    },
                    "withdrawable": "100.0",
                    "assetPositions": []
                }
            
            # 在Agent模式下查询vault地址,否则查询wallet地址
            query_address = self.vault_address if self.vault_address else self.wallet_address
            user_state = self.info.user_state(query_address)
            logger.info(f"Account state for {query_address}: balance=${user_state.get('marginSummary', {}).get('accountValue', '0')}")
            return user_state
            
        except Exception as e:
            logger.error(f"Failed to get account state: {e}")
            return {
                "marginSummary": {
                    "accountValue": "100.0",
                    "totalNtlPos": "0.0",
                    "totalRawUsd": "100.0",
                    "totalMarginUsed": "0.0"
                },
                "withdrawable": "100.0",
                "assetPositions": []
            }
    
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
            
            # 调试日志 - 深入检查账户状态
            logger.info(f"📤 Placing order: symbol={symbol}, side={side}, size={size}, is_buy={is_buy}")
            logger.info(f"   Exchange.wallet: {self.exchange.wallet.address if hasattr(self.exchange, 'wallet') else 'N/A'}")
            logger.info(f"   Exchange.vault_address: {self.exchange.vault_address if hasattr(self.exchange, 'vault_address') else 'N/A'}")
            
            # 检查账户的详细状态
            try:
                from hyperliquid.info import Info
                info_client = Info(base_url=self.exchange.base_url, skip_ws=True)
                user_state = info_client.user_state(settings.HYPERLIQUID_WALLET_ADDRESS)
                
                logger.info(f"   账户状态检查:")
                logger.info(f"      withdrawable: {user_state.get('withdrawable')}")
                
                # 检查是否有特殊字段
                special_keys = []
                for key in user_state.keys():
                    if 'multi' in key.lower() or 'sig' in key.lower() or 'cross' in key.lower():
                        special_keys.append(key)
                
                if special_keys:
                    logger.warning(f"      ⚠️ 发现特殊字段: {special_keys}")
                    for key in special_keys:
                        logger.warning(f"         {key}: {user_state.get(key)}")
                        
                # 打印所有user_state的键
                logger.info(f"      user_state所有键: {list(user_state.keys())}")
                
            except Exception as e:
                logger.error(f"   检查账户状态失败: {e}")
            
            # 临时测试：将size转换为BTC数量（假设BTC价格约$114000）
            # 这是为了测试是否是订单大小的问题
            if symbol == "BTC":
                btc_size = size / 114000  # 将USD转换为BTC数量
                # Hyperliquid要求BTC数量精度为4位小数
                btc_size = round(btc_size, 4)
                logger.info(f"   Converting ${size} to {btc_size} BTC (rounded)")
                size = btc_size
            elif symbol == "ETH":
                eth_size = size / 3400  # 假设ETH价格约$3400
                # Hyperliquid要求ETH数量精度为3位小数
                eth_size = round(eth_size, 3)
                logger.info(f"   Converting ${size} to {eth_size} ETH (rounded)")
                size = eth_size
            
            # 提交订单
            if order_type.lower() == "market":
                result = self.exchange.market_open(symbol, is_buy, size)
            else:
                result = self.exchange.limit_order(symbol, is_buy, size, price)
            
            logger.info(f"Hyperliquid API response: {result}")
            
            # Hyperliquid SDK 返回结果处理
            # 结果可能是字典、字符串或其他格式
            if isinstance(result, dict):
                if result.get("status") == "ok":
                    order_id = result.get("response", {}).get("data", {}).get("statuses", [{}])[0].get("resting", {}).get("oid", f"order_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
                    
                    # 记录交易
                    await self._record_trade(symbol, side, size, price, order_id)
                    
                    logger.info(f"✅ Trade executed successfully: {order_id} - {side} {size} {symbol}")
                    
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
                    # 处理错误响应，response可能是字符串或字典
                    response_data = result.get("response", "")
                    if isinstance(response_data, dict):
                        error_msg = response_data.get("error", str(result))
                    else:
                        error_msg = str(response_data)  # response是字符串（如'Multi-sig required'）
                    
                    logger.error(f"Trade failed: {error_msg}")
                    
                    # 特殊处理Multi-sig错误
                    if "multi-sig" in error_msg.lower():
                        logger.warning("⚠️  Multi-sig is enabled on your Hyperliquid account. API trading requires disabling multi-sig.")
                    
                    return {
                        "success": False,
                        "error": error_msg,
                        "order_id": None
                    }
            elif isinstance(result, str):
                # 如果返回的是字符串，尝试解析
                order_id = f"order_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                await self._record_trade(symbol, side, size, price, order_id)
                logger.info(f"✅ Trade executed (string response): {order_id} - {side} {size} {symbol}")
                
                return {
                    "success": True,
                    "order_id": order_id,
                    "symbol": symbol,
                    "side": side,
                    "size": size,
                    "price": price,
                    "timestamp": datetime.now().isoformat(),
                    "raw_response": result
                }
            else:
                # 未知格式,返回错误
                error_msg = f"Unexpected response format: {type(result)}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "error": error_msg,
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
        """风险检查 - 仅做基本安全检查，不限制AI自主决策"""
        try:
            # 获取账户信息
            account_state = await self.get_account_state()
            account_value = float(account_state.get('marginSummary', {}).get('accountValue', '0'))
            
            # 基本安全检查：确保交易大小不超过账户价值
            if size > account_value:
                logger.warning(f"Trade size {size} exceeds account value {account_value}")
                return False
            
            # 所有其他决策（包括交易次数、持仓大小、风险管理）
            # 完全由AI自主决定，不做任何人为限制
            logger.info(f"Risk check passed: AI autonomous trade {symbol} {side} ${size}")
            return True
            
        except Exception as e:
            logger.error(f"Risk check failed: {e}")
            return False
    
    async def _record_trade(self, symbol: str, side: str, size: float, price: Optional[float], order_id: str):
        """记录交易（同时保存到数据库和Redis）"""
        try:
            from app.models.trade import Trade
            from app.models.order import Order
            from app.core.database import AsyncSessionLocal
            from decimal import Decimal
            
            trade_data = {
                "order_id": order_id,
                "symbol": symbol,
                "side": side,
                "size": size,
                "price": price,
                "timestamp": datetime.now().isoformat(),
                "pnl": 0.0  # 初始PnL为0
            }
            
            # ✅ 保存到数据库
            async with AsyncSessionLocal() as db_session:
                try:
                    # 1. 保存订单记录
                    db_order = Order(
                        symbol=symbol,
                        side=side.upper(),
                        type="MARKET",
                        size=Decimal(str(size)),
                        filled_size=Decimal(str(size)),
                        status="FILLED",
                        exchange_order_id=order_id
                    )
                    db_session.add(db_order)
                    await db_session.flush()  # 获取订单ID
                    
                    # 2. 保存成交记录
                    db_trade = Trade(
                        order_id=db_order.id,
                        symbol=symbol,
                        side=side.upper(),
                        price=Decimal(str(price)) if price else Decimal('0'),
                        size=Decimal(str(size)),
                        pnl=Decimal('0'),
                        fee=Decimal('0'),
                        model="hyperliquid_trading"
                    )
                    db_session.add(db_trade)
                    await db_session.commit()
                    
                    logger.info(f"✅ Trade saved to database: order_id={db_order.id}, trade_id={db_trade.id}")
                    
                except Exception as db_error:
                    logger.error(f"❌ Failed to save trade to database: {db_error}")
                    await db_session.rollback()
            
            # 存储到Redis（缓存）
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
