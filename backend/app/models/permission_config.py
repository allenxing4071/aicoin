"""权限等级配置模型 - 后台可管理"""

from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, Text
from sqlalchemy.sql import func
from app.core.database import Base


class PermissionLevelConfig(Base):
    """权限等级配置表"""
    __tablename__ = "permission_level_configs"
    __table_args__ = {
        'comment': '⚙️ 权限等级配置 - 定义L0-L5各等级的交易限制、升降级条件和风控参数'
    }
    
    id = Column(Integer, primary_key=True, index=True)
    
    # 等级基本信息
    level = Column(String(10), unique=True, nullable=False, index=True)  # L0-L5
    name = Column(String(50), nullable=False)  # 保护模式、新手级等
    description = Column(Text, nullable=True)  # 等级描述
    
    # 交易权限参数
    max_position_pct = Column(Float, nullable=False, default=0.10)  # 单仓位最大占比
    max_leverage = Column(Integer, nullable=False, default=2)  # 最大杠杆
    confidence_threshold = Column(Float, nullable=False, default=0.70)  # 置信度门槛
    max_daily_trades = Column(Integer, nullable=False, default=5)  # 每日最大交易次数
    
    # 升级条件
    upgrade_win_rate_7d = Column(Float, nullable=True)  # 7日胜率要求
    upgrade_win_rate_30d = Column(Float, nullable=True)  # 30日胜率要求
    upgrade_sharpe_ratio = Column(Float, nullable=True)  # 夏普比率要求
    upgrade_min_trades = Column(Integer, nullable=True)  # 最少交易次数
    upgrade_min_days = Column(Integer, nullable=True)  # 最少运行天数
    
    # 降级条件
    downgrade_max_drawdown = Column(Float, nullable=True)  # 最大回撤触发降级
    downgrade_consecutive_losses = Column(Integer, nullable=True)  # 连续亏损次数
    downgrade_win_rate_7d = Column(Float, nullable=True)  # 7日胜率低于此值降级
    
    # 状态
    is_active = Column(Boolean, default=True, nullable=False)  # 是否启用
    is_default = Column(Boolean, default=False, nullable=False)  # 是否为默认等级
    
    # 关联 Prompt 模板
    decision_prompt_id = Column(Integer, nullable=True, comment="决策 Prompt 模板 ID")
    debate_prompt_id = Column(Integer, nullable=True, comment="辩论 Prompt 模板 ID")
    intelligence_prompt_id = Column(Integer, nullable=True, comment="情报 Prompt 模板 ID")
    
    # 时间戳
    created_at = Column(DateTime, server_default=func.now(), nullable=False)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now(), nullable=False)
    
    def to_dict(self):
        """转换为字典"""
        return {
            "id": self.id,
            "level": self.level,
            "name": self.name,
            "description": self.description,
            "trading_params": {
                "max_position_pct": self.max_position_pct,
                "max_leverage": self.max_leverage,
                "confidence_threshold": self.confidence_threshold,
                "max_daily_trades": self.max_daily_trades
            },
            "upgrade_conditions": {
                "win_rate_7d": self.upgrade_win_rate_7d,
                "win_rate_30d": self.upgrade_win_rate_30d,
                "sharpe_ratio": self.upgrade_sharpe_ratio,
                "min_trades": self.upgrade_min_trades,
                "min_days": self.upgrade_min_days
            },
            "downgrade_conditions": {
                "max_drawdown": self.downgrade_max_drawdown,
                "consecutive_losses": self.downgrade_consecutive_losses,
                "win_rate_7d": self.downgrade_win_rate_7d
            },
            "prompts": {
                "decision_prompt_id": self.decision_prompt_id,
                "debate_prompt_id": self.debate_prompt_id,
                "intelligence_prompt_id": self.intelligence_prompt_id
            },
            "is_active": self.is_active,
            "is_default": self.is_default,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }

