"""Model Performance Metrics - 模型性能指标"""

from sqlalchemy import Column, Integer, String, Float, Date, DateTime, Boolean, Text, ARRAY
from sqlalchemy.dialects.postgresql import JSONB
from datetime import datetime, date
from app.core.database import Base


class ModelPerformanceMetric(Base):
    """模型性能指标模型"""
    __tablename__ = "model_performance_metrics"
    __table_args__ = {
        'comment': '模型性能指标 - 记录各AI模型的决策准确率、盈利率、响应时间等性能数据'
    }
    
    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String, nullable=False, index=True)  # trained_70b/default_api
    metric_date = Column(Date, nullable=False, index=True)  # 指标日期
    
    # 决策准确率指标
    total_decisions = Column(Integer, nullable=False, default=0)
    correct_decisions = Column(Integer, nullable=False, default=0)
    accuracy = Column(Float, nullable=True)  # 决策准确率
    
    # 交易盈利指标
    total_trades = Column(Integer, nullable=False, default=0)
    profitable_trades = Column(Integer, nullable=False, default=0)
    profit_rate = Column(Float, nullable=True)  # 盈利率
    total_pnl = Column(Float, nullable=False, default=0.0)  # 总盈亏
    avg_pnl_per_trade = Column(Float, nullable=True)  # 平均每笔盈亏
    
    # 性能指标
    avg_response_time = Column(Float, nullable=True)  # 平均响应时间（秒）
    avg_cost = Column(Float, nullable=True)  # 平均成本
    
    # 风险指标
    max_loss = Column(Float, nullable=True)  # 最大单次亏损
    win_loss_ratio = Column(Float, nullable=True)  # 盈亏比
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "model_name": self.model_name,
            "metric_date": self.metric_date.isoformat(),
            "accuracy_metrics": {
                "total_decisions": self.total_decisions,
                "correct_decisions": self.correct_decisions,
                "accuracy": self.accuracy
            },
            "profitability_metrics": {
                "total_trades": self.total_trades,
                "profitable_trades": self.profitable_trades,
                "profit_rate": self.profit_rate,
                "total_pnl": self.total_pnl,
                "avg_pnl_per_trade": self.avg_pnl_per_trade
            },
            "performance_metrics": {
                "avg_response_time": self.avg_response_time,
                "avg_cost": self.avg_cost
            },
            "risk_metrics": {
                "max_loss": self.max_loss,
                "win_loss_ratio": self.win_loss_ratio
            },
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }


class RoutingDecision(Base):
    """路由决策日志模型"""
    __tablename__ = "routing_decisions"
    __table_args__ = {
        'comment': '路由决策日志 - 记录AI模型路由策略选择过程和多模型协作决策的详细信息'
    }
    
    id = Column(Integer, primary_key=True, index=True)
    decision_id = Column(String, nullable=False, unique=True)  # 关联决策ID
    routing_strategy = Column(String, nullable=False, index=True)  # 路由策略
    model_used = Column(String, nullable=False, index=True)  # 实际使用的模型
    models_called = Column(ARRAY(String), nullable=True)  # 调用的所有模型
    
    # 决策信息
    decision = Column(String, nullable=True)  # BUY/SELL/HOLD
    confidence = Column(Float, nullable=True)  # 置信度
    reasoning = Column(Text, nullable=True)  # 推理过程
    
    # 路由信息
    why_this_strategy = Column(Text, nullable=True)  # 为什么选择这个策略
    fallback_triggered = Column(Boolean, nullable=False, default=False)  # 是否触发降级
    routing_metadata = Column(JSONB, nullable=True)  # 其他路由元数据
    
    # 性能数据
    response_time = Column(Float, nullable=True)  # 响应时间（秒）
    cost = Column(Float, nullable=True)  # 成本
    
    # 结果跟踪（后续更新）
    actual_result = Column(String, nullable=True)  # 实际交易结果
    pnl = Column(Float, nullable=True)  # 盈亏
    was_correct = Column(Boolean, nullable=True)  # 决策是否正确
    
    # 时间戳
    created_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "decision_id": self.decision_id,
            "routing_strategy": self.routing_strategy,
            "model_used": self.model_used,
            "models_called": self.models_called,
            "decision_info": {
                "decision": self.decision,
                "confidence": self.confidence,
                "reasoning": self.reasoning
            },
            "routing_info": {
                "why_this_strategy": self.why_this_strategy,
                "fallback_triggered": self.fallback_triggered,
                "metadata": self.routing_metadata
            },
            "performance": {
                "response_time": self.response_time,
                "cost": self.cost
            },
            "result": {
                "actual_result": self.actual_result,
                "pnl": self.pnl,
                "was_correct": self.was_correct
            },
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }

