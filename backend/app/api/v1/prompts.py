"""
Prompt模板管理API路由
支持CRUD操作、热重载、版本管理
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.core.database import get_db
from app.core.redis_client import redis_client
from app.models.prompt_template import PromptTemplate
from app.services.decision.prompt_manager_db import PromptManagerDB
from pydantic import BaseModel

router = APIRouter()


class PromptTemplateCreate(BaseModel):
    """创建Prompt模板请求"""
    name: str
    category: str
    permission_level: Optional[str] = None
    content: str
    version: int = 1
    is_active: bool = True


class PromptTemplateUpdate(BaseModel):
    """更新Prompt模板请求"""
    name: Optional[str] = None
    category: Optional[str] = None
    permission_level: Optional[str] = None
    content: Optional[str] = None
    version: Optional[int] = None
    is_active: Optional[bool] = None


class PromptTemplateResponse(BaseModel):
    """Prompt模板响应"""
    id: int
    name: str
    category: str
    permission_level: Optional[str]
    content: str
    version: int
    is_active: bool
    created_at: str
    updated_at: str

    class Config:
        from_attributes = True


@router.get("/", response_model=List[PromptTemplateResponse])
async def list_prompts(
    category: Optional[str] = Query(None, description="按类别筛选"),
    permission_level: Optional[str] = Query(None, description="按权限等级筛选"),
    is_active: Optional[bool] = Query(None, description="按激活状态筛选"),
    db: AsyncSession = Depends(get_db)
):
    """获取Prompt模板列表"""
    try:
        query = select(PromptTemplate)
        
        # 添加筛选条件
        conditions = []
        if category:
            conditions.append(PromptTemplate.category == category)
        if permission_level:
            conditions.append(PromptTemplate.permission_level == permission_level)
        if is_active is not None:
            conditions.append(PromptTemplate.is_active == is_active)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(PromptTemplate.category, PromptTemplate.name)
        
        result = await db.execute(query)
        prompts = result.scalars().all()
        
        return [
            PromptTemplateResponse(
                id=p.id,
                name=p.name,
                category=p.category,
                permission_level=p.permission_level,
                content=p.content,
                version=p.version,
                is_active=p.is_active,
                created_at=p.created_at.isoformat() if p.created_at else "",
                updated_at=p.updated_at.isoformat() if p.updated_at else ""
            )
            for p in prompts
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取Prompt列表失败: {str(e)}")


@router.get("/{prompt_id}", response_model=PromptTemplateResponse)
async def get_prompt(
    prompt_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取单个Prompt模板"""
    try:
        result = await db.execute(
            select(PromptTemplate).where(PromptTemplate.id == prompt_id)
        )
        prompt = result.scalar_one_or_none()
        
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt模板不存在")
        
        return PromptTemplateResponse(
            id=prompt.id,
            name=prompt.name,
            category=prompt.category,
            permission_level=prompt.permission_level,
            content=prompt.content,
            version=prompt.version,
            is_active=prompt.is_active,
            created_at=prompt.created_at.isoformat() if prompt.created_at else "",
            updated_at=prompt.updated_at.isoformat() if prompt.updated_at else ""
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取Prompt失败: {str(e)}")


@router.post("/", response_model=PromptTemplateResponse)
async def create_prompt(
    prompt_data: PromptTemplateCreate,
    db: AsyncSession = Depends(get_db)
):
    """创建Prompt模板"""
    try:
        # 检查是否已存在同名模板
        result = await db.execute(
            select(PromptTemplate).where(
                and_(
                    PromptTemplate.name == prompt_data.name,
                    PromptTemplate.category == prompt_data.category
                )
            )
        )
        existing = result.scalar_one_or_none()
        if existing:
            raise HTTPException(
                status_code=400,
                detail=f"已存在同名Prompt: {prompt_data.category}/{prompt_data.name}"
            )
        
        # 创建新模板
        new_prompt = PromptTemplate(
            name=prompt_data.name,
            category=prompt_data.category,
            permission_level=prompt_data.permission_level,
            content=prompt_data.content,
            version=prompt_data.version,
            is_active=prompt_data.is_active
        )
        
        db.add(new_prompt)
        await db.commit()
        await db.refresh(new_prompt)
        
        # 清除Redis缓存
        await redis_client.delete(PromptManagerDB.REDIS_CACHE_KEY)
        
        return PromptTemplateResponse(
            id=new_prompt.id,
            name=new_prompt.name,
            category=new_prompt.category,
            permission_level=new_prompt.permission_level,
            content=new_prompt.content,
            version=new_prompt.version,
            is_active=new_prompt.is_active,
            created_at=new_prompt.created_at.isoformat() if new_prompt.created_at else "",
            updated_at=new_prompt.updated_at.isoformat() if new_prompt.updated_at else ""
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"创建Prompt失败: {str(e)}")


@router.put("/{prompt_id}", response_model=PromptTemplateResponse)
async def update_prompt(
    prompt_id: int,
    prompt_data: PromptTemplateUpdate,
    db: AsyncSession = Depends(get_db)
):
    """更新Prompt模板"""
    try:
        result = await db.execute(
            select(PromptTemplate).where(PromptTemplate.id == prompt_id)
        )
        prompt = result.scalar_one_or_none()
        
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt模板不存在")
        
        # 更新字段
        if prompt_data.name is not None:
            prompt.name = prompt_data.name
        if prompt_data.category is not None:
            prompt.category = prompt_data.category
        if prompt_data.permission_level is not None:
            prompt.permission_level = prompt_data.permission_level
        if prompt_data.content is not None:
            prompt.content = prompt_data.content
        if prompt_data.version is not None:
            prompt.version = prompt_data.version
        if prompt_data.is_active is not None:
            prompt.is_active = prompt_data.is_active
        
        await db.commit()
        await db.refresh(prompt)
        
        # 清除Redis缓存
        await redis_client.delete(PromptManagerDB.REDIS_CACHE_KEY)
        
        return PromptTemplateResponse(
            id=prompt.id,
            name=prompt.name,
            category=prompt.category,
            permission_level=prompt.permission_level,
            content=prompt.content,
            version=prompt.version,
            is_active=prompt.is_active,
            created_at=prompt.created_at.isoformat() if prompt.created_at else "",
            updated_at=prompt.updated_at.isoformat() if prompt.updated_at else ""
        )
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"更新Prompt失败: {str(e)}")


@router.delete("/{prompt_id}")
async def delete_prompt(
    prompt_id: int,
    db: AsyncSession = Depends(get_db)
):
    """删除Prompt模板"""
    try:
        result = await db.execute(
            select(PromptTemplate).where(PromptTemplate.id == prompt_id)
        )
        prompt = result.scalar_one_or_none()
        
        if not prompt:
            raise HTTPException(status_code=404, detail="Prompt模板不存在")
        
        await db.delete(prompt)
        await db.commit()
        
        # 清除Redis缓存
        await redis_client.delete(PromptManagerDB.REDIS_CACHE_KEY)
        
        return {"message": "Prompt模板已删除", "id": prompt_id}
    except HTTPException:
        raise
    except Exception as e:
        await db.rollback()
        raise HTTPException(status_code=500, detail=f"删除Prompt失败: {str(e)}")


@router.post("/reload")
async def reload_prompts(db: AsyncSession = Depends(get_db)):
    """热重载Prompt模板（清除缓存）"""
    try:
        # 清除Redis缓存
        await redis_client.delete(PromptManagerDB.REDIS_CACHE_KEY)
        
        # 统计当前模板数量
        result = await db.execute(select(PromptTemplate))
        count = len(result.scalars().all())
        
        return {
            "message": "Prompt模板已重载",
            "total_templates": count,
            "cache_cleared": True
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"重载Prompt失败: {str(e)}")


@router.get("/categories/list")
async def list_categories(db: AsyncSession = Depends(get_db)):
    """获取所有类别"""
    try:
        result = await db.execute(
            select(PromptTemplate.category).distinct()
        )
        categories = [row[0] for row in result.all()]
        return {"categories": categories}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取类别列表失败: {str(e)}")


@router.get("/levels/list")
async def list_levels():
    """获取所有权限等级"""
    return {
        "levels": ["L0", "L1", "L2", "L3", "L4", "L5"],
        "descriptions": {
            "L0": "极度保守",
            "L1": "保守",
            "L2": "稳健",
            "L3": "平衡",
            "L4": "积极",
            "L5": "激进"
        }
    }

