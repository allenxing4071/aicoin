"""
管理后台用户模型
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime
from app.core.database import Base


class AdminUser(Base):
    """管理后台用户表"""
    __tablename__ = "admin_users"
    __table_args__ = {
        'comment': '👤 管理员用户 - 存储后台管理系统的用户账号、角色权限和登录信息'
    }

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(20), nullable=False, default="viewer")  # admin, trader, viewer
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_login = Column(DateTime, nullable=True)

    def __repr__(self):
        return f"<AdminUser(id={self.id}, username='{self.username}', role='{self.role}')>"

