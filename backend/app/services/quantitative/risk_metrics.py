"""
Prompt风险指标计算服务
专业量化师级别的风险评估工具
"""

import logging
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal

logger = logging.getLogger(__name__)


class PromptRiskMetrics:
    """
    Prompt风险指标计算器
    
    实现专业量化基金使用的风险指标：
    1. Sharpe Ratio（夏普比率）
    2. Sortino Ratio（索提诺比率）
    3. Max Drawdown（最大回撤）
    4. Calmar Ratio（卡玛比率）
    5. VaR（风险价值）
    6. CVaR（条件风险价值）
    """
    
    def __init__(self, risk_free_rate: float = 0.02):
        """
        初始化风险指标计算器
        
        Args:
            risk_free_rate: 无风险利率（年化，默认2%）
        """
        self.risk_free_rate = risk_free_rate
    
    def calculate_sharpe_ratio(
        self,
        returns: List[float],
        periods_per_year: int = 365
    ) -> Optional[float]:
        """
        计算夏普比率
        
        公式：Sharpe = (年化收益率 - 无风险利率) / 年化波动率
        
        Args:
            returns: 收益率序列（如：[0.02, -0.01, 0.03, ...]）
            periods_per_year: 每年的周期数（日频=365，小时频=8760）
        
        Returns:
            夏普比率（>1.0为优秀，>2.0为卓越）
        """
        if not returns or len(returns) < 2:
            return None
        
        try:
            returns_array = np.array(returns)
            
            # 计算年化收益率
            mean_return = np.mean(returns_array)
            annualized_return = mean_return * periods_per_year
            
            # 计算年化波动率
            std_return = np.std(returns_array, ddof=1)  # 样本标准差
            annualized_volatility = std_return * np.sqrt(periods_per_year)
            
            if annualized_volatility == 0:
                return None
            
            # 计算夏普比率
            sharpe = (annualized_return - self.risk_free_rate) / annualized_volatility
            
            logger.info(f"夏普比率: {sharpe:.2f} (收益率: {annualized_return:.2%}, 波动率: {annualized_volatility:.2%})")
            
            return float(sharpe)
        
        except Exception as e:
            logger.error(f"计算夏普比率失败: {e}")
            return None
    
    def calculate_sortino_ratio(
        self,
        returns: List[float],
        periods_per_year: int = 365,
        target_return: float = 0.0
    ) -> Optional[float]:
        """
        计算索提诺比率（只惩罚下行波动）
        
        公式：Sortino = (年化收益率 - 目标收益率) / 下行波动率
        
        Args:
            returns: 收益率序列
            periods_per_year: 每年的周期数
            target_return: 目标收益率（默认0）
        
        Returns:
            索提诺比率（>1.5为优秀）
        """
        if not returns or len(returns) < 2:
            return None
        
        try:
            returns_array = np.array(returns)
            
            # 计算年化收益率
            mean_return = np.mean(returns_array)
            annualized_return = mean_return * periods_per_year
            
            # 计算下行偏差（只考虑负收益）
            downside_returns = returns_array[returns_array < target_return]
            if len(downside_returns) == 0:
                return None
            
            downside_deviation = np.std(downside_returns, ddof=1)
            annualized_downside_deviation = downside_deviation * np.sqrt(periods_per_year)
            
            if annualized_downside_deviation == 0:
                return None
            
            # 计算索提诺比率
            sortino = (annualized_return - target_return) / annualized_downside_deviation
            
            logger.info(f"索提诺比率: {sortino:.2f} (下行波动率: {annualized_downside_deviation:.2%})")
            
            return float(sortino)
        
        except Exception as e:
            logger.error(f"计算索提诺比率失败: {e}")
            return None
    
    def calculate_max_drawdown(self, equity_curve: List[float]) -> Optional[float]:
        """
        计算最大回撤
        
        公式：MaxDD = (谷底 - 峰值) / 峰值
        
        Args:
            equity_curve: 权益曲线（如：[10000, 10200, 9800, 10500, ...]）
        
        Returns:
            最大回撤（0-1之间，如0.15表示15%回撤）
        """
        if not equity_curve or len(equity_curve) < 2:
            return None
        
        try:
            equity_array = np.array(equity_curve)
            
            # 计算累计最大值
            running_max = np.maximum.accumulate(equity_array)
            
            # 计算回撤
            drawdown = (equity_array - running_max) / running_max
            
            # 最大回撤
            max_dd = abs(np.min(drawdown))
            
            logger.info(f"最大回撤: {max_dd:.2%}")
            
            return float(max_dd)
        
        except Exception as e:
            logger.error(f"计算最大回撤失败: {e}")
            return None
    
    def calculate_calmar_ratio(
        self,
        returns: List[float],
        equity_curve: List[float],
        periods_per_year: int = 365
    ) -> Optional[float]:
        """
        计算卡玛比率
        
        公式：Calmar = 年化收益率 / 最大回撤
        
        Args:
            returns: 收益率序列
            equity_curve: 权益曲线
            periods_per_year: 每年的周期数
        
        Returns:
            卡玛比率（>3.0为优秀）
        """
        if not returns or not equity_curve:
            return None
        
        try:
            # 计算年化收益率
            returns_array = np.array(returns)
            mean_return = np.mean(returns_array)
            annualized_return = mean_return * periods_per_year
            
            # 计算最大回撤
            max_dd = self.calculate_max_drawdown(equity_curve)
            
            if max_dd is None or max_dd == 0:
                return None
            
            # 计算卡玛比率
            calmar = annualized_return / max_dd
            
            logger.info(f"卡玛比率: {calmar:.2f} (年化收益: {annualized_return:.2%}, 最大回撤: {max_dd:.2%})")
            
            return float(calmar)
        
        except Exception as e:
            logger.error(f"计算卡玛比率失败: {e}")
            return None
    
    def calculate_var(
        self,
        returns: List[float],
        confidence_level: float = 0.95
    ) -> Optional[float]:
        """
        计算风险价值（VaR）
        
        VaR表示：在给定置信度下，最大可能损失
        
        Args:
            returns: 收益率序列
            confidence_level: 置信度（默认95%）
        
        Returns:
            VaR值（如-0.05表示5%的损失）
        """
        if not returns or len(returns) < 10:
            return None
        
        try:
            returns_array = np.array(returns)
            
            # 计算VaR（使用历史模拟法）
            var = np.percentile(returns_array, (1 - confidence_level) * 100)
            
            logger.info(f"VaR({confidence_level:.0%}): {var:.2%}")
            
            return float(var)
        
        except Exception as e:
            logger.error(f"计算VaR失败: {e}")
            return None
    
    def calculate_cvar(
        self,
        returns: List[float],
        confidence_level: float = 0.95
    ) -> Optional[float]:
        """
        计算条件风险价值（CVaR / Expected Shortfall）
        
        CVaR表示：超过VaR的损失的平均值
        
        Args:
            returns: 收益率序列
            confidence_level: 置信度（默认95%）
        
        Returns:
            CVaR值（如-0.08表示8%的平均损失）
        """
        if not returns or len(returns) < 10:
            return None
        
        try:
            returns_array = np.array(returns)
            
            # 计算VaR
            var = self.calculate_var(returns, confidence_level)
            if var is None:
                return None
            
            # 计算CVaR（超过VaR的损失的平均值）
            tail_losses = returns_array[returns_array <= var]
            if len(tail_losses) == 0:
                return None
            
            cvar = np.mean(tail_losses)
            
            logger.info(f"CVaR({confidence_level:.0%}): {cvar:.2%} (VaR: {var:.2%})")
            
            return float(cvar)
        
        except Exception as e:
            logger.error(f"计算CVaR失败: {e}")
            return None
    
    def calculate_all_metrics(
        self,
        returns: List[float],
        equity_curve: List[float],
        periods_per_year: int = 365
    ) -> Dict[str, Optional[float]]:
        """
        一次性计算所有风险指标
        
        Args:
            returns: 收益率序列
            equity_curve: 权益曲线
            periods_per_year: 每年的周期数
        
        Returns:
            所有风险指标的字典
        """
        logger.info(f"开始计算风险指标（样本数: {len(returns)}）")
        
        metrics = {
            "sharpe_ratio": self.calculate_sharpe_ratio(returns, periods_per_year),
            "sortino_ratio": self.calculate_sortino_ratio(returns, periods_per_year),
            "max_drawdown": self.calculate_max_drawdown(equity_curve),
            "calmar_ratio": self.calculate_calmar_ratio(returns, equity_curve, periods_per_year),
            "var_95": self.calculate_var(returns, 0.95),
            "cvar_95": self.calculate_cvar(returns, 0.95),
        }
        
        # 计算基础统计
        if returns:
            returns_array = np.array(returns)
            metrics["mean_return"] = float(np.mean(returns_array))
            metrics["std_return"] = float(np.std(returns_array, ddof=1))
            metrics["total_return"] = float(np.sum(returns_array))
        
        logger.info(f"✅ 风险指标计算完成")
        
        return metrics
    
    def evaluate_risk_level(self, metrics: Dict[str, Optional[float]]) -> str:
        """
        评估风险等级
        
        Args:
            metrics: 风险指标字典
        
        Returns:
            风险等级（LOW/MEDIUM/HIGH/EXTREME）
        """
        sharpe = metrics.get("sharpe_ratio", 0) or 0
        max_dd = metrics.get("max_drawdown", 1) or 1
        
        # 评估逻辑
        if sharpe > 2.0 and max_dd < 0.10:
            return "LOW"  # 低风险：高夏普 + 低回撤
        elif sharpe > 1.0 and max_dd < 0.20:
            return "MEDIUM"  # 中等风险
        elif sharpe > 0.5 and max_dd < 0.30:
            return "HIGH"  # 高风险
        else:
            return "EXTREME"  # 极端风险：低夏普或高回撤
    
    def generate_risk_report(
        self,
        metrics: Dict[str, Optional[float]],
        prompt_name: str
    ) -> str:
        """
        生成风险报告
        
        Args:
            metrics: 风险指标字典
            prompt_name: Prompt名称
        
        Returns:
            格式化的风险报告
        """
        risk_level = self.evaluate_risk_level(metrics)
        
        report = f"""
========== Prompt风险评估报告 ==========
Prompt名称: {prompt_name}
风险等级: {risk_level}

【收益指标】
- 平均收益率: {metrics.get('mean_return', 0):.2%}
- 总收益率: {metrics.get('total_return', 0):.2%}

【风险调整后收益】
- 夏普比率: {metrics.get('sharpe_ratio') or 'N/A'}
- 索提诺比率: {metrics.get('sortino_ratio') or 'N/A'}
- 卡玛比率: {metrics.get('calmar_ratio') or 'N/A'}

【风险指标】
- 最大回撤: {metrics.get('max_drawdown', 0):.2%}
- VaR(95%): {metrics.get('var_95', 0):.2%}
- CVaR(95%): {metrics.get('cvar_95', 0):.2%}
- 波动率: {metrics.get('std_return', 0):.2%}

【评估建议】
"""
        
        # 根据风险等级给出建议
        if risk_level == "LOW":
            report += "✅ 该Prompt表现优秀，风险可控，建议继续使用。"
        elif risk_level == "MEDIUM":
            report += "⚠️  该Prompt表现中等，建议监控回撤情况。"
        elif risk_level == "HIGH":
            report += "⚠️  该Prompt风险较高，建议降低仓位或优化策略。"
        else:
            report += "🚨 该Prompt风险极高，建议立即停用并重新评估！"
        
        report += "\n" + "=" * 40
        
        return report

