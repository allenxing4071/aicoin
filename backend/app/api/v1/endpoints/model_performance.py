"""Model Performance API - 模型性能对比API"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, Any, List
from datetime import datetime, timedelta, date
from pydantic import BaseModel

from app.core.database import get_db
from app.core.config import settings
from app.models.model_performance import ModelPerformanceMetric, RoutingDecision

router = APIRouter()


class StrategyUpdate(BaseModel):
    """策略更新请求"""
    strategy: str  # adaptive/single_best/ab_testing/ensemble_voting/scenario_based


@router.get("/performance")
async def get_performance_comparison(
    days: int = 7,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """获取模型性能对比"""
    cutoff_date = (datetime.now() - timedelta(days=days)).date()
    
    # 获取两个模型的性能数据
    trained_perf = await _get_aggregated_performance(db, "trained_70b", cutoff_date)
    api_perf = await _get_aggregated_performance(db, "default_api", cutoff_date)
    
    # 生成推荐
    recommendation = _generate_recommendation(trained_perf, api_perf)
    
    return {
        "trained_70b": trained_perf,
        "default_api": api_perf,
        "current_strategy": settings.DEEPSEEK_ROUTING_STRATEGY,
        "recommendation": recommendation,
        "period_days": days
    }


@router.get("/performance/history")
async def get_performance_history(
    model_name: str | None = None,
    days: int = 30,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """获取性能历史趋势"""
    cutoff_date = (datetime.now() - timedelta(days=days)).date()
    
    query = select(ModelPerformanceMetric).where(
        ModelPerformanceMetric.metric_date >= cutoff_date
    )
    
    if model_name:
        query = query.where(ModelPerformanceMetric.model_name == model_name)
    
    query = query.order_by(ModelPerformanceMetric.metric_date)
    
    result = await db.execute(query)
    metrics = result.scalars().all()
    
    # 按模型分组
    history_by_model = {}
    for metric in metrics:
        if metric.model_name not in history_by_model:
            history_by_model[metric.model_name] = []
        
        history_by_model[metric.model_name].append({
            "date": metric.metric_date.isoformat(),
            "accuracy": metric.accuracy,
            "profit_rate": metric.profit_rate,
            "total_pnl": metric.total_pnl,
            "avg_response_time": metric.avg_response_time
        })
    
    return {
        "history": history_by_model,
        "period_days": days
    }


@router.post("/strategy")
async def update_routing_strategy(
    update: StrategyUpdate,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """切换路由策略"""
    valid_strategies = ["adaptive", "single_best", "ab_testing", "ensemble_voting", "scenario_based"]
    
    if update.strategy not in valid_strategies:
        raise HTTPException(status_code=400, detail=f"无效的策略: {update.strategy}")
    
    # 更新配置（注意：这里只是演示，实际应该更新配置文件或数据库）
    settings.DEEPSEEK_ROUTING_STRATEGY = update.strategy
    
    return {
        "message": "策略已更新",
        "new_strategy": update.strategy
    }


@router.get("/routing/stats")
async def get_routing_stats(
    days: int = 7,
    db: AsyncSession = Depends(get_db)
) -> Dict[str, Any]:
    """获取路由统计"""
    cutoff_date = datetime.now() - timedelta(days=days)
    
    # 获取决策记录
    result = await db.execute(
        select(RoutingDecision).where(
            RoutingDecision.created_at >= cutoff_date
        )
    )
    decisions = result.scalars().all()
    
    # 统计
    total_decisions = len(decisions)
    by_strategy = {}
    by_model = {}
    fallback_count = 0
    
    for decision in decisions:
        # 按策略统计
        strategy = decision.routing_strategy
        if strategy not in by_strategy:
            by_strategy[strategy] = 0
        by_strategy[strategy] += 1
        
        # 按模型统计
        model = decision.model_used
        if model not in by_model:
            by_model[model] = 0
        by_model[model] += 1
        
        # 降级统计
        if decision.fallback_triggered:
            fallback_count += 1
    
    return {
        "total_decisions": total_decisions,
        "by_strategy": by_strategy,
        "by_model": by_model,
        "fallback_count": fallback_count,
        "fallback_rate": fallback_count / total_decisions if total_decisions > 0 else 0,
        "period_days": days
    }


async def _get_aggregated_performance(
    db: AsyncSession,
    model_name: str,
    cutoff_date: date
) -> Dict[str, Any]:
    """获取聚合的性能数据"""
    result = await db.execute(
        select(ModelPerformanceMetric).where(
            ModelPerformanceMetric.model_name == model_name,
            ModelPerformanceMetric.metric_date >= cutoff_date
        )
    )
    metrics = result.scalars().all()
    
    if not metrics:
        return {
            "accuracy": 0.0,
            "profit_rate": 0.0,
            "avg_response_time": 0.0,
            "total_decisions": 0,
            "total_pnl": 0.0
        }
    
    # 聚合计算
    total_decisions = sum(m.total_decisions for m in metrics)
    correct_decisions = sum(m.correct_decisions for m in metrics)
    total_trades = sum(m.total_trades for m in metrics)
    profitable_trades = sum(m.profitable_trades for m in metrics)
    total_pnl = sum(m.total_pnl for m in metrics)
    
    # 平均值
    avg_response_times = [m.avg_response_time for m in metrics if m.avg_response_time]
    avg_response_time = sum(avg_response_times) / len(avg_response_times) if avg_response_times else 0.0
    
    return {
        "accuracy": correct_decisions / total_decisions if total_decisions > 0 else 0.0,
        "profit_rate": profitable_trades / total_trades if total_trades > 0 else 0.0,
        "avg_response_time": avg_response_time,
        "total_decisions": total_decisions,
        "total_trades": total_trades,
        "total_pnl": total_pnl
    }


def _generate_recommendation(trained_perf: Dict, api_perf: Dict) -> str:
    """生成推荐策略"""
    trained_acc = trained_perf.get("accuracy", 0)
    api_acc = api_perf.get("accuracy", 0)
    
    trained_samples = trained_perf.get("total_decisions", 0)
    api_samples = api_perf.get("total_decisions", 0)
    
    min_samples = settings.MIN_SAMPLES_FOR_EVALUATION
    
    if trained_samples < min_samples or api_samples < min_samples:
        return "建议使用AB测试策略积累更多数据"
    
    accuracy_diff = abs(trained_acc - api_acc)
    
    if accuracy_diff < 0.05:
        return "两个模型效果接近，建议使用双模型投票提升可靠性"
    elif accuracy_diff > 0.15:
        better = "70B模型" if trained_acc > api_acc else "默认API"
        return f"{better}明显更优，建议使用单模型策略"
    else:
        return "建议使用场景分配策略，根据风险选择模型"

