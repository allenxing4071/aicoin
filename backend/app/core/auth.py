"""
认证和权限检查装饰器
"""

from fastapi import Depends, HTTPException, status
from typing import Callable, List
import logging

from app.core.permissions import Permission, has_permission, has_any_permission, has_all_permissions
from app.api.v1.admin.auth import verify_admin_token

logger = logging.getLogger(__name__)


def require_permissions(*required_perms: Permission):
    """
    权限检查依赖注入函数
    
    用法：
    @router.get("/users")
    async def get_users(
        token: dict = Depends(require_permissions(Permission.USERS_VIEW)),
        db: AsyncSession = Depends(get_db)
    ):
        ...
    
    Args:
        *required_perms: 需要的权限列表（需要同时拥有所有权限）
        
    Returns:
        Callable: 依赖注入函数
    """
    async def permission_checker(token: dict = Depends(verify_admin_token)) -> dict:
        """检查用户是否有所需权限"""
        user_role = token.get("role", "viewer")
        username = token.get("sub", "unknown")
        
        # 检查每个权限
        missing_perms = []
        for perm in required_perms:
            if not has_permission(user_role, perm):
                missing_perms.append(perm.value)
        
        # 如果有缺失的权限，抛出403错误
        if missing_perms:
            logger.warning(
                f"权限不足: 用户 {username} (角色: {user_role}) "
                f"尝试访问需要权限 {missing_perms}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足：需要以下权限 {', '.join(missing_perms)}"
            )
        
        logger.debug(f"权限检查通过: 用户 {username} (角色: {user_role})")
        return token
    
    return permission_checker


def require_any_permission(*required_perms: Permission):
    """
    权限检查依赖注入函数（只需要任意一个权限）
    
    用法：
    @router.get("/data")
    async def get_data(
        token: dict = Depends(require_any_permission(
            Permission.TRADES_VIEW,
            Permission.ORDERS_VIEW
        )),
        db: AsyncSession = Depends(get_db)
    ):
        ...
    
    Args:
        *required_perms: 需要的权限列表（只需要其中一个）
        
    Returns:
        Callable: 依赖注入函数
    """
    async def permission_checker(token: dict = Depends(verify_admin_token)) -> dict:
        """检查用户是否有任意一个所需权限"""
        user_role = token.get("role", "viewer")
        username = token.get("sub", "unknown")
        
        # 检查是否有任意一个权限
        if not has_any_permission(user_role, *required_perms):
            perm_list = [perm.value for perm in required_perms]
            logger.warning(
                f"权限不足: 用户 {username} (角色: {user_role}) "
                f"尝试访问需要权限（任意一个） {perm_list}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"权限不足：需要以下权限之一 {', '.join(perm_list)}"
            )
        
        logger.debug(f"权限检查通过: 用户 {username} (角色: {user_role})")
        return token
    
    return permission_checker


def require_role(*allowed_roles: str):
    """
    角色检查依赖注入函数
    
    用法：
    @router.delete("/users/{user_id}")
    async def delete_user(
        user_id: int,
        token: dict = Depends(require_role("super_admin", "admin")),
        db: AsyncSession = Depends(get_db)
    ):
        ...
    
    Args:
        *allowed_roles: 允许的角色列表
        
    Returns:
        Callable: 依赖注入函数
    """
    async def role_checker(token: dict = Depends(verify_admin_token)) -> dict:
        """检查用户角色是否在允许列表中"""
        user_role = token.get("role", "viewer")
        username = token.get("sub", "unknown")
        
        if user_role not in allowed_roles:
            logger.warning(
                f"角色权限不足: 用户 {username} (角色: {user_role}) "
                f"尝试访问需要角色 {allowed_roles}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"角色权限不足：需要以下角色之一 {', '.join(allowed_roles)}"
            )
        
        logger.debug(f"角色检查通过: 用户 {username} (角色: {user_role})")
        return token
    
    return role_checker

