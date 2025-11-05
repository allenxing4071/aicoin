"""多周期K线聚合器 - 支持现货/合约对比分析"""

import asyncio
import logging
from typing import Dict, List, Optional, Any
from decimal import Decimal

from app.services.exchange.base_adapter import BaseExchangeAdapter
from app.core.config import settings

logger = logging.getLogger(__name__)


class KlineAggregator:
    """
    多周期K线聚合器
    
    功能:
    1. 同时获取多个时间周期的K线数据
    2. 现货vs合约价格对比分析
    3. 技术指标计算(可扩展)
    """
    
    def __init__(self, exchange: BaseExchangeAdapter):
        self.exchange = exchange
        self.intervals = settings.KLINE_INTERVALS  # ["1m", "5m", "15m", "1h", "4h", "1d"]
    
    async def get_multi_timeframe_klines(
        self,
        symbol: str,
        market_type: str = 'spot',
        intervals: Optional[List[str]] = None
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        获取多周期K线数据
        
        Args:
            symbol: 交易对符号
            market_type: 市场类型 ('spot', 'futures', 'perpetual')
            intervals: 时间周期列表 (None则使用默认)
            
        Returns:
            Dict[str, List]: 每个周期的K线数据
                {
                    "1m": [kline_data...],
                    "5m": [kline_data...],
                    ...
                }
        """
        try:
            if intervals is None:
                intervals = self.intervals
            
            logger.info(f"获取多周期K线: {symbol} {market_type} {intervals}")
            
            # 并发获取所有周期的K线数据
            tasks = []
            for interval in intervals:
                task = self.exchange.get_klines(
                    symbol=symbol,
                    interval=interval,
                    limit=100,
                    market_type=market_type
                )
                tasks.append(task)
            
            # 等待所有任务完成
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # 组装结果
            multi_klines = {}
            for i, interval in enumerate(intervals):
                if isinstance(results[i], Exception):
                    logger.error(f"获取{interval}K线失败: {results[i]}")
                    multi_klines[interval] = []
                else:
                    multi_klines[interval] = results[i] or []
            
            return multi_klines
            
        except Exception as e:
            logger.error(f"获取多周期K线失败: {e}", exc_info=True)
            return {interval: [] for interval in (intervals or self.intervals)}
    
    async def get_spot_futures_comparison(
        self,
        symbol: str
    ) -> Dict[str, Any]:
        """
        现货vs合约价格对比分析
        
        Args:
            symbol: 交易对符号
            
        Returns:
            Dict: 对比分析结果
                {
                    "spot_price": float,
                    "futures_price": float,
                    "price_diff": float,
                    "premium_rate": float,  # 溢价率 (%)
                    "funding_rate": float,  # 资金费率 (仅合约)
                    "open_interest": float,  # 持仓量 (仅合约)
                    "spot_volume_24h": float,
                    "futures_volume_24h": float,
                }
        """
        try:
            # 检查交易所是否支持现货和合约
            if not self.exchange.supports_both_markets():
                logger.warning(f"{self.exchange.name} 不支持现货和合约同时查询")
                return self._empty_comparison()
            
            # 并发获取现货和合约数据
            spot_ticker_task = self.exchange.get_ticker(symbol, market_type='spot')
            futures_ticker_task = self.exchange.get_ticker(symbol, market_type='perpetual')
            
            spot_ticker, futures_ticker = await asyncio.gather(
                spot_ticker_task,
                futures_ticker_task,
                return_exceptions=True
            )
            
            # 处理异常
            if isinstance(spot_ticker, Exception):
                logger.error(f"获取现货行情失败: {spot_ticker}")
                spot_ticker = {}
            if isinstance(futures_ticker, Exception):
                logger.error(f"获取合约行情失败: {futures_ticker}")
                futures_ticker = {}
            
            spot_price = spot_ticker.get('last_price', 0)
            futures_price = futures_ticker.get('last_price', 0)
            
            # 计算价差和溢价率
            price_diff = futures_price - spot_price
            premium_rate = (price_diff / spot_price * 100) if spot_price > 0 else 0
            
            return {
                'spot_price': float(spot_price),
                'futures_price': float(futures_price),
                'price_diff': float(price_diff),
                'premium_rate': float(premium_rate),
                'funding_rate': futures_ticker.get('funding_rate'),
                'open_interest': futures_ticker.get('open_interest', 0),
                'spot_volume_24h': spot_ticker.get('volume_24h', 0),
                'futures_volume_24h': futures_ticker.get('volume_24h', 0),
                'spot_price_change_24h': spot_ticker.get('price_change_24h', 0),
                'futures_price_change_24h': futures_ticker.get('price_change_24h', 0),
            }
            
        except Exception as e:
            logger.error(f"现货合约对比分析失败: {e}", exc_info=True)
            return self._empty_comparison()
    
    def _empty_comparison(self) -> Dict[str, Any]:
        """空的对比结果"""
        return {
            'spot_price': 0,
            'futures_price': 0,
            'price_diff': 0,
            'premium_rate': 0,
            'funding_rate': None,
            'open_interest': 0,
            'spot_volume_24h': 0,
            'futures_volume_24h': 0,
            'spot_price_change_24h': 0,
            'futures_price_change_24h': 0,
        }
    
    def calculate_technical_indicators(
        self,
        klines: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        计算技术指标
        
        Args:
            klines: K线数据
            
        Returns:
            Dict: 技术指标
                {
                    "ma_5": float,
                    "ma_20": float,
                    "ma_60": float,
                    "rsi_14": float,
                    "macd": {"dif": float, "dea": float, "macd": float},
                    "volume_ma_5": float,
                }
        """
        try:
            if not klines or len(klines) < 2:
                return {}
            
            closes = [k['close'] for k in klines]
            volumes = [k['volume'] for k in klines]
            
            # 移动平均线 (MA)
            ma_5 = self._calculate_ma(closes, 5)
            ma_20 = self._calculate_ma(closes, 20)
            ma_60 = self._calculate_ma(closes, 60)
            
            # RSI
            rsi_14 = self._calculate_rsi(closes, 14)
            
            # 成交量均线
            volume_ma_5 = self._calculate_ma(volumes, 5)
            
            return {
                'ma_5': ma_5,
                'ma_20': ma_20,
                'ma_60': ma_60,
                'rsi_14': rsi_14,
                'volume_ma_5': volume_ma_5,
                'current_price': closes[-1] if closes else 0,
                'price_above_ma_20': closes[-1] > ma_20 if closes and ma_20 else False,
            }
            
        except Exception as e:
            logger.error(f"计算技术指标失败: {e}", exc_info=True)
            return {}
    
    def _calculate_ma(self, data: List[float], period: int) -> Optional[float]:
        """计算移动平均线"""
        if len(data) < period:
            return None
        return sum(data[-period:]) / period
    
    def _calculate_rsi(self, closes: List[float], period: int = 14) -> Optional[float]:
        """
        计算RSI指标
        
        RSI = 100 - (100 / (1 + RS))
        RS = Average Gain / Average Loss
        """
        if len(closes) < period + 1:
            return None
        
        try:
            gains = []
            losses = []
            
            for i in range(1, len(closes)):
                change = closes[i] - closes[i-1]
                if change > 0:
                    gains.append(change)
                    losses.append(0)
                else:
                    gains.append(0)
                    losses.append(abs(change))
            
            if len(gains) < period:
                return None
            
            avg_gain = sum(gains[-period:]) / period
            avg_loss = sum(losses[-period:]) / period
            
            if avg_loss == 0:
                return 100
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
            
        except Exception as e:
            logger.error(f"RSI计算失败: {e}")
            return None
    
    async def get_comprehensive_market_analysis(
        self,
        symbol: str,
        market_type: str = 'spot'
    ) -> Dict[str, Any]:
        """
        获取综合市场分析
        
        包括:
        1. 多周期K线
        2. 技术指标
        3. 现货合约对比(如果支持)
        
        Args:
            symbol: 交易对符号
            market_type: 市场类型
            
        Returns:
            Dict: 综合分析结果
        """
        try:
            # 1. 获取多周期K线
            multi_klines = await self.get_multi_timeframe_klines(symbol, market_type)
            
            # 2. 计算技术指标 (使用1h周期)
            indicators = {}
            if '1h' in multi_klines and multi_klines['1h']:
                indicators = self.calculate_technical_indicators(multi_klines['1h'])
            
            # 3. 现货合约对比 (如果交易所支持)
            spot_futures_compare = None
            if self.exchange.supports_both_markets():
                spot_futures_compare = await self.get_spot_futures_comparison(symbol)
            
            return {
                'symbol': symbol,
                'market_type': market_type,
                'multi_timeframe_klines': multi_klines,
                'technical_indicators': indicators,
                'spot_futures_comparison': spot_futures_compare,
                'timestamp': asyncio.get_event_loop().time()
            }
            
        except Exception as e:
            logger.error(f"综合市场分析失败: {e}", exc_info=True)
            return {
                'symbol': symbol,
                'market_type': market_type,
                'multi_timeframe_klines': {},
                'technical_indicators': {},
                'spot_futures_comparison': None,
                'error': str(e)
            }
    
    def get_kline_summary(self, klines: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        获取K线摘要信息
        
        Args:
            klines: K线数据列表
            
        Returns:
            Dict: 摘要信息
        """
        if not klines:
            return {}
        
        try:
            closes = [k['close'] for k in klines]
            highs = [k['high'] for k in klines]
            lows = [k['low'] for k in klines]
            volumes = [k['volume'] for k in klines]
            
            current_price = closes[-1]
            price_change = ((closes[-1] - closes[0]) / closes[0] * 100) if closes[0] > 0 else 0
            
            return {
                'count': len(klines),
                'current_price': current_price,
                'highest': max(highs),
                'lowest': min(lows),
                'average': sum(closes) / len(closes),
                'price_change_pct': price_change,
                'total_volume': sum(volumes),
                'first_timestamp': klines[0]['timestamp'],
                'last_timestamp': klines[-1]['timestamp'],
            }
            
        except Exception as e:
            logger.error(f"K线摘要计算失败: {e}")
            return {}

