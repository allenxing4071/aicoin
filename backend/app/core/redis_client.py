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
    
    async def zadd(self, key: str, mapping: dict, **kwargs):
        """Add members to sorted set"""
        if not self.redis:
            return 0
        return await self.redis.zadd(key, mapping, **kwargs)
    
    async def zrevrangebyscore(self, key: str, max_score: float, min_score: float, start: int = 0, num: int = -1, withscores: bool = False):
        """Get members from sorted set by score in reverse order"""
        if not self.redis:
            return []
        return await self.redis.zrevrangebyscore(key, max_score, min_score, start=start, num=num, withscores=withscores)
    
    async def hset(self, key: str, mapping: dict = None, **kwargs):
        """Set hash field"""
        if not self.redis:
            return 0
        if mapping:
            return await self.redis.hset(key, mapping=mapping)
        return await self.redis.hset(key, **kwargs)
    
    async def hget(self, key: str, field: str):
        """Get hash field value"""
        if not self.redis:
            return None
        value = await self.redis.hget(key, field)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None
    
    async def hgetall(self, key: str) -> dict:
        """Get all hash fields"""
        if not self.redis:
            return {}
        return await self.redis.hgetall(key)
    
    async def lpush(self, key: str, *values) -> int:
        """Push values to the head of a list"""
        if not self.redis:
            return 0
        return await self.redis.lpush(key, *values)
    
    async def lrange(self, key: str, start: int, end: int) -> list:
        """Get a range of elements from a list"""
        if not self.redis:
            return []
        return await self.redis.lrange(key, start, end)
    
    async def ltrim(self, key: str, start: int, end: int) -> bool:
        """Trim a list to the specified range"""
        if not self.redis:
            return False
        await self.redis.ltrim(key, start, end)
        return True


# Global Redis client instance
redis_client = RedisClient()


async def get_redis() -> RedisClient:
    """Get Redis client instance"""
    return redis_client

