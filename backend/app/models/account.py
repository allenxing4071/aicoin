"""Account snapshot model"""

from sqlalchemy import Column, Integer, Numeric, DateTime, Index
from sqlalchemy.sql import func
from app.core.database import Base


class AccountSnapshot(Base):
    """账户快照表 - 记录账户状态"""
    
    __tablename__ = "account_snapshots"
    __table_args__ = (
        Index('idx_account_timestamp', 'timestamp'),
        {'comment': '💼 账户快照 - 定期记录账户余额、权益、盈亏、夏普比率等关键财务指标'}
    )
    
    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    balance = Column(Numeric(18, 8), nullable=False)  # Available balance
    equity = Column(Numeric(18, 8), nullable=False)  # Total equity
    unrealized_pnl = Column(Numeric(18, 8), nullable=True)  # Unrealized PnL
    realized_pnl = Column(Numeric(18, 8), nullable=True)  # Realized PnL
    sharpe_ratio = Column(Numeric(10, 4), nullable=True)
    max_drawdown = Column(Numeric(5, 4), nullable=True)
    total_trades = Column(Integer, default=0)
    win_rate = Column(Numeric(5, 4), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<AccountSnapshot(id={self.id}, balance={self.balance}, equity={self.equity})>"

