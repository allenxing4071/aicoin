"""
Prompt性能长期记忆（Qdrant）
存储Prompt + 市场环境 + 决策结果的向量表示
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import json
import numpy as np
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

logger = logging.getLogger(__name__)


class PromptPerformanceMemory:
    """
    Prompt性能长期记忆（Qdrant）
    
    功能：
    1. 存储Prompt决策的向量表示
    2. 搜索相似市场环境下的Prompt表现
    3. 智能推荐最佳Prompt
    """
    
    COLLECTION_NAME = "prompt_performance_vectors"
    VECTOR_SIZE = 384  # 向量维度（假设使用sentence-transformers）
    
    def __init__(self, qdrant_client: QdrantClient):
        self.client = qdrant_client
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self):
        """确保Collection存在"""
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.COLLECTION_NAME not in collection_names:
                self.client.create_collection(
                    collection_name=self.COLLECTION_NAME,
                    vectors_config=VectorParams(
                        size=self.VECTOR_SIZE,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"✅ 创建Qdrant Collection: {self.COLLECTION_NAME}")
        
        except Exception as e:
            logger.error(f"创建Qdrant Collection失败: {e}")
    
    async def store_prompt_decision(
        self,
        decision_id: str,
        prompt_template_id: int,
        prompt_version: int,
        prompt_content: str,
        permission_level: str,
        market_data: Dict[str, Any],
        decision: Dict[str, Any]
    ) -> bool:
        """
        存储Prompt决策到Qdrant
        
        Args:
            decision_id: 决策ID
            prompt_template_id: Prompt模板ID
            prompt_version: Prompt版本
            prompt_content: Prompt内容
            permission_level: 权限等级
            market_data: 市场数据
            decision: 决策结果
        
        Returns:
            是否成功
        """
        try:
            # 1. 生成向量（这里简化为随机向量，实际应使用embedding模型）
            vector = self._generate_embedding(prompt_content, market_data)
            
            # 2. 构建payload
            payload = {
                "decision_id": decision_id,
                "prompt_template_id": prompt_template_id,
                "prompt_version": prompt_version,
                "permission_level": permission_level,
                "market_price": market_data.get("price"),
                "market_volatility": market_data.get("volatility"),
                "action": decision.get("action"),
                "confidence": decision.get("confidence"),
                "timestamp": datetime.now().isoformat()
            }
            
            # 3. 存储到Qdrant
            point = PointStruct(
                id=hash(decision_id) % (10 ** 8),  # 简化的ID生成
                vector=vector.tolist(),
                payload=payload
            )
            
            self.client.upsert(
                collection_name=self.COLLECTION_NAME,
                points=[point]
            )
            
            logger.debug(f"存储Prompt决策到Qdrant: {decision_id}")
            
            return True
        
        except Exception as e:
            logger.error(f"存储Prompt决策失败: {e}")
            return False
    
    def _generate_embedding(
        self,
        prompt_content: str,
        market_data: Dict[str, Any]
    ) -> np.ndarray:
        """
        生成Prompt + 市场数据的向量表示
        
        实际应使用：
        - sentence-transformers
        - OpenAI embeddings
        - 自定义embedding模型
        
        这里简化为随机向量
        """
        # TODO: 集成真实的embedding模型
        return np.random.rand(self.VECTOR_SIZE)
    
    async def search_similar_scenarios(
        self,
        current_market_data: Dict[str, Any],
        permission_level: str,
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """
        搜索相似市场环境下的Prompt表现
        
        Args:
            current_market_data: 当前市场数据
            permission_level: 权限等级
            limit: 返回数量
        
        Returns:
            相似场景列表
        """
        try:
            # 1. 生成查询向量
            query_vector = self._generate_embedding("", current_market_data)
            
            # 2. 搜索
            results = self.client.search(
                collection_name=self.COLLECTION_NAME,
                query_vector=query_vector.tolist(),
                limit=limit,
                query_filter={
                    "must": [
                        {"key": "permission_level", "match": {"value": permission_level}}
                    ]
                }
            )
            
            # 3. 格式化结果
            scenarios = []
            for result in results:
                scenarios.append({
                    "score": result.score,
                    "payload": result.payload
                })
            
            return scenarios
        
        except Exception as e:
            logger.error(f"搜索相似场景失败: {e}")
            return []
    
    async def recommend_best_prompt(
        self,
        current_market_data: Dict[str, Any],
        permission_level: str
    ) -> Optional[Dict[str, Any]]:
        """
        智能推荐最佳Prompt
        
        基于：
        1. 相似市场环境
        2. 历史表现
        3. 权限等级匹配
        
        Args:
            current_market_data: 当前市场数据
            permission_level: 权限等级
        
        Returns:
            推荐的Prompt信息
        """
        try:
            # 搜索相似场景
            scenarios = await self.search_similar_scenarios(
                current_market_data,
                permission_level,
                limit=20
            )
            
            if not scenarios:
                return None
            
            # 统计各Prompt的表现
            prompt_stats = {}
            for scenario in scenarios:
                prompt_id = scenario["payload"]["prompt_template_id"]
                
                if prompt_id not in prompt_stats:
                    prompt_stats[prompt_id] = {
                        "count": 0,
                        "total_confidence": 0,
                        "total_score": 0
                    }
                
                prompt_stats[prompt_id]["count"] += 1
                prompt_stats[prompt_id]["total_confidence"] += scenario["payload"].get("confidence", 0)
                prompt_stats[prompt_id]["total_score"] += scenario["score"]
            
            # 选择最佳Prompt
            best_prompt_id = None
            best_score = 0
            
            for prompt_id, stats in prompt_stats.items():
                avg_confidence = stats["total_confidence"] / stats["count"]
                avg_similarity = stats["total_score"] / stats["count"]
                
                # 综合评分
                score = avg_confidence * 0.6 + avg_similarity * 0.4
                
                if score > best_score:
                    best_score = score
                    best_prompt_id = prompt_id
            
            if best_prompt_id:
                return {
                    "prompt_template_id": best_prompt_id,
                    "confidence_score": best_score,
                    "sample_count": prompt_stats[best_prompt_id]["count"]
                }
            
            return None
        
        except Exception as e:
            logger.error(f"推荐最佳Prompt失败: {e}")
            return None

