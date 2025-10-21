"""Redis client for caching"""

import redis.asyncio as redis
from typing import Optional, Any
import json
from app.core.config import settings


class RedisClient:
    """Redis client wrapper"""
    
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
    
    async def connect(self):
        """Connect to Redis"""
        self.redis = await redis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True
        )
    
    async def disconnect(self):
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis:
            return None
        
        value = await self.redis.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    async def set(self, key: str, value: Any, expire: int = 3600):
        """Set value in cache"""
        if not self.redis:
            return False
        
        if isinstance(value, (dict, list)):
            value = json.dumps(value)
        
        await self.redis.setex(key, expire, value)
        return True
    
    async def delete(self, key: str):
        """Delete key from cache"""
        if not self.redis:
            return False
        
        await self.redis.delete(key)
        return True
    
    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.redis:
            return False
        
        return await self.redis.exists(key) > 0
    
    async def incr(self, key: str) -> int:
        """Increment counter"""
        if not self.redis:
            return 0
        
        return await self.redis.incr(key)
    
    async def expire(self, key: str, seconds: int):
        """Set expiration time"""
        if not self.redis:
            return False
        
        await self.redis.expire(key, seconds)
        return True


# Global Redis client instance
redis_client = RedisClient()


async def get_redis() -> RedisClient:
    """Get Redis client instance"""
    return redis_client

