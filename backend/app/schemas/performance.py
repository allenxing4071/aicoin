"""Performance metrics schemas"""

from pydantic import BaseModel
from typing import Optional
from decimal import Decimal


class PerformanceMetrics(BaseModel):
    """性能指标"""
    total_return: Decimal  # 总收益率
    sharpe_ratio: Optional[Decimal] = None  # 夏普比率
    max_drawdown: Optional[Decimal] = None  # 最大回撤
    win_rate: Optional[Decimal] = None  # 胜率
    profit_factor: Optional[Decimal] = None  # 盈亏比
    total_trades: int  # 总交易次数
    winning_trades: int = 0
    losing_trades: int = 0
    avg_win: Optional[Decimal] = None
    avg_loss: Optional[Decimal] = None
    current_streak: int = 0  # 当前连续盈亏次数 (正数盈利，负数亏损)

