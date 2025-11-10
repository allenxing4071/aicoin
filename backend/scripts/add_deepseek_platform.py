"""添加 DeepSeek 平台到 intelligence_platforms 表"""

import asyncio
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.models.intelligence_platform import IntelligencePlatform
from app.core.config import settings


async def add_deepseek_platform():
    """添加 DeepSeek 平台"""
    async with AsyncSessionLocal() as db:
        try:
            # 检查是否已存在
            result = await db.execute(
                select(IntelligencePlatform).where(
                    IntelligencePlatform.provider == "deepseek"
                )
            )
            existing = result.scalar_one_or_none()
            
            if existing:
                print(f"✅ DeepSeek 平台已存在: {existing.name}")
                return
            
            # 创建 DeepSeek 平台记录
            deepseek_platform = IntelligencePlatform(
                name="DeepSeek Chat",
                provider="deepseek",
                platform_type="decision",  # 决策模型
                api_key="***",  # 不存储实际密钥
                base_url="https://api.deepseek.com",
                enabled=True,
                total_calls=0,
                successful_calls=0,
                failed_calls=0,
                total_cost=0.0
            )
            
            db.add(deepseek_platform)
            await db.commit()
            await db.refresh(deepseek_platform)
            
            print(f"✅ 成功添加 DeepSeek 平台:")
            print(f"   ID: {deepseek_platform.id}")
            print(f"   名称: {deepseek_platform.name}")
            print(f"   提供商: {deepseek_platform.provider}")
            print(f"   类型: {deepseek_platform.platform_type}")
            print(f"   Base URL: {deepseek_platform.base_url}")
            
        except Exception as e:
            print(f"❌ 添加 DeepSeek 平台失败: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    print("=" * 60)
    print("添加 DeepSeek 平台到数据库")
    print("=" * 60)
    asyncio.run(add_deepseek_platform())
    print("=" * 60)
    print("完成！")

