"""
Prompt过拟合检测器
防止Prompt只适合历史数据，未来失效
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.prompt_template import PromptTemplate, PromptPerformance

logger = logging.getLogger(__name__)


class PromptOverfittingDetector:
    """
    Prompt过拟合检测器
    
    核心方法：
    1. 时间序列交叉验证（Walk-Forward Analysis）
    2. 样本内/样本外表现对比
    3. 稳定性评分
    """
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def detect_overfitting(
        self,
        prompt_id: int,
        in_sample_returns: List[float],
        out_sample_returns: List[float]
    ) -> Dict[str, any]:
        """
        检测Prompt是否过拟合
        
        Args:
            prompt_id: Prompt ID
            in_sample_returns: 样本内收益率序列（训练集）
            out_sample_returns: 样本外收益率序列（测试集）
        
        Returns:
            {
                "overfitting_score": 0.75,  # 0-1，越高越可能过拟合
                "in_sample_win_rate": 0.72,
                "out_sample_win_rate": 0.58,
                "performance_degradation": 0.14,  # 性能下降幅度
                "stability_score": 0.45,
                "warning": "高风险过拟合"
            }
        """
        if not in_sample_returns or not out_sample_returns:
            return {"overfitting_score": 0, "warning": "样本不足"}
        
        # 1. 计算样本内表现
        in_sample_win_rate = self._calculate_win_rate(in_sample_returns)
        in_sample_sharpe = self._calculate_sharpe(in_sample_returns)
        
        # 2. 计算样本外表现
        out_sample_win_rate = self._calculate_win_rate(out_sample_returns)
        out_sample_sharpe = self._calculate_sharpe(out_sample_returns)
        
        # 3. 计算性能下降幅度
        win_rate_degradation = in_sample_win_rate - out_sample_win_rate
        sharpe_degradation = (in_sample_sharpe - out_sample_sharpe) / max(in_sample_sharpe, 0.01)
        
        # 4. 计算稳定性评分
        stability_score = self._calculate_stability(in_sample_returns, out_sample_returns)
        
        # 5. 综合过拟合评分
        overfitting_score = self._calculate_overfitting_score(
            win_rate_degradation,
            sharpe_degradation,
            stability_score
        )
        
        # 6. 生成警告
        warning = self._generate_warning(overfitting_score)
        
        result = {
            "overfitting_score": round(overfitting_score, 2),
            "in_sample_win_rate": round(in_sample_win_rate, 4),
            "out_sample_win_rate": round(out_sample_win_rate, 4),
            "in_sample_sharpe": round(in_sample_sharpe, 2),
            "out_sample_sharpe": round(out_sample_sharpe, 2),
            "performance_degradation": round(win_rate_degradation, 4),
            "stability_score": round(stability_score, 2),
            "warning": warning
        }
        
        logger.info(f"Prompt {prompt_id} 过拟合检测: score={overfitting_score:.2f}, {warning}")
        
        return result
    
    def _calculate_win_rate(self, returns: List[float]) -> float:
        """计算胜率"""
        if not returns:
            return 0.0
        wins = sum(1 for r in returns if r > 0)
        return wins / len(returns)
    
    def _calculate_sharpe(self, returns: List[float]) -> float:
        """计算夏普比率（简化版）"""
        if not returns or len(returns) < 2:
            return 0.0
        
        returns_array = np.array(returns)
        mean_return = np.mean(returns_array)
        std_return = np.std(returns_array, ddof=1)
        
        if std_return == 0:
            return 0.0
        
        return mean_return / std_return * np.sqrt(252)  # 年化
    
    def _calculate_stability(
        self,
        in_sample_returns: List[float],
        out_sample_returns: List[float]
    ) -> float:
        """
        计算稳定性评分
        
        方法：比较样本内和样本外的收益率分布相似度
        
        Returns:
            0-1之间，越高越稳定
        """
        if not in_sample_returns or not out_sample_returns:
            return 0.0
        
        # 计算两组数据的统计特征
        in_mean = np.mean(in_sample_returns)
        in_std = np.std(in_sample_returns)
        out_mean = np.mean(out_sample_returns)
        out_std = np.std(out_sample_returns)
        
        # 计算均值和标准差的相对差异
        mean_diff = abs(in_mean - out_mean) / max(abs(in_mean), 0.01)
        std_diff = abs(in_std - out_std) / max(in_std, 0.01)
        
        # 稳定性评分（差异越小，稳定性越高）
        stability = 1.0 - min((mean_diff + std_diff) / 2, 1.0)
        
        return stability
    
    def _calculate_overfitting_score(
        self,
        win_rate_degradation: float,
        sharpe_degradation: float,
        stability_score: float
    ) -> float:
        """
        计算综合过拟合评分
        
        公式：
        overfitting_score = 0.4 * win_rate_deg + 0.3 * sharpe_deg + 0.3 * (1 - stability)
        
        Returns:
            0-1之间，越高越可能过拟合
        """
        # 归一化
        win_rate_deg_norm = min(max(win_rate_degradation, 0), 1)
        sharpe_deg_norm = min(max(sharpe_degradation, 0), 1)
        instability = 1.0 - stability_score
        
        # 加权求和
        score = (
            0.4 * win_rate_deg_norm +
            0.3 * sharpe_deg_norm +
            0.3 * instability
        )
        
        return min(score, 1.0)
    
    def _generate_warning(self, overfitting_score: float) -> str:
        """生成警告信息"""
        if overfitting_score < 0.3:
            return "✅ 低风险，Prompt表现稳定"
        elif overfitting_score < 0.5:
            return "⚠️  中等风险，建议监控"
        elif overfitting_score < 0.7:
            return "⚠️  高风险过拟合，建议优化"
        else:
            return "🚨 极高风险过拟合，建议立即停用"
    
    async def walk_forward_analysis(
        self,
        prompt_id: int,
        all_returns: List[Tuple[datetime, float]],
        train_window_days: int = 60,
        test_window_days: int = 30
    ) -> Dict[str, any]:
        """
        时间序列交叉验证（Walk-Forward Analysis）
        
        方法：
        1. 将数据分为多个时间窗口
        2. 每个窗口：前60天训练，后30天测试
        3. 滚动前进，重复验证
        
        Args:
            prompt_id: Prompt ID
            all_returns: [(时间戳, 收益率), ...]
            train_window_days: 训练窗口天数
            test_window_days: 测试窗口天数
        
        Returns:
            {
                "num_windows": 5,
                "avg_overfitting_score": 0.45,
                "windows": [...]
            }
        """
        if not all_returns or len(all_returns) < train_window_days + test_window_days:
            return {"error": "数据不足"}
        
        # 按时间排序
        sorted_returns = sorted(all_returns, key=lambda x: x[0])
        
        windows = []
        window_size = train_window_days + test_window_days
        
        # 滚动窗口
        for i in range(0, len(sorted_returns) - window_size + 1, test_window_days):
            # 训练集
            train_start = i
            train_end = i + train_window_days
            train_returns = [r[1] for r in sorted_returns[train_start:train_end]]
            
            # 测试集
            test_start = train_end
            test_end = test_start + test_window_days
            test_returns = [r[1] for r in sorted_returns[test_start:test_end]]
            
            # 检测过拟合
            result = await self.detect_overfitting(prompt_id, train_returns, test_returns)
            
            windows.append({
                "window_id": len(windows) + 1,
                "train_period": f"{sorted_returns[train_start][0].date()} ~ {sorted_returns[train_end-1][0].date()}",
                "test_period": f"{sorted_returns[test_start][0].date()} ~ {sorted_returns[test_end-1][0].date()}",
                "overfitting_score": result["overfitting_score"],
                "in_sample_win_rate": result["in_sample_win_rate"],
                "out_sample_win_rate": result["out_sample_win_rate"]
            })
        
        # 计算平均过拟合评分
        avg_score = np.mean([w["overfitting_score"] for w in windows])
        
        logger.info(f"Walk-Forward分析完成: {len(windows)}个窗口, 平均过拟合评分={avg_score:.2f}")
        
        return {
            "num_windows": len(windows),
            "avg_overfitting_score": round(avg_score, 2),
            "windows": windows
        }
    
    async def monitor_out_of_sample_performance(
        self,
        prompt_id: int,
        threshold: float = 0.10
    ) -> Dict[str, any]:
        """
        监控样本外表现
        
        方法：
        1. 获取Prompt的历史表现（样本内）
        2. 获取最近30天的表现（样本外）
        3. 对比差异
        
        Args:
            prompt_id: Prompt ID
            threshold: 警告阈值（如0.10表示胜率下降10%触发警告）
        
        Returns:
            {
                "historical_win_rate": 0.65,
                "recent_win_rate": 0.52,
                "degradation": 0.13,
                "alert": True
            }
        """
        # TODO: 从数据库查询历史数据
        # 这里简化为示例
        
        return {
            "historical_win_rate": 0.65,
            "recent_win_rate": 0.52,
            "degradation": 0.13,
            "alert": True,
            "message": "样本外表现显著下降，建议重新评估Prompt"
        }

