"""
测试AI使用日志记录功能
验证真实调用数据的记录和统计
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal
from app.services.ai_usage_logger import log_ai_call
from app.models.ai_model_pricing import AIModelUsageLog
from app.models.intelligence_platform import IntelligencePlatform
from sqlalchemy import select, func
from datetime import datetime, timedelta


async def test_log_ai_call():
    """测试记录AI调用"""
    print("\n" + "="*80)
    print("📝 测试AI调用日志记录功能")
    print("="*80)
    
    async with AsyncSessionLocal() as db:
        # 1. 记录几条测试日志
        print("\n1️⃣ 记录测试调用日志...")
        
        test_calls = [
            {
                "model_name": "deepseek-chat",
                "input_tokens": 1000,
                "output_tokens": 500,
                "cost": 0.002,
                "platform_id": 1,
                "success": True,
                "response_time": 1.5,
                "purpose": "decision",
                "symbol": "BTCUSDT"
            },
            {
                "model_name": "qwen-plus",
                "input_tokens": 2000,
                "output_tokens": 800,
                "cost": 0.018,
                "platform_id": 2,
                "success": True,
                "response_time": 2.3,
                "purpose": "intelligence"
            },
            {
                "model_name": "deepseek-chat",
                "input_tokens": 800,
                "output_tokens": 0,
                "cost": 0.0,
                "platform_id": 1,
                "success": False,
                "error_message": "Request timeout",
                "response_time": 30.0,
                "purpose": "decision"
            }
        ]
        
        for call_data in test_calls:
            await log_ai_call(db=db, **call_data)
            status = "✅ 成功" if call_data["success"] else "❌ 失败"
            print(f"   {status} | {call_data['model_name']} | Cost: ¥{call_data['cost']:.4f}")
        
        # 2. 查询日志记录
        print("\n2️⃣ 查询记录的日志...")
        result = await db.execute(
            select(AIModelUsageLog)
            .order_by(AIModelUsageLog.created_at.desc())
            .limit(5)
        )
        logs = result.scalars().all()
        
        print(f"\n   最近5条日志记录:")
        for log in logs:
            status = "✅" if log.success else "❌"
            print(f"   {status} {log.model_name} | "
                  f"Tokens: {log.input_tokens}→{log.output_tokens} | "
                  f"Cost: ¥{log.cost:.4f} | "
                  f"Time: {log.response_time:.2f}s")
        
        # 3. 查询平台统计
        print("\n3️⃣ 查询平台统计...")
        result = await db.execute(select(IntelligencePlatform))
        platforms = result.scalars().all()
        
        for platform in platforms:
            if platform.total_calls > 0:
                success_rate = platform.successful_calls / platform.total_calls * 100
                print(f"\n   📊 {platform.name} ({platform.provider}):")
                print(f"      总调用: {platform.total_calls}")
                print(f"      成功: {platform.successful_calls}")
                print(f"      失败: {platform.failed_calls}")
                print(f"      成功率: {success_rate:.1f}%")
                print(f"      总成本: ¥{platform.total_cost:.4f}")
                if platform.avg_response_time:
                    print(f"      平均响应: {platform.avg_response_time:.2f}s")
        
        # 4. 按时间统计
        print("\n4️⃣ 按时间统计 (今日)...")
        now = datetime.utcnow()
        today_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
        
        result = await db.execute(
            select(
                func.count(AIModelUsageLog.id).label('total'),
                func.sum(AIModelUsageLog.cost).label('cost'),
                func.avg(AIModelUsageLog.response_time).label('avg_time')
            ).where(AIModelUsageLog.created_at >= today_start)
        )
        stats = result.first()
        
        if stats and stats.total > 0:
            print(f"   总调用: {stats.total}")
            print(f"   总成本: ¥{stats.cost:.4f}")
            print(f"   平均响应: {stats.avg_time:.2f}s")
        else:
            print("   今日暂无调用记录")
        
        print("\n" + "="*80)
        print("✅ 测试完成！")
        print("="*80 + "\n")


async def test_stats_api_data():
    """测试统计API能否正确读取数据"""
    print("\n" + "="*80)
    print("📊 测试统计API数据读取")
    print("="*80)
    
    async with AsyncSessionLocal() as db:
        # 模拟API查询逻辑
        now = datetime.utcnow()
        start_time = now - timedelta(days=7)  # 最近7天
        
        # 查询DeepSeek数据
        result = await db.execute(
            select(
                func.count(AIModelUsageLog.id).label('count'),
                func.sum(AIModelUsageLog.cost).label('total_cost'),
                func.avg(AIModelUsageLog.response_time).label('avg_time')
            ).where(
                AIModelUsageLog.created_at >= start_time,
                func.lower(AIModelUsageLog.model_name).like('%deepseek%')
            )
        )
        data = result.first()
        
        print("\n📈 DeepSeek 平台统计 (最近7天):")
        if data and data.count > 0:
            print(f"   调用次数: {data.count}")
            print(f"   总成本: ¥{data.total_cost:.4f}")
            print(f"   平均响应: {data.avg_time:.2f}s")
        else:
            print("   暂无数据")
        
        # 查询Qwen数据
        result = await db.execute(
            select(
                func.count(AIModelUsageLog.id).label('count'),
                func.sum(AIModelUsageLog.cost).label('total_cost'),
                func.avg(AIModelUsageLog.response_time).label('avg_time')
            ).where(
                AIModelUsageLog.created_at >= start_time,
                func.lower(AIModelUsageLog.model_name).like('%qwen%')
            )
        )
        data = result.first()
        
        print("\n📈 Qwen 平台统计 (最近7天):")
        if data and data.count > 0:
            print(f"   调用次数: {data.count}")
            print(f"   总成本: ¥{data.total_cost:.4f}")
            print(f"   平均响应: {data.avg_time:.2f}s")
        else:
            print("   暂无数据")
        
        print("\n" + "="*80 + "\n")


async def clear_test_logs():
    """清除测试日志"""
    print("\n⚠️  警告：这将删除所有AI使用日志！")
    confirm = input("确认清除？(yes/no): ")
    
    if confirm.lower() == 'yes':
        from sqlalchemy import delete
        async with AsyncSessionLocal() as db:
            await db.execute(delete(AIModelUsageLog))
            await db.commit()
            print("✅ 已清除所有日志")
    else:
        print("❌ 已取消")


async def main():
    """主函数"""
    import argparse
    
    parser = argparse.ArgumentParser(description='测试AI使用日志记录功能')
    parser.add_argument('--clear', action='store_true', help='清除所有日志')
    parser.add_argument('--stats', action='store_true', help='只查看统计')
    args = parser.parse_args()
    
    if args.clear:
        await clear_test_logs()
    elif args.stats:
        await test_stats_api_data()
    else:
        await test_log_ai_call()
        await test_stats_api_data()


if __name__ == "__main__":
    asyncio.run(main())

