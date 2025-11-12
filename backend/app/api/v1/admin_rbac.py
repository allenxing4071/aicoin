"""
RBAC管理API - 权限和角色管理
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.api.v1.admin_db import get_current_user
from app.services.permission_service import PermissionService
from app.models import AdminUser

router = APIRouter()


# ==================== Pydantic Models ====================

class PermissionBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    resource_type: Optional[str] = None
    resource_path: Optional[str] = None


class PermissionCreate(PermissionBase):
    pass


class PermissionUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    resource_type: Optional[str] = None
    resource_path: Optional[str] = None


class PermissionResponse(PermissionBase):
    id: int
    
    class Config:
        from_attributes = True


class RoleBase(BaseModel):
    code: str
    name: str
    description: Optional[str] = None
    parent_role_id: Optional[int] = None


class RoleCreate(RoleBase):
    pass


class RoleUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    parent_role_id: Optional[int] = None


class RoleResponse(RoleBase):
    id: int
    is_system: bool
    permission_count: Optional[int] = None
    
    class Config:
        from_attributes = True


class RolePermissionsUpdate(BaseModel):
    permission_ids: List[int]


class ApiResponse(BaseModel):
    success: bool
    message: str
    data: Optional[dict] = None


# ==================== 依赖注入 ====================

async def get_permission_service(db: AsyncSession = Depends(get_db)) -> PermissionService:
    """获取权限服务"""
    return PermissionService(db)


async def require_super_admin(current_user: dict = Depends(get_current_user)):
    """要求超级管理员权限"""
    # 从token解析用户角色
    role = current_user.get("role", "viewer")
    if role != "super_admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="需要超级管理员权限"
        )
    return current_user


# ==================== 权限管理API ====================

@router.get("/permissions", response_model=ApiResponse)
async def list_permissions(
    service: PermissionService = Depends(get_permission_service),
    current_user: dict = Depends(get_current_user),
):
    """获取所有权限列表"""
    permissions = await service.get_all_permissions()
    return ApiResponse(
        success=True,
        message="获取权限列表成功",
        data={
            "permissions": [
                {
                    "id": p.id,
                    "code": p.code,
                    "name": p.name,
                    "description": p.description,
                    "resource_type": p.resource_type,
                    "resource_path": p.resource_path,
                }
                for p in permissions
            ],
            "total": len(permissions),
        }
    )


@router.get("/permissions/{permission_id}", response_model=ApiResponse)
async def get_permission(
    permission_id: int,
    service: PermissionService = Depends(get_permission_service),
    current_user: dict = Depends(get_current_user),
):
    """获取权限详情"""
    permission = await service.get_permission_by_id(permission_id)
    if not permission:
        raise HTTPException(status_code=404, detail="权限不存在")
    
    return ApiResponse(
        success=True,
        message="获取权限详情成功",
        data={
            "id": permission.id,
            "code": permission.code,
            "name": permission.name,
            "description": permission.description,
            "resource_type": permission.resource_type,
            "resource_path": permission.resource_path,
        }
    )


@router.post("/permissions", response_model=ApiResponse)
async def create_permission(
    data: PermissionCreate,
    service: PermissionService = Depends(get_permission_service),
    current_user: dict = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    """创建权限（仅超级管理员）"""
    # 检查code是否已存在
    existing = await service.get_permission_by_code(data.code)
    if existing:
        raise HTTPException(status_code=400, detail="权限代码已存在")
    
    # 获取当前用户ID
    result = await db.execute(
        f"SELECT id FROM admin_users WHERE username = '{current_user['sub']}'"
    )
    user_id = result.scalar_one_or_none()
    
    permission = await service.create_permission(
        code=data.code,
        name=data.name,
        description=data.description,
        resource_type=data.resource_type,
        resource_path=data.resource_path,
        operator_id=user_id,
    )
    
    return ApiResponse(
        success=True,
        message="权限创建成功",
        data={"id": permission.id}
    )


@router.put("/permissions/{permission_id}", response_model=ApiResponse)
async def update_permission(
    permission_id: int,
    data: PermissionUpdate,
    service: PermissionService = Depends(get_permission_service),
    current_user: dict = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    """更新权限（仅超级管理员）"""
    # 获取当前用户ID
    result = await db.execute(
        f"SELECT id FROM admin_users WHERE username = '{current_user['sub']}'"
    )
    user_id = result.scalar_one_or_none()
    
    permission = await service.update_permission(
        permission_id=permission_id,
        name=data.name,
        description=data.description,
        resource_type=data.resource_type,
        resource_path=data.resource_path,
        operator_id=user_id,
    )
    
    if not permission:
        raise HTTPException(status_code=404, detail="权限不存在")
    
    return ApiResponse(success=True, message="权限更新成功")


@router.delete("/permissions/{permission_id}", response_model=ApiResponse)
async def delete_permission(
    permission_id: int,
    service: PermissionService = Depends(get_permission_service),
    current_user: dict = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    """删除权限（仅超级管理员）"""
    # 获取当前用户ID
    result = await db.execute(
        f"SELECT id FROM admin_users WHERE username = '{current_user['sub']}'"
    )
    user_id = result.scalar_one_or_none()
    
    success = await service.delete_permission(permission_id, operator_id=user_id)
    if not success:
        raise HTTPException(status_code=404, detail="权限不存在")
    
    return ApiResponse(success=True, message="权限删除成功")


# ==================== 角色管理API ====================

@router.get("/roles", response_model=ApiResponse)
async def list_roles(
    include_permissions: bool = False,
    service: PermissionService = Depends(get_permission_service),
    current_user: dict = Depends(get_current_user),
):
    """获取所有角色列表"""
    roles = await service.get_all_roles(include_permissions=include_permissions)
    
    roles_data = []
    for role in roles:
        role_data = {
            "id": role.id,
            "code": role.code,
            "name": role.name,
            "description": role.description,
            "is_system": role.is_system,
            "parent_role_id": role.parent_role_id,
        }
        
        if include_permissions:
            permissions = await service.get_role_permissions(role.id)
            role_data["permissions"] = [
                {"id": p.id, "code": p.code, "name": p.name}
                for p in permissions
            ]
            role_data["permission_count"] = len(permissions)
        
        roles_data.append(role_data)
    
    return ApiResponse(
        success=True,
        message="获取角色列表成功",
        data={"roles": roles_data, "total": len(roles_data)}
    )


@router.get("/roles/{role_id}", response_model=ApiResponse)
async def get_role(
    role_id: int,
    include_permissions: bool = True,
    service: PermissionService = Depends(get_permission_service),
    current_user: dict = Depends(get_current_user),
):
    """获取角色详情"""
    role = await service.get_role_by_id(role_id, include_permissions=include_permissions)
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    role_data = {
        "id": role.id,
        "code": role.code,
        "name": role.name,
        "description": role.description,
        "is_system": role.is_system,
        "parent_role_id": role.parent_role_id,
    }
    
    if include_permissions:
        permissions = await service.get_role_permissions(role.id)
        role_data["permissions"] = [
            {"id": p.id, "code": p.code, "name": p.name}
            for p in permissions
        ]
    
    return ApiResponse(
        success=True,
        message="获取角色详情成功",
        data=role_data
    )


@router.post("/roles", response_model=ApiResponse)
async def create_role(
    data: RoleCreate,
    service: PermissionService = Depends(get_permission_service),
    current_user: dict = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    """创建角色（仅超级管理员）"""
    # 检查code是否已存在
    existing = await service.get_role_by_code(data.code)
    if existing:
        raise HTTPException(status_code=400, detail="角色代码已存在")
    
    # 获取当前用户ID
    result = await db.execute(
        f"SELECT id FROM admin_users WHERE username = '{current_user['sub']}'"
    )
    user_id = result.scalar_one_or_none()
    
    role = await service.create_role(
        code=data.code,
        name=data.name,
        description=data.description,
        parent_role_id=data.parent_role_id,
        operator_id=user_id,
    )
    
    return ApiResponse(
        success=True,
        message="角色创建成功",
        data={"id": role.id}
    )


@router.put("/roles/{role_id}", response_model=ApiResponse)
async def update_role(
    role_id: int,
    data: RoleUpdate,
    service: PermissionService = Depends(get_permission_service),
    current_user: dict = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    """更新角色（仅超级管理员）"""
    # 获取当前用户ID
    result = await db.execute(
        f"SELECT id FROM admin_users WHERE username = '{current_user['sub']}'"
    )
    user_id = result.scalar_one_or_none()
    
    role = await service.update_role(
        role_id=role_id,
        name=data.name,
        description=data.description,
        parent_role_id=data.parent_role_id,
        operator_id=user_id,
    )
    
    if not role:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    return ApiResponse(success=True, message="角色更新成功")


@router.delete("/roles/{role_id}", response_model=ApiResponse)
async def delete_role(
    role_id: int,
    service: PermissionService = Depends(get_permission_service),
    current_user: dict = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    """删除角色（仅超级管理员，系统角色不可删除）"""
    try:
        # 获取当前用户ID
        result = await db.execute(
            f"SELECT id FROM admin_users WHERE username = '{current_user['sub']}'"
        )
        user_id = result.scalar_one_or_none()
        
        success = await service.delete_role(role_id, operator_id=user_id)
        if not success:
            raise HTTPException(status_code=404, detail="角色不存在或为系统角色")
        
        return ApiResponse(success=True, message="角色删除成功")
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/roles/{role_id}/permissions", response_model=ApiResponse)
async def update_role_permissions(
    role_id: int,
    data: RolePermissionsUpdate,
    service: PermissionService = Depends(get_permission_service),
    current_user: dict = Depends(require_super_admin),
    db: AsyncSession = Depends(get_db),
):
    """更新角色权限（仅超级管理员）"""
    # 获取当前用户ID
    result = await db.execute(
        f"SELECT id FROM admin_users WHERE username = '{current_user['sub']}'"
    )
    user_id = result.scalar_one_or_none()
    
    success = await service.assign_permissions_to_role(
        role_id=role_id,
        permission_ids=data.permission_ids,
        operator_id=user_id,
    )
    
    if not success:
        raise HTTPException(status_code=404, detail="角色不存在")
    
    return ApiResponse(success=True, message="角色权限更新成功")


@router.get("/audit-logs", response_model=ApiResponse)
async def get_audit_logs(
    limit: int = 100,
    service: PermissionService = Depends(get_permission_service),
    current_user: dict = Depends(require_super_admin),
):
    """获取审计日志（仅超级管理员）"""
    logs = await service.get_audit_logs(limit=limit)
    
    return ApiResponse(
        success=True,
        message="获取审计日志成功",
        data={
            "logs": [
                {
                    "id": log.id,
                    "operator_id": log.operator_id,
                    "action": log.action,
                    "target_type": log.target_type,
                    "target_id": log.target_id,
                    "details": log.details,
                    "created_at": log.created_at.isoformat() if log.created_at else None,
                }
                for log in logs
            ],
            "total": len(logs),
        }
    )

