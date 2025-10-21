"""Performance metrics API endpoints"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from decimal import Decimal
import logging

from app.core.database import get_db
from app.models.trade import Trade
from app.schemas.performance import PerformanceMetrics

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/metrics", response_model=PerformanceMetrics)
async def get_performance_metrics(db: AsyncSession = Depends(get_db)):
    """
    获取性能指标
    
    Returns:
        性能指标(收益率、夏普比率、回撤等)
    """
    try:
        # 查询所有交易
        result = await db.execute(
            select(Trade).where(Trade.pnl.isnot(None)).order_by(Trade.timestamp)
        )
        trades = result.scalars().all()
        
        if not trades:
            return PerformanceMetrics(
                total_return=Decimal(0),
                total_trades=0
            )
        
        # 计算基础指标
        total_pnl = sum(t.pnl for t in trades if t.pnl)
        total_trades = len(trades)
        winning_trades = sum(1 for t in trades if t.pnl and t.pnl > 0)
        losing_trades = sum(1 for t in trades if t.pnl and t.pnl < 0)
        
        # 胜率
        win_rate = Decimal(winning_trades) / Decimal(total_trades) if total_trades > 0 else Decimal(0)
        
        # 平均盈亏
        wins = [t.pnl for t in trades if t.pnl and t.pnl > 0]
        losses = [abs(t.pnl) for t in trades if t.pnl and t.pnl < 0]
        
        avg_win = sum(wins) / len(wins) if wins else Decimal(0)
        avg_loss = sum(losses) / len(losses) if losses else Decimal(0)
        
        # 盈亏比
        profit_factor = avg_win / avg_loss if avg_loss > 0 else Decimal(0)
        
        # 总收益率 (假设初始资金10000)
        initial_balance = Decimal(10000)
        total_return = total_pnl / initial_balance if initial_balance > 0 else Decimal(0)
        
        # TODO: 计算夏普比率和最大回撤 (需要更复杂的逻辑)
        
        return PerformanceMetrics(
            total_return=total_return,
            sharpe_ratio=None,
            max_drawdown=None,
            win_rate=win_rate,
            profit_factor=profit_factor,
            total_trades=total_trades,
            winning_trades=winning_trades,
            losing_trades=losing_trades,
            avg_win=avg_win,
            avg_loss=avg_loss,
            current_streak=0
        )
        
    except Exception as e:
        logger.error(f"Error calculating performance metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

