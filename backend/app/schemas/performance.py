"""Performance metrics schemas"""

from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal


# ===== 原有的PerformanceMetrics（保持兼容） =====
class PerformanceMetrics(BaseModel):
    """性能指标（原版，保持兼容）"""
    total_return: Decimal  # 总收益率
    sharpe_ratio: Optional[Decimal] = None  # 夏普比率
    max_drawdown: Optional[Decimal] = None  # 最大回撤
    win_rate: Optional[Decimal] = None  # 胜率
    profit_factor: Optional[Decimal] = None  # 盈亏比
    total_trades: int  # 总交易次数
    winning_trades: int = 0
    losing_trades: int = 0
    avg_win: Optional[Decimal] = None
    avg_loss: Optional[Decimal] = None
    current_streak: int = 0  # 当前连续盈亏次数 (正数盈利，负数亏损)


# ===== v2.0 新增：详细的性能指标schemas =====

class ReturnsMetrics(BaseModel):
    """收益指标"""
    total_return: float = Field(..., description="总收益率 (%)")
    annual_return: float = Field(..., description="年化收益率 (%)")
    daily_return: float = Field(..., description="日收益率 (%)")
    mtd_return: float = Field(..., description="月度收益率 (%)")
    ytd_return: float = Field(0.0, description="年度收益率 (%)")


class RiskMetrics(BaseModel):
    """风险指标"""
    max_drawdown: float = Field(..., description="最大回撤 (%)")
    current_drawdown: float = Field(..., description="当前回撤 (%)")
    max_drawdown_duration: int = Field(..., description="最大回撤持续时间 (小时)")
    annual_volatility: float = Field(..., description="年化波动率 (%)")
    downside_volatility: float = Field(..., description="下行波动率 (%)")
    var_95: float = Field(0.0, description="95% VaR (风险价值)")
    cvar_95: float = Field(0.0, description="95% CVaR (条件风险价值)")


class RatiosMetrics(BaseModel):
    """风险调整收益比率"""
    sharpe_ratio: float = Field(..., description="夏普比率")
    sortino_ratio: float = Field(..., description="索提诺比率")
    calmar_ratio: float = Field(..., description="卡玛比率")
    information_ratio: float = Field(..., description="信息比率")
    omega_ratio: float = Field(0.0, description="欧米茄比率")
    mar_ratio: float = Field(0.0, description="MAR比率")


class WinRateMetrics(BaseModel):
    """胜率指标"""
    overall: float = Field(..., description="总胜率 (%)")
    long: float = Field(0.0, description="多头胜率 (%)")
    short: float = Field(0.0, description="空头胜率 (%)")
    win_rate_90d: float = Field(..., description="90日胜率 (%)")
    profit_consistency: float = Field(..., description="盈利稳定性 (0-1)")
    total_trades: int = Field(..., description="总交易数")
    winning_trades: int = Field(..., description="盈利交易数")
    losing_trades: int = Field(..., description="亏损交易数")


class EfficiencyMetrics(BaseModel):
    """效率指标"""
    expectancy: float = Field(..., description="期望收益 ($)")
    kelly_criterion: float = Field(..., description="凯利公式 (%)")
    trades_per_day: float = Field(..., description="日均交易次数")
    capital_turnover: float = Field(..., description="资金周转率")
    tracking_error: float = Field(0.0, description="跟踪误差 (%)")
    profit_factor: float = Field(0.0, description="盈亏比")


class PerformanceMetricsResponse(BaseModel):
    """性能指标完整响应"""
    returns: ReturnsMetrics = Field(..., description="收益指标")
    risk: RiskMetrics = Field(..., description="风险指标")
    ratios: RatiosMetrics = Field(..., description="风险调整收益比率")
    win_rate: WinRateMetrics = Field(..., description="胜率指标")
    efficiency: EfficiencyMetrics = Field(..., description="效率指标")
    period_days: int = Field(..., description="统计周期（天）")

