"""
权限服务 - RBAC核心逻辑
"""
from typing import List, Optional, Dict, Any
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Permission, Role, RolePermission, AdminUser, PermissionAuditLog


class PermissionService:
    """权限服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ==================== 权限管理 ====================
    
    async def get_all_permissions(self) -> List[Permission]:
        """获取所有权限"""
        result = await self.db.execute(select(Permission).order_by(Permission.code))
        return result.scalars().all()
    
    async def get_permission_by_id(self, permission_id: int) -> Optional[Permission]:
        """通过ID获取权限"""
        result = await self.db.execute(
            select(Permission).where(Permission.id == permission_id)
        )
        return result.scalar_one_or_none()
    
    async def get_permission_by_code(self, code: str) -> Optional[Permission]:
        """通过code获取权限"""
        result = await self.db.execute(
            select(Permission).where(Permission.code == code)
        )
        return result.scalar_one_or_none()
    
    async def create_permission(
        self,
        code: str,
        name: str,
        description: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_path: Optional[str] = None,
        operator_id: Optional[int] = None,
    ) -> Permission:
        """创建权限"""
        permission = Permission(
            code=code,
            name=name,
            description=description,
            resource_type=resource_type,
            resource_path=resource_path,
        )
        self.db.add(permission)
        await self.db.flush()
        
        # 记录审计日志
        if operator_id:
            await self._log_action(
                operator_id=operator_id,
                action="create_permission",
                target_type="permission",
                target_id=permission.id,
                details={"code": code, "name": name}
            )
        
        await self.db.commit()
        await self.db.refresh(permission)
        return permission
    
    async def update_permission(
        self,
        permission_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        resource_type: Optional[str] = None,
        resource_path: Optional[str] = None,
        operator_id: Optional[int] = None,
    ) -> Optional[Permission]:
        """更新权限"""
        permission = await self.get_permission_by_id(permission_id)
        if not permission:
            return None
        
        if name is not None:
            permission.name = name
        if description is not None:
            permission.description = description
        if resource_type is not None:
            permission.resource_type = resource_type
        if resource_path is not None:
            permission.resource_path = resource_path
        
        # 记录审计日志
        if operator_id:
            await self._log_action(
                operator_id=operator_id,
                action="update_permission",
                target_type="permission",
                target_id=permission_id,
                details={"updates": {"name": name, "description": description}}
            )
        
        await self.db.commit()
        await self.db.refresh(permission)
        return permission
    
    async def delete_permission(self, permission_id: int, operator_id: Optional[int] = None) -> bool:
        """删除权限"""
        permission = await self.get_permission_by_id(permission_id)
        if not permission:
            return False
        
        # 记录审计日志
        if operator_id:
            await self._log_action(
                operator_id=operator_id,
                action="delete_permission",
                target_type="permission",
                target_id=permission_id,
                details={"code": permission.code}
            )
        
        await self.db.delete(permission)
        await self.db.commit()
        return True
    
    # ==================== 角色管理 ====================
    
    async def get_all_roles(self, include_permissions: bool = False) -> List[Role]:
        """获取所有角色"""
        query = select(Role)
        if include_permissions:
            query = query.options(selectinload(Role.role_permissions).selectinload(RolePermission.permission))
        result = await self.db.execute(query.order_by(Role.code))
        return result.scalars().all()
    
    async def get_role_by_id(self, role_id: int, include_permissions: bool = False) -> Optional[Role]:
        """通过ID获取角色"""
        query = select(Role).where(Role.id == role_id)
        if include_permissions:
            query = query.options(selectinload(Role.role_permissions).selectinload(RolePermission.permission))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def get_role_by_code(self, code: str, include_permissions: bool = False) -> Optional[Role]:
        """通过code获取角色"""
        query = select(Role).where(Role.code == code)
        if include_permissions:
            query = query.options(selectinload(Role.role_permissions).selectinload(RolePermission.permission))
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
    
    async def create_role(
        self,
        code: str,
        name: str,
        description: Optional[str] = None,
        is_system: bool = False,
        parent_role_id: Optional[int] = None,
        operator_id: Optional[int] = None,
    ) -> Role:
        """创建角色"""
        role = Role(
            code=code,
            name=name,
            description=description,
            is_system=is_system,
            parent_role_id=parent_role_id,
        )
        self.db.add(role)
        await self.db.flush()
        
        # 记录审计日志
        if operator_id:
            await self._log_action(
                operator_id=operator_id,
                action="create_role",
                target_type="role",
                target_id=role.id,
                details={"code": code, "name": name}
            )
        
        await self.db.commit()
        await self.db.refresh(role)
        return role
    
    async def update_role(
        self,
        role_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        parent_role_id: Optional[int] = None,
        operator_id: Optional[int] = None,
    ) -> Optional[Role]:
        """更新角色"""
        role = await self.get_role_by_id(role_id)
        if not role:
            return None
        
        if role.is_system:
            # 系统角色只能更新描述
            if description is not None:
                role.description = description
        else:
            if name is not None:
                role.name = name
            if description is not None:
                role.description = description
            if parent_role_id is not None:
                role.parent_role_id = parent_role_id
        
        # 记录审计日志
        if operator_id:
            await self._log_action(
                operator_id=operator_id,
                action="update_role",
                target_type="role",
                target_id=role_id,
                details={"updates": {"name": name, "description": description}}
            )
        
        await self.db.commit()
        await self.db.refresh(role)
        return role
    
    async def delete_role(self, role_id: int, operator_id: Optional[int] = None) -> bool:
        """删除角色（系统角色不可删除）"""
        role = await self.get_role_by_id(role_id)
        if not role or role.is_system:
            return False
        
        # 检查是否有用户使用此角色
        result = await self.db.execute(
            select(AdminUser).where(AdminUser.role_id == role_id).limit(1)
        )
        if result.scalar_one_or_none():
            raise ValueError("Cannot delete role: users are still assigned to this role")
        
        # 记录审计日志
        if operator_id:
            await self._log_action(
                operator_id=operator_id,
                action="delete_role",
                target_type="role",
                target_id=role_id,
                details={"code": role.code}
            )
        
        await self.db.delete(role)
        await self.db.commit()
        return True
    
    # ==================== 角色权限管理 ====================
    
    async def get_role_permissions(self, role_id: int) -> List[Permission]:
        """获取角色的所有权限（包括继承的）"""
        role = await self.get_role_by_id(role_id, include_permissions=True)
        if not role:
            return []
        
        permissions = []
        
        # 获取直接权限
        for rp in role.role_permissions:
            permissions.append(rp.permission)
        
        # 获取继承的权限
        if role.parent_role_id:
            parent_permissions = await self.get_role_permissions(role.parent_role_id)
            permissions.extend(parent_permissions)
        
        # 去重
        seen = set()
        unique_permissions = []
        for perm in permissions:
            if perm.id not in seen:
                seen.add(perm.id)
                unique_permissions.append(perm)
        
        return unique_permissions
    
    async def assign_permissions_to_role(
        self,
        role_id: int,
        permission_ids: List[int],
        operator_id: Optional[int] = None,
    ) -> bool:
        """分配权限给角色（覆盖方式）"""
        role = await self.get_role_by_id(role_id)
        if not role:
            return False
        
        # 删除旧的权限关联
        await self.db.execute(
            delete(RolePermission).where(RolePermission.role_id == role_id)
        )
        
        # 添加新的权限关联
        for perm_id in permission_ids:
            rp = RolePermission(role_id=role_id, permission_id=perm_id)
            self.db.add(rp)
        
        # 记录审计日志
        if operator_id:
            await self._log_action(
                operator_id=operator_id,
                action="assign_permissions",
                target_type="role",
                target_id=role_id,
                details={"permission_ids": permission_ids}
            )
        
        await self.db.commit()
        return True
    
    async def add_permission_to_role(
        self,
        role_id: int,
        permission_id: int,
        operator_id: Optional[int] = None,
    ) -> bool:
        """添加权限到角色"""
        # 检查是否已存在
        result = await self.db.execute(
            select(RolePermission)
            .where(RolePermission.role_id == role_id)
            .where(RolePermission.permission_id == permission_id)
        )
        if result.scalar_one_or_none():
            return True  # 已存在
        
        rp = RolePermission(role_id=role_id, permission_id=permission_id)
        self.db.add(rp)
        
        # 记录审计日志
        if operator_id:
            await self._log_action(
                operator_id=operator_id,
                action="add_permission",
                target_type="role",
                target_id=role_id,
                details={"permission_id": permission_id}
            )
        
        await self.db.commit()
        return True
    
    async def remove_permission_from_role(
        self,
        role_id: int,
        permission_id: int,
        operator_id: Optional[int] = None,
    ) -> bool:
        """移除角色的权限"""
        result = await self.db.execute(
            delete(RolePermission)
            .where(RolePermission.role_id == role_id)
            .where(RolePermission.permission_id == permission_id)
        )
        
        # 记录审计日志
        if operator_id:
            await self._log_action(
                operator_id=operator_id,
                action="remove_permission",
                target_type="role",
                target_id=role_id,
                details={"permission_id": permission_id}
            )
        
        await self.db.commit()
        return result.rowcount > 0
    
    # ==================== 用户权限查询 ====================
    
    async def get_user_permissions(self, user_id: int) -> List[str]:
        """获取用户的所有权限代码（角色权限 + 自定义权限）"""
        user = await self.db.get(AdminUser, user_id)
        if not user or not user.is_active:
            return []
        
        permission_codes = set()
        
        # 1. 获取角色权限
        if user.role_id:
            permissions = await self.get_role_permissions(user.role_id)
            permission_codes.update([p.code for p in permissions])
        
        # 2. 获取用户级别的自定义权限
        if user.custom_permissions:
            permission_codes.update(user.custom_permissions)
        
        return list(permission_codes)
    
    async def check_user_permission(self, user_id: int, permission_code: str) -> bool:
        """检查用户是否有指定权限"""
        permissions = await self.get_user_permissions(user_id)
        return permission_code in permissions
    
    # ==================== 审计日志 ====================
    
    async def _log_action(
        self,
        operator_id: int,
        action: str,
        target_type: str,
        target_id: int,
        details: Dict[str, Any],
    ):
        """记录审计日志"""
        log = PermissionAuditLog(
            operator_id=operator_id,
            action=action,
            target_type=target_type,
            target_id=target_id,
            details=details,
        )
        self.db.add(log)
    
    async def get_audit_logs(
        self,
        operator_id: Optional[int] = None,
        action: Optional[str] = None,
        limit: int = 100,
    ) -> List[PermissionAuditLog]:
        """获取审计日志"""
        query = select(PermissionAuditLog).order_by(PermissionAuditLog.created_at.desc())
        
        if operator_id:
            query = query.where(PermissionAuditLog.operator_id == operator_id)
        if action:
            query = query.where(PermissionAuditLog.action == action)
        
        query = query.limit(limit)
        result = await self.db.execute(query)
        return result.scalars().all()

