"""Memory system models - Three-layer memory architecture"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, Index
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.sql import func
from app.core.database import Base


class AILesson(Base):
    """AI经验教训表 - 知识库(L3)"""
    
    __tablename__ = "ai_lessons"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    lesson_type = Column(String(50), nullable=False)  # 'success' | 'failure' | 'insight'
    market_regime = Column(String(50), nullable=True)
    symbol = Column(String(10), nullable=True)
    action = Column(String(20), nullable=True)
    
    # 教训内容
    title = Column(String(200), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    confidence_score = Column(Float, default=0.5)
    
    # 关联数据
    related_decisions = Column(ARRAY(Text), nullable=True)  # decision_ids数组
    sample_count = Column(Integer, default=1)
    
    # 验证状态
    validated = Column(Boolean, default=False)
    validation_trades = Column(Integer, default=0)
    validation_success_rate = Column(Float, default=0)
    
    # Indexes
    __table_args__ = (
        Index('idx_ai_lessons_type', 'lesson_type'),
        Index('idx_ai_lessons_regime', 'market_regime'),
        Index('idx_ai_lessons_confidence', 'confidence_score'),
    )
    
    def __repr__(self):
        return f"<AILesson(id={self.id}, type={self.lesson_type}, title={self.title})>"


class AIStrategy(Base):
    """AI策略评估表 - 知识库(L3)"""
    
    __tablename__ = "ai_strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    strategy_name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    
    # 适用条件
    market_regime = Column(String(50), nullable=True)
    applicable_symbols = Column(ARRAY(Text), nullable=True)
    
    # 性能指标
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    win_rate = Column(Float, default=0)
    avg_pnl = Column(Float, default=0)
    sharpe_ratio = Column(Float, default=0)
    max_drawdown = Column(Float, default=0)
    
    # 状态
    status = Column(String(20), default='active')  # 'active' | 'deprecated' | 'testing'
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_ai_strategies_status', 'status'),
        Index('idx_ai_strategies_performance', 'win_rate', 'sharpe_ratio'),
    )
    
    def __repr__(self):
        return f"<AIStrategy(id={self.id}, name={self.strategy_name}, win_rate={self.win_rate})>"


class MarketPattern(Base):
    """市场模式表 - 知识库(L3)"""
    
    __tablename__ = "market_patterns"
    
    id = Column(Integer, primary_key=True, index=True)
    detected_at = Column(DateTime(timezone=True), server_default=func.now())
    
    pattern_type = Column(String(50), nullable=False)  # 'trend_reversal', 'breakout', 'consolidation'
    symbol = Column(String(10), nullable=False)
    
    # 模式特征
    features = Column(JSONB, nullable=False)
    
    # 历史表现
    occurrences = Column(Integer, default=1)
    success_rate = Column(Float, nullable=True)
    avg_profit = Column(Float, nullable=True)
    
    # 最近发生
    last_seen_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Indexes
    __table_args__ = (
        Index('idx_market_patterns_type', 'pattern_type'),
        Index('idx_market_patterns_symbol', 'symbol'),
        Index('idx_market_patterns_last_seen', 'last_seen_at'),
    )
    
    def __repr__(self):
        return f"<MarketPattern(id={self.id}, type={self.pattern_type}, symbol={self.symbol})>"

