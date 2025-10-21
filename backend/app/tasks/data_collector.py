"""Data collection Celery tasks"""

import logging
from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)


@celery_app.task(name="app.tasks.data_collector.collect_market_data")
def collect_market_data():
    """
    采集市场数据 - 定时任务
    
    每1分钟执行一次,采集K线和订单簿数据
    """
    import asyncio
    from app.core.database import AsyncSessionLocal
    from app.services.market.hyperliquid_client import hyperliquid_client
    from app.core.config import settings
    from app.models.market_data import MarketDataKline
    from datetime import datetime
    
    async def run():
        logger.info("Collecting market data...")
        
        async with AsyncSessionLocal() as db:
            try:
                symbol = settings.DEFAULT_SYMBOL
                
                # 获取1小时K线
                klines = await hyperliquid_client.get_klines(symbol, interval="1h", limit=1)
                
                if klines and len(klines) > 0:
                    kline = klines[0]
                    
                    # 保存到数据库 (如果不存在)
                    # 使用upsert避免重复
                    # TODO: 实现完整的upsert逻辑
                    
                    logger.info(f"Market data collected for {symbol}")
                
                return {"status": "success", "symbol": symbol}
                
            except Exception as e:
                logger.error(f"Error collecting market data: {e}")
                return {"status": "error", "error": str(e)}
    
    return asyncio.run(run())


@celery_app.task(name="app.tasks.data_collector.collect_account_snapshot")
def collect_account_snapshot():
    """
    采集账户快照 - 定时任务
    
    每5分钟执行一次,记录账户状态
    """
    import asyncio
    from app.core.database import AsyncSessionLocal
    from app.services.market.hyperliquid_client import hyperliquid_client
    from app.models.account import AccountSnapshot
    from decimal import Decimal
    
    async def run():
        logger.info("Collecting account snapshot...")
        
        async with AsyncSessionLocal() as db:
            try:
                # 获取账户信息
                balance_data = await hyperliquid_client.get_account_balance()
                
                # 创建快照
                snapshot = AccountSnapshot(
                    balance=Decimal(balance_data['balance']),
                    equity=Decimal(balance_data['equity']),
                    unrealized_pnl=Decimal(balance_data.get('unrealized_pnl', 0)),
                    realized_pnl=Decimal(balance_data.get('realized_pnl', 0))
                )
                
                db.add(snapshot)
                await db.commit()
                
                logger.info("Account snapshot saved")
                
                return {"status": "success", "balance": str(snapshot.balance)}
                
            except Exception as e:
                logger.error(f"Error collecting account snapshot: {e}")
                await db.rollback()
                return {"status": "error", "error": str(e)}
    
    return asyncio.run(run())

