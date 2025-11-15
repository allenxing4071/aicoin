"""
短期记忆扩展 - Prompt追踪
扩展现有ShortTermMemory以支持Prompt使用信息追踪
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json

from app.core.redis_client import RedisClient

logger = logging.getLogger(__name__)


class PromptMemoryExtension:
    """
    Prompt记忆扩展（Redis）
    追踪Prompt使用信息、版本、权限等级
    """
    
    # Redis Key前缀
    KEY_PROMPT_RECENT_DECISIONS = "prompt:recent_decisions:"  # List
    KEY_PROMPT_PERFORMANCE = "prompt:performance:"  # Hash
    KEY_PROMPT_USAGE_COUNT = "prompt:usage_count:"  # String
    
    # 数据保留时间
    TTL = 86400 * 7  # 7天
    
    def __init__(self, redis_client: RedisClient):
        self.redis = redis_client
    
    async def record_prompt_usage(
        self,
        decision_id: str,
        prompt_template_id: int,
        prompt_version: int,
        permission_level: str,
        timestamp: datetime,
        market_data: Dict[str, Any],
        decision_result: Dict[str, Any]
    ) -> bool:
        """
        记录Prompt使用信息
        
        Args:
            decision_id: 决策ID
            prompt_template_id: Prompt模板ID
            prompt_version: Prompt版本号
            permission_level: 权限等级
            timestamp: 时间戳
            market_data: 市场数据
            decision_result: 决策结果
        
        Returns:
            是否成功
        """
        try:
            # 1. 记录到Prompt的最近决策列表
            prompt_key = f"{self.KEY_PROMPT_RECENT_DECISIONS}{prompt_template_id}"
            
            usage_data = {
                "decision_id": decision_id,
                "prompt_version": prompt_version,
                "permission_level": permission_level,
                "timestamp": timestamp.isoformat(),
                "action": decision_result.get("action"),
                "confidence": decision_result.get("confidence"),
                "market_price": market_data.get("price")
            }
            
            await self.redis.redis.lpush(prompt_key, json.dumps(usage_data))
            await self.redis.redis.ltrim(prompt_key, 0, 99)  # 保留最近100条
            await self.redis.redis.expire(prompt_key, self.TTL)
            
            # 2. 增加使用计数
            count_key = f"{self.KEY_PROMPT_USAGE_COUNT}{prompt_template_id}"
            await self.redis.redis.incr(count_key)
            await self.redis.redis.expire(count_key, self.TTL)
            
            logger.debug(f"记录Prompt使用: template_id={prompt_template_id}, decision_id={decision_id}")
            
            return True
        
        except Exception as e:
            logger.error(f"记录Prompt使用失败: {e}")
            return False
    
    async def get_prompt_recent_performance(
        self,
        prompt_template_id: int,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        获取Prompt的最近表现
        
        Args:
            prompt_template_id: Prompt模板ID
            limit: 返回数量限制
        
        Returns:
            最近的决策列表
        """
        try:
            prompt_key = f"{self.KEY_PROMPT_RECENT_DECISIONS}{prompt_template_id}"
            
            # 获取最近的决策
            decisions = await self.redis.redis.lrange(prompt_key, 0, limit - 1)
            
            result = []
            for decision_json in decisions:
                if isinstance(decision_json, bytes):
                    decision_json = decision_json.decode('utf-8')
                result.append(json.loads(decision_json))
            
            return result
        
        except Exception as e:
            logger.error(f"获取Prompt最近表现失败: {e}")
            return []
    
    async def get_prompt_usage_count(
        self,
        prompt_template_id: int
    ) -> int:
        """
        获取Prompt的使用次数（7天内）
        
        Args:
            prompt_template_id: Prompt模板ID
        
        Returns:
            使用次数
        """
        try:
            count_key = f"{self.KEY_PROMPT_USAGE_COUNT}{prompt_template_id}"
            count = await self.redis.redis.get(count_key)
            return int(count) if count else 0
        
        except Exception as e:
            logger.error(f"获取Prompt使用次数失败: {e}")
            return 0
    
    async def update_prompt_performance(
        self,
        prompt_template_id: int,
        pnl: float,
        is_win: bool
    ) -> bool:
        """
        更新Prompt性能指标
        
        Args:
            prompt_template_id: Prompt模板ID
            pnl: 盈亏
            is_win: 是否盈利
        
        Returns:
            是否成功
        """
        try:
            perf_key = f"{self.KEY_PROMPT_PERFORMANCE}{prompt_template_id}"
            
            # 使用Hash存储性能指标
            await self.redis.redis.hincrby(perf_key, "total_decisions", 1)
            
            if is_win:
                await self.redis.redis.hincrby(perf_key, "winning_decisions", 1)
            
            # 累加盈亏
            current_pnl = await self.redis.redis.hget(perf_key, "total_pnl")
            current_pnl = float(current_pnl) if current_pnl else 0.0
            new_pnl = current_pnl + pnl
            await self.redis.redis.hset(perf_key, "total_pnl", str(new_pnl))
            
            # 设置过期时间
            await self.redis.redis.expire(perf_key, self.TTL)
            
            return True
        
        except Exception as e:
            logger.error(f"更新Prompt性能失败: {e}")
            return False

