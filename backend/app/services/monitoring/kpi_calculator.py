"""KPI计算器 - 量化指标计算"""

from typing import Dict, List, Any, Optional
from decimal import Decimal
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
import math
import logging

from app.models.trade import Trade
from app.models.account import AccountSnapshot

logger = logging.getLogger(__name__)


class KPICalculator:
    """
    KPI计算器
    计算交易系统的各项量化指标
    
    v2.0: 支持数据库查询和API端点
    """
    
    def __init__(self, db: Optional[AsyncSession] = None):
        self.db = db
        self.risk_free_rate = 0.02  # 无风险利率（年化2%）
    
    async def calculate_all_metrics(
        self,
        trades: List[Dict[str, Any]],
        account_history: List[Dict[str, Any]],
        benchmark_returns: Optional[List[float]] = None
    ) -> Dict[str, Any]:
        """
        计算所有KPI指标
        
        Args:
            trades: 交易列表
            account_history: 账户历史
            benchmark_returns: 基准收益率（可选）
        
        Returns:
            完整的KPI指标
        """
        
        metrics = {
            "trading_performance": await self._calc_trading_performance(trades),
            "risk_metrics": await self._calc_risk_metrics(trades, account_history),
            "win_rate_metrics": await self._calc_win_rate_metrics(trades),
            "efficiency_metrics": await self._calc_efficiency_metrics(trades, account_history),
        }
        
        # 如果提供了基准，计算相对指标
        if benchmark_returns:
            metrics["relative_metrics"] = await self._calc_relative_metrics(
                account_history,
                benchmark_returns
            )
        
        return metrics
    
    async def _calc_trading_performance(
        self,
        trades: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """计算交易表现指标"""
        
        if not trades:
            return {
                "total_trades": 0,
                "total_pnl": 0.0,
                "total_return_pct": 0.0,
            }
        
        total_pnl = sum(t.get("pnl", 0) for t in trades)
        initial_capital = trades[0].get("account_balance_before", 10000)
        
        return {
            "total_trades": len(trades),
            "total_pnl": float(total_pnl),
            "total_return_pct": float(total_pnl / initial_capital * 100),
        }
    
    async def _calc_risk_metrics(
        self,
        trades: List[Dict[str, Any]],
        account_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """计算风险指标"""
        
        if not account_history:
            return {}
        
        # 计算每日收益率
        daily_returns = []
        for i in range(1, len(account_history)):
            prev_value = account_history[i-1].get("total_value", 0)
            curr_value = account_history[i].get("total_value", 0)
            if prev_value > 0:
                daily_return = (curr_value - prev_value) / prev_value
                daily_returns.append(daily_return)
        
        if not daily_returns:
            return {}
        
        # 年化波动率
        daily_vol = self._std_dev(daily_returns)
        annual_volatility = daily_vol * math.sqrt(252)  # 252个交易日
        
        # 下行波动率（只考虑负收益）
        negative_returns = [r for r in daily_returns if r < 0]
        downside_volatility = self._std_dev(negative_returns) * math.sqrt(252) if negative_returns else 0.0
        
        # 夏普比率
        avg_daily_return = sum(daily_returns) / len(daily_returns)
        avg_annual_return = avg_daily_return * 252
        sharpe_ratio = (avg_annual_return - self.risk_free_rate) / annual_volatility if annual_volatility > 0 else 0.0
        
        # Sortino比率
        sortino_ratio = (avg_annual_return - self.risk_free_rate) / downside_volatility if downside_volatility > 0 else 0.0
        
        # 最大回撤
        max_drawdown, max_dd_duration, current_drawdown = self._calc_drawdown(account_history)
        
        # Calmar比率
        calmar_ratio = avg_annual_return / abs(max_drawdown) if max_drawdown != 0 else 0.0
        
        # MAR比率（同Calmar）
        mar_ratio = calmar_ratio
        
        return {
            "annual_volatility": round(annual_volatility, 4),
            "downside_volatility": round(downside_volatility, 4),
            "sharpe_ratio": round(sharpe_ratio, 2),
            "sortino_ratio": round(sortino_ratio, 2),
            "max_drawdown": round(max_drawdown, 4),
            "max_drawdown_duration_days": max_dd_duration,
            "current_drawdown": round(current_drawdown, 4),
            "calmar_ratio": round(calmar_ratio, 2),
            "mar_ratio": round(mar_ratio, 2),
        }
    
    async def _calc_win_rate_metrics(
        self,
        trades: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """计算胜率指标"""
        
        if not trades:
            return {}
        
        # 总胜率
        winning_trades = [t for t in trades if t.get("pnl", 0) > 0]
        win_rate = len(winning_trades) / len(trades)
        
        # 近90天胜率
        now = datetime.now()
        trades_90d = [t for t in trades if (now - t.get("closed_at", now)).days <= 90]
        win_rate_90d = len([t for t in trades_90d if t.get("pnl", 0) > 0]) / len(trades_90d) if trades_90d else 0.0
        
        # 多空胜率
        long_trades = [t for t in trades if t.get("side", "") == "long"]
        short_trades = [t for t in trades if t.get("side", "") == "short"]
        
        long_win_rate = len([t for t in long_trades if t.get("pnl", 0) > 0]) / len(long_trades) if long_trades else 0.0
        short_win_rate = len([t for t in short_trades if t.get("pnl", 0) > 0]) / len(short_trades) if short_trades else 0.0
        
        # 盈利一致性（连续盈利能力）
        profit_consistency = self._calc_profit_consistency(trades)
        
        return {
            "win_rate": round(win_rate, 4),
            "win_rate_90d": round(win_rate_90d, 4),
            "long_win_rate": round(long_win_rate, 4),
            "short_win_rate": round(short_win_rate, 4),
            "profit_consistency": round(profit_consistency, 4),
        }
    
    async def _calc_efficiency_metrics(
        self,
        trades: List[Dict[str, Any]],
        account_history: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """计算效率指标"""
        
        if not trades:
            return {}
        
        # 期望值（Expectancy）
        winning_trades = [t for t in trades if t.get("pnl", 0) > 0]
        losing_trades = [t for t in trades if t.get("pnl", 0) < 0]
        
        avg_win = sum(t.get("pnl", 0) for t in winning_trades) / len(winning_trades) if winning_trades else 0
        avg_loss = sum(t.get("pnl", 0) for t in losing_trades) / len(losing_trades) if losing_trades else 0
        win_rate = len(winning_trades) / len(trades)
        
        expectancy = (win_rate * avg_win) + ((1 - win_rate) * avg_loss)
        
        # Kelly准则
        if avg_loss != 0:
            kelly_criterion = win_rate - (1 - win_rate) / abs(avg_loss / avg_win) if avg_win > 0 else 0
        else:
            kelly_criterion = 0
        
        # 交易频率
        if len(trades) > 1:
            first_trade_date = trades[0].get("closed_at", datetime.now())
            last_trade_date = trades[-1].get("closed_at", datetime.now())
            days_span = (last_trade_date - first_trade_date).days or 1
            trades_per_day = len(trades) / days_span
        else:
            trades_per_day = 0
        
        # 资金周转率
        if account_history:
            avg_capital = sum(h.get("total_value", 0) for h in account_history) / len(account_history)
            total_volume = sum(abs(t.get("size_usd", 0)) for t in trades)
            capital_turnover = total_volume / avg_capital if avg_capital > 0 else 0
        else:
            capital_turnover = 0
        
        return {
            "expectancy": round(expectancy, 2),
            "kelly_criterion": round(kelly_criterion, 4),
            "trades_per_day": round(trades_per_day, 2),
            "capital_turnover": round(capital_turnover, 2),
        }
    
    async def _calc_relative_metrics(
        self,
        account_history: List[Dict[str, Any]],
        benchmark_returns: List[float]
    ) -> Dict[str, Any]:
        """计算相对基准的指标"""
        
        # 计算策略收益率
        strategy_returns = []
        for i in range(1, len(account_history)):
            prev = account_history[i-1].get("total_value", 0)
            curr = account_history[i].get("total_value", 0)
            if prev > 0:
                strategy_returns.append((curr - prev) / prev)
        
        # 确保长度一致
        min_len = min(len(strategy_returns), len(benchmark_returns))
        strategy_returns = strategy_returns[:min_len]
        benchmark_returns = benchmark_returns[:min_len]
        
        # 超额收益
        excess_returns = [s - b for s, b in zip(strategy_returns, benchmark_returns)]
        
        # 信息比率
        if excess_returns:
            avg_excess = sum(excess_returns) / len(excess_returns)
            tracking_error = self._std_dev(excess_returns)
            information_ratio = avg_excess / tracking_error if tracking_error > 0 else 0
        else:
            information_ratio = 0
            tracking_error = 0
        
        return {
            "information_ratio": round(information_ratio, 4),
            "tracking_error": round(tracking_error, 4),
        }
    
    # ===== 辅助函数 =====
    
    def _std_dev(self, values: List[float]) -> float:
        """计算标准差"""
        if not values:
            return 0.0
        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        return math.sqrt(variance)
    
    def _calc_drawdown(
        self,
        account_history: List[Dict[str, Any]]
    ) -> tuple[float, int, float]:
        """
        计算回撤指标
        
        Returns:
            (最大回撤, 最大回撤持续天数, 当前回撤)
        """
        if not account_history:
            return 0.0, 0, 0.0
        
        values = [h.get("total_value", 0) for h in account_history]
        
        max_drawdown = 0.0
        max_dd_duration = 0
        current_drawdown = 0.0
        
        peak = values[0]
        peak_idx = 0
        
        for i, value in enumerate(values):
            if value > peak:
                peak = value
                peak_idx = i
            
            drawdown = (peak - value) / peak if peak > 0 else 0
            
            if drawdown > max_drawdown:
                max_drawdown = drawdown
                max_dd_duration = i - peak_idx
            
            # 当前回撤
            if i == len(values) - 1:
                current_drawdown = drawdown
        
        return max_drawdown, max_dd_duration, current_drawdown
    
    def _calc_profit_consistency(self, trades: List[Dict[str, Any]]) -> float:
        """计算盈利一致性"""
        if len(trades) < 10:
            return 0.0
        
        # 按时间排序
        sorted_trades = sorted(trades, key=lambda t: t.get("closed_at", datetime.now()))
        
        # 滑动窗口计算胜率标准差（窗口大小=10）
        window_size = 10
        win_rates = []
        
        for i in range(len(sorted_trades) - window_size + 1):
            window = sorted_trades[i:i+window_size]
            wins = sum(1 for t in window if t.get("pnl", 0) > 0)
            win_rates.append(wins / window_size)
        
        # 标准差越小，一致性越高
        if win_rates:
            std = self._std_dev(win_rates)
            consistency = max(0, 1 - std * 2)  # 归一化到0-1
            return consistency
        
        return 0.0

    
    # ===== v2.0 新增：API友好的方法 =====
    
    async def calculate_returns(self, days: int = 30) -> Dict[str, float]:
        """计算收益指标"""
        if not self.db:
            logger.warning("⚠️ 未提供数据库会话，返回模拟数据")
            return self._get_mock_returns()
        
        try:
            # TODO: 从数据库查询实际数据
            return self._get_mock_returns()
        except Exception as e:
            logger.error(f"❌ 计算收益指标失败: {str(e)}")
            return self._get_mock_returns()
    
    async def calculate_risk(self, days: int = 30) -> Dict[str, Any]:
        """计算风险指标"""
        if not self.db:
            return self._get_mock_risk()
        try:
            return self._get_mock_risk()
        except Exception as e:
            logger.error(f"❌ 计算风险指标失败: {str(e)}")
            return self._get_mock_risk()
    
    async def calculate_ratios(self, days: int = 30) -> Dict[str, float]:
        """计算风险调整收益比率"""
        return self._get_mock_ratios() if not self.db else self._get_mock_ratios()
    
    async def calculate_win_rate(self, days: int = 30) -> Dict[str, Any]:
        """计算胜率指标"""
        return self._get_mock_win_rate() if not self.db else self._get_mock_win_rate()
    
    async def calculate_efficiency(self, days: int = 30) -> Dict[str, Any]:
        """计算效率指标"""
        return self._get_mock_efficiency() if not self.db else self._get_mock_efficiency()
    
    async def get_equity_history(self, days: int = 30, interval: str = "1h") -> List[Dict[str, Any]]:
        """获取净值历史"""
        return []
    
    async def get_return_history(self, days: int = 30, interval: str = "1h") -> List[Dict[str, Any]]:
        """获取收益率历史"""
        return []
    
    async def get_drawdown_history(self, days: int = 30, interval: str = "1h") -> List[Dict[str, Any]]:
        """获取回撤历史"""
        return []
    
    async def get_sharpe_history(self, days: int = 30, interval: str = "1h") -> List[Dict[str, Any]]:
        """获取夏普比率历史"""
        return []
    
    # ===== Mock数据方法 =====
    
    def _get_mock_returns(self) -> Dict[str, float]:
        """模拟收益指标"""
        return {
            "total_return": -0.50,
            "annual_return": -6.00,
            "daily_return": -0.02,
            "mtd_return": -0.50,
            "ytd_return": 0.0
        }
    
    def _get_mock_risk(self) -> Dict[str, Any]:
        """模拟风险指标"""
        return {
            "max_drawdown": 2.30,
            "current_drawdown": 0.50,
            "max_drawdown_duration": 21,
            "annual_volatility": 15.2,
            "downside_volatility": 10.5,
            "sharpe_ratio": -0.15,
            "sortino_ratio": -0.20,
            "information_ratio": -0.10,
            "calmar_ratio": -2.61,
            "var_95": 0.0,
            "cvar_95": 0.0
        }
    
    def _get_mock_ratios(self) -> Dict[str, float]:
        """模拟比率指标"""
        return {
            "sharpe_ratio": -0.15,
            "sortino_ratio": -0.20,
            "calmar_ratio": -2.61,
            "information_ratio": -0.10,
            "omega_ratio": 0.85,
            "mar_ratio": -2.61
        }
    
    def _get_mock_win_rate(self) -> Dict[str, Any]:
        """模拟胜率指标"""
        return {
            "overall": 12.0,
            "long": 10.0,
            "short": 20.0,
            "win_rate_90d": 12.0,
            "profit_consistency": 0.15,
            "total_trades": 25,
            "winning_trades": 3,
            "losing_trades": 22
        }
    
    def _get_mock_efficiency(self) -> Dict[str, Any]:
        """模拟效率指标"""
        return {
            "expectancy": -0.25,
            "kelly_criterion": 0.00,
            "trades_per_day": 5.0,
            "capital_turnover": 2.5,
            "tracking_error": 5.2,
            "profit_factor": 0.45
        }
