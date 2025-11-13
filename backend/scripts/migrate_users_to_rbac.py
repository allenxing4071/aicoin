#!/usr/bin/env python3
"""
用户数据迁移脚本：将现有用户的role映射到RBAC系统的role_id

使用方法：
    python scripts/migrate_users_to_rbac.py
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.core.database import async_session_maker
from app.models.admin_user import AdminUser
from app.models.permission import Role


# 角色映射表：旧系统role -> RBAC系统role_code
ROLE_MAPPING = {
    "super_admin": "super_admin",
    "admin": "admin",
    "risk_manager": "risk_manager",
    "trader": "trader",
    "analyst": "analyst",
    "viewer": "viewer"
}


async def migrate_users():
    """迁移用户数据到RBAC系统"""
    print("=" * 60)
    print("开始用户数据迁移到RBAC系统")
    print("=" * 60)
    
    async with async_session_maker() as db:
        try:
            # 1. 获取所有用户
            result = await db.execute(select(AdminUser))
            users = result.scalars().all()
            
            if not users:
                print("⚠️  没有找到用户，迁移结束")
                return
            
            print(f"\n找到 {len(users)} 个用户需要迁移")
            
            # 2. 获取所有RBAC角色
            roles_result = await db.execute(select(Role))
            rbac_roles = {role.code: role for role in roles_result.scalars().all()}
            
            if not rbac_roles:
                print("❌ 错误：RBAC角色表为空，请先运行 init_rbac.py 初始化RBAC系统")
                return
            
            print(f"找到 {len(rbac_roles)} 个RBAC角色")
            print(f"角色列表：{', '.join(rbac_roles.keys())}")
            
            # 3. 迁移每个用户
            migrated_count = 0
            skipped_count = 0
            error_count = 0
            
            for user in users:
                try:
                    # 如果已经有role_id，跳过
                    if user.role_id:
                        print(f"⏭️  跳过用户 {user.username}（已有role_id={user.role_id}）")
                        skipped_count += 1
                        continue
                    
                    # 映射role到role_code
                    role_code = ROLE_MAPPING.get(user.role)
                    if not role_code:
                        print(f"⚠️  警告：用户 {user.username} 的角色 '{user.role}' 无法映射，跳过")
                        error_count += 1
                        continue
                    
                    # 查找对应的RBAC角色
                    rbac_role = rbac_roles.get(role_code)
                    if not rbac_role:
                        print(f"⚠️  警告：找不到角色代码 '{role_code}' 对应的RBAC角色，跳过用户 {user.username}")
                        error_count += 1
                        continue
                    
                    # 更新用户的role_id
                    user.role_id = rbac_role.id
                    print(f"✅ 迁移用户 {user.username}: role='{user.role}' -> role_id={rbac_role.id} ({rbac_role.name})")
                    migrated_count += 1
                    
                except Exception as e:
                    print(f"❌ 迁移用户 {user.username} 时出错: {str(e)}")
                    error_count += 1
                    continue
            
            # 4. 提交更改
            if migrated_count > 0:
                await db.commit()
                print(f"\n✅ 数据库更改已提交")
            
            # 5. 验证迁移结果
            print("\n" + "=" * 60)
            print("迁移结果验证")
            print("=" * 60)
            
            result = await db.execute(select(AdminUser))
            all_users = result.scalars().all()
            
            print(f"\n总用户数：{len(all_users)}")
            print(f"已迁移：{migrated_count}")
            print(f"已跳过：{skipped_count}")
            print(f"错误：{error_count}")
            
            # 显示迁移后的用户状态
            print("\n用户状态：")
            print(f"{'用户名':<20} {'旧角色':<15} {'新role_id':<10} {'状态'}")
            print("-" * 60)
            
            for user in all_users:
                status = "✅" if user.role_id else "❌"
                print(f"{user.username:<20} {user.role:<15} {user.role_id or 'NULL':<10} {status}")
            
            # 统计未迁移的用户
            unmigrated = [u for u in all_users if not u.role_id]
            if unmigrated:
                print(f"\n⚠️  警告：还有 {len(unmigrated)} 个用户未迁移")
                for user in unmigrated:
                    print(f"  - {user.username} (role={user.role})")
            else:
                print("\n🎉 所有用户已成功迁移到RBAC系统！")
            
        except Exception as e:
            print(f"\n❌ 迁移过程中发生错误: {str(e)}")
            await db.rollback()
            raise


async def main():
    """主函数"""
    try:
        await migrate_users()
    except Exception as e:
        print(f"\n❌ 迁移失败: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())

