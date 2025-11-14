"""
初始化辩论系统配置
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.models.debate import DebateConfig


async def init_debate_config():
    """初始化辩论配置"""
    
    # 创建异步引擎
    engine = create_async_engine(
        settings.DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://'),
        echo=True
    )
    
    # 创建会话工厂
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    # 默认配置
    default_configs = [
        {
            "config_key": "debate_enabled",
            "config_value": "true",
            "description": "是否启用辩论机制"
        },
        {
            "config_key": "max_debate_rounds",
            "config_value": "1",
            "description": "最大辩论轮次（1-3）"
        },
        {
            "config_key": "min_position_size",
            "config_value": "1000",
            "description": "触发辩论的最小仓位金额（USD）"
        },
        {
            "config_key": "min_permission_level",
            "config_value": "L3",
            "description": "触发辩论的最低权限等级"
        },
        {
            "config_key": "debate_timeout_seconds",
            "config_value": "60",
            "description": "辩论超时时间（秒）"
        },
        {
            "config_key": "use_memory",
            "config_value": "true",
            "description": "是否使用历史记忆"
        },
        {
            "config_key": "daily_limit",
            "config_value": "100",
            "description": "每日最大辩论次数"
        },
        {
            "config_key": "hourly_limit",
            "config_value": "10",
            "description": "每小时最大辩论次数"
        }
    ]
    
    async with async_session() as session:
        try:
            # 检查是否已存在配置
            from sqlalchemy import select
            result = await session.execute(select(DebateConfig))
            existing = result.scalars().all()
            
            if existing:
                print(f"✅ 辩论配置已存在，共 {len(existing)} 条")
                for config in existing:
                    print(f"   - {config.config_key}: {config.config_value}")
                return
            
            # 插入默认配置
            for config_data in default_configs:
                config = DebateConfig(**config_data)
                session.add(config)
            
            await session.commit()
            print(f"✅ 成功初始化 {len(default_configs)} 条辩论配置")
            
            for config_data in default_configs:
                print(f"   - {config_data['config_key']}: {config_data['config_value']}")
                
        except Exception as e:
            print(f"❌ 初始化失败: {e}")
            await session.rollback()
            raise
        finally:
            await engine.dispose()


if __name__ == "__main__":
    print("🚀 开始初始化辩论系统配置...")
    asyncio.run(init_debate_config())
    print("✅ 初始化完成！")

