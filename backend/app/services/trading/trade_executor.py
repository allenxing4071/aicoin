"""Trade Execution System"""

from decimal import Decimal
from typing import Dict, Any, Optional
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from app.services.market.hyperliquid_client import hyperliquid_client
from app.models.trade import Trade
from app.models.order import Order
from app.schemas.decision import AIDecisionOutput

logger = logging.getLogger(__name__)


class TradeExecutor:
    """交易执行器"""
    
    async def execute_decision(
        self,
        decision: AIDecisionOutput,
        symbol: str,
        current_price: Decimal,
        db: AsyncSession
    ) -> Dict[str, Any]:
        """
        执行AI交易决策
        
        Args:
            decision: AI决策
            symbol: 交易品种
            current_price: 当前价格
            db: 数据库会话
            
        Returns:
            执行结果
        """
        try:
            if decision.action == "HOLD" or decision.size == 0:
                logger.info("Decision is HOLD, no action taken")
                return {
                    "success": True,
                    "action": "HOLD",
                    "message": "No trade executed"
                }
            
            # 创建订单记录
            order = Order(
                symbol=symbol,
                side=decision.action,
                type="MARKET",
                size=decision.size,
                status="PENDING"
            )
            db.add(order)
            await db.flush()  # 获取order.id
            
            logger.info(f"Executing {decision.action} order: {decision.size} {symbol}")
            
            # 调用交易所API下单
            order_result = await hyperliquid_client.place_order(
                symbol=symbol,
                side=decision.action,
                size=decision.size,
                order_type="MARKET"
            )
            
            if order_result.get('success'):
                # 更新订单状态
                order.status = "FILLED"
                order.exchange_order_id = order_result.get('order_id')
                order.filled_size = decision.size
                
                # 创建交易记录
                trade = Trade(
                    order_id=order.id,
                    symbol=symbol,
                    side=decision.action,
                    price=current_price,
                    size=decision.size,
                    fee=Decimal(0),  # TODO: 计算真实手续费
                    ai_reasoning=decision.reasoning,
                    confidence=decision.confidence
                )
                db.add(trade)
                
                await db.commit()
                
                logger.info(f"Trade executed successfully: {trade.id}")
                
                return {
                    "success": True,
                    "action": decision.action,
                    "trade_id": trade.id,
                    "order_id": order.id,
                    "size": str(decision.size),
                    "price": str(current_price),
                    "message": "Trade executed successfully"
                }
            else:
                # 订单失败
                order.status = "FAILED"
                await db.commit()
                
                reason = order_result.get('reason', 'Unknown error')
                logger.error(f"Order execution failed: {reason}")
                
                return {
                    "success": False,
                    "action": decision.action,
                    "message": f"Order failed: {reason}"
                }
                
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            await db.rollback()
            
            return {
                "success": False,
                "action": decision.action if decision else "UNKNOWN",
                "message": f"Execution error: {str(e)}"
            }
    
    async def calculate_pnl(
        self,
        entry_price: Decimal,
        exit_price: Decimal,
        size: Decimal,
        side: str
    ) -> Decimal:
        """
        计算盈亏
        
        Args:
            entry_price: 开仓价格
            exit_price: 平仓价格
            size: 交易数量
            side: 交易方向 (BUY/SELL)
            
        Returns:
            盈亏金额
        """
        if side == "BUY":
            pnl = (exit_price - entry_price) * size
        else:  # SELL
            pnl = (entry_price - exit_price) * size
        
        return pnl


# Global trade executor instance
trade_executor = TradeExecutor()

