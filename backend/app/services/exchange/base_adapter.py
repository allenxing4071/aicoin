"""交易所适配器基类 - 定义统一接口"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any
from decimal import Decimal
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class BaseExchangeAdapter(ABC):
    """
    交易所适配器基类
    
    所有交易所适配器必须实现此接口,提供统一的交易和市场数据访问方法。
    支持现货、合约、永续合约等多种市场类型。
    """
    
    def __init__(self):
        self.name: str = ""  # 交易所名称
        self.is_initialized: bool = False
        
    @abstractmethod
    async def initialize(self) -> bool:
        """
        初始化交易所连接
        
        Returns:
            bool: 初始化是否成功
        """
        pass
    
    @abstractmethod
    async def get_klines(
        self, 
        symbol: str, 
        interval: str, 
        limit: int = 100,
        market_type: str = 'spot'
    ) -> List[Dict[str, Any]]:
        """
        获取K线数据
        
        Args:
            symbol: 交易对符号 (如 'BTC', 'BTCUSDT')
            interval: K线周期 ('1m', '5m', '15m', '1h', '4h', '1d')
            limit: 返回数量
            market_type: 市场类型 ('spot', 'futures', 'perpetual')
            
        Returns:
            List[Dict]: K线数据列表,每个元素包含:
                - timestamp: 时间戳
                - open: 开盘价
                - high: 最高价
                - low: 最低价
                - close: 收盘价
                - volume: 成交量
                - (可选) funding_rate: 资金费率 (仅合约)
                - (可选) open_interest: 持仓量 (仅合约)
        """
        pass
    
    @abstractmethod
    async def get_account_balance(self, market_type: str = 'spot') -> Dict[str, Any]:
        """
        获取账户余额
        
        Args:
            market_type: 市场类型 ('spot', 'futures', 'perpetual')
            
        Returns:
            Dict: 账户余额信息
                - total_balance: 总余额 (USD)
                - available_balance: 可用余额
                - locked_balance: 锁定余额
                - assets: 各币种余额详情
        """
        pass
    
    @abstractmethod
    async def place_order(
        self,
        symbol: str,
        side: str,
        size: Decimal,
        price: Optional[Decimal] = None,
        order_type: str = "market",
        market_type: str = 'spot'
    ) -> Dict[str, Any]:
        """
        下单
        
        Args:
            symbol: 交易对符号
            side: 方向 ('buy', 'sell', 'long', 'short')
            size: 数量 (对于现货是币数量,对于合约是USD价值)
            price: 价格 (限价单必填)
            order_type: 订单类型 ('market', 'limit')
            market_type: 市场类型 ('spot', 'futures', 'perpetual')
            
        Returns:
            Dict: 订单结果
                - success: 是否成功
                - order_id: 订单ID
                - status: 订单状态
                - filled_size: 成交数量
                - filled_price: 成交价格
                - error: 错误信息(如果失败)
        """
        pass
    
    @abstractmethod
    async def cancel_order(
        self,
        order_id: str,
        symbol: str,
        market_type: str = 'spot'
    ) -> Dict[str, Any]:
        """
        撤销订单
        
        Args:
            order_id: 订单ID
            symbol: 交易对符号
            market_type: 市场类型
            
        Returns:
            Dict: 撤销结果
                - success: 是否成功
                - message: 消息
        """
        pass
    
    @abstractmethod
    async def get_positions(self, symbol: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取持仓 (仅合约市场)
        
        Args:
            symbol: 交易对符号 (None表示获取所有持仓)
            
        Returns:
            List[Dict]: 持仓列表
                - symbol: 交易对
                - side: 方向 ('long', 'short')
                - size: 持仓数量
                - entry_price: 开仓价格
                - mark_price: 标记价格
                - unrealized_pnl: 未实现盈亏
                - liquidation_price: 强平价格
                - leverage: 杠杆倍数
        """
        pass
    
    @abstractmethod
    async def close_position(
        self,
        symbol: str,
        side: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        平仓 (仅合约市场)
        
        Args:
            symbol: 交易对符号
            side: 方向 (None表示平掉所有方向)
            
        Returns:
            Dict: 平仓结果
                - success: 是否成功
                - closed_size: 平仓数量
                - realized_pnl: 已实现盈亏
        """
        pass
    
    @abstractmethod
    async def get_ticker(self, symbol: str, market_type: str = 'spot') -> Dict[str, Any]:
        """
        获取实时行情
        
        Args:
            symbol: 交易对符号
            market_type: 市场类型
            
        Returns:
            Dict: 行情数据
                - symbol: 交易对
                - last_price: 最新价格
                - bid_price: 买一价
                - ask_price: 卖一价
                - volume_24h: 24小时成交量
                - price_change_24h: 24小时涨跌幅
                - (可选) funding_rate: 资金费率
                - (可选) open_interest: 持仓量
        """
        pass
    
    @abstractmethod
    async def get_order_book(
        self,
        symbol: str,
        depth: int = 20,
        market_type: str = 'spot'
    ) -> Dict[str, Any]:
        """
        获取订单簿
        
        Args:
            symbol: 交易对符号
            depth: 深度
            market_type: 市场类型
            
        Returns:
            Dict: 订单簿数据
                - bids: 买单 [[price, size], ...]
                - asks: 卖单 [[price, size], ...]
                - timestamp: 时间戳
        """
        pass
    
    def supports_spot(self) -> bool:
        """是否支持现货交易"""
        return True
    
    def supports_futures(self) -> bool:
        """是否支持合约交易"""
        return True
    
    def supports_both_markets(self) -> bool:
        """是否同时支持现货和合约"""
        return self.supports_spot() and self.supports_futures()
    
    async def get_funding_rate(self, symbol: str) -> Optional[float]:
        """
        获取资金费率 (仅合约市场)
        
        Args:
            symbol: 交易对符号
            
        Returns:
            float: 资金费率 (如 0.0001 表示 0.01%)
        """
        try:
            ticker = await self.get_ticker(symbol, market_type='perpetual')
            return ticker.get('funding_rate')
        except Exception as e:
            logger.warning(f"获取资金费率失败: {e}")
            return None
    
    async def get_open_interest(self, symbol: str) -> Optional[float]:
        """
        获取持仓量 (仅合约市场)
        
        Args:
            symbol: 交易对符号
            
        Returns:
            float: 持仓量
        """
        try:
            ticker = await self.get_ticker(symbol, market_type='perpetual')
            return ticker.get('open_interest')
        except Exception as e:
            logger.warning(f"获取持仓量失败: {e}")
            return None
    
    def _normalize_symbol(self, symbol: str, market_type: str = 'spot') -> str:
        """
        标准化交易对符号
        不同交易所可能有不同的符号格式,子类应该重写此方法
        
        Args:
            symbol: 原始符号 (如 'BTC')
            market_type: 市场类型
            
        Returns:
            str: 标准化后的符号
        """
        return symbol
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(name={self.name}, initialized={self.is_initialized})>"

