"""
权限管理数据模型
"""
from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, JSON, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Permission(Base):
    """权限表"""
    __tablename__ = "permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(100), unique=True, nullable=False, index=True, comment="🔐 权限代码，如: users.view")
    name = Column(String(100), nullable=False, comment="🔐 权限名称")
    description = Column(Text, comment="🔐 权限描述")
    resource_type = Column(String(50), comment="🔐 资源类型: page, api, button")
    resource_path = Column(String(200), comment="🔐 资源路径: /admin/users, /api/v1/trades")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    role_permissions = relationship("RolePermission", back_populates="permission", cascade="all, delete-orphan")


class Role(Base):
    """角色表"""
    __tablename__ = "roles"
    
    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(50), unique=True, nullable=False, index=True, comment="🔐 角色代码")
    name = Column(String(100), nullable=False, comment="🔐 角色名称")
    description = Column(Text, comment="🔐 角色描述")
    is_system = Column(Boolean, default=False, comment="🔐 系统内置角色不可删除")
    parent_role_id = Column(Integer, ForeignKey("roles.id"), nullable=True, comment="🔐 父角色ID，支持继承")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    
    # 关系
    role_permissions = relationship("RolePermission", back_populates="role", cascade="all, delete-orphan")
    parent_role = relationship("Role", remote_side=[id], backref="child_roles")


class RolePermission(Base):
    """角色-权限关联表"""
    __tablename__ = "role_permissions"
    
    id = Column(Integer, primary_key=True, index=True)
    role_id = Column(Integer, ForeignKey("roles.id", ondelete="CASCADE"), nullable=False)
    permission_id = Column(Integer, ForeignKey("permissions.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # 关系
    role = relationship("Role", back_populates="role_permissions")
    permission = relationship("Permission", back_populates="role_permissions")
    
    # 唯一约束
    __table_args__ = (
        {"schema": None, "comment": "🔐 角色权限关联表"},
    )


class PermissionAuditLog(Base):
    """权限审计日志"""
    __tablename__ = "permission_audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    operator_id = Column(Integer, ForeignKey("admin_users.id"), comment="🔐 操作人ID")
    action = Column(String(50), nullable=False, comment="🔐 操作类型: grant, revoke, create_role等")
    target_type = Column(String(50), comment="🔐 目标类型: role, user, permission")
    target_id = Column(Integer, comment="🔐 目标ID")
    details = Column(JSON, comment="🔐 详细信息")
    created_at = Column(DateTime(timezone=True), server_default=func.now())

