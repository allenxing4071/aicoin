"""权限等级配置的Pydantic模型"""

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PermissionLevelConfigBase(BaseModel):
    """权限等级配置基础模型"""
    level: str = Field(..., description="权限等级 (L0-L5)")
    name: str = Field(..., description="等级名称")
    description: Optional[str] = Field(None, description="等级描述")
    
    # 交易权限参数
    max_position_pct: float = Field(..., description="单仓位最大占比")
    max_leverage: int = Field(..., description="最大杠杆")
    confidence_threshold: float = Field(..., description="置信度门槛")
    max_daily_trades: int = Field(..., description="每日最大交易次数")
    
    # 升级条件
    upgrade_win_rate_7d: Optional[float] = Field(None, description="7日胜率要求")
    upgrade_win_rate_30d: Optional[float] = Field(None, description="30日胜率要求")
    upgrade_sharpe_ratio: Optional[float] = Field(None, description="夏普比率要求")
    upgrade_min_trades: Optional[int] = Field(None, description="最少交易次数")
    upgrade_min_days: Optional[int] = Field(None, description="最少运行天数")
    
    # 降级条件
    downgrade_max_drawdown: Optional[float] = Field(None, description="最大回撤触发降级")
    downgrade_consecutive_losses: Optional[int] = Field(None, description="连续亏损次数")
    downgrade_win_rate_7d: Optional[float] = Field(None, description="7日胜率低于此值降级")
    
    # 状态
    is_active: bool = Field(True, description="是否启用")
    is_default: bool = Field(False, description="是否为默认等级")

    # 关联 Prompt 模板
    decision_prompt_id: Optional[int] = Field(None, description="决策 Prompt 模板 ID")
    debate_prompt_id: Optional[int] = Field(None, description="辩论 Prompt 模板 ID")
    intelligence_prompt_id: Optional[int] = Field(None, description="情报 Prompt 模板 ID")


class PermissionLevelConfigCreate(PermissionLevelConfigBase):
    """创建权限等级配置"""
    pass


class PermissionLevelConfigUpdate(BaseModel):
    """更新权限等级配置 (所有字段可选)"""
    name: Optional[str] = None
    description: Optional[str] = None
    max_position_pct: Optional[float] = None
    max_leverage: Optional[int] = None
    confidence_threshold: Optional[float] = None
    max_daily_trades: Optional[int] = None
    upgrade_win_rate_7d: Optional[float] = None
    upgrade_win_rate_30d: Optional[float] = None
    upgrade_sharpe_ratio: Optional[float] = None
    upgrade_min_trades: Optional[int] = None
    upgrade_min_days: Optional[int] = None
    downgrade_max_drawdown: Optional[float] = None
    downgrade_consecutive_losses: Optional[int] = None
    downgrade_win_rate_7d: Optional[float] = None
    is_active: Optional[bool] = None
    is_default: Optional[bool] = None
    decision_prompt_id: Optional[int] = None
    debate_prompt_id: Optional[int] = None
    intelligence_prompt_id: Optional[int] = None


class PermissionLevelConfigResponse(PermissionLevelConfigBase):
    """权限等级配置响应"""
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class PermissionLevelConfigListResponse(BaseModel):
    """权限等级配置列表响应"""
    items: list[PermissionLevelConfigResponse]
    total: int

