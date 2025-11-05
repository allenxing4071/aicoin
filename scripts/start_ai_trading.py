#!/usr/bin/env python3
"""启动AI交易系统"""
import asyncio
import sys
import os

sys.path.insert(0, '/Users/xinghailong/Documents/soft/AIcoin/backend')

from app.core.redis_client import RedisClient
from app.services.hyperliquid_trading import HyperliquidTradingService
from app.services.hyperliquid_market_data import HyperliquidMarketData
from app.services.orchestrator_v2 import AITradingOrchestratorV2
from app.core.database import get_db
from app.core.config import settings

async def main():
    print("🚀 启动AI交易系统...")
    
    # 初始化服务
    redis_client = RedisClient()
    trading_service = HyperliquidTradingService(redis_client, testnet=False)
    market_data_service = HyperliquidMarketData(redis_client, testnet=False)
    
    # 获取数据库会话
    db_gen = get_db()
    db_session = next(db_gen)
    
    # 初始化编排器
    orchestrator = AITradingOrchestratorV2(
        redis_client=redis_client,
        trading_service=trading_service,
        market_data_service=market_data_service,
        db_session=db_session,
        decision_interval=300
    )
    
    print("✅ AI交易系统已初始化")
    print("🔄 开始交易循环...")
    
    # 运行
    await orchestrator.run()

if __name__ == "__main__":
    asyncio.run(main())
