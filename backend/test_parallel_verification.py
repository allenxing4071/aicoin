"""测试云平台并行调用和交叉验证功能"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent))

from app.services.intelligence.cloud_platform_coordinator import CloudPlatformCoordinator
from app.core.config import settings


async def test_parallel_verification():
    """测试并行验证功能"""
    print("=" * 60)
    print("🧪 云平台并行调用与交叉验证测试")
    print("=" * 60)
    
    # 检查配置
    print("\n📋 配置检查:")
    print(f"  百度智能云: {'✓ 已配置' if settings.BAIDU_QWEN_API_KEY and settings.ENABLE_BAIDU_QWEN else '✗ 未配置'}")
    print(f"  腾讯云:     {'✓ 已配置' if settings.TENCENT_QWEN_API_KEY and settings.ENABLE_TENCENT_QWEN else '✗ 未配置'}")
    print(f"  火山引擎:   {'✓ 已配置' if settings.VOLCANO_QWEN_API_KEY and settings.ENABLE_VOLCANO_QWEN else '✗ 未配置'}")
    print(f"  AWS:        {'✓ 已配置' if settings.AWS_QWEN_API_KEY and settings.ENABLE_AWS_QWEN else '✗ 未配置'}")
    
    # 初始化协调器
    print("\n🔧 初始化云平台协调器...")
    coordinator = CloudPlatformCoordinator()
    
    if len(coordinator.platforms) < 2:
        print(f"\n⚠️  警告: 只有 {len(coordinator.platforms)} 个平台可用，建议至少配置2个以上进行交叉验证")
        print("   请在 backend/.env 中配置相应的API密钥")
        return
    
    print(f"✓ 协调器初始化成功，已加载 {len(coordinator.platforms)} 个平台")
    
    # 准备测试数据
    test_data_sources = {
        "query": "比特币最新市场动态和价格走势",
        "symbol": "BTC/USDT",
        "current_price": 45000,
        "market_context": {
            "24h_change": "+3.5%",
            "volume": "high",
            "trend": "bullish"
        }
    }
    
    test_query_context = {
        "urgency": "high",
        "focus": "market_sentiment"
    }
    
    # 执行并行搜索和验证
    print("\n🚀 开始并行调用云平台...")
    print(f"  查询主题: {test_data_sources['query']}")
    print(f"  交易对: {test_data_sources['symbol']}")
    
    try:
        result = await coordinator.parallel_search_and_verify(
            data_sources=test_data_sources,
            query_context=test_query_context
        )
        
        # 显示结果
        print("\n" + "=" * 60)
        print("📊 验证结果:")
        print("=" * 60)
        
        print(f"\n✅ 综合置信度: {result['confidence']:.2%}")
        
        metadata = result.get("verification_metadata", {})
        print(f"\n📈 验证统计:")
        print(f"  调用平台数: {metadata.get('total_platforms_called', 0)}")
        print(f"  成功平台数: {metadata.get('successful_platforms', 0)}")
        print(f"  平台共识度: {metadata.get('platform_consensus', 0):.1%}")
        print(f"  处理时间: {metadata.get('processing_time_seconds', 0):.2f}秒")
        
        print(f"\n🔍 情报分类:")
        print(f"  高置信度情报: {metadata.get('high_confidence_items', 0)} 条")
        print(f"  中置信度情报: {metadata.get('medium_confidence_items', 0)} 条")
        print(f"  低置信度情报: {metadata.get('low_confidence_items', 0)} 条")
        
        print(f"\n📝 关键发现:")
        for i, finding in enumerate(result.get("key_findings", [])[:5], 1):
            consensus = finding.get("consensus_platforms", 0)
            total = finding.get("total_platforms", 0)
            print(f"\n  {i}. {finding.get('content', 'N/A')}")
            if consensus and total:
                print(f"     [共识: {consensus}/{total} 个平台]")
        
        if result.get("risk_warnings"):
            print(f"\n⚠️  风险警告:")
            for i, warning in enumerate(result["risk_warnings"][:3], 1):
                print(f"  {i}. {warning}")
        
        print(f"\n💬 综合摘要:")
        print(result.get("intelligence_summary", "无摘要"))
        
        print(f"\n🌐 平台详情:")
        for platform_info in result.get("platform_details", []):
            status = "✓" if platform_info["success"] else "✗"
            print(f"  {status} {platform_info['platform']}: "
                  f"{platform_info['key_findings_count']} 个发现, "
                  f"置信度 {platform_info['confidence']:.2%}")
        
        print("\n" + "=" * 60)
        print("✅ 测试完成！")
        print("=" * 60)
        
        # 测试结论
        if result["confidence"] > 0.7:
            print("\n🎉 结论: 并行验证工作正常，置信度高")
        elif result["confidence"] > 0.5:
            print("\n⚠️  结论: 并行验证基本正常，但建议增加更多平台")
        else:
            print("\n❌ 结论: 置信度较低，建议检查平台配置和API密钥")
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    print("\n🔧 启动测试...")
    asyncio.run(test_parallel_verification())

