"""
初始化AI平台配置

添加以下平台：
1. Qwen-Plus (通义千问) - 情报模型
2. 腾讯云 (Qwen搜索) - 情报模型
3. 火山引擎 (Qwen搜索) - 情报模型
4. 百度智能云 (Qwen搜索) - 情报模型
5. DeepSeek Chat - 决策模型
"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import text
from app.core.database import get_db

async def init_platforms():
    """初始化AI平台配置"""
    
    platforms = [
        {
            "name": "Qwen-Plus",
            "provider": "qwen",
            "platform_type": "intelligence",
            "base_url": "https://dashscope.aliyuncs.com/compatible-mode/v1",
            "enabled": True,
            "config_json": {
                "model_name": "qwen-plus",
                "input_price_per_million": 1.0,
                "output_price_per_million": 1.5,
                "description": "阿里云通义千问Plus模型，用于情报收集和分析"
            }
        },
        {
            "name": "腾讯云 (Qwen搜索)",
            "provider": "tencent",
            "platform_type": "intelligence",
            "base_url": "https://api.hunyuan.cloud.tencent.com/v1",
            "enabled": True,
            "config_json": {
                "model_name": "hunyuan-lite",
                "input_price_per_million": 1.0,
                "output_price_per_million": 1.5,
                "description": "腾讯混元模型，用于情报收集和分析"
            }
        },
        {
            "name": "火山引擎 (Qwen搜索)",
            "provider": "volcano",
            "platform_type": "intelligence",
            "base_url": "https://ark.cn-beijing.volces.com/api/v3",
            "enabled": True,
            "config_json": {
                "model_name": "doubao-lite-4k",
                "input_price_per_million": 1.0,
                "output_price_per_million": 1.5,
                "description": "火山引擎豆包模型，用于情报收集和分析"
            }
        },
        {
            "name": "百度智能云 (Qwen搜索)",
            "provider": "baidu",
            "platform_type": "intelligence",
            "base_url": "https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop",
            "enabled": True,
            "config_json": {
                "model_name": "ernie-lite-8k",
                "input_price_per_million": 1.0,
                "output_price_per_million": 1.5,
                "description": "百度文心一言模型，用于情报收集和分析"
            }
        },
        {
            "name": "DeepSeek Chat",
            "provider": "deepseek",
            "platform_type": "decision",
            "base_url": "https://api.deepseek.com/v1",
            "enabled": True,
            "config_json": {
                "model_name": "deepseek-chat",
                "input_price_per_million": 1.0,
                "output_price_per_million": 1.5,
                "description": "DeepSeek模型，用于交易决策"
            }
        }
    ]
    
    async for db in get_db():
        try:
            # 检查表是否存在
            result = await db.execute(text("""
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_name = 'intelligence_platforms'
                )
            """))
            table_exists = result.scalar()
            
            if not table_exists:
                print("❌ intelligence_platforms 表不存在，请先运行数据库迁移")
                return
            
            # 清空现有数据（可选）
            print("🗑️  清空现有平台数据...")
            await db.execute(text("DELETE FROM intelligence_platforms"))
            await db.commit()
            
            # 插入新数据
            print("\n📝 插入AI平台配置...")
            for platform in platforms:
                import json
                await db.execute(text("""
                    INSERT INTO intelligence_platforms (
                        name, provider, platform_type, base_url,
                        enabled, config_json, total_calls, successful_calls, failed_calls,
                        total_cost, created_at, updated_at
                    ) VALUES (
                        :name, :provider, :platform_type, :base_url,
                        :enabled, :config_json, 0, 0, 0, 0, NOW(), NOW()
                    )
                """), {
                    "name": platform["name"],
                    "provider": platform["provider"],
                    "platform_type": platform["platform_type"],
                    "base_url": platform["base_url"],
                    "enabled": platform["enabled"],
                    "config_json": json.dumps(platform["config_json"])
                })
                print(f"  ✅ {platform['name']} ({platform['platform_type']})")
            
            await db.commit()
            
            # 验证插入结果
            result = await db.execute(text("SELECT COUNT(*) FROM intelligence_platforms"))
            count = result.scalar()
            
            print(f"\n✅ 成功初始化 {count} 个AI平台配置")
            
            # 显示详细信息
            result = await db.execute(text("""
                SELECT name, provider, platform_type, enabled 
                FROM intelligence_platforms 
                ORDER BY platform_type, provider
            """))
            rows = result.fetchall()
            
            print("\n📊 当前平台列表：")
            print("-" * 80)
            print(f"{'平台名称':<30} {'提供商':<15} {'类型':<15} {'状态':<10}")
            print("-" * 80)
            for row in rows:
                status = "✓ 已启用" if row[3] else "✗ 已禁用"
                print(f"{row[0]:<30} {row[1]:<15} {row[2]:<15} {status:<10}")
            print("-" * 80)
            
        except Exception as e:
            print(f"❌ 错误: {e}")
            await db.rollback()
            raise

if __name__ == "__main__":
    print("=" * 80)
    print("🚀 初始化AI平台配置")
    print("=" * 80)
    asyncio.run(init_platforms())
    print("\n✅ 初始化完成！")
    print("\n💡 提示：")
    print("   1. 访问 http://localhost:3000/admin/ai-platforms/intelligence 查看情报模型")
    print("   2. 访问 http://localhost:3000/admin/ai-platforms/decision 查看决策模型")
    print("=" * 80)

