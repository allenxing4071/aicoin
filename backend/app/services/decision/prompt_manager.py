"""
Prompt模板管理器 - 借鉴NOFX的成熟框架

核心设计理念：
1. 极简设计：使用Python原生字符串格式化，无需Jinja2
2. 文件即配置：.txt文件直接作为模板
3. 优雅降级：模板加载失败时自动回退到default或内置版本
4. 线程安全：使用RLock保护模板字典
"""

import os
import glob
import logging
import threading
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


@dataclass
class PromptTemplate:
    """Prompt模板数据类"""
    name: str                    # 模板名称（文件名，不含扩展名）
    category: str                # 类别（decision/debate/intelligence）
    content: str                 # 模板内容
    file_path: str              # 文件路径
    created_at: datetime         # 创建时间
    updated_at: datetime         # 更新时间
    
    def render(self, **variables) -> str:
        """
        渲染模板（使用Python原生字符串格式化）
        
        借鉴NOFX的做法：不使用Jinja2等复杂框架，直接使用字符串拼接
        这样更简单、更快、更易维护
        
        Args:
            **variables: 模板变量
        
        Returns:
            渲染后的字符串
        """
        try:
            # 使用format方法进行简单替换
            # 注意：这里不做复杂的模板语法，保持简单
            return self.content.format(**variables)
        except KeyError as e:
            logger.warning(f"模板变量缺失: {e}，将保留原始占位符")
            return self.content
        except Exception as e:
            logger.error(f"模板渲染失败: {e}")
            return self.content


class PromptManager:
    """
    Prompt模板管理器
    
    完全借鉴NOFX的实现（nofx/decision/prompt_manager.go）：
    - 从指定目录加载所有.txt文件
    - 支持按类别（category）和名称（name）获取模板
    - 支持热重载
    - 线程安全
    """
    
    def __init__(self, prompts_dir: str = "prompts"):
        """
        初始化Prompt管理器
        
        Args:
            prompts_dir: Prompt模板根目录（相对于backend/）
        """
        self.prompts_dir = prompts_dir
        self.templates: Dict[str, PromptTemplate] = {}  # key: "category/name"
        self._lock = threading.RLock()
        
        # 自动加载所有模板
        self._load_all_templates()
    
    def _load_all_templates(self) -> None:
        """加载所有类别的模板"""
        categories = ["decision", "debate", "intelligence"]
        
        for category in categories:
            try:
                self.load_templates(category)
            except Exception as e:
                logger.warning(f"加载类别 {category} 的模板失败: {e}")
    
    def load_templates(self, category: str) -> None:
        """
        从指定类别目录加载所有.txt模板
        
        完全借鉴NOFX的LoadTemplates方法
        
        Args:
            category: 类别名称（decision/debate/intelligence）
        """
        with self._lock:
            category_dir = os.path.join(self.prompts_dir, category)
            
            # 检查目录是否存在
            if not os.path.exists(category_dir):
                logger.warning(f"⚠️  Prompt目录不存在: {category_dir}")
                return
            
            # 扫描所有.txt文件
            pattern = os.path.join(category_dir, "*.txt")
            files = glob.glob(pattern)
            
            if not files:
                logger.warning(f"⚠️  类别 {category} 中没有找到.txt文件")
                return
            
            # 加载每个模板文件
            for file_path in files:
                try:
                    # 读取文件内容
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 提取文件名（不含扩展名）作为模板名称
                    file_name = os.path.basename(file_path)
                    template_name = os.path.splitext(file_name)[0]
                    
                    # 获取文件时间信息
                    stat = os.stat(file_path)
                    created_at = datetime.fromtimestamp(stat.st_ctime)
                    updated_at = datetime.fromtimestamp(stat.st_mtime)
                    
                    # 创建模板对象
                    template = PromptTemplate(
                        name=template_name,
                        category=category,
                        content=content,
                        file_path=file_path,
                        created_at=created_at,
                        updated_at=updated_at
                    )
                    
                    # 存储模板（key格式: "category/name"）
                    key = f"{category}/{template_name}"
                    self.templates[key] = template
                    
                    logger.info(f"  📄 加载Prompt模板: {key} ({file_name})")
                
                except Exception as e:
                    logger.error(f"⚠️  读取Prompt文件失败 {file_path}: {e}")
                    continue
            
            logger.info(f"✅ 已加载 {category} 类别的 {len([k for k in self.templates.keys() if k.startswith(category)])} 个模板")
    
    def get_template(self, category: str, name: str = "default") -> PromptTemplate:
        """
        获取指定模板
        
        完全借鉴NOFX的GetTemplate方法，支持优雅降级：
        1. 尝试获取指定模板
        2. 如果不存在，尝试获取default模板
        3. 如果default也不存在，返回内置简化版本
        
        Args:
            category: 类别名称
            name: 模板名称（默认为"default"）
        
        Returns:
            PromptTemplate对象
        """
        with self._lock:
            key = f"{category}/{name}"
            
            # 尝试获取指定模板
            if key in self.templates:
                return self.templates[key]
            
            # 如果不存在且不是default，尝试降级到default
            if name != "default":
                logger.warning(f"⚠️  模板 '{key}' 不存在，尝试使用 {category}/default")
                default_key = f"{category}/default"
                if default_key in self.templates:
                    return self.templates[default_key]
            
            # 如果连default都不存在，返回内置简化版本
            logger.error(f"❌ 无法加载任何模板（{key}），使用内置简化版本")
            return self._get_builtin_template(category, name)
    
    def _get_builtin_template(self, category: str, name: str) -> PromptTemplate:
        """
        获取内置简化版本模板（作为最后的fallback）
        
        Args:
            category: 类别名称
            name: 模板名称
        
        Returns:
            内置的PromptTemplate对象
        """
        builtin_contents = {
            "decision": "你是专业的加密货币交易AI。请根据市场数据做出交易决策。\n",
            "debate": "你是专业的市场分析师。请基于提供的数据进行分析。\n",
            "intelligence": "你是专业的情报分析师。请分析市场情报并提供洞察。\n"
        }
        
        content = builtin_contents.get(category, "你是专业的AI助手。\n")
        
        return PromptTemplate(
            name=name,
            category=category,
            content=content,
            file_path="<builtin>",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
    
    def list_templates(self, category: str) -> List[str]:
        """
        列出指定类别的所有模板名称
        
        Args:
            category: 类别名称
        
        Returns:
            模板名称列表
        """
        with self._lock:
            prefix = f"{category}/"
            names = [
                key.replace(prefix, "")
                for key in self.templates.keys()
                if key.startswith(prefix)
            ]
            return sorted(names)
    
    def reload_templates(self, category: Optional[str] = None) -> None:
        """
        重新加载模板（热重载）
        
        完全借鉴NOFX的ReloadTemplates方法
        
        Args:
            category: 指定类别（None表示重载所有类别）
        """
        with self._lock:
            if category:
                # 清空指定类别的模板
                keys_to_remove = [k for k in self.templates.keys() if k.startswith(f"{category}/")]
                for key in keys_to_remove:
                    del self.templates[key]
                
                # 重新加载
                self.load_templates(category)
                logger.info(f"🔄 已重新加载 {category} 类别的模板")
            else:
                # 清空所有模板
                self.templates.clear()
                
                # 重新加载所有类别
                self._load_all_templates()
                logger.info("🔄 已重新加载所有模板")
    
    def get_all_templates(self) -> List[PromptTemplate]:
        """
        获取所有模板
        
        Returns:
            所有PromptTemplate对象的列表
        """
        with self._lock:
            return list(self.templates.values())
    
    def template_exists(self, category: str, name: str) -> bool:
        """
        检查模板是否存在
        
        Args:
            category: 类别名称
            name: 模板名称
        
        Returns:
            是否存在
        """
        with self._lock:
            key = f"{category}/{name}"
            return key in self.templates


# 全局单例（借鉴NOFX的globalPromptManager）
_global_prompt_manager: Optional[PromptManager] = None
_global_lock = threading.Lock()


def get_global_prompt_manager(prompts_dir: str = "prompts") -> PromptManager:
    """
    获取全局Prompt管理器单例
    
    借鉴NOFX的全局管理器设计
    
    Args:
        prompts_dir: Prompt模板根目录
    
    Returns:
        全局PromptManager实例
    """
    global _global_prompt_manager
    
    with _global_lock:
        if _global_prompt_manager is None:
            _global_prompt_manager = PromptManager(prompts_dir)
            logger.info(f"✅ 初始化全局Prompt管理器（目录: {prompts_dir}）")
        
        return _global_prompt_manager


def reload_global_templates(category: Optional[str] = None) -> None:
    """
    重新加载全局模板（热重载）
    
    Args:
        category: 指定类别（None表示重载所有类别）
    """
    global _global_prompt_manager
    
    if _global_prompt_manager:
        _global_prompt_manager.reload_templates(category)
    else:
        logger.warning("全局Prompt管理器尚未初始化")

