"""Intelligence Data Models"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional
from enum import Enum


class SentimentType(str, Enum):
    """Market sentiment types"""
    BULLISH = "bullish"
    BEARISH = "bearish"
    NEUTRAL = "neutral"


@dataclass
class NewsItem:
    """Crypto news item"""
    title: str
    source: str
    url: str
    published_at: datetime
    content: Optional[str] = None
    impact: str = "medium"  # low, medium, high
    sentiment: str = "neutral"
    

@dataclass
class WhaleActivity:
    """Whale transaction activity"""
    symbol: str
    action: str  # buy, sell, transfer
    amount_usd: float
    address: str
    timestamp: datetime
    exchange: Optional[str] = None
    

@dataclass
class OnChainMetrics:
    """On-chain data metrics"""
    exchange_net_flow: float  # Net inflow/outflow to exchanges
    active_addresses: int
    gas_price: float
    transaction_volume: float
    timestamp: datetime


@dataclass
class IntelligenceReport:
    """Complete intelligence report from Qwen"""
    timestamp: datetime
    market_sentiment: SentimentType
    sentiment_score: float  # -1.0 to 1.0
    key_news: List[NewsItem]
    whale_signals: List[WhaleActivity]
    on_chain_metrics: OnChainMetrics
    risk_factors: List[str]
    opportunities: List[str]
    qwen_analysis: str  # Qwen's comprehensive analysis in Chinese
    confidence: float = 0.5  # Confidence in the analysis
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage"""
        return {
            "timestamp": self.timestamp.isoformat(),
            "market_sentiment": self.market_sentiment.value,
            "sentiment_score": self.sentiment_score,
            "key_news": [
                {
                    "title": n.title,
                    "source": n.source,
                    "url": n.url,
                    "published_at": n.published_at.isoformat(),
                    "content": n.content,
                    "impact": n.impact,
                    "sentiment": n.sentiment
                }
                for n in self.key_news
            ],
            "whale_signals": [
                {
                    "symbol": w.symbol,
                    "action": w.action,
                    "amount_usd": w.amount_usd,
                    "address": w.address,
                    "timestamp": w.timestamp.isoformat(),
                    "exchange": w.exchange
                }
                for w in self.whale_signals
            ],
            "on_chain_metrics": {
                "exchange_net_flow": self.on_chain_metrics.exchange_net_flow,
                "active_addresses": self.on_chain_metrics.active_addresses,
                "gas_price": self.on_chain_metrics.gas_price,
                "transaction_volume": self.on_chain_metrics.transaction_volume,
                "timestamp": self.on_chain_metrics.timestamp.isoformat()
            },
            "risk_factors": self.risk_factors,
            "opportunities": self.opportunities,
            "qwen_analysis": self.qwen_analysis,
            "confidence": self.confidence
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "IntelligenceReport":
        """Create from dictionary"""
        return cls(
            timestamp=datetime.fromisoformat(data["timestamp"]),
            market_sentiment=SentimentType(data["market_sentiment"]),
            sentiment_score=data["sentiment_score"],
            key_news=[
                NewsItem(
                    title=n["title"],
                    source=n["source"],
                    url=n["url"],
                    published_at=datetime.fromisoformat(n["published_at"]),
                    content=n.get("content"),
                    impact=n.get("impact", "medium"),
                    sentiment=n.get("sentiment", "neutral")
                )
                for n in data["key_news"]
            ],
            whale_signals=[
                WhaleActivity(
                    symbol=w["symbol"],
                    action=w["action"],
                    amount_usd=w["amount_usd"],
                    address=w["address"],
                    timestamp=datetime.fromisoformat(w["timestamp"]),
                    exchange=w.get("exchange")
                )
                for w in data["whale_signals"]
            ],
            on_chain_metrics=OnChainMetrics(
                exchange_net_flow=data["on_chain_metrics"]["exchange_net_flow"],
                active_addresses=data["on_chain_metrics"]["active_addresses"],
                gas_price=data["on_chain_metrics"]["gas_price"],
                transaction_volume=data["on_chain_metrics"]["transaction_volume"],
                timestamp=datetime.fromisoformat(data["on_chain_metrics"]["timestamp"])
            ),
            risk_factors=data["risk_factors"],
            opportunities=data["opportunities"],
            qwen_analysis=data["qwen_analysis"],
            confidence=data.get("confidence", 0.5)
        )

