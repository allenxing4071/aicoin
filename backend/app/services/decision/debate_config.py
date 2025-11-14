"""
Debate Configuration Manager - 辩论配置管理
"""

from typing import Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import logging

from app.models.debate import DebateConfig

logger = logging.getLogger(__name__)


class DebateConfigManager:
    """辩论配置管理器"""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        self._config_cache: Dict[str, str] = {}
    
    async def get_config(self, key: str, default: str = "") -> str:
        """
        获取配置值
        
        Args:
            key: 配置键
            default: 默认值
        
        Returns:
            配置值
        """
        # 先从缓存获取
        if key in self._config_cache:
            return self._config_cache[key]
        
        try:
            stmt = select(DebateConfig).where(DebateConfig.config_key == key)
            result = await self.db_session.execute(stmt)
            config = result.scalars().first()
            
            if config:
                value = config.config_value
                self._config_cache[key] = value
                return value
            else:
                return default
                
        except Exception as e:
            logger.error(f"获取配置失败 {key}: {e}")
            return default
    
    async def set_config(self, key: str, value: str) -> bool:
        """
        设置配置值
        
        Args:
            key: 配置键
            value: 配置值
        
        Returns:
            是否成功
        """
        try:
            stmt = select(DebateConfig).where(DebateConfig.config_key == key)
            result = await self.db_session.execute(stmt)
            config = result.scalars().first()
            
            if config:
                config.config_value = value
            else:
                config = DebateConfig(config_key=key, config_value=value)
                self.db_session.add(config)
            
            await self.db_session.commit()
            
            # 更新缓存
            self._config_cache[key] = value
            
            logger.info(f"✅ 配置已更新: {key} = {value}")
            return True
            
        except Exception as e:
            logger.error(f"设置配置失败 {key}: {e}")
            await self.db_session.rollback()
            return False
    
    async def get_all_configs(self) -> Dict[str, str]:
        """获取所有配置"""
        try:
            stmt = select(DebateConfig)
            result = await self.db_session.execute(stmt)
            configs = result.scalars().all()
            
            return {config.config_key: config.config_value for config in configs}
            
        except Exception as e:
            logger.error(f"获取所有配置失败: {e}")
            return {}
    
    async def is_debate_enabled(self) -> bool:
        """判断辩论功能是否启用"""
        enabled = await self.get_config("debate_enabled", "false")
        return enabled.lower() == "true"
    
    async def get_max_debate_rounds(self) -> int:
        """获取最大辩论轮次"""
        rounds = await self.get_config("max_debate_rounds", "1")
        try:
            return int(rounds)
        except:
            return 1
    
    async def get_min_position_size(self) -> float:
        """获取触发辩论的最小仓位"""
        size = await self.get_config("min_position_size", "1000")
        try:
            return float(size)
        except:
            return 1000.0
    
    async def get_min_permission_level(self) -> str:
        """获取触发辩论的最低权限等级"""
        return await self.get_config("min_permission_level", "L3")
    
    async def get_debate_timeout(self) -> int:
        """获取辩论超时时间（秒）"""
        timeout = await self.get_config("debate_timeout_seconds", "60")
        try:
            return int(timeout)
        except:
            return 60
    
    async def should_use_memory(self) -> bool:
        """判断是否使用历史记忆"""
        use_memory = await self.get_config("use_memory", "true")
        return use_memory.lower() == "true"
    
    async def should_trigger_debate(self, account_state: Dict[str, Any]) -> bool:
        """
        判断是否应该触发辩论
        
        Args:
            account_state: 账户状态
        
        Returns:
            是否触发辩论
        """
        # 检查是否启用
        if not await self.is_debate_enabled():
            return False
        
        # 检查仓位大小
        position_size = account_state.get("position_size_usd", 0)
        min_size = await self.get_min_position_size()
        if position_size < min_size:
            return False
        
        # 检查权限等级
        permission_level = account_state.get("permission_level", "L1")
        min_level = await self.get_min_permission_level()
        
        # 权限等级比较（L0 < L1 < L2 < L3 < L4 < L5）
        level_order = ["L0", "L1", "L2", "L3", "L4", "L5"]
        try:
            current_idx = level_order.index(permission_level)
            min_idx = level_order.index(min_level)
            if current_idx < min_idx:
                return False
        except ValueError:
            return False
        
        return True
    
    def clear_cache(self):
        """清空配置缓存"""
        self._config_cache.clear()
        logger.info("🔄 配置缓存已清空")

