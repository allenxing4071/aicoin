"""
性能指标API端点
提供30+量化指标用于前端展示
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
import logging

from app.core.database import get_db
from app.services.monitoring.kpi_calculator import KPICalculator
from app.schemas.performance import (
    PerformanceMetricsResponse,
    ReturnsMetrics,
    RiskMetrics,
    RatiosMetrics,
    WinRateMetrics,
    EfficiencyMetrics
)

router = APIRouter(tags=["performance"])
logger = logging.getLogger(__name__)


@router.get("/metrics", response_model=PerformanceMetricsResponse)
async def get_performance_metrics(
    days: int = 30,
    db: AsyncSession = Depends(get_db)
) -> PerformanceMetricsResponse:
    """
    获取性能指标
    
    Args:
        days: 统计天数，默认30天
        db: 数据库会话
        
    Returns:
        PerformanceMetricsResponse: 包含收益、风险、胜率、效率等指标
    """
    try:
        # 初始化KPI计算器
        calculator = KPICalculator(db)
        
        # 计算所有指标
        returns = await calculator.calculate_returns(days=days)
        risk = await calculator.calculate_risk(days=days)
        ratios = await calculator.calculate_ratios(days=days)
        win_rate = await calculator.calculate_win_rate(days=days)
        efficiency = await calculator.calculate_efficiency(days=days)
        
        # 构建响应
        response = PerformanceMetricsResponse(
            returns=ReturnsMetrics(**returns),
            risk=RiskMetrics(**risk),
            ratios=RatiosMetrics(**ratios),
            win_rate=WinRateMetrics(**win_rate),
            efficiency=EfficiencyMetrics(**efficiency),
            period_days=days
        )
        
        logger.info(f"📊 成功计算{days}天性能指标")
        return response
        
    except Exception as e:
        logger.error(f"❌ 计算性能指标失败: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"计算性能指标失败: {str(e)}"
        )


@router.get("/summary")
async def get_performance_summary(
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取性能摘要（简化版）
    
    Returns:
        Dict: 关键指标摘要
    """
    try:
        calculator = KPICalculator(db)
        
        # 只计算关键指标
        returns = await calculator.calculate_returns(days=30)
        risk = await calculator.calculate_risk(days=30)
        win_rate = await calculator.calculate_win_rate(days=30)
        
        summary = {
            "total_return": returns.get("total_return", 0.0),
            "annual_return": returns.get("annual_return", 0.0),
            "max_drawdown": risk.get("max_drawdown", 0.0),
            "sharpe_ratio": risk.get("sharpe_ratio", 0.0),
            "win_rate": win_rate.get("overall", 0.0),
            "total_trades": win_rate.get("total_trades", 0),
            "period": "30d"
        }
        
        logger.info("📊 成功获取性能摘要")
        return summary
        
    except Exception as e:
        logger.error(f"❌ 获取性能摘要失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取性能摘要失败: {str(e)}"
        )


@router.get("/history")
async def get_performance_history(
    metric: str = "equity",
    days: int = 30,
    interval: str = "1h",
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """
    获取性能历史数据（用于图表展示）
    
    Args:
        metric: 指标类型 (equity, return, drawdown, sharpe)
        days: 历史天数
        interval: 时间间隔 (1h, 4h, 1d)
        db: 数据库会话
        
    Returns:
        Dict: 包含时间序列数据
    """
    try:
        calculator = KPICalculator(db)
        
        # 根据指标类型获取历史数据
        if metric == "equity":
            data = await calculator.get_equity_history(days=days, interval=interval)
        elif metric == "return":
            data = await calculator.get_return_history(days=days, interval=interval)
        elif metric == "drawdown":
            data = await calculator.get_drawdown_history(days=days, interval=interval)
        elif metric == "sharpe":
            data = await calculator.get_sharpe_history(days=days, interval=interval)
        else:
            raise HTTPException(
                status_code=400,
                detail=f"不支持的指标类型: {metric}"
            )
        
        logger.info(f"📈 成功获取{metric}历史数据 ({days}天, {interval})")
        return {
            "metric": metric,
            "days": days,
            "interval": interval,
            "data": data
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ 获取性能历史失败: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"获取性能历史失败: {str(e)}"
        )
