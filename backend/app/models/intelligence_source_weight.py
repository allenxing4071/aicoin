"""Intelligence Source Weight Model - 情报源权重模型"""

from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.sql import func
from app.core.database import Base


class IntelligenceSourceWeight(Base):
    """
    情报源权重表
    
    用于存储和管理各个情报源的权重信息
    """
    __tablename__ = "intelligence_source_weights"
    __table_args__ = {
        'comment': '⚖️ 情报源权重 - 记录各情报源（RSS、API等）的权重和有效性评分，用于智能筛选'
    }
    
    id = Column(Integer, primary_key=True, index=True)
    source_name = Column(String(100), nullable=False, unique=True, index=True)
    source_type = Column(String(50), nullable=False, index=True)  # news/whale/onchain/search/platform
    category = Column(String(50))  # 可选分类
    
    # 权重信息
    base_weight = Column(Float, default=0.5)  # 基础权重
    dynamic_weight = Column(Float, default=0.5)  # 动态权重
    
    # 使用统计
    usage_count = Column(Integer, default=0)
    positive_feedback_count = Column(Integer, default=0)
    effectiveness_score = Column(Float, default=0.5)  # 有效性评分
    
    # 时间戳
    last_used_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<IntelligenceSourceWeight(name={self.source_name}, weight={self.dynamic_weight:.3f})>"


class IntelligenceFeedback(Base):
    """
    情报使用反馈表
    
    记录情报的使用反馈和效果评估
    """
    __tablename__ = "intelligence_feedback"
    __table_args__ = {
        'comment': '💬 情报反馈 - 记录用户对情报的反馈和使用效果，用于优化情报质量'
    }
    
    id = Column(Integer, primary_key=True, index=True)
    report_id = Column(String(100), nullable=False, index=True)
    source_name = Column(String(100), nullable=False, index=True)
    
    # 交互信息
    user_interaction = Column(String(50))  # view/click/bookmark/share等
    effectiveness_rating = Column(Float)  # 0.0-1.0
    
    # 决策影响
    decision_influenced = Column(Boolean, default=False)
    decision_outcome = Column(String(50))  # success/failure/pending
    
    # 反馈类型
    feedback_type = Column(String(50))  # positive/negative/neutral
    
    # 时间戳
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    def __repr__(self):
        return f"<IntelligenceFeedback(report_id={self.report_id}, source={self.source_name})>"

