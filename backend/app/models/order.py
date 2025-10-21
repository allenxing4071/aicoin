"""Order model"""

from sqlalchemy import Column, Integer, String, Numeric, DateTime, Index
from sqlalchemy.sql import func
from app.core.database import Base


class Order(Base):
    """订单表"""
    
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True, index=True)
    trade_id = Column(Integer, nullable=True)
    symbol = Column(String(20), nullable=False)
    side = Column(String(10), nullable=False)  # BUY or SELL
    type = Column(String(10), nullable=False)  # MARKET or LIMIT
    price = Column(Numeric(18, 8), nullable=True)  # For LIMIT orders
    size = Column(Numeric(18, 8), nullable=False)
    filled_size = Column(Numeric(18, 8), default=0)
    status = Column(String(20), nullable=False)  # PENDING, FILLED, CANCELLED, FAILED
    exchange_order_id = Column(String(100), nullable=True)  # External order ID
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_orders_status', 'status'),
        Index('idx_orders_created', 'created_at'),
    )
    
    def __repr__(self):
        return f"<Order(id={self.id}, symbol={self.symbol}, side={self.side}, status={self.status})>"

