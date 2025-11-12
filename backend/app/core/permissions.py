"""
权限管理系统
定义角色和权限的映射关系
"""

from enum import Enum
from typing import Dict, List, Set


class Permission(str, Enum):
    """权限枚举 - 定义系统中所有可用的权限"""
    
    # ========== 用户管理权限 ==========
    USERS_VIEW = "users:view"           # 查看用户列表
    USERS_CREATE = "users:create"       # 创建新用户
    USERS_UPDATE = "users:update"       # 更新用户信息
    USERS_DELETE = "users:delete"       # 删除用户
    USERS_MANAGE_ROLES = "users:roles"  # 管理用户角色
    
    # ========== 交易管理权限 ==========
    TRADES_VIEW = "trades:view"         # 查看交易记录
    TRADES_EXECUTE = "trades:execute"   # 执行交易
    TRADES_CANCEL = "trades:cancel"     # 取消交易
    TRADES_EXPORT = "trades:export"     # 导出交易数据
    
    # ========== 订单管理权限 ==========
    ORDERS_VIEW = "orders:view"         # 查看订单
    ORDERS_CREATE = "orders:create"     # 创建订单
    ORDERS_CANCEL = "orders:cancel"     # 取消订单
    
    # ========== AI决策权限 ==========
    AI_VIEW = "ai:view"                 # 查看AI决策
    AI_CONFIG = "ai:config"             # 配置AI参数
    AI_CONTROL = "ai:control"           # 控制AI启停
    AI_MODELS = "ai:models"             # 管理AI模型
    
    # ========== 风控管理权限 ==========
    RISK_VIEW = "risk:view"             # 查看风控事件
    RISK_CONFIG = "risk:config"         # 配置风控规则
    RISK_OVERRIDE = "risk:override"     # 覆盖风控决策
    
    # ========== 系统设置权限 ==========
    SYSTEM_VIEW = "system:view"         # 查看系统信息
    SYSTEM_CONFIG = "system:config"     # 配置系统参数
    SYSTEM_RESTART = "system:restart"   # 重启系统服务
    
    # ========== 交易所管理权限 ==========
    EXCHANGE_VIEW = "exchange:view"     # 查看交易所配置
    EXCHANGE_CONFIG = "exchange:config" # 配置交易所
    EXCHANGE_SWITCH = "exchange:switch" # 切换交易所
    
    # ========== 数据备份权限 ==========
    BACKUP_VIEW = "backup:view"         # 查看备份列表
    BACKUP_CREATE = "backup:create"     # 创建备份
    BACKUP_RESTORE = "backup:restore"   # 恢复备份
    BACKUP_DELETE = "backup:delete"     # 删除备份
    BACKUP_CLEANUP = "backup:cleanup"   # 清理旧数据
    
    # ========== 日志管理权限 ==========
    LOGS_VIEW = "logs:view"             # 查看日志
    LOGS_DOWNLOAD = "logs:download"     # 下载日志
    LOGS_DELETE = "logs:delete"         # 删除日志
    LOGS_CONFIG = "logs:config"         # 配置日志级别
    
    # ========== 数据库管理权限 ==========
    DATABASE_VIEW = "database:view"     # 查看数据库
    DATABASE_QUERY = "database:query"   # 执行查询
    DATABASE_MODIFY = "database:modify" # 修改数据
    DATABASE_EXPORT = "database:export" # 导出数据
    
    # ========== 智能情报权限 ==========
    INTEL_VIEW = "intel:view"           # 查看情报
    INTEL_CONFIG = "intel:config"       # 配置情报源
    INTEL_EXPORT = "intel:export"       # 导出情报
    
    # ========== 记忆系统权限 ==========
    MEMORY_VIEW = "memory:view"         # 查看记忆数据
    MEMORY_MANAGE = "memory:manage"     # 管理记忆系统
    MEMORY_EXPORT = "memory:export"     # 导出记忆数据
    
    # ========== 账户管理权限 ==========
    ACCOUNT_VIEW = "account:view"       # 查看账户信息
    ACCOUNT_EXPORT = "account:export"   # 导出账户数据
    
    # ========== 权限管理权限 ==========
    PERMISSIONS_VIEW = "permissions:view"     # 查看权限配置
    PERMISSIONS_CONFIG = "permissions:config" # 配置权限等级


# ========== 角色定义 ==========
class Role(str, Enum):
    """系统角色枚举"""
    SUPER_ADMIN = "super_admin"     # 超级管理员
    ADMIN = "admin"                 # 管理员
    RISK_MANAGER = "risk_manager"   # 风控经理
    TRADER = "trader"               # 交易员
    ANALYST = "analyst"             # 分析师
    VIEWER = "viewer"               # 观察者


# ========== 角色权限映射 ==========
ROLE_PERMISSIONS: Dict[str, Set[Permission]] = {
    
    # 超级管理员 - 拥有所有权限
    Role.SUPER_ADMIN: {
        *list(Permission)  # 所有权限
    },
    
    # 管理员 - 除了超级管理员特权外的所有管理权限
    Role.ADMIN: {
        # 用户管理
        Permission.USERS_VIEW,
        Permission.USERS_CREATE,
        Permission.USERS_UPDATE,
        Permission.USERS_MANAGE_ROLES,
        
        # 交易管理
        Permission.TRADES_VIEW,
        Permission.TRADES_EXPORT,
        Permission.ORDERS_VIEW,
        
        # AI管理
        Permission.AI_VIEW,
        Permission.AI_CONFIG,
        Permission.AI_CONTROL,
        Permission.AI_MODELS,
        
        # 风控管理
        Permission.RISK_VIEW,
        Permission.RISK_CONFIG,
        
        # 系统管理
        Permission.SYSTEM_VIEW,
        Permission.SYSTEM_CONFIG,
        Permission.EXCHANGE_VIEW,
        Permission.EXCHANGE_CONFIG,
        Permission.EXCHANGE_SWITCH,
        
        # 备份管理
        Permission.BACKUP_VIEW,
        Permission.BACKUP_CREATE,
        Permission.BACKUP_DELETE,
        Permission.BACKUP_CLEANUP,
        
        # 日志管理
        Permission.LOGS_VIEW,
        Permission.LOGS_DOWNLOAD,
        Permission.LOGS_CONFIG,
        
        # 数据库管理
        Permission.DATABASE_VIEW,
        Permission.DATABASE_QUERY,
        Permission.DATABASE_EXPORT,
        
        # 情报管理
        Permission.INTEL_VIEW,
        Permission.INTEL_CONFIG,
        Permission.INTEL_EXPORT,
        
        # 记忆系统
        Permission.MEMORY_VIEW,
        Permission.MEMORY_MANAGE,
        Permission.MEMORY_EXPORT,
        
        # 账户管理
        Permission.ACCOUNT_VIEW,
        Permission.ACCOUNT_EXPORT,
        
        # 权限管理
        Permission.PERMISSIONS_VIEW,
        Permission.PERMISSIONS_CONFIG,
    },
    
    # 风控经理 - 专注于风控和监控
    Role.RISK_MANAGER: {
        # 交易查看
        Permission.TRADES_VIEW,
        Permission.TRADES_EXPORT,
        Permission.ORDERS_VIEW,
        
        # AI查看
        Permission.AI_VIEW,
        
        # 风控管理（完整权限）
        Permission.RISK_VIEW,
        Permission.RISK_CONFIG,
        Permission.RISK_OVERRIDE,
        
        # 系统查看
        Permission.SYSTEM_VIEW,
        Permission.EXCHANGE_VIEW,
        
        # 日志查看
        Permission.LOGS_VIEW,
        Permission.LOGS_DOWNLOAD,
        
        # 数据库查看
        Permission.DATABASE_VIEW,
        Permission.DATABASE_QUERY,
        
        # 情报查看
        Permission.INTEL_VIEW,
        
        # 账户查看
        Permission.ACCOUNT_VIEW,
        
        # 权限查看
        Permission.PERMISSIONS_VIEW,
    },
    
    # 交易员 - 执行交易和查看相关信息
    Role.TRADER: {
        # 交易管理
        Permission.TRADES_VIEW,
        Permission.TRADES_EXECUTE,
        Permission.TRADES_CANCEL,
        Permission.ORDERS_VIEW,
        Permission.ORDERS_CREATE,
        Permission.ORDERS_CANCEL,
        
        # AI查看
        Permission.AI_VIEW,
        
        # 风控查看
        Permission.RISK_VIEW,
        
        # 系统查看
        Permission.SYSTEM_VIEW,
        Permission.EXCHANGE_VIEW,
        
        # 情报查看
        Permission.INTEL_VIEW,
        
        # 账户查看
        Permission.ACCOUNT_VIEW,
    },
    
    # 分析师 - 只读数据分析
    Role.ANALYST: {
        # 交易查看
        Permission.TRADES_VIEW,
        Permission.TRADES_EXPORT,
        Permission.ORDERS_VIEW,
        
        # AI查看
        Permission.AI_VIEW,
        
        # 风控查看
        Permission.RISK_VIEW,
        
        # 系统查看
        Permission.SYSTEM_VIEW,
        Permission.EXCHANGE_VIEW,
        
        # 日志查看
        Permission.LOGS_VIEW,
        Permission.LOGS_DOWNLOAD,
        
        # 数据库查看
        Permission.DATABASE_VIEW,
        Permission.DATABASE_QUERY,
        Permission.DATABASE_EXPORT,
        
        # 情报查看
        Permission.INTEL_VIEW,
        Permission.INTEL_EXPORT,
        
        # 记忆查看
        Permission.MEMORY_VIEW,
        Permission.MEMORY_EXPORT,
        
        # 账户查看
        Permission.ACCOUNT_VIEW,
        Permission.ACCOUNT_EXPORT,
    },
    
    # 观察者 - 基础查看权限
    Role.VIEWER: {
        # 交易查看
        Permission.TRADES_VIEW,
        Permission.ORDERS_VIEW,
        
        # AI查看
        Permission.AI_VIEW,
        
        # 风控查看
        Permission.RISK_VIEW,
        
        # 系统查看
        Permission.SYSTEM_VIEW,
        Permission.EXCHANGE_VIEW,
        
        # 情报查看
        Permission.INTEL_VIEW,
        
        # 账户查看
        Permission.ACCOUNT_VIEW,
    },
}


# ========== 角色显示名称 ==========
ROLE_DISPLAY_NAMES: Dict[str, str] = {
    Role.SUPER_ADMIN: "超级管理员",
    Role.ADMIN: "管理员",
    Role.RISK_MANAGER: "风控经理",
    Role.TRADER: "交易员",
    Role.ANALYST: "分析师",
    Role.VIEWER: "观察者",
}


# ========== 角色描述 ==========
ROLE_DESCRIPTIONS: Dict[str, str] = {
    Role.SUPER_ADMIN: "拥有系统所有权限，可以管理所有用户和系统配置",
    Role.ADMIN: "系统管理员，可以管理用户、配置系统、查看所有数据",
    Role.RISK_MANAGER: "风控经理，专注于风险管理和交易监控",
    Role.TRADER: "交易员，可以执行交易和管理订单",
    Role.ANALYST: "数据分析师，拥有所有数据的只读权限",
    Role.VIEWER: "观察者，只能查看基础信息",
}


# ========== 权限检查函数 ==========

def has_permission(role: str, permission: Permission) -> bool:
    """
    检查角色是否有指定权限
    
    Args:
        role: 用户角色
        permission: 要检查的权限
        
    Returns:
        bool: 是否有权限
    """
    role_perms = ROLE_PERMISSIONS.get(role, set())
    return permission in role_perms


def has_any_permission(role: str, *permissions: Permission) -> bool:
    """
    检查角色是否有任意一个指定权限
    
    Args:
        role: 用户角色
        *permissions: 要检查的权限列表
        
    Returns:
        bool: 是否有任意一个权限
    """
    role_perms = ROLE_PERMISSIONS.get(role, set())
    return any(perm in role_perms for perm in permissions)


def has_all_permissions(role: str, *permissions: Permission) -> bool:
    """
    检查角色是否有所有指定权限
    
    Args:
        role: 用户角色
        *permissions: 要检查的权限列表
        
    Returns:
        bool: 是否有所有权限
    """
    role_perms = ROLE_PERMISSIONS.get(role, set())
    return all(perm in role_perms for perm in permissions)


def get_role_permissions(role: str) -> Set[Permission]:
    """
    获取角色的所有权限
    
    Args:
        role: 用户角色
        
    Returns:
        Set[Permission]: 权限集合
    """
    return ROLE_PERMISSIONS.get(role, set())


def get_role_display_name(role: str) -> str:
    """
    获取角色的显示名称
    
    Args:
        role: 用户角色
        
    Returns:
        str: 显示名称
    """
    return ROLE_DISPLAY_NAMES.get(role, role)


def get_role_description(role: str) -> str:
    """
    获取角色的描述
    
    Args:
        role: 用户角色
        
    Returns:
        str: 角色描述
    """
    return ROLE_DESCRIPTIONS.get(role, "")


def get_all_roles() -> List[Dict[str, str]]:
    """
    获取所有角色信息
    
    Returns:
        List[Dict]: 角色列表，包含 value, label, description
    """
    return [
        {
            "value": role,
            "label": ROLE_DISPLAY_NAMES.get(role, role),
            "description": ROLE_DESCRIPTIONS.get(role, ""),
            "permission_count": len(ROLE_PERMISSIONS.get(role, set()))
        }
        for role in Role
    ]

