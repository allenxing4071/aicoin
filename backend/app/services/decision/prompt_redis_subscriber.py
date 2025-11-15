"""
Prompt Redis热重载订阅器
监听Redis的prompt_reload频道，自动重载Prompt
"""

import asyncio
import logging
import json
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.redis_client import RedisClient
from app.services.decision.prompt_manager_db import PromptManagerDB

logger = logging.getLogger(__name__)


class PromptRedisSubscriber:
    """
    Prompt Redis订阅器
    
    功能：
    1. 监听Redis的prompt_reload频道
    2. 收到消息后自动重载Prompt
    3. 支持全量重载和分类重载
    """
    
    def __init__(
        self,
        redis_client: RedisClient,
        prompt_manager: PromptManagerDB,
        db: AsyncSession
    ):
        self.redis_client = redis_client
        self.prompt_manager = prompt_manager
        self.db = db
        self.running = False
        self.task: Optional[asyncio.Task] = None
    
    async def start(self) -> None:
        """启动订阅器"""
        if self.running:
            logger.warning("Prompt Redis订阅器已在运行")
            return
        
        self.running = True
        self.task = asyncio.create_task(self._listen())
        logger.info("✅ Prompt Redis订阅器已启动")
    
    async def stop(self) -> None:
        """停止订阅器"""
        self.running = False
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass
        logger.info("⏹️  Prompt Redis订阅器已停止")
    
    async def _listen(self) -> None:
        """监听Redis消息"""
        try:
            # 创建pub/sub
            pubsub = self.redis_client.redis.pubsub()
            await pubsub.subscribe("prompt_reload")
            
            logger.info("📡 开始监听Redis prompt_reload频道")
            
            async for message in pubsub.listen():
                if not self.running:
                    break
                
                if message["type"] == "message":
                    await self._handle_message(message)
        
        except Exception as e:
            logger.error(f"Redis订阅器异常: {e}")
            if self.running:
                # 重试
                await asyncio.sleep(5)
                await self._listen()
    
    async def _handle_message(self, message: dict) -> None:
        """
        处理Redis消息
        
        消息格式：
        - "all": 重载所有Prompt
        - "decision": 重载decision类别
        - "debate": 重载debate类别
        - "intelligence": 重载intelligence类别
        """
        try:
            data = message["data"]
            
            # 解析消息
            if isinstance(data, bytes):
                data = data.decode('utf-8')
            
            if isinstance(data, str):
                try:
                    payload = json.loads(data)
                    category = payload.get("category")
                except json.JSONDecodeError:
                    category = data if data != "all" else None
            else:
                category = None
            
            # 重载Prompt
            logger.info(f"🔄 收到Prompt重载消息: {category or 'all'}")
            await self.prompt_manager.reload_templates(category)
            logger.info(f"✅ Prompt重载完成: {category or 'all'}")
        
        except Exception as e:
            logger.error(f"处理Prompt重载消息失败: {e}")


async def publish_prompt_reload(
    redis_client: RedisClient,
    category: Optional[str] = None
) -> None:
    """
    发布Prompt重载消息
    
    Args:
        redis_client: Redis客户端
        category: 类别（None表示重载所有）
    """
    try:
        message = json.dumps({"category": category}) if category else "all"
        await redis_client.redis.publish("prompt_reload", message)
        logger.info(f"📤 发布Prompt重载消息: {category or 'all'}")
    except Exception as e:
        logger.error(f"发布Prompt重载消息失败: {e}")

