"""
管理后台 - 认证相关API
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from passlib.context import CryptContext
import jwt

from app.core.database import get_db
from app.models.admin_user import AdminUser
from app.core.config import settings

router = APIRouter()

# 密码加密上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# JWT配置
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 8  # 8小时


# ============ Pydantic 模型 ============

class LoginRequest(BaseModel):
    """登录请求"""
    username: str
    password: str


class LoginResponse(BaseModel):
    """登录响应"""
    success: bool
    message: str
    data: Optional[dict] = None


# ============ 工具函数 ============

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """验证密码 (bcrypt限制72字节)"""
    password_truncated = plain_password[:72]
    return pwd_context.verify(password_truncated, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """创建访问令牌"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    # 使用固定的SECRET_KEY
    secret_key = "your-secret-key-here-change-in-production"
    import logging
    logger = logging.getLogger(__name__)
    logger.warning(f"🔑 CREATE TOKEN: Using SECRET_KEY={secret_key}")
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=ALGORITHM)
    logger.warning(f"✅ Token created: {encoded_jwt[:80]}")
    return encoded_jwt


async def verify_admin_token(authorization: Optional[str] = Header(None, alias="Authorization")) -> dict:
    """验证管理员token"""
    import logging
    logger = logging.getLogger(__name__)
    
    if not authorization or not authorization.startswith("Bearer "):
        logger.warning("Missing or invalid authorization header")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="未提供有效的认证令牌"
        )
    
    token = authorization.replace("Bearer ", "")
    # 使用固定的SECRET_KEY
    secret_key = "your-secret-key-here-change-in-production"
    logger.warning(f"🔑 VERIFY TOKEN: Using SECRET_KEY={secret_key}")
    logger.warning(f"📩 Token to verify: {token[:80]}")
    
    try:
        payload = jwt.decode(token, secret_key, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            logger.error("Token payload missing 'sub' field")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="无效的令牌"
            )
        logger.info(f"Token verified successfully for user: {username}")
        return payload
    except jwt.ExpiredSignatureError:
        logger.error("Token expired")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="令牌已过期"
        )
    except Exception as e:
        logger.error(f"Token verification failed: {type(e).__name__}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的令牌"
        )


# ============ API 端点 ============

@router.post("/login", response_model=LoginResponse)
async def login(
    login_data: LoginRequest,
    db: AsyncSession = Depends(get_db)
):
    """
    管理员登录
    
    默认账号: admin / admin123
    """
    try:
        # 查找用户
        result = await db.execute(
            select(AdminUser).where(AdminUser.username == login_data.username)
        )
        user = result.scalar_one_or_none()
        
        # 验证用户和密码
        if not user or not verify_password(login_data.password, user.hashed_password):
            return LoginResponse(
                success=False,
                message="用户名或密码错误"
            )
        
        # 检查用户是否被禁用
        if not user.is_active:
            return LoginResponse(
                success=False,
                message="该账户已被禁用"
            )
        
        # 更新最后登录时间
        user.last_login = datetime.utcnow()
        await db.commit()
        
        # 创建访问令牌
        import logging
        logger = logging.getLogger(__name__)
        logger.warning(f"⚡ 准备创建token for user: {user.username}")
        access_token = create_access_token(
            data={"sub": user.username, "role": user.role}
        )
        logger.warning(f"⚡ Token创建完成: {access_token[:50]}...")
        
        return LoginResponse(
            success=True,
            message="登录成功",
            data={
                "token": access_token,
                "username": user.username,
                "role": user.role,
                "email": user.email
            }
        )
    
    except Exception as e:
        return LoginResponse(
            success=False,
            message=f"登录失败: {str(e)}"
        )


@router.post("/logout")
async def logout(token: dict = Depends(verify_admin_token)):
    """
    管理员登出
    """
    return {
        "success": True,
        "message": "登出成功"
    }


@router.get("/verify")
async def verify_token(token: dict = Depends(verify_admin_token)):
    """
    验证token是否有效
    """
    return {
        "success": True,
        "message": "令牌有效",
        "data": {
            "username": token.get("sub"),
            "role": token.get("role")
        }
    }

