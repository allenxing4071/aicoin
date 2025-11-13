"""Risk event model"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, ForeignKey, Index
from sqlalchemy.sql import func
from app.core.database import Base


class RiskEvent(Base):
    """风控事件表"""
    
    __tablename__ = "risk_events"
    __table_args__ = (
        Index('idx_risk_timestamp', 'timestamp'),
        Index('idx_risk_severity', 'severity'),
        {'comment': '风控事件 - 记录触发的风控警报、事件类型、严重程度和处理措施'}
    )
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    event_type = Column(String(50), nullable=False)  # POSITION_LIMIT, DAILY_LOSS, etc.
    severity = Column(String(20), nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    description = Column(Text, nullable=False)
    related_trade_id = Column(Integer, ForeignKey("trades.id"), nullable=True)
    action_taken = Column(Text, nullable=True)  # What action was taken
    resolved = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<RiskEvent(id={self.id}, type={self.event_type}, severity={self.severity})>"

