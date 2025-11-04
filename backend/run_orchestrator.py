#!/usr/bin/env python3
"""独立运行AI交易编排器"""
import asyncio
import sys
import os

# 添加项目路径
sys.path.insert(0, '/app')

from app.services.orchestrator_v2 import AITradingOrchestratorV2

async def main():
    print("🚀 启动AI交易编排器V2...")
    orchestrator = AITradingOrchestratorV2()
    await orchestrator.run()

if __name__ == "__main__":
    asyncio.run(main())
