#!/usr/bin/env python3
"""
初始化RBAC权限系统
- 创建基础权限
- 创建系统角色
- 分配权限给角色
"""
import asyncio
import sys
from pathlib import Path

# 添加项目路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import select
from app.core.database import get_db, engine, Base
from app.models import Permission, Role, RolePermission, AdminUser


# 定义所有权限
PERMISSIONS = [
    # 用户管理
    {"code": "users.view", "name": "查看用户", "resource_type": "page", "resource_path": "/admin/users"},
    {"code": "users.create", "name": "创建用户", "resource_type": "api", "resource_path": "/api/v1/admin/users"},
    {"code": "users.update", "name": "更新用户", "resource_type": "api", "resource_path": "/api/v1/admin/users/*"},
    {"code": "users.delete", "name": "删除用户", "resource_type": "api", "resource_path": "/api/v1/admin/users/*"},
    
    # 交易管理
    {"code": "trades.view", "name": "查看交易", "resource_type": "page", "resource_path": "/admin/trades"},
    {"code": "trades.export", "name": "导出交易", "resource_type": "button", "resource_path": ""},
    
    # 订单管理
    {"code": "orders.view", "name": "查看订单", "resource_type": "page", "resource_path": "/admin/orders"},
    {"code": "orders.cancel", "name": "取消订单", "resource_type": "api", "resource_path": "/api/v1/orders/*/cancel"},
    
    # AI管理
    {"code": "ai.view", "name": "查看AI", "resource_type": "page", "resource_path": "/admin/ai-*"},
    {"code": "ai.config", "name": "配置AI", "resource_type": "api", "resource_path": "/api/v1/ai/*"},
    
    # 风控管理
    {"code": "risk.view", "name": "查看风控", "resource_type": "page", "resource_path": "/admin/risk-events"},
    {"code": "risk.config", "name": "配置风控", "resource_type": "api", "resource_path": "/api/v1/risk/*"},
    
    # 系统管理
    {"code": "system.view", "name": "查看系统", "resource_type": "page", "resource_path": "/admin/database"},
    {"code": "system.config", "name": "配置系统", "resource_type": "api", "resource_path": "/api/v1/system/*"},
    
    # 备份管理
    {"code": "backup.view", "name": "查看备份", "resource_type": "page", "resource_path": "/admin/backup"},
    {"code": "backup.create", "name": "创建备份", "resource_type": "api", "resource_path": "/api/v1/admin/backup/backup"},
    {"code": "backup.delete", "name": "删除备份", "resource_type": "api", "resource_path": "/api/v1/admin/backup/delete/*"},
    
    # 日志管理
    {"code": "logs.view", "name": "查看日志", "resource_type": "page", "resource_path": "/admin/logs"},
    {"code": "logs.download", "name": "下载日志", "resource_type": "api", "resource_path": "/api/v1/admin/logs/download/*"},
    {"code": "logs.delete", "name": "删除日志", "resource_type": "api", "resource_path": "/api/v1/admin/logs/delete/*"},
    
    # 权限管理
    {"code": "permissions.view", "name": "查看权限", "resource_type": "page", "resource_path": "/admin/permissions"},
    {"code": "permissions.create", "name": "创建权限", "resource_type": "api", "resource_path": "/api/v1/admin/permissions"},
    {"code": "permissions.update", "name": "更新权限", "resource_type": "api", "resource_path": "/api/v1/admin/permissions/*"},
    {"code": "permissions.delete", "name": "删除权限", "resource_type": "api", "resource_path": "/api/v1/admin/permissions/*"},
    
    # 角色管理
    {"code": "roles.view", "name": "查看角色", "resource_type": "page", "resource_path": "/admin/roles"},
    {"code": "roles.create", "name": "创建角色", "resource_type": "api", "resource_path": "/api/v1/admin/roles"},
    {"code": "roles.update", "name": "更新角色", "resource_type": "api", "resource_path": "/api/v1/admin/roles/*"},
    {"code": "roles.delete", "name": "删除角色", "resource_type": "api", "resource_path": "/api/v1/admin/roles/*"},
    {"code": "roles.manage", "name": "管理角色权限", "resource_type": "api", "resource_path": "/api/v1/admin/roles/*/permissions"},
    
    # 交易所管理
    {"code": "exchange.view", "name": "查看交易所", "resource_type": "page", "resource_path": "/admin/exchanges"},
    {"code": "exchange.config", "name": "配置交易所", "resource_type": "api", "resource_path": "/api/v1/exchanges/*"},
    
    # 情报管理
    {"code": "intel.view", "name": "查看情报", "resource_type": "page", "resource_path": "/admin/intelligence"},
    {"code": "intel.export", "name": "导出情报", "resource_type": "button", "resource_path": ""},
    
    # 记忆系统
    {"code": "memory.view", "name": "查看记忆", "resource_type": "page", "resource_path": "/admin/memory"},
    {"code": "memory.manage", "name": "管理记忆", "resource_type": "api", "resource_path": "/api/v1/memory/*"},
    
    # 账户管理
    {"code": "accounts.view", "name": "查看账户", "resource_type": "page", "resource_path": "/admin/accounts"},
    {"code": "accounts.export", "name": "导出账户", "resource_type": "button", "resource_path": ""},
]

# 定义系统角色及其权限
ROLES = {
    "super_admin": {
        "name": "超级管理员",
        "description": "拥有系统所有权限",
        "is_system": True,
        "permissions": "*",  # 所有权限
    },
    "admin": {
        "name": "管理员",
        "description": "系统管理员，负责系统配置和用户管理",
        "is_system": True,
        "permissions": [
            "users.view", "users.create", "users.update",
            "trades.view", "orders.view",
            "ai.view", "ai.config",
            "risk.view", "risk.config",
            "system.view", "system.config",
            "backup.view", "backup.create",
            "logs.view",
            "exchange.view", "exchange.config",
            "intel.view",
            "memory.view",
            "accounts.view",
        ],
    },
    "risk_manager": {
        "name": "风控经理",
        "description": "负责风控策略配置和交易监控",
        "is_system": True,
        "permissions": [
            "trades.view",
            "orders.view",
            "ai.view",
            "risk.view", "risk.config",
            "logs.view",
            "accounts.view",
        ],
    },
    "trader": {
        "name": "交易员",
        "description": "负责执行交易操作",
        "is_system": True,
        "permissions": [
            "trades.view",
            "orders.view", "orders.cancel",
            "ai.view",
            "accounts.view",
        ],
    },
    "analyst": {
        "name": "分析师",
        "description": "数据分析和报告，只读权限",
        "is_system": True,
        "permissions": [
            "trades.view", "trades.export",
            "orders.view",
            "ai.view",
            "risk.view",
            "logs.view",
            "intel.view", "intel.export",
            "memory.view",
            "accounts.view", "accounts.export",
        ],
    },
    "viewer": {
        "name": "观察者",
        "description": "基础查看权限",
        "is_system": True,
        "permissions": [
            "trades.view",
            "ai.view",
        ],
    },
}


async def init_rbac():
    """初始化RBAC系统"""
    print("🚀 开始初始化RBAC权限系统...")
    
    # 创建表
    print("📋 创建数据库表...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ 数据库表创建完成")
    
    async for db in get_db():
        try:
            # 1. 创建权限
            print("\n📝 创建权限...")
            perm_map = {}
            for perm_data in PERMISSIONS:
                # 检查是否已存在
                result = await db.execute(
                    select(Permission).where(Permission.code == perm_data["code"])
                )
                existing = result.scalar_one_or_none()
                
                if existing:
                    perm_map[perm_data["code"]] = existing
                    print(f"  - {perm_data['code']} (已存在)")
                else:
                    perm = Permission(**perm_data)
                    db.add(perm)
                    await db.flush()
                    perm_map[perm_data["code"]] = perm
                    print(f"  + {perm_data['code']} (新创建)")
            
            await db.commit()
            print(f"✅ 权限创建完成，共 {len(perm_map)} 个")
            
            # 2. 创建角色
            print("\n👥 创建角色...")
            role_map = {}
            for role_code, role_data in ROLES.items():
                # 检查是否已存在
                result = await db.execute(
                    select(Role).where(Role.code == role_code)
                )
                existing = result.scalar_one_or_none()
                
                if existing:
                    role_map[role_code] = existing
                    print(f"  - {role_code} ({role_data['name']}) (已存在)")
                else:
                    role = Role(
                        code=role_code,
                        name=role_data["name"],
                        description=role_data["description"],
                        is_system=role_data["is_system"]
                    )
                    db.add(role)
                    await db.flush()
                    role_map[role_code] = role
                    print(f"  + {role_code} ({role_data['name']}) (新创建)")
            
            await db.commit()
            print(f"✅ 角色创建完成，共 {len(role_map)} 个")
            
            # 3. 分配权限给角色
            print("\n🔗 分配权限...")
            for role_code, role_data in ROLES.items():
                role = role_map[role_code]
                permissions = role_data["permissions"]
                
                if permissions == "*":
                    # 超级管理员拥有所有权限
                    permissions = list(perm_map.keys())
                
                # 清除旧的权限关联（如果需要更新）
                await db.execute(
                    select(RolePermission).where(RolePermission.role_id == role.id)
                )
                
                for perm_code in permissions:
                    perm = perm_map.get(perm_code)
                    if not perm:
                        print(f"  ⚠️  权限 {perm_code} 不存在")
                        continue
                    
                    # 检查是否已关联
                    result = await db.execute(
                        select(RolePermission)
                        .where(RolePermission.role_id == role.id)
                        .where(RolePermission.permission_id == perm.id)
                    )
                    existing = result.scalar_one_or_none()
                    
                    if not existing:
                        rp = RolePermission(role_id=role.id, permission_id=perm.id)
                        db.add(rp)
                
                await db.commit()
                print(f"  ✅ {role_code}: {len(permissions)} 个权限")
            
            print("\n🎉 RBAC系统初始化完成！")
            
        except Exception as e:
            print(f"\n❌ 初始化失败: {e}")
            await db.rollback()
            raise
        finally:
            break


if __name__ == "__main__":
    asyncio.run(init_rbac())

