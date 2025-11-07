"""更新数据库表注释脚本"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from app.core.database import AsyncSessionLocal


async def update_table_comments():
    """更新所有表的注释"""
    
    # 表注释映射
    comments = [
        ('intelligence_platforms', '☁️ 情报平台配置 - 管理AI云平台（Qwen、腾讯混元、火山引擎等）的连接配置和性能指标'),
        ('intelligence_source_weights', '⚖️ 情报源权重 - 记录各情报源（RSS、API等）的权重和有效性评分，用于智能筛选'),
        ('intelligence_feedback', '💬 情报反馈 - 记录用户对情报的反馈和使用效果，用于优化情报质量'),
        ('intelligence_reports', '📊 情报报告 - Qwen情报官收集的市场情报和分析报告，包含新闻、巨鲸活动、链上数据等'),
        ('exchange_configs', '🏦 交易所配置 - 存储币安等交易所的API密钥和连接配置'),
        ('market_data_kline', '📈 K线数据 - 存储各币种的历史K线图数据（开高低收、成交量等）'),
        ('market_patterns', '📊 市场模式 - AI识别的市场走势模式（趋势反转、突破、盘整等）及其历史表现'),
        ('model_performance_metrics', '📈 模型性能指标 - 记录各AI模型的决策准确率、盈利率、响应时间等性能数据'),
        ('routing_decisions', '🔀 路由决策日志 - 记录AI模型路由策略选择过程和多模型协作决策的详细信息'),
        ('users', '👥 用户表 - 存储系统用户的基本信息和权限配置'),
    ]
    
    print("🔧 开始更新数据库表注释...\n")
    
    async with AsyncSessionLocal() as db:
        for table_name, comment in comments:
            try:
                # 转义单引号
                escaped_comment = comment.replace("'", "''")
                sql = text(f"COMMENT ON TABLE {table_name} IS '{escaped_comment}'")
                await db.execute(sql)
                print(f"✅ 已更新表 {table_name}")
                print(f"   注释: {comment}\n")
            except Exception as e:
                print(f"❌ 更新表 {table_name} 失败: {e}\n")
        
        await db.commit()
    
    print("✅ 所有表注释更新完成！")


if __name__ == "__main__":
    asyncio.run(update_table_comments())

