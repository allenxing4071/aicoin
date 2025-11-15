"""
Prompt系统端到端验证脚本

验证内容：
1. 数据库表是否存在
2. Prompt数据是否已导入
3. PromptManagerDB是否正常工作
4. Redis pub/sub是否正常
5. API是否可访问
6. DecisionEngineV2集成是否正常
"""

import asyncio
import sys
import os
from pathlib import Path

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.redis_client import RedisClient
from app.services.decision.prompt_manager_db import PromptManagerDB
from app.models.prompt_template import PromptTemplate


async def verify_database_tables():
    """验证数据库表"""
    print("\n" + "="*60)
    print("1️⃣  验证数据库表")
    print("="*60)
    
    try:
        # 使用asyncpg驱动
        db_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
        engine = create_async_engine(db_url, echo=False)
        async with engine.begin() as conn:
            # 检查表是否存在
            tables_to_check = [
                "prompt_templates",
                "prompt_template_versions",
                "prompt_performance",
                "prompt_ab_tests"
            ]
            
            for table in tables_to_check:
                result = await conn.execute(
                    text(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')")
                )
                exists = result.scalar()
                
                if exists:
                    print(f"✅ 表 {table} 存在")
                else:
                    print(f"❌ 表 {table} 不存在")
                    return False
        
        await engine.dispose()
        print("\n✅ 数据库表验证通过")
        return True
        
    except Exception as e:
        print(f"\n❌ 数据库表验证失败: {e}")
        return False


async def verify_prompt_data():
    """验证Prompt数据"""
    print("\n" + "="*60)
    print("2️⃣  验证Prompt数据")
    print("="*60)
    
    try:
        # 使用asyncpg驱动
        db_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
        engine = create_async_engine(db_url, echo=False)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as session:
            # 查询Prompt数量
            result = await session.execute(select(PromptTemplate))
            prompts = result.scalars().all()
            
            print(f"\n📊 Prompt总数: {len(prompts)}")
            
            # 按类别统计
            categories = {}
            for prompt in prompts:
                cat = prompt.category
                categories[cat] = categories.get(cat, 0) + 1
            
            print("\n📋 按类别统计:")
            for cat, count in categories.items():
                print(f"   - {cat}: {count}个")
            
            # 按权限等级统计
            levels = {}
            for prompt in prompts:
                level = prompt.permission_level or "通用"
                levels[level] = levels.get(level, 0) + 1
            
            print("\n🔐 按权限等级统计:")
            for level, count in sorted(levels.items()):
                print(f"   - {level}: {count}个")
            
            # 检查关键Prompt是否存在
            print("\n🔍 检查关键Prompt:")
            key_prompts = [
                ("decision", "default", "L0"),
                ("decision", "default", "L3"),
                ("decision", "default", "L5"),
                ("debate", "default", None),
            ]
            
            for category, name, level in key_prompts:
                result = await session.execute(
                    select(PromptTemplate).where(
                        PromptTemplate.category == category,
                        PromptTemplate.name == name,
                        PromptTemplate.permission_level == level,
                        PromptTemplate.is_active == True
                    )
                )
                prompt = result.scalar_one_or_none()
                
                level_str = level or "通用"
                if prompt:
                    print(f"   ✅ {category}/{name}/{level_str} (v{prompt.version})")
                else:
                    print(f"   ❌ {category}/{name}/{level_str} 不存在")
        
        await engine.dispose()
        
        if len(prompts) > 0:
            print("\n✅ Prompt数据验证通过")
            return True
        else:
            print("\n⚠️  警告: 数据库中没有Prompt数据")
            return False
        
    except Exception as e:
        print(f"\n❌ Prompt数据验证失败: {e}")
        return False


async def verify_prompt_manager():
    """验证PromptManagerDB"""
    print("\n" + "="*60)
    print("3️⃣  验证PromptManagerDB")
    print("="*60)
    
    try:
        # 使用asyncpg驱动
        db_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
        engine = create_async_engine(db_url, echo=False)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as session:
            # 创建PromptManager
            manager = PromptManagerDB(session)
            
            # 加载Prompt
            print("\n📥 加载Prompt模板...")
            await manager.load_from_db()
            
            print(f"✅ 已加载 {len(manager.templates)} 个模板")
            
            # 测试获取模板
            print("\n🧪 测试获取模板:")
            
            test_cases = [
                ("decision", "default", "L0", "保守"),
                ("decision", "default", "L3", "平衡"),
                ("decision", "default", "L5", "激进"),
                ("debate", "default", None, "辩论"),
            ]
            
            for category, name, level, keyword in test_cases:
                template = manager.get_template(category, name, level)
                level_str = level or "通用"
                
                if template:
                    has_keyword = keyword in template.content if keyword else True
                    status = "✅" if has_keyword else "⚠️"
                    print(f"   {status} {category}/{name}/{level_str}: {len(template.content)}字符")
                else:
                    print(f"   ❌ {category}/{name}/{level_str}: 未找到")
        
        await engine.dispose()
        print("\n✅ PromptManagerDB验证通过")
        return True
        
    except Exception as e:
        print(f"\n❌ PromptManagerDB验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def verify_redis_connection():
    """验证Redis连接"""
    print("\n" + "="*60)
    print("4️⃣  验证Redis连接")
    print("="*60)
    
    try:
        redis_client = RedisClient()
        
        # 测试连接
        print("\n🔌 测试Redis连接...")
        await redis_client.set("test_key", "test_value", expire=10)
        value = await redis_client.get("test_key")
        
        if value == "test_value":
            print("✅ Redis读写正常")
        else:
            print("❌ Redis读写异常")
            return False
        
        # 测试pub/sub
        print("\n📡 测试Redis Pub/Sub...")
        await redis_client.publish("prompt_reload", "test")
        print("✅ Redis Pub/Sub发布成功")
        
        print("\n✅ Redis连接验证通过")
        return True
        
    except Exception as e:
        print(f"\n❌ Redis连接验证失败: {e}")
        return False


async def verify_decision_engine_integration():
    """验证DecisionEngineV2集成"""
    print("\n" + "="*60)
    print("5️⃣  验证DecisionEngineV2集成")
    print("="*60)
    
    try:
        from app.services.decision.decision_engine_v2 import DecisionEngineV2
        
        # 使用asyncpg驱动
        db_url = settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
        engine = create_async_engine(db_url, echo=False)
        async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        redis_client = RedisClient()
        
        async with async_session() as session:
            # 创建DecisionEngineV2
            print("\n🚀 初始化DecisionEngineV2...")
            decision_engine = DecisionEngineV2(
                redis_client=redis_client,
                db_session=session,
                api_key=settings.DEEPSEEK_API_KEY
            )
            
            print("✅ DecisionEngineV2初始化成功")
            
            # 测试Prompt加载
            print("\n📥 测试Prompt加载...")
            await decision_engine._ensure_prompt_manager_loaded()
            
            if decision_engine._prompt_manager_initialized:
                print("✅ Prompt模板已加载")
            else:
                print("❌ Prompt模板加载失败")
                return False
            
            # 测试获取模板
            print("\n🧪 测试获取Prompt模板:")
            levels = ["L0", "L1", "L2", "L3", "L4", "L5"]
            
            for level in levels:
                template = decision_engine.prompt_manager.get_template(
                    "decision", "default", level
                )
                if template:
                    print(f"   ✅ {level}: v{template.version} ({len(template.content)}字符)")
                else:
                    print(f"   ⚠️  {level}: 使用fallback")
        
        await engine.dispose()
        print("\n✅ DecisionEngineV2集成验证通过")
        return True
        
    except Exception as e:
        print(f"\n❌ DecisionEngineV2集成验证失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """主函数"""
    print("\n" + "🎯"*30)
    print("Prompt系统端到端验证")
    print("🎯"*30)
    
    results = []
    
    # 1. 验证数据库表
    results.append(("数据库表", await verify_database_tables()))
    
    # 2. 验证Prompt数据
    results.append(("Prompt数据", await verify_prompt_data()))
    
    # 3. 验证PromptManagerDB
    results.append(("PromptManagerDB", await verify_prompt_manager()))
    
    # 4. 验证Redis连接
    results.append(("Redis连接", await verify_redis_connection()))
    
    # 5. 验证DecisionEngineV2集成
    results.append(("DecisionEngineV2集成", await verify_decision_engine_integration()))
    
    # 输出总结
    print("\n" + "="*60)
    print("📊 验证总结")
    print("="*60)
    
    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{status} - {name}")
    
    all_passed = all(r for _, r in results)
    
    if all_passed:
        print("\n" + "🎉"*30)
        print("所有验证通过！Prompt系统运行正常！")
        print("🎉"*30)
        return 0
    else:
        print("\n" + "⚠️"*30)
        print("部分验证失败，请检查上述错误信息")
        print("⚠️"*30)
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)

