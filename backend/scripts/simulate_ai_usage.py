"""
模拟AI平台使用，生成测试数据
用于演示成本追踪功能
"""
import asyncio
import sys
from pathlib import Path
import random
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal
from app.models.intelligence_platform import IntelligencePlatform
from sqlalchemy import select


async def simulate_platform_usage():
    """模拟平台使用，生成测试数据"""
    
    async with AsyncSessionLocal() as db:
        # 获取所有平台
        result = await db.execute(select(IntelligencePlatform))
        platforms = result.scalars().all()
        
        print(f"\n📊 开始模拟 {len(platforms)} 个AI平台的使用数据...\n")
        
        for platform in platforms:
            # 根据平台类型生成不同的使用数据
            if platform.provider == 'deepseek':
                # DeepSeek - 交易决策，调用频繁
                calls = random.randint(50, 100)
                success_rate = random.uniform(0.92, 0.98)
                avg_response_time = random.uniform(800, 1500)
                # DeepSeek定价: 输入¥1/M, 输出¥2/M
                avg_input_tokens = random.randint(1000, 2000)
                avg_output_tokens = random.randint(500, 1000)
                cost_per_call = (avg_input_tokens / 1_000_000 * 1.0) + (avg_output_tokens / 1_000_000 * 2.0)
                
            else:
                # Qwen系列 - 情报收集，调用相对少
                calls = random.randint(20, 50)
                success_rate = random.uniform(0.88, 0.95)
                avg_response_time = random.uniform(1000, 2000)
                # Qwen定价: 输入¥4/M, 输出¥12/M
                avg_input_tokens = random.randint(1500, 3000)
                avg_output_tokens = random.randint(800, 1500)
                cost_per_call = (avg_input_tokens / 1_000_000 * 4.0) + (avg_output_tokens / 1_000_000 * 12.0)
            
            # 更新统计数据
            successful_calls = int(calls * success_rate)
            failed_calls = calls - successful_calls
            total_cost = calls * cost_per_call
            
            # 更新数据库字段
            platform.total_calls = calls
            platform.successful_calls = successful_calls
            platform.failed_calls = failed_calls
            platform.total_cost = round(total_cost, 4)
            platform.avg_response_time = round(avg_response_time, 2)
            platform.last_health_check = datetime.utcnow()
            platform.health_status = 'healthy' if success_rate > 0.9 else 'degraded'
            platform.updated_at = datetime.utcnow()
            
            print(f"✅ {platform.name:25} | 调用: {calls:3} | 成功率: {success_rate*100:5.1f}% | 成本: ¥{total_cost:8.4f} | 响应: {avg_response_time:6.0f}ms")
        
        # 提交更改
        await db.commit()
        
        print(f"\n🎉 模拟数据生成完成！\n")
        
        # 显示汇总
        total_calls = sum(p.total_calls for p in platforms)
        total_cost = sum(p.total_cost for p in platforms)
        avg_success_rate = sum(p.successful_calls for p in platforms) / total_calls if total_calls > 0 else 0
        
        print("=" * 80)
        print(f"📈 汇总统计:")
        print(f"   总调用次数: {total_calls}")
        print(f"   总成本: ¥{total_cost:.4f}")
        print(f"   平均成功率: {avg_success_rate*100:.2f}%")
        print(f"   启用平台数: {len([p for p in platforms if p.enabled])}")
        print("=" * 80)


async def reset_platform_stats():
    """重置平台统计数据为0"""
    
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(IntelligencePlatform))
        platforms = result.scalars().all()
        
        print(f"\n🔄 重置 {len(platforms)} 个平台的统计数据...\n")
        
        for platform in platforms:
            platform.total_calls = 0
            platform.successful_calls = 0
            platform.failed_calls = 0
            platform.total_cost = 0.0
            platform.avg_response_time = None
            platform.last_health_check = None
            platform.health_status = None
            
            print(f"✅ {platform.name} 已重置")
        
        await db.commit()
        print(f"\n🎉 重置完成！\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='模拟AI平台使用数据')
    parser.add_argument('--reset', action='store_true', help='重置统计数据为0')
    args = parser.parse_args()
    
    if args.reset:
        asyncio.run(reset_platform_stats())
    else:
        asyncio.run(simulate_platform_usage())

