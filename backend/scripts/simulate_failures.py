"""
模拟AI平台失败数据
用于测试失败原因分析和稳定性趋势功能
"""

import asyncio
import random
from datetime import datetime, timedelta
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from app.core.database import AsyncSessionLocal
from app.models.intelligence_platform import IntelligencePlatform
from sqlalchemy import select, text

# 失败原因模板
ERROR_TEMPLATES = {
    "请求超时": [
        "Request timeout after 30 seconds",
        "Connection timeout",
        "Read timeout exceeded",
        "API响应超时"
    ],
    "频率限制": [
        "Rate limit exceeded",
        "Too many requests",
        "API调用频率超限",
        "请求过于频繁，请稍后重试"
    ],
    "认证失败": [
        "Invalid API key",
        "Authentication failed",
        "API密钥无效",
        "认证令牌已过期"
    ],
    "配额不足": [
        "Insufficient quota",
        "Account balance insufficient",
        "配额已用尽",
        "余额不足"
    ],
    "网络错误": [
        "Network connection failed",
        "DNS resolution failed",
        "网络连接中断",
        "无法连接到服务器"
    ],
    "参数错误": [
        "Invalid parameter: temperature",
        "Missing required field: messages",
        "参数格式错误",
        "请求参数不合法"
    ],
    "其他错误": [
        "Internal server error",
        "Service temporarily unavailable",
        "服务暂时不可用",
        "未知错误"
    ]
}


async def simulate_failure_data():
    """生成模拟失败数据"""
    async with AsyncSessionLocal() as db:
        # 获取所有平台
        result = await db.execute(select(IntelligencePlatform))
        platforms = result.scalars().all()
        
        print(f"\n📊 开始为 {len(platforms)} 个平台生成失败数据...\n")
        
        # 生成过去7天的数据
        now = datetime.utcnow()
        
        for platform in platforms:
            model_name = platform.provider or platform.name
            
            # 每个平台生成10-30条失败记录
            num_failures = random.randint(10, 30)
            
            print(f"🔧 {platform.name:30} | 生成 {num_failures} 条失败记录")
            
            for _ in range(num_failures):
                # 随机选择失败类型
                error_category = random.choice(list(ERROR_TEMPLATES.keys()))
                error_message = random.choice(ERROR_TEMPLATES[error_category])
                
                # 随机时间（过去7天）
                days_ago = random.uniform(0, 7)
                timestamp = now - timedelta(days=days_ago)
                
                # 插入失败记录
                await db.execute(text("""
                    INSERT INTO ai_model_usage_log 
                    (model_name, input_tokens, output_tokens, cost, timestamp, success, error_message, purpose)
                    VALUES (:model_name, 0, 0, 0, :timestamp, false, :error_message, 'test')
                """), {
                    "model_name": model_name,
                    "timestamp": timestamp,
                    "error_message": error_message
                })
            
            # 同时生成一些成功记录（用于趋势分析）
            num_success = random.randint(50, 100)
            for _ in range(num_success):
                days_ago = random.uniform(0, 7)
                timestamp = now - timedelta(days=days_ago)
                cost = random.uniform(0.01, 0.05)
                
                await db.execute(text("""
                    INSERT INTO ai_model_usage_log 
                    (model_name, input_tokens, output_tokens, cost, timestamp, success, purpose)
                    VALUES (:model_name, :input_tokens, :output_tokens, :cost, :timestamp, true, 'test')
                """), {
                    "model_name": model_name,
                    "input_tokens": random.randint(100, 1000),
                    "output_tokens": random.randint(50, 500),
                    "cost": cost,
                    "timestamp": timestamp
                })
        
        await db.commit()
        
        print(f"\n✅ 模拟数据生成完成！\n")
        
        # 统计信息
        result = await db.execute(text("""
            SELECT 
                COUNT(*) FILTER (WHERE success = false) as failures,
                COUNT(*) FILTER (WHERE success = true) as successes,
                COUNT(*) as total
            FROM ai_model_usage_log
            WHERE timestamp >= :start_time
        """), {"start_time": now - timedelta(days=7)})
        
        stats = result.fetchone()
        print(f"📈 过去7天统计:")
        print(f"   - 总调用: {stats.total}")
        print(f"   - 成功: {stats.successes}")
        print(f"   - 失败: {stats.failures}")
        print(f"   - 成功率: {(stats.successes / stats.total * 100):.2f}%\n")


async def clear_test_data():
    """清除测试数据"""
    async with AsyncSessionLocal() as db:
        print("\n🗑️  清除测试数据...\n")
        
        result = await db.execute(text("""
            DELETE FROM ai_model_usage_log 
            WHERE purpose = 'test'
        """))
        
        await db.commit()
        
        print(f"✅ 已删除 {result.rowcount} 条测试记录\n")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Simulate AI platform failure data.")
    parser.add_argument("--clear", action="store_true", help="Clear test data instead of generating.")
    args = parser.parse_args()
    
    if args.clear:
        asyncio.run(clear_test_data())
    else:
        asyncio.run(simulate_failure_data())

