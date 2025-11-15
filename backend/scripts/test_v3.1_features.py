#!/usr/bin/env python3
"""
v3.1 功能完整测试脚本
测试所有新功能和优化
"""

import asyncio
import sys
import logging
import json
from datetime import datetime
import aiohttp

# 设置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 测试配置
BASE_URL = "http://localhost:8000"
TEST_RESULTS = []

class TestResult:
    def __init__(self, name, passed, message=""):
        self.name = name
        self.passed = passed
        self.message = message
        self.timestamp = datetime.now()

async def test_intelligence_coordinator():
    """测试IntelligenceCoordinator"""
    logger.info("=" * 60)
    logger.info("测试1: IntelligenceCoordinator集成")
    logger.info("=" * 60)
    
    try:
        from app.core.redis_client import RedisClient
        from app.services.intelligence.intelligence_coordinator import IntelligenceCoordinator
        
        redis_client = RedisClient()
        await redis_client.connect()
        
        coordinator = IntelligenceCoordinator(redis_client, None)
        
        # 检查配置
        assert coordinator.use_multi_platform is not None
        assert coordinator.use_storage_layers is not None
        assert coordinator.l1_cache is not None
        
        logger.info("✅ IntelligenceCoordinator初始化成功")
        TEST_RESULTS.append(TestResult("IntelligenceCoordinator", True))
        return True
        
    except Exception as e:
        logger.error(f"❌ IntelligenceCoordinator测试失败: {e}")
        TEST_RESULTS.append(TestResult("IntelligenceCoordinator", False, str(e)))
        return False

async def test_storage_layers():
    """测试四层存储"""
    logger.info("\n" + "=" * 60)
    logger.info("测试2: 四层存储架构")
    logger.info("=" * 60)
    
    try:
        from app.core.redis_client import RedisClient
        from app.services.intelligence.storage_layers import (
            ShortTermIntelligenceCache,
            MidTermIntelligenceAnalyzer,
            LongTermIntelligenceStore,
            IntelligenceVectorKB
        )
        
        redis_client = RedisClient()
        await redis_client.connect()
        
        # L1测试
        l1 = ShortTermIntelligenceCache(redis_client)
        test_data = {
            "timestamp": datetime.now().isoformat(),
            "market_sentiment": "BULLISH",
            "confidence": 0.85
        }
        await l1.store_report("test_v31", test_data)
        logger.info("✅ L1缓存写入成功")
        
        # L4测试（检查是否已初始化）
        l4 = IntelligenceVectorKB(redis_client, None)
        logger.info("✅ L4向量库初始化成功")
        
        TEST_RESULTS.append(TestResult("四层存储", True))
        return True
        
    except Exception as e:
        logger.error(f"❌ 四层存储测试失败: {e}")
        TEST_RESULTS.append(TestResult("四层存储", False, str(e)))
        return False

async def test_api_endpoints():
    """测试API端点"""
    logger.info("\n" + "=" * 60)
    logger.info("测试3: API端点")
    logger.info("=" * 60)
    
    endpoints = [
        ("健康检查", f"{BASE_URL}/api/v1/intelligence/storage/system/health"),
        ("性能指标", f"{BASE_URL}/api/v1/intelligence/storage/system/metrics"),
        ("系统摘要", f"{BASE_URL}/api/v1/intelligence/storage/system/summary"),
        ("最新报告", f"{BASE_URL}/api/v1/intelligence/storage/reports/latest"),
    ]
    
    passed = 0
    failed = 0
    
    async with aiohttp.ClientSession() as session:
        for name, url in endpoints:
            try:
                async with session.get(url, timeout=5) as response:
                    if response.status == 200:
                        data = await response.json()
                        logger.info(f"✅ {name}: 正常 (HTTP 200)")
                        passed += 1
                    elif response.status == 404:
                        logger.warning(f"⚠️  {name}: 未找到 (HTTP 404)")
                        failed += 1
                    else:
                        logger.warning(f"⚠️  {name}: 异常 (HTTP {response.status})")
                        failed += 1
            except asyncio.TimeoutError:
                logger.error(f"❌ {name}: 超时")
                failed += 1
            except Exception as e:
                logger.error(f"❌ {name}: 错误 - {e}")
                failed += 1
    
    success = passed > failed
    TEST_RESULTS.append(TestResult("API端点", success, f"{passed}/{len(endpoints)}通过"))
    return success

async def test_debate_system():
    """测试辩论系统"""
    logger.info("\n" + "=" * 60)
    logger.info("测试4: 辩论系统")
    logger.info("=" * 60)
    
    try:
        from app.services.decision.debate_system import (
            BullAnalyst,
            BearAnalyst,
            ResearchManager,
            format_intelligence_with_verification
        )
        
        # 测试公共格式化函数
        test_report = {
            "market_sentiment": "BULLISH",
            "confidence": 0.85,
            "platform_contributions": {
                "qwen": {"weight": 0.5},
                "deepseek": {"weight": 0.3}
            },
            "platform_consensus": 0.8
        }
        
        formatted = format_intelligence_with_verification(test_report)
        assert "Multi-Platform Verified" in formatted
        assert "Platform Consensus" in formatted
        
        logger.info("✅ 辩论系统格式化函数正常")
        TEST_RESULTS.append(TestResult("辩论系统", True))
        return True
        
    except Exception as e:
        logger.error(f"❌ 辩论系统测试失败: {e}")
        TEST_RESULTS.append(TestResult("辩论系统", False, str(e)))
        return False

async def test_multi_platform_coordinator():
    """测试多平台协调器"""
    logger.info("\n" + "=" * 60)
    logger.info("测试5: 多平台协调器")
    logger.info("=" * 60)
    
    try:
        from app.services.intelligence.multi_platform_coordinator import MultiPlatformCoordinator
        from app.core.redis_client import RedisClient
        
        redis_client = RedisClient()
        await redis_client.connect()
        
        coordinator = MultiPlatformCoordinator(redis_client, None)
        
        # 检查是否有平台适配器
        logger.info(f"已加载平台适配器: {len(coordinator.platforms)}个")
        
        TEST_RESULTS.append(TestResult("多平台协调器", True))
        return True
        
    except Exception as e:
        logger.error(f"❌ 多平台协调器测试失败: {e}")
        TEST_RESULTS.append(TestResult("多平台协调器", False, str(e)))
        return False

async def test_decision_engine():
    """测试决策引擎"""
    logger.info("\n" + "=" * 60)
    logger.info("测试6: 决策引擎V2")
    logger.info("=" * 60)
    
    try:
        from app.services.decision.decision_engine_v2 import DecisionEngineV2
        from app.core.redis_client import RedisClient
        
        redis_client = RedisClient()
        await redis_client.connect()
        
        engine = DecisionEngineV2(redis_client, None)
        
        # 检查是否集成了辩论系统（使用debate_coordinator）
        assert engine.debate_coordinator is not None
        
        logger.info("✅ 决策引擎V2初始化成功")
        TEST_RESULTS.append(TestResult("决策引擎V2", True))
        return True
        
    except Exception as e:
        logger.error(f"❌ 决策引擎测试失败: {e}")
        TEST_RESULTS.append(TestResult("决策引擎V2", False, str(e)))
        return False

async def test_manual_intelligence_collection():
    """测试手动触发情报收集"""
    logger.info("\n" + "=" * 60)
    logger.info("测试7: 手动触发情报收集")
    logger.info("=" * 60)
    
    try:
        async with aiohttp.ClientSession() as session:
            url = f"{BASE_URL}/api/v1/intelligence/refresh"
            logger.info(f"发送POST请求: {url}")
            
            async with session.post(url, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info(f"✅ 情报收集成功")
                    logger.info(f"   消息: {data.get('message', 'N/A')}")
                    TEST_RESULTS.append(TestResult("手动情报收集", True))
                    return True
                else:
                    logger.warning(f"⚠️  情报收集返回HTTP {response.status}")
                    TEST_RESULTS.append(TestResult("手动情报收集", False, f"HTTP {response.status}"))
                    return False
                    
    except Exception as e:
        logger.error(f"❌ 手动情报收集失败: {e}")
        TEST_RESULTS.append(TestResult("手动情报收集", False, str(e)))
        return False

async def main():
    """主测试流程"""
    logger.info("\n" + "🧪" * 30)
    logger.info("AIcoin v3.1 功能完整测试")
    logger.info("🧪" * 30 + "\n")
    
    # 执行所有测试
    await test_intelligence_coordinator()
    await test_storage_layers()
    await test_debate_system()
    await test_multi_platform_coordinator()
    await test_decision_engine()
    await test_api_endpoints()
    await test_manual_intelligence_collection()
    
    # 汇总结果
    logger.info("\n" + "=" * 60)
    logger.info("测试结果汇总")
    logger.info("=" * 60)
    
    passed = sum(1 for r in TEST_RESULTS if r.passed)
    failed = len(TEST_RESULTS) - passed
    
    for result in TEST_RESULTS:
        status = "✅ 通过" if result.passed else "❌ 失败"
        message = f" ({result.message})" if result.message else ""
        logger.info(f"{result.name:30s} {status}{message}")
    
    logger.info("=" * 60)
    logger.info(f"总计: {passed}个通过, {failed}个失败")
    logger.info("=" * 60)
    
    if failed == 0:
        logger.info("\n🎉 所有测试通过！v3.1功能正常。")
        return 0
    else:
        logger.error(f"\n⚠️  有{failed}个测试失败，请查看上面的错误信息。")
        return 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

