"""Market data schemas"""

from pydantic import BaseModel
from typing import List, Tuple, Optional
from datetime import datetime
from decimal import Decimal


class KlineData(BaseModel):
    """K线数据"""
    symbol: str
    interval: str
    open_time: datetime
    close_time: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    
    class Config:
        from_attributes = True


class OrderbookLevel(BaseModel):
    """订单簿价格档位"""
    price: Decimal
    size: Decimal


class OrderbookData(BaseModel):
    """订单簿数据"""
    symbol: str
    bids: List[OrderbookLevel]  # 买单
    asks: List[OrderbookLevel]  # 卖单
    timestamp: datetime


class TickerData(BaseModel):
    """实时价格数据"""
    symbol: str
    price: Decimal
    change_24h: Optional[Decimal] = None
    volume_24h: Optional[Decimal] = None
    timestamp: datetime

