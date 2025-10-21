"""Trading loop Celery task"""

from decimal import Decimal
import logging
from app.core.celery_app import celery_app
from app.core.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.trading_loop.execute_trading_decision")
def execute_trading_decision():
    """
    执行交易决策循环 - 定时任务
    
    该任务每5-15分钟执行一次(可配置)
    """
    import asyncio
    from app.core.database import AsyncSessionLocal
    from app.services.ai.decision_engine import decision_engine
    from app.services.trading.risk_manager import risk_manager
    from app.services.trading.trade_executor import trade_executor
    from app.services.market.hyperliquid_client import hyperliquid_client
    
    async def run():
        # 检查交易是否启用
        if not settings.TRADING_ENABLED:
            logger.info("Trading is disabled, skipping decision loop")
            return {"status": "skipped", "reason": "Trading disabled"}
        
        logger.info("Starting trading decision loop...")
        
        async with AsyncSessionLocal() as db:
            try:
                symbol = settings.DEFAULT_SYMBOL
                
                # 1. 获取市场数据
                logger.info(f"Fetching market data for {symbol}")
                klines = await hyperliquid_client.get_klines(symbol, interval="1h", limit=24)
                orderbook = await hyperliquid_client.get_orderbook(symbol, depth=20)
                ticker = await hyperliquid_client.get_ticker(symbol)
                
                current_price = Decimal(ticker['price'])
                
                market_data = {
                    'current_price': current_price,
                    'klines': klines,
                    'orderbook': orderbook,
                    'ticker': ticker
                }
                
                # 2. 获取账户信息
                logger.info("Fetching account info")
                account_balance_data = await hyperliquid_client.get_account_balance()
                positions = await hyperliquid_client.get_positions()
                
                account_info = {
                    'balance': Decimal(account_balance_data['balance']),
                    'position': positions[0] if positions else {}
                }
                
                # 3. AI决策
                logger.info("Making AI decision...")
                decision, latency_ms = await decision_engine.make_decision(
                    symbol=symbol,
                    market_data=market_data,
                    account_info=account_info
                )
                
                logger.info(
                    f"AI Decision: {decision.action} {decision.size} @ "
                    f"confidence {decision.confidence}"
                )
                
                # 4. 风控验证
                logger.info("Validating decision with risk manager...")
                is_valid, reject_reason = await risk_manager.validate_decision(
                    decision=decision,
                    account_balance=account_info['balance'],
                    current_price=current_price,
                    position_size=Decimal(str(positions[0].get('size', 0))) if positions else Decimal(0),
                    db=db
                )
                
                if not is_valid:
                    logger.warning(f"Decision rejected: {reject_reason}")
                    return {
                        "status": "rejected",
                        "reason": reject_reason,
                        "decision": decision.dict()
                    }
                
                # 5. 执行订单
                logger.info("Executing decision...")
                execution_result = await trade_executor.execute_decision(
                    decision=decision,
                    symbol=symbol,
                    current_price=current_price,
                    db=db
                )
                
                logger.info(f"Execution result: {execution_result}")
                
                return {
                    "status": "success",
                    "decision": decision.dict(),
                    "execution": execution_result
                }
                
            except Exception as e:
                logger.error(f"Error in trading loop: {e}", exc_info=True)
                return {"status": "error", "error": str(e)}
    
    # Run async code
    return asyncio.run(run())

