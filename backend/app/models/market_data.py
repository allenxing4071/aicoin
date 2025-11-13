"""Market data model"""

from sqlalchemy import Column, Integer, String, Numeric, DateTime, Index, UniqueConstraint
from sqlalchemy.sql import func
from app.core.database import Base


class MarketDataKline(Base):
    """K线数据表"""
    
    __tablename__ = "market_data_kline"
    
    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(20), nullable=False)
    interval = Column(String(10), nullable=False)  # 1m, 5m, 1h, 4h, 1d
    open_time = Column(DateTime(timezone=True), nullable=False)
    close_time = Column(DateTime(timezone=True), nullable=False)
    open = Column(Numeric(18, 8), nullable=False)
    high = Column(Numeric(18, 8), nullable=False)
    low = Column(Numeric(18, 8), nullable=False)
    close = Column(Numeric(18, 8), nullable=False)
    volume = Column(Numeric(18, 8), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Unique constraint and indexes
    __table_args__ = (
        UniqueConstraint('symbol', 'interval', 'open_time', name='uq_kline_symbol_interval_time'),
        Index('idx_kline_symbol_interval_time', 'symbol', 'interval', 'open_time'),
        {'comment': '📈 K线数据 - 存储各币种的历史K线图数据（开高低收、成交量等）'}
    )
    
    def __repr__(self):
        return f"<MarketDataKline(symbol={self.symbol}, interval={self.interval}, close={self.close})>"

