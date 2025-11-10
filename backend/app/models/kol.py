"""
KOL追踪数据模型

用于追踪和分析KOL（意见领袖）的观点和预测
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, JSON, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class KOLSource(Base):
    """KOL数据源表"""
    __tablename__ = "kol_sources"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, comment="KOL名称")
    platform = Column(String(50), nullable=False, comment="平台类型：twitter/telegram")
    channel_id = Column(String(200), nullable=False, comment="频道ID或用户名")
    influence_score = Column(Float, default=0.0, comment="影响力评分（0-100）")
    accuracy_rate = Column(Float, default=0.0, comment="历史准确率")
    enabled = Column(Boolean, default=True, comment="是否启用")
    last_update = Column(DateTime(timezone=True), comment="最后更新时间")
    total_posts = Column(Integer, default=0, comment="总发帖数")
    successful_predictions = Column(Integer, default=0, comment="成功预测数")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    # 关系
    opinions = relationship("KOLOpinion", back_populates="kol", cascade="all, delete-orphan")


class KOLOpinion(Base):
    """KOL意见表"""
    __tablename__ = "kol_opinions"

    id = Column(Integer, primary_key=True, index=True)
    kol_id = Column(Integer, ForeignKey("kol_sources.id", ondelete="CASCADE"), nullable=False)
    platform = Column(String(50), nullable=False, comment="来源平台")
    content = Column(Text, nullable=False, comment="意见内容")
    sentiment = Column(String(20), comment="情绪：bullish/bearish/neutral")
    mentioned_coins = Column(JSON, comment="提及的币种（JSON数组）")
    confidence = Column(Float, comment="置信度")
    post_url = Column(String(500), comment="原文链接")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

    # 关系
    kol = relationship("KOLSource", back_populates="opinions")

