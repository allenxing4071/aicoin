#!/usr/bin/env python3
"""创建管理员用户脚本"""

import asyncio
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.models.admin_user import AdminUser
from app.core.security import get_password_hash
from app.core.config import settings


async def create_admin_user():
    """创建管理员用户"""
    
    # 创建数据库引擎
    engine = create_async_engine(
        settings.DATABASE_URL.replace('postgresql+asyncpg://', 'postgresql+asyncpg://'),
        echo=True
    )
    
    # 创建会话
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        try:
            # 创建表（如果不存在）
            from app.models.base import Base
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)
            
            print("✅ 数据库表创建成功")
            
            # 检查是否已存在admin用户
            from sqlalchemy import select
            result = await session.execute(
                select(AdminUser).where(AdminUser.username == 'admin')
            )
            existing_admin = result.scalar_one_or_none()
            
            if existing_admin:
                print("⚠️  管理员用户已存在")
                print(f"   用户名: {existing_admin.username}")
                print(f"   邮箱: {existing_admin.email}")
                return
            
            # 创建管理员用户
            admin_user = AdminUser(
                username='admin',
                email='admin@aicoin.com',
                hashed_password=get_password_hash('admin123'),
                is_active=True,
                is_superuser=True
            )
            
            session.add(admin_user)
            await session.commit()
            
            print("✅ 管理员用户创建成功!")
            print(f"   用户名: admin")
            print(f"   密码: admin123")
            print(f"   邮箱: admin@aicoin.com")
            
        except Exception as e:
            print(f"❌ 创建管理员用户失败: {e}")
            import traceback
            traceback.print_exc()
            await session.rollback()
        finally:
            await engine.dispose()


if __name__ == '__main__':
    asyncio.run(create_admin_user())

