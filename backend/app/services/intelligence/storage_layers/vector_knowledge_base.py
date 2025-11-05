"""Intelligence Vector Knowledge Base - Qwen情报员向量知识库（Qdrant）"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition

logger = logging.getLogger(__name__)


class IntelligenceVectorKB:
    """
    Qwen情报员向量知识库（Layer 4）
    
    职责：
    1. 向量化情报内容
    2. 语义相似度检索
    3. 情报模式识别
    4. 知识积累与复用
    
    存储介质：Qdrant向量数据库
    保留策略：永久保存，支持版本管理
    """
    
    def __init__(
        self,
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
        collection_name: str = "intelligence_knowledge",
        embedding_provider: str = "qwen"
    ):
        """
        初始化向量知识库
        
        Args:
            qdrant_host: Qdrant主机
            qdrant_port: Qdrant端口
            collection_name: 集合名称
            embedding_provider: embedding提供者（qwen/deepseek/openai）
        """
        self.client = QdrantClient(host=qdrant_host, port=qdrant_port)
        self.collection_name = collection_name
        self.embedding_provider = embedding_provider
        self.vector_size = 1536  # OpenAI/DeepSeek标准维度
        
        # 初始化collection
        self._init_collection()
        
        logger.info(f"✅ Qwen情报向量知识库初始化完成 (provider={embedding_provider})")
    
    def _init_collection(self):
        """初始化向量集合"""
        try:
            self.client.get_collection(self.collection_name)
            logger.info(f"✓ Collection '{self.collection_name}' 已存在")
        except:
            # 创建collection
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=self.vector_size,
                    distance=Distance.COSINE
                )
            )
            logger.info(f"✓ Collection '{self.collection_name}' 已创建")
    
    async def vectorize_intelligence(
        self,
        intelligence_id: str,
        content: str,
        metadata: Dict[str, Any]
    ) -> bool:
        """
        向量化情报内容
        
        Args:
            intelligence_id: 情报ID
            content: 情报文本内容
            metadata: 元数据（源、类型、时间等）
        
        Returns:
            是否向量化成功
        """
        try:
            # 生成embedding向量
            vector = await self._generate_embedding(content)
            
            if not vector:
                logger.warning(f"⚠️ 无法生成向量: {intelligence_id}")
                return False
            
            # 构建payload
            payload = {
                "intelligence_id": intelligence_id,
                "content": content[:500],  # 只存储前500字符
                "source": metadata.get("source", "unknown"),
                "category": metadata.get("category", "general"),
                "sentiment": metadata.get("sentiment", "neutral"),
                "importance": metadata.get("importance", 0.5),
                "timestamp": metadata.get("timestamp", datetime.now()).isoformat(),
                "vectorized_at": datetime.now().isoformat()
            }
            
            # 存储到Qdrant
            point = PointStruct(
                id=abs(hash(intelligence_id)) % (2**63),
                vector=vector,
                payload=payload
            )
            
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            logger.debug(f"✅ 情报已向量化: {intelligence_id}")
            return True
            
        except Exception as e:
            logger.error(f"❌ 向量化失败: {e}", exc_info=True)
            return False
    
    async def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """
        生成embedding向量
        
        Args:
            text: 输入文本
        
        Returns:
            向量列表
        """
        try:
            if self.embedding_provider == "qwen":
                return await self._qwen_embedding(text)
            elif self.embedding_provider == "deepseek":
                return await self._deepseek_embedding(text)
            elif self.embedding_provider == "openai":
                return await self._openai_embedding(text)
            else:
                # 默认使用模拟向量（开发环境）
                import random
                return [random.random() for _ in range(self.vector_size)]
                
        except Exception as e:
            logger.error(f"❌ 生成embedding失败: {e}")
            return None
    
    async def _qwen_embedding(self, text: str) -> Optional[List[float]]:
        """使用Qwen生成embedding"""
        try:
            # TODO: 调用Qwen embedding API
            # 参考：https://help.aliyun.com/document_detail/2712195.html
            logger.warning("⚠️ Qwen embedding暂未实现，使用模拟向量")
            import random
            return [random.random() for _ in range(self.vector_size)]
        except Exception as e:
            logger.error(f"Qwen embedding失败: {e}")
            return None
    
    async def _deepseek_embedding(self, text: str) -> Optional[List[float]]:
        """使用DeepSeek生成embedding"""
        try:
            # TODO: 调用DeepSeek embedding API（如果支持）
            logger.warning("⚠️ DeepSeek embedding暂未实现，使用模拟向量")
            import random
            return [random.random() for _ in range(self.vector_size)]
        except Exception as e:
            logger.error(f"DeepSeek embedding失败: {e}")
            return None
    
    async def _openai_embedding(self, text: str) -> Optional[List[float]]:
        """使用OpenAI生成embedding"""
        try:
            import openai
            from app.core.config import settings
            
            client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
            response = await client.embeddings.create(
                input=text,
                model="text-embedding-3-small"
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI embedding失败: {e}")
            return None
    
    async def search_similar(
        self,
        query_text: str,
        limit: int = 10,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        搜索相似情报
        
        Args:
            query_text: 查询文本
            limit: 返回数量
            filters: 过滤条件（可选）
        
        Returns:
            相似情报列表
        """
        try:
            # 生成查询向量
            query_vector = await self._generate_embedding(query_text)
            
            if not query_vector:
                logger.warning("无法生成查询向量")
                return []
            
            # 构建过滤条件
            query_filter = None
            if filters:
                conditions = []
                for key, value in filters.items():
                    conditions.append(
                        FieldCondition(key=key, match={"value": value})
                    )
                if conditions:
                    query_filter = Filter(must=conditions)
            
            # 向量搜索
            search_result = self.client.search(
                collection_name=self.collection_name,
                query_vector=query_vector,
                query_filter=query_filter,
                limit=limit,
                with_payload=True
            )
            
            # 格式化结果
            similar_items = []
            for hit in search_result:
                similar_items.append({
                    "intelligence_id": hit.payload.get("intelligence_id"),
                    "similarity_score": hit.score,
                    "content": hit.payload.get("content", ""),
                    "source": hit.payload.get("source", ""),
                    "category": hit.payload.get("category", ""),
                    "sentiment": hit.payload.get("sentiment", ""),
                    "importance": hit.payload.get("importance", 0.0),
                    "timestamp": hit.payload.get("timestamp", "")
                })
            
            logger.info(f"✅ 找到 {len(similar_items)} 个相似情报")
            return similar_items
            
        except Exception as e:
            logger.error(f"❌ 相似度搜索失败: {e}", exc_info=True)
            return []
    
    async def get_knowledge_stats(self) -> Dict[str, Any]:
        """
        获取知识库统计信息
        
        Returns:
            统计数据
        """
        try:
            collection_info = self.client.get_collection(self.collection_name)
            
            return {
                "collection_name": self.collection_name,
                "total_vectors": collection_info.points_count,
                "vector_size": self.vector_size,
                "embedding_provider": self.embedding_provider,
                "status": collection_info.status
            }
            
        except Exception as e:
            logger.error(f"❌ 获取统计信息失败: {e}")
            return {}
    
    async def find_patterns(
        self,
        category: str,
        min_importance: float = 0.7,
        days: int = 30
    ) -> List[Dict[str, Any]]:
        """
        查找情报模式
        
        Args:
            category: 类别
            min_importance: 最小重要性
            days: 天数范围
        
        Returns:
            模式列表
        """
        try:
            from datetime import timedelta
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # 使用scroll API遍历所有符合条件的记录
            patterns = []
            offset = None
            
            while True:
                response = self.client.scroll(
                    collection_name=self.collection_name,
                    scroll_filter=Filter(
                        must=[
                            FieldCondition(key="category", match={"value": category}),
                            FieldCondition(key="importance", range={"gte": min_importance}),
                            FieldCondition(key="timestamp", range={"gte": cutoff_date})
                        ]
                    ),
                    limit=100,
                    offset=offset,
                    with_payload=True
                )
                
                for point in response[0]:
                    patterns.append({
                        "intelligence_id": point.payload.get("intelligence_id"),
                        "content": point.payload.get("content", ""),
                        "importance": point.payload.get("importance", 0.0),
                        "timestamp": point.payload.get("timestamp", "")
                    })
                
                if response[1] is None:  # 没有更多记录
                    break
                offset = response[1]
            
            logger.info(f"✅ 找到 {len(patterns)} 个模式")
            return patterns
            
        except Exception as e:
            logger.error(f"❌ 查找模式失败: {e}")
            return []
    
    async def delete_old_vectors(self, days: int = 90) -> int:
        """
        删除旧向量
        
        Args:
            days: 保留天数
        
        Returns:
            删除的数量
        """
        try:
            from datetime import timedelta
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            # 查找要删除的向量IDs
            points_to_delete = []
            offset = None
            
            while True:
                response = self.client.scroll(
                    collection_name=self.collection_name,
                    scroll_filter=Filter(
                        must=[
                            FieldCondition(key="timestamp", range={"lt": cutoff_date})
                        ]
                    ),
                    limit=100,
                    offset=offset,
                    with_payload=False,
                    with_vectors=False
                )
                
                for point in response[0]:
                    points_to_delete.append(point.id)
                
                if response[1] is None:
                    break
                offset = response[1]
            
            # 批量删除
            if points_to_delete:
                self.client.delete(
                    collection_name=self.collection_name,
                    points_selector=points_to_delete
                )
            
            deleted_count = len(points_to_delete)
            logger.info(f"✅ 删除旧向量: {deleted_count} 个")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"❌ 删除旧向量失败: {e}")
            return 0

