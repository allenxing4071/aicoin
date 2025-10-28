"""Trade schemas"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime
from decimal import Decimal


class TradeBase(BaseModel):
    """Base trade schema"""
    symbol: str
    side: str  # BUY or SELL
    price: Decimal
    size: Decimal


class TradeCreate(TradeBase):
    """Create trade schema"""
    order_id: Optional[int] = None
    pnl: Optional[Decimal] = None
    fee: Optional[Decimal] = None
    ai_reasoning: Optional[str] = None
    confidence: Optional[Decimal] = None


class TradeResponse(TradeBase):
    """Trade response schema"""
    id: int
    order_id: Optional[int]
    pnl: Optional[Decimal]
    fee: Optional[Decimal]
    ai_reasoning: Optional[str]
    confidence: Optional[Decimal]
    model: Optional[str] = None  # AI model name
    timestamp: datetime
    created_at: datetime
    
    class Config:
        from_attributes = True


class TradeList(BaseModel):
    """List of trades"""
    trades: List[TradeResponse]
    total: int
    page: int = 1
    page_size: int = 20

