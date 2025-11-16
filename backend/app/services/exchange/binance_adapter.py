"""币安交易所适配器 - 支持现货和合约交易"""

import asyncio
from typing import Dict, List, Optional, Any
from decimal import Decimal
from datetime import datetime
import logging

from binance.client import Client
from binance.exceptions import BinanceAPIException
from binance import AsyncClient

from app.services.exchange.base_adapter import BaseExchangeAdapter
from app.core.config import settings

logger = logging.getLogger(__name__)


class BinanceAdapter(BaseExchangeAdapter):
    """
    币安交易所适配器
    
    支持现货(Spot)和合约(Futures/Perpetual)交易
    """
    
    def __init__(self, api_key: str, api_secret: str, testnet: bool = False):
        super().__init__()
        self.name = "binance"
        self.api_key = api_key
        self.api_secret = api_secret
        self.testnet = testnet
        
        # 客户端
        self.spot_client: Optional[AsyncClient] = None
        self.futures_client: Optional[AsyncClient] = None
        
    async def initialize(self) -> bool:
        """初始化币安客户端"""
        try:
            logger.info(f"初始化币安适配器 (testnet={self.testnet})...")
            
            # 创建异步现货客户端
            self.spot_client = await AsyncClient.create(
                api_key=self.api_key,
                api_secret=self.api_secret,
                testnet=self.testnet
            )
            
            # 创建异步合约客户端  
            # 注意: 币安的合约客户端使用相同的API密钥
            self.futures_client = await AsyncClient.create(
                api_key=self.api_key,
                api_secret=self.api_secret,
                testnet=self.testnet
            )
            
            # 验证连接
            await self._verify_connection()
            
            self.is_initialized = True
            logger.info("✅ 币安适配器初始化成功")
            return True
            
        except Exception as e:
            logger.error(f"❌ 币安初始化失败: {e}", exc_info=True)
            self.is_initialized = False
            return False
    
    async def _verify_connection(self):
        """验证API连接"""
        try:
            # 测试现货API
            account = await self.spot_client.get_account()
            logger.info(f"现货账户余额验证成功")
            
            # 测试合约API
            if self.supports_futures():
                try:
                    futures_account = await self.futures_client.futures_account()
                    logger.info(f"合约账户验证成功: totalWalletBalance={futures_account.get('totalWalletBalance', 0)}")
                except Exception as fe:
                    logger.warning(f"合约账户验证失败（可能未开通合约或API权限不足）: {fe}")
                
        except Exception as e:
            raise Exception(f"API连接验证失败: {e}")
    
    def _normalize_symbol(self, symbol: str, market_type: str = 'spot') -> str:
        """
        标准化交易对符号
        
        币安格式: BTCUSDT (现货和合约都一样)
        输入: BTC -> BTCUSDT
        """
        if 'USDT' in symbol.upper():
            return symbol.upper()
        return f"{symbol.upper()}USDT"
    
    def _normalize_interval(self, interval: str) -> str:
        """
        标准化时间周期
        
        统一格式 -> 币安格式
        1m -> 1m
        5m -> 5m
        15m -> 15m
        1h -> 1h
        4h -> 4h
        1d -> 1d
        """
        return interval.lower()
    
    async def get_klines(
        self,
        symbol: str,
        interval: str,
        limit: int = 100,
        market_type: str = 'spot'
    ) -> List[Dict[str, Any]]:
        """获取K线数据"""
        try:
            normalized_symbol = self._normalize_symbol(symbol, market_type)
            normalized_interval = self._normalize_interval(interval)
            
            if market_type == 'spot':
                klines = await self.spot_client.get_klines(
                    symbol=normalized_symbol,
                    interval=normalized_interval,
                    limit=limit
                )
            else:
                # 合约K线
                klines = await self.futures_client.futures_klines(
                    symbol=normalized_symbol,
                    interval=normalized_interval,
                    limit=limit
                )
            
            # 标准化返回格式
            return self._normalize_klines(klines, market_type)
            
        except BinanceAPIException as e:
            logger.error(f"获取K线失败: {e}")
            return []
        except Exception as e:
            logger.error(f"获取K线异常: {e}", exc_info=True)
            return []
    
    def _normalize_klines(self, klines: List, market_type: str) -> List[Dict[str, Any]]:
        """
        标准化K线数据格式
        
        币安K线格式:
        [
          [
            1499040000000,      // 开盘时间
            "0.01634790",       // 开盘价
            "0.80000000",       // 最高价
            "0.01575800",       // 最低价
            "0.01577100",       // 收盘价
            "148976.11427815",  // 成交量
            ...
          ]
        ]
        """
        result = []
        for k in klines:
            result.append({
                'timestamp': int(k[0]) // 1000,  # 毫秒转秒
                'open': float(k[1]),
                'high': float(k[2]),
                'low': float(k[3]),
                'close': float(k[4]),
                'volume': float(k[5]),
                'source': 'binance',
                'market_type': market_type
            })
        return result
    
    async def get_account_balance(self, market_type: str = 'spot') -> Dict[str, Any]:
        """获取账户余额（汇总所有账户的总资产）"""
        try:
            # 🔥 获取所有账户的总资产（现货+合约+资金账户）
            total_spot_usdt = 0.0
            total_futures_usdt = 0.0
            
            # 1. 获取现货账户余额
            try:
                account = await self.spot_client.get_account()
                balances = account['balances']
                
                for balance in balances:
                    asset = balance['asset']
                    free = float(balance['free'])
                    locked = float(balance['locked'])
                    total_amount = free + locked
                    
                    if total_amount > 0:
                        if asset == 'USDT':
                            asset_value_usdt = total_amount
                            logger.debug(f"现货资产: {asset} = {total_amount:.8f} (价值 ${asset_value_usdt:.2f})")
                        else:
                            try:
                                ticker = await self.spot_client.get_symbol_ticker(symbol=f"{asset}USDT")
                                price = float(ticker['price'])
                                asset_value_usdt = total_amount * price
                                if asset_value_usdt > 0.01:  # 只记录价值超过0.01的资产
                                    logger.info(f"现货资产: {asset} = {total_amount:.8f} × ${price:.4f} = ${asset_value_usdt:.2f}")
                            except Exception as e:
                                logger.debug(f"无法获取 {asset} 价格: {e}")
                                asset_value_usdt = 0
                        
                        total_spot_usdt += asset_value_usdt
                        
            except Exception as e:
                logger.warning(f"获取现货账户失败: {e}")
            
            # 2. 获取合约账户余额
            try:
                futures_account = await self.futures_client.futures_account()
                total_futures_usdt = float(futures_account.get('totalWalletBalance', 0))
            except Exception as e:
                logger.warning(f"获取合约账户失败: {e}")
            
            # 3. 获取资金账户余额（使用FUNDING类型快照）
            total_funding_usdt = 0.0
            try:
                # 尝试使用FUNDING类型快照获取资金账户
                import time
                try:
                    funding_snapshot_params = {
                        'type': 'FUNDING',  # 专门查询资金账户
                        'timestamp': int(time.time() * 1000)
                    }
                    funding_snapshot = await self.spot_client._request('get', 'sapi/v1/accountSnapshot', signed=True, data=funding_snapshot_params)
                    
                    if funding_snapshot.get('code') == 200:
                        funding_snapshots = funding_snapshot.get('snapshotVos', [])
                        if funding_snapshots:
                            latest_funding = funding_snapshots[-1]
                            funding_data = latest_funding.get('data', {})
                            funding_balances = funding_data.get('balances', [])
                            
                            logger.info(f"✅ 成功获取资金账户快照，共 {len(funding_balances)} 种资产")
                            
                            for balance_info in funding_balances:
                                asset_name = balance_info.get('asset', '')
                                free = float(balance_info.get('free', 0))
                                locked = float(balance_info.get('locked', 0))
                                total_amount = free + locked
                                
                                if total_amount > 0.001:  # 忽略极小金额
                                    if asset_name == 'USDT':
                                        asset_value_usdt = total_amount
                                        logger.info(f"💰 资金账户: {asset_name} = {total_amount:.8f} USDT (价值 ${asset_value_usdt:.2f})")
                                    else:
                                        try:
                                            ticker = await self.spot_client.get_symbol_ticker(symbol=f"{asset_name}USDT")
                                            price = float(ticker['price'])
                                            asset_value_usdt = total_amount * price
                                            if asset_value_usdt > 0.01:
                                                logger.info(f"💰 资金账户: {asset_name} = {total_amount:.8f} × ${price:.4f} = ${asset_value_usdt:.2f}")
                                        except:
                                            asset_value_usdt = 0
                                    
                                    total_funding_usdt += asset_value_usdt
                    else:
                        logger.debug(f"资金账户快照返回: {funding_snapshot}")
                        
                except Exception as e:
                    logger.warning(f"获取资金账户快照失败: {e}")
                    
            except Exception as e:
                logger.warning(f"获取资金账户失败: {e}")
            
            # 4. 汇总总资产
            total_balance = total_spot_usdt + total_futures_usdt + total_funding_usdt
            
            logger.info(f"币安账户汇总: 现货={total_spot_usdt:.2f}, 合约={total_futures_usdt:.2f}, 资金={total_funding_usdt:.2f}, 总计={total_balance:.2f} USDT")
            
            return {
                'total_balance': total_balance,
                'available_balance': total_balance,  # 简化处理，总余额即可用余额
                'locked_balance': 0,
                'unrealized_pnl': 0,
                'assets': {
                    'spot': total_spot_usdt,
                    'futures': total_futures_usdt
                }
            }
                
        except Exception as e:
            logger.error(f"获取账户余额失败: {e}", exc_info=True)
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
        market_type: str = 'spot'
    ) -> Dict[str, Any]:
        """下单"""
        try:
            normalized_symbol = self._normalize_symbol(symbol, market_type)
            
            # 标准化方向
            binance_side = self._normalize_side(side)
            binance_order_type = order_type.upper()
            
            if market_type == 'spot':
                return await self._place_spot_order(
                    normalized_symbol, binance_side, size, price, binance_order_type
                )
            else:
                return await self._place_futures_order(
                    normalized_symbol, binance_side, size, price, binance_order_type
                )
                
        except Exception as e:
            logger.error(f"下单失败: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def _normalize_side(self, side: str) -> str:
        """标准化方向"""
        side_lower = side.lower()
        if side_lower in ['buy', 'long']:
            return 'BUY'
        elif side_lower in ['sell', 'short']:
            return 'SELL'
        else:
            return side.upper()
    
    async def _place_spot_order(
        self,
        symbol: str,
        side: str,
        size: Decimal,
        price: Optional[Decimal],
        order_type: str
    ) -> Dict[str, Any]:
        """现货下单"""
        try:
            params = {
                'symbol': symbol,
                'side': side,
                'type': order_type,
                'quantity': float(size),
            }
            
            if order_type == 'LIMIT':
                params['price'] = float(price)
                params['timeInForce'] = 'GTC'
            
            order = await self.spot_client.create_order(**params)
            
            return {
                'success': True,
                'order_id': str(order['orderId']),
                'status': order['status'],
                'filled_size': float(order.get('executedQty', 0)),
                'filled_price': float(order.get('price', 0)) if order.get('price') else 0,
            }
            
        except BinanceAPIException as e:
            return {
                'success': False,
                'error': f"Binance API错误: {e.message}"
            }
    
    async def _place_futures_order(
        self,
        symbol: str,
        side: str,
        size: Decimal,
        price: Optional[Decimal],
        order_type: str
    ) -> Dict[str, Any]:
        """合约下单 - size 是 USD 价值，需要转换为币的数量"""
        try:
            # 1. 获取当前价格（如果是市价单）
            if order_type == 'MARKET':
                ticker = await self.futures_client.futures_symbol_ticker(symbol=symbol)
                current_price = float(ticker['price'])
            else:
                current_price = float(price)
            
            # 2. 计算币的数量 = USD价值 / 当前价格
            quantity = float(size) / current_price
            
            # 3. 获取交易对精度信息
            exchange_info = await self.futures_client.futures_exchange_info()
            symbol_info = next((s for s in exchange_info['symbols'] if s['symbol'] == symbol), None)
            
            if symbol_info:
                # 获取数量精度
                quantity_precision = symbol_info.get('quantityPrecision', 3)
                # 四舍五入到正确的精度
                quantity = round(quantity, quantity_precision)
                logger.info(f"💡 {symbol}: USD ${float(size):.2f} ÷ ${current_price:.4f} = {quantity} (精度: {quantity_precision})")
            else:
                logger.warning(f"⚠️ 无法获取 {symbol} 的精度信息，使用默认精度 3")
                quantity = round(quantity, 3)
            
            params = {
                'symbol': symbol,
                'side': side,
                'type': order_type,
                'quantity': quantity,
            }
            
            if order_type == 'LIMIT':
                params['price'] = float(price)
                params['timeInForce'] = 'GTC'
            
            order = await self.futures_client.futures_create_order(**params)
            
            return {
                'success': True,
                'order_id': str(order['orderId']),
                'status': order['status'],
                'filled_size': float(order.get('executedQty', 0)),
                'filled_price': float(order.get('avgPrice', 0)) if order.get('avgPrice') else 0,
            }
            
        except BinanceAPIException as e:
            return {
                'success': False,
                'error': f"Binance API错误: {e.message}"
            }
    
    async def cancel_order(
        self,
        order_id: str,
        symbol: str,
        market_type: str = 'spot'
    ) -> Dict[str, Any]:
        """撤销订单"""
        try:
            normalized_symbol = self._normalize_symbol(symbol, market_type)
            
            if market_type == 'spot':
                result = await self.spot_client.cancel_order(
                    symbol=normalized_symbol,
                    orderId=int(order_id)
                )
            else:
                result = await self.futures_client.futures_cancel_order(
                    symbol=normalized_symbol,
                    orderId=int(order_id)
                )
            
            return {
                'success': True,
                'message': f"订单 {order_id} 已撤销"
            }
            
        except Exception as e:
            logger.error(f"撤销订单失败: {e}")
            return {
                'success': False,
                'message': str(e)
            }
    
    async def get_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """获取持仓 (仅合约)"""
        try:
            positions = await self.futures_client.futures_position_information()
            
            result = []
            for pos in positions:
                position_amt = float(pos['positionAmt'])
                
                # 过滤掉0持仓
                if position_amt == 0:
                    continue
                
                # 如果指定了symbol,过滤
                if symbol and pos['symbol'] != self._normalize_symbol(symbol, 'futures'):
                    continue
                
                result.append({
                    'symbol': pos['symbol'],
                    'side': 'long' if position_amt > 0 else 'short',
                    'size': abs(position_amt),
                    'entry_price': float(pos['entryPrice']),
                    'mark_price': float(pos['markPrice']),
                    'unrealized_pnl': float(pos['unRealizedProfit']),
                    'liquidation_price': float(pos['liquidationPrice']),
                    'leverage': int(pos['leverage'])
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
        """平仓 (仅合约)"""
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
                # 如果指定了方向,只平指定方向
                if side and pos['side'] != side:
                    continue
                
                # 平仓方向与持仓相反
                close_side = 'SELL' if pos['side'] == 'long' else 'BUY'
                
                result = await self._place_futures_order(
                    symbol=pos['symbol'],
                    side=close_side,
                    size=Decimal(str(pos['size'])),
                    price=None,
                    order_type='MARKET'
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
            return {
                'success': False,
                'error': str(e)
            }
    
    async def get_ticker(self, symbol: str, market_type: str = 'spot') -> Dict[str, Any]:
        """获取实时行情"""
        try:
            normalized_symbol = self._normalize_symbol(symbol, market_type)
            
            if market_type == 'spot':
                ticker = await self.spot_client.get_ticker(symbol=normalized_symbol)
                
                return {
                    'symbol': normalized_symbol,
                    'last_price': float(ticker['lastPrice']),
                    'bid_price': float(ticker['bidPrice']),
                    'ask_price': float(ticker['askPrice']),
                    'volume_24h': float(ticker['volume']),
                    'price_change_24h': float(ticker['priceChangePercent']) / 100,
                }
            else:
                # 合约行情
                ticker = await self.futures_client.futures_ticker(symbol=normalized_symbol)
                
                # 获取资金费率
                funding_rate = await self.futures_client.futures_funding_rate(
                    symbol=normalized_symbol,
                    limit=1
                )
                
                return {
                    'symbol': normalized_symbol,
                    'last_price': float(ticker['lastPrice']),
                    'bid_price': float(ticker.get('bidPrice', 0)),
                    'ask_price': float(ticker.get('askPrice', 0)),
                    'volume_24h': float(ticker['volume']),
                    'price_change_24h': float(ticker['priceChangePercent']) / 100,
                    'funding_rate': float(funding_rate[0]['fundingRate']) if funding_rate else None,
                    'open_interest': float(ticker.get('openInterest', 0)),
                }
                
        except Exception as e:
            logger.error(f"获取行情失败: {e}", exc_info=True)
            return {}
    
    async def get_order_book(
        self,
        symbol: str,
        depth: int = 20,
        market_type: str = 'spot'
    ) -> Dict[str, Any]:
        """获取订单簿"""
        try:
            normalized_symbol = self._normalize_symbol(symbol, market_type)
            
            if market_type == 'spot':
                orderbook = await self.spot_client.get_order_book(
                    symbol=normalized_symbol,
                    limit=depth
                )
            else:
                orderbook = await self.futures_client.futures_order_book(
                    symbol=normalized_symbol,
                    limit=depth
                )
            
            return {
                'bids': [[float(p), float(q)] for p, q in orderbook['bids']],
                'asks': [[float(p), float(q)] for p, q in orderbook['asks']],
                'timestamp': orderbook.get('lastUpdateId', int(datetime.now().timestamp()))
            }
            
        except Exception as e:
            logger.error(f"获取订单簿失败: {e}", exc_info=True)
            return {'bids': [], 'asks': [], 'timestamp': 0}
    
    def supports_spot(self) -> bool:
        """支持现货交易"""
        return True
    
    def supports_futures(self) -> bool:
        """支持合约交易"""
        return True
    
    async def close(self):
        """关闭连接"""
        if self.spot_client:
            await self.spot_client.close_connection()
        if self.futures_client:
            await self.futures_client.close_connection()
        logger.info("币安适配器连接已关闭")

