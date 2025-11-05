"""Hyperliquid交易所适配器 - 重构自HyperliquidTradingService"""

import asyncio
from typing import Dict, List, Optional, Any
from decimal import Decimal
from datetime import datetime
import logging

from eth_account import Account
from hyperliquid.info import Info
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants

from app.services.exchange.base_adapter import BaseExchangeAdapter
from app.core.config import settings

logger = logging.getLogger(__name__)


class HyperliquidAdapter(BaseExchangeAdapter):
    """
    Hyperliquid去中心化交易所适配器
    
    仅支持永续合约交易(Perpetual)
    """
    
    def __init__(
        self,
        wallet_address: str,
        private_key: str,
        vault_address: Optional[str] = None,
        testnet: bool = False
    ):
        super().__init__()
        self.name = "hyperliquid"
        self.wallet_address = wallet_address
        self.private_key = private_key
        self.vault_address = vault_address  # Agent模式: 代理主钱包交易
        self.testnet = testnet
        
        # 客户端
        self.info: Optional[Info] = None
        self.exchange: Optional[Exchange] = None
        
    async def initialize(self) -> bool:
        """初始化Hyperliquid连接"""
        try:
            logger.info(f"初始化Hyperliquid适配器 (testnet={self.testnet})...")
            
            # 初始化Info客户端
            self.info = Info(skip_ws=True)
            
            # 创建LocalAccount对象
            wallet = Account.from_key(self.private_key)
            
            # 选择API端点
            base_url = constants.TESTNET_API_URL if self.testnet else constants.MAINNET_API_URL
            
            # 初始化Exchange客户端
            if self.vault_address:
                # Agent模式: API钱包代表主钱包交易
                self.exchange = Exchange(
                    wallet=wallet,
                    base_url=base_url,
                    vault_address=self.vault_address
                )
                logger.info(f"Agent模式: API钱包 {self.wallet_address} 代理 vault {self.vault_address}")
            else:
                # 直接模式: 使用钱包本身交易
                self.exchange = Exchange(
                    wallet=wallet,
                    base_url=base_url
                )
                logger.info(f"直接模式: 钱包 {self.wallet_address}")
            
            # 验证连接
            await self._verify_connection()
            
            self.is_initialized = True
            logger.info("✅ Hyperliquid适配器初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ Hyperliquid初始化失败: {e}", exc_info=True)
            self.is_initialized = False
            return False
    
    async def _verify_connection(self):
        """验证API连接"""
        try:
            query_address = self.vault_address if self.vault_address else self.wallet_address
            user_state = self.info.user_state(query_address)
            logger.info(f"连接验证成功, 账户余额: ${user_state.get('marginSummary', {}).get('accountValue', 0)}")
        except Exception as e:
            raise Exception(f"API连接验证失败: {e}")
    
    def _normalize_symbol(self, symbol: str, market_type: str = 'perpetual') -> str:
        """
        标准化交易对符号
        
        Hyperliquid格式: BTC (不加后缀)
        输入: BTC -> BTC, BTCUSDT -> BTC
        """
        # 移除常见后缀
        symbol = symbol.upper()
        for suffix in ['USDT', 'USD', '-PERP', '-PERPETUAL']:
            if symbol.endswith(suffix):
                symbol = symbol[:len(symbol) - len(suffix)]
        return symbol
    
    def _normalize_interval(self, interval: str) -> str:
        """
        标准化时间周期
        
        Hyperliquid支持: 1m, 1h, 1d
        """
        interval_map = {
            '1m': '1m',
            '5m': '1m',  # Hyperliquid不支持5m,使用1m
            '15m': '1m',  # 使用1m
            '1h': '1h',
            '4h': '1h',  # 使用1h
            '1d': '1d'
        }
        return interval_map.get(interval.lower(), '1h')
    
    async def get_klines(
        self,
        symbol: str,
        interval: str,
        limit: int = 100,
        market_type: str = 'perpetual'
    ) -> List[Dict[str, Any]]:
        """获取K线数据"""
        try:
            if not self.is_initialized or not self.info:
                return []
            
            normalized_symbol = self._normalize_symbol(symbol)
            normalized_interval = self._normalize_interval(interval)
            
            # 计算时间范围
            import time
            end_time = int(time.time() * 1000)
            
            # 根据周期计算开始时间
            interval_ms = {
                '1m': 60 * 1000,
                '1h': 60 * 60 * 1000,
                '1d': 24 * 60 * 60 * 1000
            }
            start_time = end_time - (limit * interval_ms.get(normalized_interval, 60000))
            
            # 获取K线数据
            candles = self.info.candles_snapshot(
                normalized_symbol,
                normalized_interval,
                start_time,
                end_time
            )
            
            if not candles:
                return []
            
            # 标准化返回格式
            result = []
            for candle in candles:
                result.append({
                    'timestamp': candle.get('t', 0) // 1000,  # 毫秒转秒
                    'open': float(candle.get('o', 0)),
                    'high': float(candle.get('h', 0)),
                    'low': float(candle.get('l', 0)),
                    'close': float(candle.get('c', 0)),
                    'volume': float(candle.get('v', 0)),
                    'source': 'hyperliquid',
                    'market_type': 'perpetual'
                })
            
            return result
            
        except Exception as e:
            logger.error(f"获取K线失败: {e}", exc_info=True)
            return []
    
    async def get_account_balance(self, market_type: str = 'perpetual') -> Dict[str, Any]:
        """获取账户余额"""
        try:
            if not self.is_initialized or not self.info:
                return self._empty_balance()
            
            query_address = self.vault_address if self.vault_address else self.wallet_address
            user_state = self.info.user_state(query_address)
            
            margin_summary = user_state.get('marginSummary', {})
            
            return {
                'total_balance': float(margin_summary.get('accountValue', 0)),
                'available_balance': float(user_state.get('withdrawable', 0)),
                'locked_balance': float(margin_summary.get('totalMarginUsed', 0)),
                'unrealized_pnl': 0,  # 计算所有持仓的未实现盈亏
                'assets': {}
            }
            
        except Exception as e:
            logger.error(f"获取账户余额失败: {e}", exc_info=True)
            return self._empty_balance()
    
    def _empty_balance(self) -> Dict[str, Any]:
        """空余额"""
        return {
            'total_balance': 0,
            'available_balance': 0,
            'locked_balance': 0,
            'assets': {}
        }
    
    async def place_order(
        self,
        symbol: str,
        side: str,
        size: Decimal,
        price: Optional[Decimal] = None,
        order_type: str = "market",
        market_type: str = 'perpetual'
    ) -> Dict[str, Any]:
        """下单"""
        try:
            if not self.is_initialized or not self.exchange:
                return {'success': False, 'error': '交易所未初始化'}
            
            normalized_symbol = self._normalize_symbol(symbol)
            is_buy = side.lower() in ['buy', 'long']
            
            # Hyperliquid下单参数
            order_request = {
                'a': self.vault_address if self.vault_address else self.wallet_address,
                'b': is_buy,
                's': float(size),
                'r': False,  # reduce_only
                't': {'limit': {'tif': 'Gtc'}} if order_type == 'limit' else {'market': {}}
            }
            
            if order_type == 'limit' and price:
                order_request['p'] = str(float(price))
            
            # 执行下单
            result = self.exchange.order(normalized_symbol, is_buy, float(size), None, order_request)
            
            logger.info(f"下单结果: {result}")
            
            return {
                'success': True,
                'order_id': str(result.get('response', {}).get('data', {}).get('statuses', [{}])[0].get('oid', '')),
                'status': 'filled' if result.get('status') == 'ok' else 'pending',
                'filled_size': float(size),
                'filled_price': float(price) if price else 0
            }
            
        except Exception as e:
            logger.error(f"下单失败: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}
    
    async def cancel_order(
        self,
        order_id: str,
        symbol: str,
        market_type: str = 'perpetual'
    ) -> Dict[str, Any]:
        """撤销订单"""
        try:
            if not self.is_initialized or not self.exchange:
                return {'success': False, 'message': '交易所未初始化'}
            
            normalized_symbol = self._normalize_symbol(symbol)
            
            # Hyperliquid撤单
            result = self.exchange.cancel(normalized_symbol, int(order_id))
            
            return {
                'success': result.get('status') == 'ok',
                'message': f"订单 {order_id} 已撤销"
            }
            
        except Exception as e:
            logger.error(f"撤销订单失败: {e}")
            return {'success': False, 'message': str(e)}
    
    async def get_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取持仓"""
        try:
            if not self.is_initialized or not self.info:
                return []
            
            query_address = self.vault_address if self.vault_address else self.wallet_address
            user_state = self.info.user_state(query_address)
            
            positions = user_state.get('assetPositions', [])
            
            result = []
            for pos in positions:
                position_data = pos.get('position', {})
                coin = position_data.get('coin', '')
                
                # 如果指定了symbol,过滤
                if symbol and self._normalize_symbol(symbol) != coin:
                    continue
                
                size = float(position_data.get('szi', 0))
                if size == 0:
                    continue
                
                result.append({
                    'symbol': coin,
                    'side': 'long' if size > 0 else 'short',
                    'size': abs(size),
                    'entry_price': float(position_data.get('entryPx', 0)),
                    'mark_price': float(position_data.get('markPx', 0)),
                    'unrealized_pnl': float(pos.get('unrealizedPnl', 0)),
                    'liquidation_price': float(position_data.get('liquidationPx', 0)),
                    'leverage': int(position_data.get('leverage', {}).get('value', 1))
                })
            
            return result
            
        except Exception as e:
            logger.error(f"获取持仓失败: {e}", exc_info=True)
            return []
    
    async def close_position(
        self,
        symbol: str,
        side: Optional[str] = None
    ) -> Dict[str, Any]:
        """平仓"""
        try:
            positions = await self.get_positions(symbol)
            
            if not positions:
                return {
                    'success': True,
                    'closed_size': 0,
                    'realized_pnl': 0,
                    'message': '无持仓需要平仓'
                }
            
            total_closed = 0
            total_pnl = 0
            
            for pos in positions:
                if side and pos['side'] != side:
                    continue
                
                # 平仓方向与持仓相反
                close_side = 'sell' if pos['side'] == 'long' else 'buy'
                
                result = await self.place_order(
                    symbol=pos['symbol'],
                    side=close_side,
                    size=Decimal(str(pos['size'])),
                    price=None,
                    order_type='market'
                )
                
                if result['success']:
                    total_closed += pos['size']
                    total_pnl += pos['unrealized_pnl']
            
            return {
                'success': True,
                'closed_size': total_closed,
                'realized_pnl': total_pnl
            }
            
        except Exception as e:
            logger.error(f"平仓失败: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}
    
    async def get_ticker(self, symbol: str, market_type: str = 'perpetual') -> Dict[str, Any]:
        """获取实时行情"""
        try:
            if not self.is_initialized or not self.info:
                return {}
            
            normalized_symbol = self._normalize_symbol(symbol)
            
            # 获取所有市场元数据
            meta = self.info.all_mids()
            
            if normalized_symbol not in meta:
                return {}
            
            price = float(meta[normalized_symbol])
            
            return {
                'symbol': normalized_symbol,
                'last_price': price,
                'bid_price': price,  # Hyperliquid不提供bid/ask分离
                'ask_price': price,
                'volume_24h': 0,  # 需要额外API调用
                'price_change_24h': 0,
                'funding_rate': None,  # 需要额外API调用
                'open_interest': 0
            }
            
        except Exception as e:
            logger.error(f"获取行情失败: {e}", exc_info=True)
            return {}
    
    async def get_order_book(
        self,
        symbol: str,
        depth: int = 20,
        market_type: str = 'perpetual'
    ) -> Dict[str, Any]:
        """获取订单簿"""
        try:
            if not self.is_initialized or not self.info:
                return {'bids': [], 'asks': [], 'timestamp': 0}
            
            normalized_symbol = self._normalize_symbol(symbol)
            
            # Hyperliquid订单簿
            l2_data = self.info.l2_snapshot(normalized_symbol)
            
            if not l2_data:
                return {'bids': [], 'asks': [], 'timestamp': 0}
            
            return {
                'bids': [[float(level['px']), float(level['sz'])] for level in l2_data.get('levels', [])[:depth] if level.get('n') > 0][:depth],
                'asks': [[float(level['px']), float(level['sz'])] for level in l2_data.get('levels', [])[:depth] if level.get('n') < 0][:depth],
                'timestamp': l2_data.get('time', int(datetime.now().timestamp() * 1000))
            }
            
        except Exception as e:
            logger.error(f"获取订单簿失败: {e}", exc_info=True)
            return {'bids': [], 'asks': [], 'timestamp': 0}
    
    def supports_spot(self) -> bool:
        """不支持现货交易"""
        return False
    
    def supports_futures(self) -> bool:
        """支持永续合约"""
        return True

