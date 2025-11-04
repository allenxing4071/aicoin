"""Intelligence Report Database Models"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, Text, JSON, Index
from app.core.database import Base


class IntelligenceReport(Base):
    """情报报告持久化存储模型"""
    __tablename__ = "intelligence_reports"
    
    # 主键
    id = Column(Integer, primary_key=True, index=True)
    
    # 时间戳（业务主键）
    timestamp = Column(DateTime, nullable=False, unique=True, index=True)
    
    # 市场情绪
    market_sentiment = Column(String(20), nullable=False, index=True)  # BULLISH/BEARISH/NEUTRAL
    sentiment_score = Column(Float, nullable=False)  # -1.0 to 1.0
    
    # 置信度
    confidence = Column(Float, nullable=False, default=0.5)  # 0.0 to 1.0
    
    # 新闻数据（JSON格式）
    key_news = Column(JSON, nullable=True)
    # [{title, source, url, published_at, content, impact, sentiment}, ...]
    
    # 巨鲸活动（JSON格式）
    whale_signals = Column(JSON, nullable=True)
    # [{symbol, action, amount_usd, address, timestamp, exchange}, ...]
    
    # 链上指标（JSON格式）
    on_chain_metrics = Column(JSON, nullable=True)
    # {exchange_net_flow, active_addresses, gas_price, transaction_volume, timestamp}
    
    # 风险因素（JSON数组）
    risk_factors = Column(JSON, nullable=True)
    # ["风险1", "风险2", ...]
    
    # 机会点（JSON数组）
    opportunities = Column(JSON, nullable=True)
    # ["机会1", "机会2", ...]
    
    # Qwen分析（长文本）
    qwen_analysis = Column(Text, nullable=True)
    
    # 元数据
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # 索引
    __table_args__ = (
        Index('idx_intelligence_timestamp', 'timestamp'),
        Index('idx_intelligence_sentiment', 'market_sentiment'),
        Index('idx_intelligence_created', 'created_at'),
        Index('idx_intelligence_confidence', 'confidence'),
    )
    
    def __repr__(self):
        return f"<IntelligenceReport(timestamp={self.timestamp}, sentiment={self.market_sentiment}, confidence={self.confidence:.2f})>"
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "market_sentiment": self.market_sentiment,
            "sentiment_score": self.sentiment_score,
            "confidence": self.confidence,
            "key_news": self.key_news or [],
            "whale_signals": self.whale_signals or [],
            "on_chain_metrics": self.on_chain_metrics or {},
            "risk_factors": self.risk_factors or [],
            "opportunities": self.opportunities or [],
            "qwen_analysis": self.qwen_analysis,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

