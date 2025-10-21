"""Trade model"""

from sqlalchemy import Column, Integer, String, Numeric, DateTime, Text, ForeignKey, Index
from sqlalchemy.sql import func
from app.core.database import Base


class Trade(Base):
    """交易记录表"""
    
    __tablename__ = "trades"
    
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
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_trades_timestamp', 'timestamp'),
        Index('idx_trades_symbol', 'symbol'),
        Index('idx_trades_side', 'side'),
    )
    
    def __repr__(self):
        return f"<Trade(id={self.id}, symbol={self.symbol}, side={self.side}, price={self.price})>"

