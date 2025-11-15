#!/usr/bin/env python3
"""
初始化权限等级的 Prompt 关联字段
确保数据库中的字段存在且可以正确保存
"""

import sys
import os
import asyncio

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from sqlalchemy import select, text
from app.core.database import AsyncSessionLocal
from app.models.permission_config import PermissionLevelConfig


async def check_and_init_prompt_fields():
    """检查并初始化 Prompt 关联字段"""
    
    async with AsyncSessionLocal() as db:
        try:
            # 1. 检查表结构
            print("=" * 60)
            print("📋 检查数据库表结构...")
            print("=" * 60)
            
            result = await db.execute(text("""
                SELECT column_name, data_type, is_nullable 
                FROM information_schema.columns 
                WHERE table_name = 'permission_level_configs' 
                AND column_name IN ('decision_prompt_id', 'debate_prompt_id', 'intelligence_prompt_id')
                ORDER BY column_name;
            """))
            
            columns = result.fetchall()
            
            if not columns:
                print("❌ 错误：Prompt 关联字段不存在！")
                print("   请运行数据库迁移：alembic upgrade head")
                return False
            
            print("✅ 表结构检查通过：")
            for col in columns:
                print(f"   - {col[0]}: {col[1]} (nullable: {col[2]})")
            
            # 2. 查询当前数据
            print("\n" + "=" * 60)
            print("📊 当前权限等级的 Prompt 关联状态...")
            print("=" * 60)
            
            stmt = select(PermissionLevelConfig).order_by(PermissionLevelConfig.level)
            result = await db.execute(stmt)
            configs = result.scalars().all()
            
            if not configs:
                print("❌ 错误：没有找到任何权限等级配置！")
                return False
            
            print(f"✅ 找到 {len(configs)} 个权限等级：\n")
            
            for config in configs:
                print(f"📌 {config.level} ({config.name})")
                print(f"   ID: {config.id}")
                print(f"   决策 Prompt ID: {config.decision_prompt_id}")
                print(f"   辩论 Prompt ID: {config.debate_prompt_id}")
                print(f"   情报 Prompt ID: {config.intelligence_prompt_id}")
                print()
            
            # 3. 测试更新功能
            print("=" * 60)
            print("🧪 测试 Prompt 关联更新功能...")
            print("=" * 60)
            
            # 找一个测试对象（L2）
            test_config = next((c for c in configs if c.level == 'L2'), None)
            
            if not test_config:
                print("⚠️  警告：没有找到 L2 权限等级，跳过测试")
                return True
            
            print(f"\n测试对象：{test_config.level} ({test_config.name})")
            print(f"更新前 decision_prompt_id: {test_config.decision_prompt_id}")
            
            # 保存原值
            original_value = test_config.decision_prompt_id
            
            # 尝试更新
            test_value = 999  # 使用一个测试值
            test_config.decision_prompt_id = test_value
            
            await db.commit()
            await db.refresh(test_config)
            
            print(f"更新后 decision_prompt_id: {test_config.decision_prompt_id}")
            
            if test_config.decision_prompt_id == test_value:
                print("✅ 测试成功：字段可以正确更新！")
                
                # 恢复原值
                test_config.decision_prompt_id = original_value
                await db.commit()
                print(f"✅ 已恢复原值: {original_value}")
            else:
                print("❌ 测试失败：字段更新后值不正确！")
                return False
            
            print("\n" + "=" * 60)
            print("✅ 所有检查通过！Prompt 关联功能正常")
            print("=" * 60)
            
            return True
            
        except Exception as e:
            print(f"\n❌ 错误：{str(e)}")
            import traceback
            traceback.print_exc()
            return False


if __name__ == "__main__":
    print("\n🚀 开始检查 Prompt 关联功能...\n")
    
    success = asyncio.run(check_and_init_prompt_fields())
    
    if success:
        print("\n✅ 检查完成！系统正常")
        sys.exit(0)
    else:
        print("\n❌ 检查失败！请查看上面的错误信息")
        sys.exit(1)

