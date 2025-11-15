"""
Prompt管理API - 借鉴NOFX的Web UI设计

提供Prompt模板的CRUD操作和热重载功能
"""

from fastapi import APIRouter, HTTPException, Depends, status
from typing import List, Dict, Any
from pydantic import BaseModel
import logging
import os

from app.core.permissions import require_admin
from app.services.decision.prompt_manager import get_global_prompt_manager, reload_global_templates

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/prompts", tags=["prompts"])


# === Pydantic Models ===

class PromptTemplateInfo(BaseModel):
    """Prompt模板信息"""
    name: str
    category: str
    content: str
    file_path: str
    created_at: str
    updated_at: str


class PromptTemplateUpdate(BaseModel):
    """Prompt模板更新请求"""
    content: str


class PromptStrategySwitch(BaseModel):
    """策略切换请求"""
    category: str
    strategy: str


# === API Endpoints ===

@router.get("/{category}", response_model=List[str])
async def list_templates(
    category: str,
    _: Dict = Depends(require_admin)
):
    """
    列出指定类别的所有模板名称
    
    Args:
        category: 类别名称（decision/debate/intelligence）
    
    Returns:
        模板名称列表
    """
    try:
        prompt_manager = get_global_prompt_manager()
        templates = prompt_manager.list_templates(category)
        
        logger.info(f"📋 列出 {category} 类别的模板: {len(templates)} 个")
        
        return templates
    
    except Exception as e:
        logger.error(f"列出模板失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to list templates: {str(e)}"
        )


@router.get("/{category}/{name}", response_model=PromptTemplateInfo)
async def get_template(
    category: str,
    name: str,
    _: Dict = Depends(require_admin)
):
    """
    获取指定模板的详细信息
    
    Args:
        category: 类别名称
        name: 模板名称
    
    Returns:
        模板详细信息
    """
    try:
        prompt_manager = get_global_prompt_manager()
        template = prompt_manager.get_template(category, name)
        
        logger.info(f"📄 获取模板: {category}/{name}")
        
        return PromptTemplateInfo(
            name=template.name,
            category=template.category,
            content=template.content,
            file_path=template.file_path,
            created_at=template.created_at.isoformat(),
            updated_at=template.updated_at.isoformat()
        )
    
    except Exception as e:
        logger.error(f"获取模板失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template not found: {category}/{name}"
        )


@router.put("/{category}/{name}")
async def update_template(
    category: str,
    name: str,
    update_data: PromptTemplateUpdate,
    _: Dict = Depends(require_admin)
):
    """
    更新模板内容
    
    借鉴NOFX的做法：直接写入文件，然后热重载
    
    Args:
        category: 类别名称
        name: 模板名称
        update_data: 更新内容
    
    Returns:
        更新结果
    """
    try:
        prompt_manager = get_global_prompt_manager()
        
        # 获取模板文件路径
        template = prompt_manager.get_template(category, name)
        file_path = template.file_path
        
        # 检查文件是否存在且不是内置模板
        if file_path == "<builtin>":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot update builtin template"
            )
        
        if not os.path.exists(file_path):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Template file not found: {file_path}"
            )
        
        # 写入新内容
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(update_data.content)
        
        # 热重载该类别的模板
        prompt_manager.reload_templates(category)
        
        logger.info(f"✅ 更新模板成功: {category}/{name}")
        
        return {
            "success": True,
            "message": f"Template {category}/{name} updated successfully",
            "file_path": file_path
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"更新模板失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update template: {str(e)}"
        )


@router.post("/reload")
async def reload_templates(
    category: str = None,
    _: Dict = Depends(require_admin)
):
    """
    热重载模板
    
    完全借鉴NOFX的ReloadPromptTemplates功能
    
    Args:
        category: 指定类别（可选，None表示重载所有）
    
    Returns:
        重载结果
    """
    try:
        reload_global_templates(category)
        
        if category:
            logger.info(f"🔄 已重新加载 {category} 类别的模板")
            message = f"Reloaded templates for category: {category}"
        else:
            logger.info("🔄 已重新加载所有模板")
            message = "Reloaded all templates"
        
        return {
            "success": True,
            "message": message
        }
    
    except Exception as e:
        logger.error(f"重载模板失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to reload templates: {str(e)}"
        )


@router.get("/")
async def get_all_templates(
    _: Dict = Depends(require_admin)
):
    """
    获取所有模板的概览信息
    
    Returns:
        所有模板的列表
    """
    try:
        prompt_manager = get_global_prompt_manager()
        all_templates = prompt_manager.get_all_templates()
        
        result = []
        for template in all_templates:
            result.append({
                "name": template.name,
                "category": template.category,
                "file_path": template.file_path,
                "content_length": len(template.content),
                "created_at": template.created_at.isoformat(),
                "updated_at": template.updated_at.isoformat()
            })
        
        logger.info(f"📋 获取所有模板: {len(result)} 个")
        
        return {
            "total": len(result),
            "templates": result
        }
    
    except Exception as e:
        logger.error(f"获取所有模板失败: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get all templates: {str(e)}"
        )

