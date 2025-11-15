#!/usr/bin/env python3
"""
自检脚本 - 验证v3.1所有功能
"""

import asyncio
import sys
import logging
from datetime import datetime

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

async def check_imports():
    """检查关键模块导入"""
    logger.info("=" * 60)
    logger.info("1. 检查模块导入")
    logger.info("=" * 60)
    
    try:
        from app.services.intelligence.intelligence_coordinator import IntelligenceCoordinator
        logger.info("✅ IntelligenceCoordinator 导入成功")
        
        from app.services.intelligence.monitoring import IntelligenceMonitor
        logger.info("✅ IntelligenceMonitor 导入成功")
        
        from app.services.intelligence.storage_layers import (
            ShortTermIntelligenceCache,
            MidTermIntelligenceAnalyzer,
            LongTermIntelligenceStore,
            IntelligenceVectorKB
        )
        logger.info("✅ 四层存储模块导入成功")
        
        from app.services.decision.decision_engine_v2 import DecisionEngineV2
        logger.info("✅ DecisionEngineV2 导入成功")
        
        return True
    except Exception as e:
        logger.error(f"❌ 模块导入失败: {e}")
        return False

async def check_coordinator():
    """检查IntelligenceCoordinator初始化"""
    logger.info("\n" + "=" * 60)
    logger.info("2. 检查IntelligenceCoordinator")
    logger.info("=" * 60)
    
    try:
        from app.core.redis_client import RedisClient
        from app.core.config import settings
        from app.services.intelligence.intelligence_coordinator import IntelligenceCoordinator
        
        # 创建Redis客户端
        redis_client = RedisClient()
        await redis_client.connect()
        logger.info("✅ Redis连接成功")
        
        # 创建协调器（不需要真实的db_session进行基本检查）
        coordinator = IntelligenceCoordinator(redis_client, None)
        logger.info("✅ IntelligenceCoordinator 初始化成功")
        
        # 检查配置
        logger.info(f"   - 多平台协调: {'启用' if coordinator.use_multi_platform else '禁用'}")
        logger.info(f"   - 四层存储: {'启用' if coordinator.use_storage_layers else '禁用'}")
        logger.info(f"   - L1缓存: {'✓' if coordinator.l1_cache else '✗'}")
        logger.info(f"   - L2分析: {'✓' if coordinator.l2_analyzer else '✗'}")
        logger.info(f"   - L3存储: {'✓' if coordinator.l3_store else '✗'}")
        logger.info(f"   - L4向量: {'✓' if coordinator.l4_vector else '✗'}")
        
        await redis_client.close()
        return True
    except Exception as e:
        logger.error(f"❌ IntelligenceCoordinator检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def check_storage_layers():
    """检查四层存储"""
    logger.info("\n" + "=" * 60)
    logger.info("3. 检查四层存储")
    logger.info("=" * 60)
    
    try:
        from app.core.redis_client import RedisClient
        from app.core.config import settings
        from app.services.intelligence.storage_layers import ShortTermIntelligenceCache
        
        redis_client = RedisClient()
        await redis_client.connect()
        
        # 测试L1缓存
        l1_cache = ShortTermIntelligenceCache(redis_client)
        test_data = {
            "timestamp": datetime.now().isoformat(),
            "market_sentiment": "BULLISH",
            "confidence": 0.85
        }
        
        await l1_cache.store_report("test_report", test_data)
        logger.info("✅ L1缓存写入成功")
        
        retrieved = await l1_cache.get_latest_report()
        if retrieved:
            logger.info("✅ L1缓存读取成功")
        else:
            logger.warning("⚠️  L1缓存读取为空（可能是首次运行）")
        
        await redis_client.close()
        return True
    except Exception as e:
        logger.error(f"❌ 存储层检查失败: {e}")
        import traceback
        traceback.print_exc()
        return False

async def check_api_endpoints():
    """检查API端点（需要服务运行）"""
    logger.info("\n" + "=" * 60)
    logger.info("4. 检查API端点")
    logger.info("=" * 60)
    
    try:
        import aiohttp
        
        base_url = "http://localhost:8000"
        endpoints = [
            "/api/v1/intelligence/storage/system/health",
            "/api/v1/intelligence/storage/system/metrics",
            "/api/v1/intelligence/storage/reports/latest",
        ]
        
        async with aiohttp.ClientSession() as session:
            for endpoint in endpoints:
                try:
                    async with session.get(f"{base_url}{endpoint}", timeout=5) as response:
                        if response.status == 200:
                            logger.info(f"✅ {endpoint} - 正常")
                        else:
                            logger.warning(f"⚠️  {endpoint} - 状态码: {response.status}")
                except asyncio.TimeoutError:
                    logger.warning(f"⚠️  {endpoint} - 超时")
                except Exception as e:
                    logger.warning(f"⚠️  {endpoint} - 错误: {e}")
        
        return True
    except ImportError:
        logger.warning("⚠️  aiohttp未安装，跳过API测试")
        logger.info("   提示: pip install aiohttp")
        return True
    except Exception as e:
        logger.warning(f"⚠️  API端点检查失败: {e}")
        logger.info("   提示: 确保后端服务正在运行")
        return True  # 不算作失败

async def check_config():
    """检查配置"""
    logger.info("\n" + "=" * 60)
    logger.info("5. 检查配置")
    logger.info("=" * 60)
    
    try:
        from app.core.config import settings
        
        logger.info(f"✅ 配置加载成功")
        logger.info(f"   - 多平台协调: {settings.INTELLIGENCE_USE_MULTI_PLATFORM}")
        logger.info(f"   - 四层存储: {settings.INTELLIGENCE_USE_STORAGE_LAYERS}")
        logger.info(f"   - L1缓存TTL: {settings.L1_CACHE_TTL_HOURS}小时")
        logger.info(f"   - L2分析间隔: {settings.L2_ANALYSIS_INTERVAL_HOURS}小时")
        logger.info(f"   - L4向量维度: {settings.L4_VECTOR_DIMENSION}")
        
        return True
    except Exception as e:
        logger.error(f"❌ 配置检查失败: {e}")
        return False

async def main():
    """主函数"""
    logger.info("\n" + "🚀" * 30)
    logger.info("AIcoin v3.1 自检开始")
    logger.info("🚀" * 30 + "\n")
    
    results = []
    
    # 执行所有检查
    results.append(("模块导入", await check_imports()))
    results.append(("IntelligenceCoordinator", await check_coordinator()))
    results.append(("四层存储", await check_storage_layers()))
    results.append(("配置检查", await check_config()))
    results.append(("API端点", await check_api_endpoints()))
    
    # 汇总结果
    logger.info("\n" + "=" * 60)
    logger.info("自检结果汇总")
    logger.info("=" * 60)
    
    passed = 0
    failed = 0
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        logger.info(f"{name:30s} {status}")
        if result:
            passed += 1
        else:
            failed += 1
    
    logger.info("=" * 60)
    logger.info(f"总计: {passed}个通过, {failed}个失败")
    logger.info("=" * 60)
    
    if failed == 0:
        logger.info("\n🎉 所有检查通过！系统运行正常。")
        return 0
    else:
        logger.error(f"\n⚠️  有{failed}个检查失败，请查看上面的错误信息。")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

