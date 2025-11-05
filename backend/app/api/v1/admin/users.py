"""
管理后台 - 用户管理API
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext

from app.core.database import get_db
from app.models.admin_user import AdminUser
from app.api.v1.admin.auth import verify_admin_token

router = APIRouter()

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ============ Pydantic 模型 ============

class UserBase(BaseModel):
    """用户基础模型"""
    username: str
    email: EmailStr
    role: str  # admin, trader, viewer
    is_active: bool = True


class UserCreate(UserBase):
    """创建用户请求"""
    password: str


class UserUpdate(BaseModel):
    """更新用户请求"""
    email: Optional[EmailStr] = None
    password: Optional[str] = None
    role: Optional[str] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase):
    """用户响应"""
    id: int
    created_at: datetime
    updated_at: datetime
    last_login: Optional[datetime] = None

    class Config:
        from_attributes = True


class UsersStats(BaseModel):
    """用户统计"""
    total: int
    active: int
    admins: int
    traders: int
    viewers: int


# ============ API 端点 ============

@router.get("/stats", response_model=UsersStats)
async def get_users_stats(
    token: dict = Depends(verify_admin_token),
    db: AsyncSession = Depends(get_db)
):
    """获取用户统计信息"""
    try:
        # 总用户数
        total_result = await db.execute(select(func.count(AdminUser.id)))
        total = total_result.scalar() or 0
        
        # 活跃用户数
        active_result = await db.execute(
            select(func.count(AdminUser.id)).where(AdminUser.is_active == True)
        )
        active = active_result.scalar() or 0
        
        # 按角色统计
        admins_result = await db.execute(
            select(func.count(AdminUser.id)).where(AdminUser.role == "admin")
        )
        admins = admins_result.scalar() or 0
        
        traders_result = await db.execute(
            select(func.count(AdminUser.id)).where(AdminUser.role == "trader")
        )
        traders = traders_result.scalar() or 0
        
        viewers_result = await db.execute(
            select(func.count(AdminUser.id)).where(AdminUser.role == "viewer")
        )
        viewers = viewers_result.scalar() or 0
        
        return UsersStats(
            total=total,
            active=active,
            admins=admins,
            traders=traders,
            viewers=viewers
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户统计失败: {str(e)}"
        )


@router.get("", response_model=List[UserResponse])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    role: Optional[str] = None,
    is_active: Optional[bool] = None,
    token: dict = Depends(verify_admin_token),
    db: AsyncSession = Depends(get_db)
):
    """获取用户列表"""
    try:
        query = select(AdminUser)
        
        # 应用过滤条件
        if role:
            query = query.where(AdminUser.role == role)
        if is_active is not None:
            query = query.where(AdminUser.is_active == is_active)
        
        # 分页
        query = query.offset(skip).limit(limit)
        
        result = await db.execute(query)
        users = result.scalars().all()
        
        return [UserResponse.model_validate(user) for user in users]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户列表失败: {str(e)}"
        )


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    token: dict = Depends(verify_admin_token),
    db: AsyncSession = Depends(get_db)
):
    """获取单个用户详情"""
    try:
        result = await db.execute(
            select(AdminUser).where(AdminUser.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        return UserResponse.model_validate(user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户详情失败: {str(e)}"
        )


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    token: dict = Depends(verify_admin_token),
    db: AsyncSession = Depends(get_db)
):
    """创建新用户"""
    try:
        # 检查用户名是否已存在
        username_result = await db.execute(
            select(AdminUser).where(AdminUser.username == user_data.username)
        )
        if username_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="用户名已存在"
            )
        
        # 检查邮箱是否已存在
        email_result = await db.execute(
            select(AdminUser).where(AdminUser.email == user_data.email)
        )
        if email_result.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="邮箱已存在"
            )
        
        # 验证角色
        if user_data.role not in ["admin", "trader", "viewer"]:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="无效的角色类型"
            )
        
        # 创建用户 (bcrypt限制72字节)
        password_truncated = user_data.password[:72]
        hashed_password = pwd_context.hash(password_truncated)
        new_user = AdminUser(
            username=user_data.username,
            email=user_data.email,
            hashed_password=hashed_password,
            role=user_data.role,
            is_active=user_data.is_active,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        db.add(new_user)
        await db.commit()
        await db.refresh(new_user)
        
        return UserResponse.model_validate(new_user)
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"创建用户失败: {str(e)}"
        )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    token: dict = Depends(verify_admin_token),
    db: AsyncSession = Depends(get_db)
):
    """更新用户信息"""
    try:
        # 查找用户
        result = await db.execute(
            select(AdminUser).where(AdminUser.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 更新字段
        if user_data.email is not None:
            # 检查邮箱是否被其他用户使用
            email_result = await db.execute(
                select(AdminUser).where(
                    AdminUser.email == user_data.email,
                    AdminUser.id != user_id
                )
            )
            if email_result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="邮箱已被使用"
                )
            user.email = user_data.email
        
        if user_data.password is not None:
            # bcrypt限制72字节
            password_truncated = user_data.password[:72]
            user.hashed_password = pwd_context.hash(password_truncated)
        
        if user_data.role is not None:
            if user_data.role not in ["admin", "trader", "viewer"]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="无效的角色类型"
                )
            user.role = user_data.role
        
        if user_data.is_active is not None:
            user.is_active = user_data.is_active
        
        user.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(user)
        
        return UserResponse.model_validate(user)
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新用户失败: {str(e)}"
        )


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    token: dict = Depends(verify_admin_token),
    db: AsyncSession = Depends(get_db)
):
    """删除用户"""
    try:
        # 查找用户
        result = await db.execute(
            select(AdminUser).where(AdminUser.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 不允许删除默认管理员
        if user.username == "admin":
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="不能删除默认管理员账户"
            )
        
        # 删除用户
        await db.delete(user)
        await db.commit()
        
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除用户失败: {str(e)}"
        )


@router.post("/{user_id}/toggle-active", response_model=UserResponse)
async def toggle_user_active(
    user_id: int,
    token: dict = Depends(verify_admin_token),
    db: AsyncSession = Depends(get_db)
):
    """切换用户激活状态"""
    try:
        result = await db.execute(
            select(AdminUser).where(AdminUser.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="用户不存在"
            )
        
        # 不允许禁用默认管理员
        if user.username == "admin" and user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="不能禁用默认管理员账户"
            )
        
        user.is_active = not user.is_active
        user.updated_at = datetime.utcnow()
        
        await db.commit()
        await db.refresh(user)
        
        return UserResponse.model_validate(user)
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"切换用户状态失败: {str(e)}"
        )

