"""Risk Management System"""

from decimal import Decimal
from typing import Tuple, Optional
import logging
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.core.config import settings
from app.models.trade import Trade
from app.models.risk_event import RiskEvent
from app.schemas.decision import AIDecisionOutput

logger = logging.getLogger(__name__)


class RiskManager:
    """风险管理器"""
    
    async def validate_decision(
        self,
        decision: AIDecisionOutput,
        account_balance: Decimal,
        current_price: Decimal,
        position_size: Decimal,
        db: AsyncSession
    ) -> Tuple[bool, Optional[str]]:
        """
        验证AI决策是否符合风控规则
        
        Args:
            decision: AI决策
            account_balance: 账户余额
            current_price: 当前价格
            position_size: 当前持仓
            db: 数据库会话
            
        Returns:
            (是否通过, 拒绝原因)
        """
        try:
            # 如果是HOLD，直接通过
            if decision.action == "HOLD" or decision.size == 0:
                return True, None
            
            # RC-001: 单笔仓位限制检查
            is_valid, reason = await self.check_position_limit(
                decision.size,
                current_price,
                account_balance
            )
            if not is_valid:
                await self.log_risk_event(
                    db,
                    "POSITION_LIMIT",
                    "HIGH",
                    reason,
                    "Order rejected"
                )
                return False, reason
            
            # RC-002: 单日亏损限制检查
            is_valid, reason = await self.check_daily_loss(db, account_balance)
            if not is_valid:
                await self.log_risk_event(
                    db,
                    "DAILY_LOSS_LIMIT",
                    "CRITICAL",
                    reason,
                    "Trading paused"
                )
                return False, reason
            
            # RC-003: 最大回撤检查
            is_valid, reason = await self.check_max_drawdown(db, account_balance)
            if not is_valid:
                await self.log_risk_event(
                    db,
                    "MAX_DRAWDOWN",
                    "CRITICAL",
                    reason,
                    "All positions closed"
                )
                return False, reason
            
            # RC-004: 连续亏损检查
            is_valid, reason = await self.check_consecutive_losses(db)
            if not is_valid:
                await self.log_risk_event(
                    db,
                    "CONSECUTIVE_LOSSES",
                    "HIGH",
                    reason,
                    "Manual review required"
                )
                return False, reason
            
            # 信心度检查
            if decision.confidence < Decimal('0.6'):
                reason = f"Confidence too low: {decision.confidence} < 0.6"
                logger.warning(reason)
                return False, reason
            
            logger.info("Risk validation passed")
            return True, None
            
        except Exception as e:
            logger.error(f"Error in risk validation: {e}")
            return False, f"Risk validation error: {str(e)}"
    
    async def check_position_limit(
        self,
        order_size: Decimal,
        price: Decimal,
        total_balance: Decimal
    ) -> Tuple[bool, Optional[str]]:
        """
        RC-001: 单笔仓位限制检查
        
        规则: 单笔仓位 ≤ 20%总资金
        """
        order_value = order_size * price
        max_position_value = total_balance * Decimal(str(settings.MAX_POSITION_PCT))
        
        if order_value > max_position_value:
            reason = (
                f"Position limit exceeded: ${order_value} > "
                f"${max_position_value} (20% of ${total_balance})"
            )
            logger.warning(reason)
            return False, reason
        
        return True, None
    
    async def check_daily_loss(
        self,
        db: AsyncSession,
        total_balance: Decimal
    ) -> Tuple[bool, Optional[str]]:
        """
        RC-002: 单日亏损限制检查
        
        规则: 单日亏损 ≤ 5%
        """
        try:
            today_start = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            
            # 查询今日交易盈亏
            result = await db.execute(
                select(func.sum(Trade.pnl))
                .where(Trade.timestamp >= today_start)
                .where(Trade.pnl.isnot(None))
            )
            today_pnl = result.scalar() or Decimal(0)
            
            max_daily_loss = total_balance * Decimal(str(settings.MAX_DAILY_LOSS_PCT))
            
            if today_pnl < -max_daily_loss:
                reason = (
                    f"Daily loss limit reached: ${-today_pnl} > "
                    f"${max_daily_loss} (5% of ${total_balance})"
                )
                logger.error(reason)
                return False, reason
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error checking daily loss: {e}")
            return True, None  # 失败时不阻止交易，但记录错误
    
    async def check_max_drawdown(
        self,
        db: AsyncSession,
        current_balance: Decimal,
        initial_balance: Decimal = Decimal("10000")
    ) -> Tuple[bool, Optional[str]]:
        """
        RC-003: 最大回撤检查
        
        规则: 最大回撤 ≤ 10%
        """
        try:
            # 计算当前回撤
            drawdown = (initial_balance - current_balance) / initial_balance
            max_allowed_drawdown = Decimal(str(settings.MAX_DRAWDOWN_PCT))
            
            if drawdown > max_allowed_drawdown:
                reason = (
                    f"Max drawdown exceeded: {drawdown*100:.2f}% > "
                    f"{max_allowed_drawdown*100:.2f}%"
                )
                logger.error(reason)
                return False, reason
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error checking max drawdown: {e}")
            return True, None
    
    async def check_consecutive_losses(
        self,
        db: AsyncSession,
        max_losses: int = 3
    ) -> Tuple[bool, Optional[str]]:
        """
        RC-004: 连续亏损检查
        
        规则: 连续亏损 ≤ 3笔
        """
        try:
            # 查询最近的交易
            result = await db.execute(
                select(Trade.pnl)
                .where(Trade.pnl.isnot(None))
                .order_by(Trade.timestamp.desc())
                .limit(max_losses)
            )
            recent_pnls = [row[0] for row in result.fetchall()]
            
            if len(recent_pnls) >= max_losses:
                # 检查是否全部亏损
                if all(pnl < 0 for pnl in recent_pnls):
                    reason = f"Consecutive losses detected: {max_losses} losses in a row"
                    logger.warning(reason)
                    return False, reason
            
            return True, None
            
        except Exception as e:
            logger.error(f"Error checking consecutive losses: {e}")
            return True, None
    
    async def log_risk_event(
        self,
        db: AsyncSession,
        event_type: str,
        severity: str,
        description: str,
        action_taken: str
    ):
        """记录风控事件"""
        try:
            risk_event = RiskEvent(
                event_type=event_type,
                severity=severity,
                description=description,
                action_taken=action_taken,
                resolved=False
            )
            db.add(risk_event)
            await db.commit()
            
            logger.info(f"Risk event logged: {event_type} - {severity}")
            
        except Exception as e:
            logger.error(f"Error logging risk event: {e}")
            await db.rollback()


# Global risk manager instance
risk_manager = RiskManager()

