"""
Prompt模板管理器 - 数据库版本
从PostgreSQL加载Prompt，支持L0-L5权限等级
"""

import logging
import threading
from typing import Dict, List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.prompt_template import PromptTemplate as PromptTemplateModel

logger = logging.getLogger(__name__)


class PromptTemplateDB:
    """数据库版Prompt模板数据类"""
    
    def __init__(self, db_model: PromptTemplateModel):
        self.id = db_model.id
        self.name = db_model.name
        self.category = db_model.category
        self.permission_level = db_model.permission_level
        self.content = db_model.content
        self.version = db_model.version
        self.is_active = db_model.is_active
        self.created_at = db_model.created_at
        self.updated_at = db_model.updated_at
    
    def render(self, **variables) -> str:
        """渲染模板"""
        try:
            return self.content.format(**variables)
        except KeyError as e:
            logger.warning(f"模板变量缺失: {e}")
            return self.content
        except Exception as e:
            logger.error(f"模板渲染失败: {e}")
            return self.content


class PromptManagerDB:
    """
    Prompt模板管理器（数据库版）
    
    核心功能：
    1. 从PostgreSQL加载Prompt
    2. 支持L0-L5权限等级
    3. 内存缓存 + 线程安全
    4. 优雅降级
    """
    
    def __init__(self, db: AsyncSession):
        """
        初始化Prompt管理器
        
        Args:
            db: 数据库会话
        """
        self.db = db
        self.templates: Dict[str, PromptTemplateDB] = {}  # key: "category/name/level"
        self._lock = threading.RLock()
    
    async def load_from_db(self) -> None:
        """从数据库加载所有激活的Prompt"""
        with self._lock:
            try:
                # 查询所有激活的Prompt
                query = select(PromptTemplateModel).where(
                    PromptTemplateModel.is_active == True
                )
                result = await self.db.execute(query)
                templates = result.scalars().all()
                
                # 清空缓存
                self.templates.clear()
                
                # 加载到内存
                for t in templates:
                    key = self._build_key(t.category, t.name, t.permission_level)
                    self.templates[key] = PromptTemplateDB(t)
                
                logger.info(f"✅ 从数据库加载了 {len(templates)} 个Prompt模板")
                
            except Exception as e:
                logger.error(f"从数据库加载Prompt失败: {e}")
    
    def _build_key(
        self,
        category: str,
        name: str,
        permission_level: Optional[str] = None
    ) -> str:
        """构建缓存key"""
        if permission_level:
            return f"{category}/{name}/{permission_level}"
        else:
            return f"{category}/{name}"
    
    def get_template(
        self,
        category: str,
        name: str = "default",
        permission_level: Optional[str] = None
    ) -> Optional[PromptTemplateDB]:
        """
        获取Prompt模板（支持权限等级）
        
        优先级：
        1. 尝试获取特定等级的模板（如：decision/default/L3）
        2. 降级到通用模板（如：decision/default）
        3. 降级到内置模板
        
        Args:
            category: 类别（decision/debate/intelligence）
            name: 模板名称（默认default）
            permission_level: 权限等级（L0-L5，可选）
        
        Returns:
            Prompt模板对象
        """
        with self._lock:
            # 1. 尝试获取特定等级模板
            if permission_level:
                key = self._build_key(category, name, permission_level)
                if key in self.templates:
                    logger.debug(f"使用特定等级模板: {key}")
                    return self.templates[key]
            
            # 2. 降级到通用模板
            key = self._build_key(category, name)
            if key in self.templates:
                logger.debug(f"使用通用模板: {key}")
                return self.templates[key]
            
            # 3. 如果不是default，尝试降级到default
            if name != "default":
                logger.warning(f"模板 '{category}/{name}' 不存在，尝试使用default")
                return self.get_template(category, "default", permission_level)
            
            # 4. 最后降级到内置模板
            logger.error(f"无法加载任何模板（{category}/{name}），使用内置简化版本")
            return self._get_builtin_template(category, name, permission_level)
    
    def _get_builtin_template(
        self,
        category: str,
        name: str,
        permission_level: Optional[str] = None
    ) -> PromptTemplateDB:
        """获取内置简化版本模板（作为最后的fallback）"""
        builtin_contents = {
            "decision": "你是专业的加密货币交易AI。请根据市场数据做出交易决策。\n",
            "debate": "你是专业的市场分析师。请基于提供的数据进行分析。\n",
            "intelligence": "你是专业的情报分析师。请分析市场情报并提供洞察。\n"
        }
        
        content = builtin_contents.get(category, "你是专业的AI助手。\n")
        
        # 创建一个模拟的数据库模型
        class BuiltinModel:
            id = -1
            name = name
            category = category
            permission_level = permission_level
            content = content
            version = 0
            is_active = True
            created_at = None
            updated_at = None
        
        return PromptTemplateDB(BuiltinModel())
    
    def list_templates(
        self,
        category: Optional[str] = None,
        permission_level: Optional[str] = None
    ) -> List[PromptTemplateDB]:
        """
        列出模板
        
        Args:
            category: 类别过滤（可选）
            permission_level: 权限等级过滤（可选）
        
        Returns:
            模板列表
        """
        with self._lock:
            templates = []
            
            for key, template in self.templates.items():
                # 类别过滤
                if category and template.category != category:
                    continue
                
                # 权限等级过滤
                if permission_level and template.permission_level != permission_level:
                    continue
                
                templates.append(template)
            
            return templates
    
    async def reload_templates(self, category: Optional[str] = None) -> None:
        """
        重新加载模板（热重载）
        
        Args:
            category: 指定类别（None表示重载所有）
        """
        if category:
            # 只重载指定类别
            with self._lock:
                # 移除该类别的缓存
                keys_to_remove = [
                    k for k in self.templates.keys()
                    if k.startswith(f"{category}/")
                ]
                for key in keys_to_remove:
                    del self.templates[key]
            
            # 重新加载
            await self.load_from_db()
            logger.info(f"🔄 已重新加载 {category} 类别的模板")
        else:
            # 重载所有
            await self.load_from_db()
            logger.info("🔄 已重新加载所有模板")
    
    def template_exists(
        self,
        category: str,
        name: str,
        permission_level: Optional[str] = None
    ) -> bool:
        """检查模板是否存在"""
        with self._lock:
            key = self._build_key(category, name, permission_level)
            return key in self.templates


# 全局单例
_global_prompt_manager_db: Optional[PromptManagerDB] = None
_global_lock = threading.Lock()


async def get_global_prompt_manager_db(db: AsyncSession) -> PromptManagerDB:
    """
    获取全局Prompt管理器单例（数据库版）
    
    Args:
        db: 数据库会话
    
    Returns:
        全局PromptManagerDB实例
    """
    global _global_prompt_manager_db
    
    with _global_lock:
        if _global_prompt_manager_db is None:
            _global_prompt_manager_db = PromptManagerDB(db)
            await _global_prompt_manager_db.load_from_db()
            logger.info("✅ 初始化全局Prompt管理器（数据库版）")
        
        return _global_prompt_manager_db


async def reload_global_templates_db(
    db: AsyncSession,
    category: Optional[str] = None
) -> None:
    """
    重新加载全局模板（热重载）
    
    Args:
        db: 数据库会话
        category: 指定类别（None表示重载所有）
    """
    global _global_prompt_manager_db
    
    if _global_prompt_manager_db:
        await _global_prompt_manager_db.reload_templates(category)
    else:
        logger.warning("全局Prompt管理器尚未初始化")

