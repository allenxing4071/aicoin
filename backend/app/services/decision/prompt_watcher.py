"""
Prompt文件监控器 - 实现热重载

借鉴NOFX的设计理念，但使用Python的watchdog库实现文件监控
"""

import logging
import time
from pathlib import Path
from typing import Optional
from threading import Thread

try:
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler
    WATCHDOG_AVAILABLE = True
except ImportError:
    WATCHDOG_AVAILABLE = False
    logging.warning("watchdog库未安装，热重载功能将不可用。安装: pip install watchdog")

from app.services.decision.prompt_manager import reload_global_templates

logger = logging.getLogger(__name__)


class PromptFileHandler(FileSystemEventHandler):
    """
    Prompt文件变化处理器
    
    监听.txt文件的修改事件，自动触发热重载
    """
    
    def __init__(self, debounce_seconds: float = 1.0):
        """
        初始化文件处理器
        
        Args:
            debounce_seconds: 防抖时间（秒），避免频繁重载
        """
        super().__init__()
        self.debounce_seconds = debounce_seconds
        self.last_reload_time = 0
    
    def on_modified(self, event):
        """文件修改事件"""
        if event.is_directory:
            return
        
        # 只处理.txt文件
        if not event.src_path.endswith('.txt'):
            return
        
        # 防抖：避免短时间内多次重载
        current_time = time.time()
        if current_time - self.last_reload_time < self.debounce_seconds:
            return
        
        self.last_reload_time = current_time
        
        try:
            # 提取类别（从路径中）
            path = Path(event.src_path)
            category = path.parent.name
            
            logger.info(f"🔄 检测到Prompt文件变化: {event.src_path}")
            logger.info(f"🔄 重新加载 {category} 类别的模板...")
            
            # 热重载
            reload_global_templates(category)
            
            logger.info(f"✅ 热重载完成: {category}")
        
        except Exception as e:
            logger.error(f"❌ 热重载失败: {e}", exc_info=True)


class PromptWatcher:
    """
    Prompt文件监控器
    
    借鉴NOFX的热重载设计，使用watchdog实现文件监控
    """
    
    def __init__(self, prompts_dir: str, debounce_seconds: float = 1.0):
        """
        初始化监控器
        
        Args:
            prompts_dir: Prompt模板目录
            debounce_seconds: 防抖时间（秒）
        """
        if not WATCHDOG_AVAILABLE:
            logger.warning("⚠️  watchdog库未安装，热重载功能不可用")
            self.observer = None
            return
        
        self.prompts_dir = prompts_dir
        self.event_handler = PromptFileHandler(debounce_seconds)
        self.observer = Observer()
        self.observer.schedule(self.event_handler, prompts_dir, recursive=True)
        self._running = False
    
    def start(self):
        """启动监控"""
        if not WATCHDOG_AVAILABLE or self.observer is None:
            logger.warning("⚠️  热重载功能不可用")
            return
        
        if self._running:
            logger.warning("⚠️  监控器已经在运行")
            return
        
        try:
            self.observer.start()
            self._running = True
            logger.info(f"✅ Prompt文件监控已启动: {self.prompts_dir}")
        except Exception as e:
            logger.error(f"❌ 启动监控器失败: {e}")
    
    def stop(self):
        """停止监控"""
        if not WATCHDOG_AVAILABLE or self.observer is None:
            return
        
        if not self._running:
            return
        
        try:
            self.observer.stop()
            self.observer.join(timeout=5)
            self._running = False
            logger.info("✅ Prompt文件监控已停止")
        except Exception as e:
            logger.error(f"❌ 停止监控器失败: {e}")
    
    def is_running(self) -> bool:
        """检查监控器是否运行中"""
        return self._running


# 全局监控器实例
_global_watcher: Optional[PromptWatcher] = None


def start_global_watcher(prompts_dir: str, debounce_seconds: float = 1.0):
    """
    启动全局Prompt文件监控器
    
    Args:
        prompts_dir: Prompt模板目录
        debounce_seconds: 防抖时间（秒）
    """
    global _global_watcher
    
    if _global_watcher is not None and _global_watcher.is_running():
        logger.warning("⚠️  全局监控器已经在运行")
        return
    
    _global_watcher = PromptWatcher(prompts_dir, debounce_seconds)
    _global_watcher.start()


def stop_global_watcher():
    """停止全局Prompt文件监控器"""
    global _global_watcher
    
    if _global_watcher is not None:
        _global_watcher.stop()
        _global_watcher = None

