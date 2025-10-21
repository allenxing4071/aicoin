"""Account schemas"""

from pydantic import BaseModel
from typing import Optional, List
from decimal import Decimal


class PositionInfo(BaseModel):
    """持仓信息"""
    symbol: str
    size: Decimal
    entry_price: Decimal
    current_price: Optional[Decimal] = None
    unrealized_pnl: Optional[Decimal] = None
    unrealized_pnl_pct: Optional[Decimal] = None


class AccountInfo(BaseModel):
    """账户信息"""
    balance: Decimal
    equity: Decimal
    unrealized_pnl: Decimal
    realized_pnl: Decimal
    margin_used: Optional[Decimal] = None
    margin_available: Optional[Decimal] = None
    positions: List[PositionInfo] = []

