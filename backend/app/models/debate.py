"""Debate system database models"""

from sqlalchemy import Column, Integer, String, Text, Float, DateTime, Boolean, Index
from sqlalchemy.sql import func
from app.core.database import Base


class DebateHistory(Base):
    """辩论历史记录表"""
    
    __tablename__ = "debate_history"
    
    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(String(100), unique=True, nullable=False, index=True, comment="关联的决策ID")
    symbol = Column(String(20), nullable=False, index=True, comment="交易标的")
    debate_rounds = Column(Integer, default=1, comment="辩论轮次")
    
    # 辩论内容
    bull_arguments = Column(Text, comment="多头论点（完整历史）")
    bear_arguments = Column(Text, comment="空头论点（完整历史）")
    debate_full_history = Column(Text, comment="完整辩论历史")
    
    # 最终决策
    final_recommendation = Column(String(20), comment="最终推荐（BUY/SELL/HOLD）")
    confidence = Column(Float, comment="置信度（0-1）")
    consensus_level = Column(Float, comment="共识度（0-1）")
    
    # 元数据
    debate_duration_seconds = Column(Integer, comment="辩论耗时（秒）")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    # 添加索引
    __table_args__ = (
        Index('idx_debate_symbol_created', 'symbol', 'created_at'),
        Index('idx_debate_recommendation', 'final_recommendation'),
        {'comment': '辩论历史记录表'}
    )


class DebateConfig(Base):
    """辩论配置表"""
    
    __tablename__ = "debate_config"
    
    id = Column(Integer, primary_key=True, index=True)
    config_key = Column(String(100), unique=True, nullable=False, index=True, comment="配置键")
    config_value = Column(Text, comment="配置值")
    description = Column(Text, comment="配置说明")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
    
    __table_args__ = (
        {'comment': '辩论配置表'}
    )


class DebateStatistics(Base):
    """辩论统计表（按日统计）"""
    
    __tablename__ = "debate_statistics"
    
    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), unique=True, nullable=False, index=True, comment="统计日期")
    
    # 基础统计
    total_debates = Column(Integer, default=0, comment="总辩论次数")
    bull_wins = Column(Integer, default=0, comment="多头胜利次数")
    bear_wins = Column(Integer, default=0, comment="空头胜利次数")
    holds = Column(Integer, default=0, comment="持有次数")
    
    # 平均指标
    avg_consensus = Column(Float, comment="平均共识度")
    avg_confidence = Column(Float, comment="平均置信度")
    avg_duration = Column(Float, comment="平均辩论时长（秒）")
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    
    __table_args__ = (
        {'comment': '辩论统计表'}
    )

