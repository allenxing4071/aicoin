"""
Debate Memory System - 基于 Qdrant 的辩论记忆系统
借鉴 TradingAgents 的 FinancialSituationMemory，使用 AIcoin 现有的 Qdrant
"""

import uuid
from typing import List, Dict, Tuple
from datetime import datetime
import logging

from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
import openai

logger = logging.getLogger(__name__)


class DebateMemory:
    """
    辩论记忆系统
    完全复用 TradingAgents 的 FinancialSituationMemory 逻辑，适配 Qdrant
    """
    
    def __init__(
        self,
        collection_name: str,
        qdrant_client: QdrantClient,
        embedding_client: openai.OpenAI,
        embedding_model: str = "text-embedding-3-small"
    ):
        """
        初始化记忆系统
        
        Args:
            collection_name: 记忆集合名称（如 "bull_memory", "bear_memory"）
            qdrant_client: Qdrant 客户端
            embedding_client: OpenAI 客户端（用于 embedding）
            embedding_model: Embedding 模型名称
        """
        self.collection_name = collection_name
        self.client = qdrant_client
        self.embedding_client = embedding_client
        self.embedding_model = embedding_model
        
        # 创建集合（如果不存在）
        self._ensure_collection()
        
        logger.info(f"✅ 辩论记忆系统初始化: {collection_name}")
    
    def _ensure_collection(self):
        """确保集合存在"""
        try:
            collections = self.client.get_collections().collections
            collection_names = [c.name for c in collections]
            
            if self.collection_name not in collection_names:
                self.client.create_collection(
                    collection_name=self.collection_name,
                    vectors_config=VectorParams(
                        size=1536,  # text-embedding-3-small 的维度
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"📦 创建新集合: {self.collection_name}")
        except Exception as e:
            logger.warning(f"集合检查/创建失败: {e}")
    
    def get_embedding(self, text: str) -> List[float]:
        """
        获取文本的向量表示
        完全复用 TradingAgents 的实现
        
        Args:
            text: 输入文本
        
        Returns:
            向量列表
        """
        try:
            response = self.embedding_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"获取 embedding 失败: {e}")
            # 返回零向量作为后备
            return [0.0] * 1536
    
    def add_memory(self, situation: str, recommendation: str):
        """
        添加单条记忆
        
        Args:
            situation: 市场情况描述
            recommendation: 建议或经验教训
        """
        self.add_memories([(situation, recommendation)])
    
    def add_memories(self, situations_and_advice: List[Tuple[str, str]]):
        """
        批量添加记忆
        完全复用 TradingAgents 的实现
        
        Args:
            situations_and_advice: [(situation, recommendation), ...]
        """
        try:
            points = []
            
            for situation, recommendation in situations_and_advice:
                # 获取 embedding
                embedding = self.get_embedding(situation)
                
                # 创建点
                point = PointStruct(
                    id=str(uuid.uuid4()),
                    vector=embedding,
                    payload={
                        "situation": situation,
                        "recommendation": recommendation,
                        "timestamp": datetime.now().isoformat()
                    }
                )
                points.append(point)
            
            # 批量插入
            self.client.upsert(
                collection_name=self.collection_name,
                points=points
            )
            
            logger.info(f"📝 添加 {len(situations_and_advice)} 条记忆到 {self.collection_name}")
            
        except Exception as e:
            logger.error(f"添加记忆失败: {e}", exc_info=True)
    
    def search_memories(self, query: str, limit: int = 2) -> List[Dict]:
        """
        检索相似的历史记忆
        完全复用 TradingAgents 的实现
        
        Args:
            query: 当前市场情况描述
            limit: 返回最相似的 N 条记忆
        
        Returns:
            [
                {
                    "matched_situation": "...",
                    "recommendation": "...",
                    "similarity_score": 0.85
                },
                ...
            ]
        """
        try:
            # 获取查询向量
            query_embedding = self.get_embedding(query)
            
            # 搜索相似记忆
            results = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_embedding,
                limit=limit
            )
            
            matched_results = []
            for hit in results:
                matched_results.append({
                    "matched_situation": hit.payload.get("situation", ""),
                    "recommendation": hit.payload.get("recommendation", ""),
                    "similarity_score": hit.score
                })
            
            logger.info(f"🔍 检索到 {len(matched_results)} 条相似记忆 from {self.collection_name}")
            
            return matched_results
            
        except Exception as e:
            logger.error(f"检索记忆失败: {e}", exc_info=True)
            return []
    
    def get_memory_count(self) -> int:
        """获取记忆数量"""
        try:
            collection_info = self.client.get_collection(self.collection_name)
            return collection_info.points_count
        except:
            return 0
    
    def clear_memories(self):
        """清空所有记忆（危险操作）"""
        try:
            self.client.delete_collection(self.collection_name)
            self._ensure_collection()
            logger.warning(f"🗑️  清空记忆集合: {self.collection_name}")
        except Exception as e:
            logger.error(f"清空记忆失败: {e}")


class DebateMemoryManager:
    """
    管理多个角色的记忆
    为 Bull/Bear/Manager 分别维护独立记忆空间
    """
    
    def __init__(
        self,
        qdrant_client: QdrantClient,
        embedding_client: openai.OpenAI,
        embedding_model: str = "text-embedding-3-small"
    ):
        """
        初始化记忆管理器
        
        Args:
            qdrant_client: Qdrant 客户端
            embedding_client: OpenAI 客户端
            embedding_model: Embedding 模型
        """
        self.bull_memory = DebateMemory(
            "debate_bull_memory",
            qdrant_client,
            embedding_client,
            embedding_model
        )
        self.bear_memory = DebateMemory(
            "debate_bear_memory",
            qdrant_client,
            embedding_client,
            embedding_model
        )
        self.manager_memory = DebateMemory(
            "debate_manager_memory",
            qdrant_client,
            embedding_client,
            embedding_model
        )
        
        logger.info("✅ 辩论记忆管理器初始化完成")
    
    def get_bull_memories(self, situation: str, n: int = 2) -> List[Dict]:
        """获取多头分析师的历史记忆"""
        return self.bull_memory.search_memories(situation, n)
    
    def get_bear_memories(self, situation: str, n: int = 2) -> List[Dict]:
        """获取空头分析师的历史记忆"""
        return self.bear_memory.search_memories(situation, n)
    
    def get_manager_memories(self, situation: str, n: int = 2) -> List[Dict]:
        """获取研究经理的历史记忆"""
        return self.manager_memory.search_memories(situation, n)
    
    def add_debate_outcome(
        self,
        situation: str,
        bull_argument: str,
        bear_argument: str,
        final_decision: str,
        actual_outcome: str
    ):
        """
        添加辩论结果到记忆
        
        Args:
            situation: 市场情况描述
            bull_argument: 多头论点
            bear_argument: 空头论点
            final_decision: 最终决策
            actual_outcome: 实际结果（盈利/亏损）
        """
        # 为 Bull 添加记忆
        bull_recommendation = f"In similar situation, bull argued: {bull_argument[:200]}... Final decision: {final_decision}. Outcome: {actual_outcome}"
        self.bull_memory.add_memory(situation, bull_recommendation)
        
        # 为 Bear 添加记忆
        bear_recommendation = f"In similar situation, bear argued: {bear_argument[:200]}... Final decision: {final_decision}. Outcome: {actual_outcome}"
        self.bear_memory.add_memory(situation, bear_recommendation)
        
        # 为 Manager 添加记忆
        manager_recommendation = f"Debate summary - Bull: {bull_argument[:100]}... Bear: {bear_argument[:100]}... Decision: {final_decision}. Outcome: {actual_outcome}"
        self.manager_memory.add_memory(situation, manager_recommendation)
        
        logger.info(f"💾 辩论结果已保存到记忆系统")
    
    def get_memory_stats(self) -> Dict[str, int]:
        """获取记忆统计"""
        return {
            "bull_memory_count": self.bull_memory.get_memory_count(),
            "bear_memory_count": self.bear_memory.get_memory_count(),
            "manager_memory_count": self.manager_memory.get_memory_count(),
            "total_memory_count": (
                self.bull_memory.get_memory_count() +
                self.bear_memory.get_memory_count() +
                self.manager_memory.get_memory_count()
            )
        }
    
    def clear_all_memories(self):
        """清空所有记忆（危险操作）"""
        self.bull_memory.clear_memories()
        self.bear_memory.clear_memories()
        self.manager_memory.clear_memories()
        logger.warning("🗑️  清空所有辩论记忆")

