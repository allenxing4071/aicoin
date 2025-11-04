"""Admin Memory System API - 三层记忆系统管理"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Dict, Any
import logging

from app.core.database import get_db
from app.core.redis_client import redis_client
from app.services.memory.short_term_memory import ShortTermMemory
from app.services.memory.long_term_memory import LongTermMemory
from app.core.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.get("/overview")
async def get_memory_overview(db: AsyncSession = Depends(get_db)) -> Dict[str, Any]:
    """
    获取三层记忆系统概览
    
    Returns:
        - L1 短期记忆 (Redis): 最近决策、当日统计
        - L2 长期记忆 (Qdrant): 向量数量、collection状态
        - L3 知识库 (PostgreSQL): 经验教训、策略评估、市场模式
    """
    try:
        # L1: 短期记忆 (Redis)
        short_memory = ShortTermMemory(redis_client)
        recent_decisions = await short_memory.get_recent_decisions(limit=100)
        
        # 获取今日交易次数（从Redis中查询）
        try:
            today_trade_count_raw = await redis_client.get("trading:today_count")
            today_trade_count = int(today_trade_count_raw) if today_trade_count_raw else 0
        except:
            today_trade_count = 0
        
        # L2: 长期记忆 (Qdrant) - 使用REST API绕过客户端版本兼容问题
        try:
            import requests
            qdrant_url = f"http://{settings.QDRANT_HOST}:{settings.QDRANT_PORT}/collections/trading_memories"
            logger.info(f"🔍 尝试连接Qdrant: {qdrant_url}")
            
            response = requests.get(qdrant_url, timeout=5)
            logger.info(f"📡 Qdrant响应状态: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                result = data.get("result", {})
                points_count = result.get("points_count", 0)
                vectors_count = result.get("vectors_count") or points_count
                
                logger.info(f"✅ Qdrant状态: points={points_count}, vectors={vectors_count}")
                
                # 计算索引大小
                index_size_mb = (vectors_count * 1536 * 4 / 1024 / 1024) if vectors_count else 0
                
                qdrant_status = {
                    "total_vectors": points_count,
                    "collection_status": "ready",  # collection存在且可用
                    "index_size_mb": round(index_size_mb, 2),
                    "last_updated": None
                }
            else:
                raise Exception(f"HTTP {response.status_code}")
        except Exception as e:
            logger.error(f"❌ Qdrant连接失败或collection不存在: {e}")
            import traceback
            logger.error(traceback.format_exc())
            qdrant_status = {
                "total_vectors": 0,
                "collection_status": "not_initialized",  # 未初始化
                "index_size_mb": 0,
                "last_updated": None
            }
        
        # L3: 知识库 (PostgreSQL)
        try:
            from app.models.knowledge import AILessonsLearned, AIStrategyEvaluation, MarketPattern
            from sqlalchemy import select, func
            
            # 统计经验教训数量
            lessons_stmt = select(func.count(AILessonsLearned.id))
            lessons_result = await db.execute(lessons_stmt)
            lessons_count = lessons_result.scalar() or 0
            
            # 统计策略评估数量
            strategies_stmt = select(func.count(AIStrategyEvaluation.id))
            strategies_result = await db.execute(strategies_stmt)
            strategies_count = strategies_result.scalar() or 0
            
            # 统计市场模式数量
            patterns_stmt = select(func.count(MarketPattern.id))
            patterns_result = await db.execute(patterns_stmt)
            patterns_count = patterns_result.scalar() or 0
        except Exception as e:
            logger.warning(f"知识库查询失败: {e}")
            lessons_count = 0
            strategies_count = 0
            patterns_count = 0
        
        return {
            "success": True,
            "data": {
                "short_term_memory": {
                    "recent_decisions_count": len(recent_decisions),
                    "today_trade_count": today_trade_count,
                    "performance_7d": None,  # TODO: 实现7日性能统计
                    "performance_30d": None  # TODO: 实现30日性能统计
                },
                "long_term_memory": qdrant_status,
                "knowledge_base_lessons": lessons_count,
                "knowledge_base_strategies": strategies_count,
                "knowledge_base_patterns": patterns_count
            }
        }
    
    except Exception as e:
        logger.error(f"获取记忆系统概览失败: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"获取记忆系统概览失败: {str(e)}")

