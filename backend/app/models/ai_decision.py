"""AI decision log model"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func
from app.core.database import Base


class AIDecision(Base):
    """AI决策日志表"""
    
    __tablename__ = "ai_decisions"
    __table_args__ = (
        Index('idx_ai_timestamp', 'timestamp'),
        Index('idx_ai_executed', 'executed'),
        Index('idx_ai_symbol', 'symbol'),
        {'comment': '🤖 AI决策日志 - 记录AI每次决策的市场数据输入、决策输出、执行状态和拒绝原因'}
    )
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    symbol = Column(String(20), nullable=False)
    market_data = Column(JSONB, nullable=False)  # Input market data
    decision = Column(JSONB, nullable=False)  # AI decision output
    executed = Column(Boolean, default=False)  # Whether decision was executed
    reject_reason = Column(Text, nullable=True)  # Why decision was rejected
    model_name = Column(String(50), default='deepseek')
    latency_ms = Column(Integer, nullable=True)  # API call latency
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<AIDecision(id={self.id}, symbol={self.symbol}, executed={self.executed})>"

