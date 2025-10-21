"""Performance metrics calculation Celery task"""

import logging
from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.metrics_calculator.calculate_performance_metrics")
def calculate_performance_metrics():
    """
    计算性能指标 - 定时任务
    
    每1小时执行一次,计算夏普比率、最大回撤等指标
    """
    import asyncio
    from app.core.database import AsyncSessionLocal
    from sqlalchemy import select, func
    from app.models.trade import Trade
    from app.models.account import AccountSnapshot
    from decimal import Decimal
    
    async def run():
        logger.info("Calculating performance metrics...")
        
        async with AsyncSessionLocal() as db:
            try:
                # 查询所有交易
                result = await db.execute(
                    select(Trade).where(Trade.pnl.isnot(None)).order_by(Trade.timestamp)
                )
                trades = result.scalars().all()
                
                if not trades:
                    logger.info("No trades found, skipping metrics calculation")
                    return {"status": "skipped", "reason": "No trades"}
                
                # 计算基础指标
                total_trades = len(trades)
                winning_trades = sum(1 for t in trades if t.pnl and t.pnl > 0)
                win_rate = Decimal(winning_trades) / Decimal(total_trades)
                
                # TODO: 实现更复杂的指标计算
                # - 夏普比率: 需要计算收益率的标准差
                # - 最大回撤: 需要追踪历史最高净值
                
                logger.info(
                    f"Metrics calculated: {total_trades} trades, "
                    f"{win_rate*100:.1f}% win rate"
                )
                
                return {
                    "status": "success",
                    "total_trades": total_trades,
                    "win_rate": str(win_rate)
                }
                
            except Exception as e:
                logger.error(f"Error calculating metrics: {e}")
                return {"status": "error", "error": str(e)}
    
    return asyncio.run(run())

