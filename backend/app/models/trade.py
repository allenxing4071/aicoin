"""Trade model"""

from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, ForeignKey, Index
from sqlalchemy.sql import func
from app.core.database import Base


class Trade(Base):
    """交易记录表"""
    
    __tablename__ = "trades"
    __table_args__ = (
        Index('idx_trades_timestamp', 'timestamp'),
        Index('idx_trades_symbol', 'symbol'),
        Index('idx_trades_side', 'side'),
        {'comment': '成交记录 - 记录所有已成交的交易明细，包括价格、数量、盈亏、AI决策依据等完整信息'}
    )
    
    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=True)
    symbol = Column(String(20), nullable=False, index=True)
    side = Column(String(10), nullable=False)  # BUY or SELL
    price = Column(Numeric(18, 8), nullable=False)
    size = Column(Numeric(18, 8), nullable=False)
    pnl = Column(Numeric(18, 8), nullable=True)  # Realized PnL
    fee = Column(Numeric(18, 8), nullable=True)
    ai_reasoning = Column(Text, nullable=True)  # AI decision reasoning
    confidence = Column(Numeric(3, 2), nullable=True)  # AI confidence score
    model = Column(String(50), nullable=True, index=True)  # AI model name (deepseek-chat-v3.1, qwen3-max)
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<Trade(id={self.id}, symbol={self.symbol}, side={self.side}, price={self.price})>"

