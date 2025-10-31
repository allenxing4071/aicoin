"""长期记忆服务 - Qdrant向量数据库实现"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib
import json
import logging

import openai
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

from app.core.config import settings

logger = logging.getLogger(__name__)


class MarketStateVectorizer:
    """市场状态向量化器"""
    
    def __init__(self, api_key: str, model: str = "text-embedding-ada-002"):
        self.client = openai.OpenAI(api_key=api_key)
        self.model = model
    
    def extract_features(self, market_data: Dict[str, Any], decision: Dict[str, Any]) -> List[float]:
        """
        提取市场特征并转换为文本描述
        
        Returns:
            特征向量
        """
        # 1. 构建文本描述
        text_description = self._build_text_description(market_data, decision)
        
        # 2. 调用Embedding API
        try:
            response = self.client.embeddings.create(
                model=self.model,
                input=text_description
            )
            return response.data[0].embedding
        
        except Exception as e:
            logger.error(f"向量化失败: {e}")
            # 返回零向量（1536维）
            return [0.0] * 1536
    
    def _build_text_description(self, market_data: Dict[str, Any], decision: Dict[str, Any]) -> str:
        """构建市场状态的文本描述"""
        
        symbol = decision.get("symbol", "BTC")
        action = decision.get("action", "hold")
        confidence = decision.get("confidence", 0.0)
        
        # 提取市场数据
        price = market_data.get(symbol, {}).get("price", 0)
        change_24h = market_data.get(symbol, {}).get("change_24h", 0)
        volume = market_data.get(symbol, {}).get("volume_24h", 0)
        
        # 构建描述
        description = f"""
        Trading Decision Context:
        - Symbol: {symbol}
        - Current Price: ${price:,.2f}
        - 24h Change: {change_24h:+.2f}%
        - 24h Volume: ${volume:,.0f}
        - Action: {action}
        - Confidence: {confidence:.2f}
        
        Market Sentiment: {'Bullish' if change_24h > 0 else 'Bearish'}
        Volatility: {'High' if abs(change_24h) > 5 else 'Moderate' if abs(change_24h) > 2 else 'Low'}
        """
        
        return description.strip()


class LongTermMemory:
    """
    长期记忆服务（Qdrant向量数据库）
    存储历史交易经验，用于相似场景检索
    """
    
    COLLECTION_NAME = "trading_memories"
    VECTOR_DIM = 1536  # OpenAI text-embedding-ada-002
    
    def __init__(
        self,
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
        api_key: Optional[str] = None
    ):
        self.client = QdrantClient(host=qdrant_host, port=qdrant_port)
        self.vectorizer = MarketStateVectorizer(api_key or settings.OPENAI_API_KEY)
        
        # 初始化collection
        self._init_collection()
    
    def _init_collection(self):
        """初始化Qdrant collection"""
        try:
            # 检查collection是否存在
            collections = self.client.get_collections().collections
            exists = any(c.name == self.COLLECTION_NAME for c in collections)
            
            if not exists:
                self.client.create_collection(
                    collection_name=self.COLLECTION_NAME,
                    vectors_config=VectorParams(
                        size=self.VECTOR_DIM,
                        distance=Distance.COSINE
                    )
                )
                logger.info(f"创建Qdrant collection: {self.COLLECTION_NAME}")
            else:
                logger.info(f"Qdrant collection已存在: {self.COLLECTION_NAME}")
        
        except Exception as e:
            logger.error(f"初始化Qdrant collection失败: {e}")
    
    async def store_decision(
        self,
        decision_id: str,
        timestamp: datetime,
        market_data: Dict[str, Any],
        decision: Dict[str, Any],
        result: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        存储决策到向量数据库
        
        Args:
            decision_id: 决策ID
            timestamp: 时间戳
            market_data: 市场数据
            decision: 决策内容
            result: 执行结果（可选）
        
        Returns:
            是否成功
        """
        try:
            # 1. 向量化市场状态
            vector = self.vectorizer.extract_features(market_data, decision)
            
            # 2. 构建payload
            payload = {
                "decision_id": decision_id,
                "timestamp": timestamp.isoformat(),
                "symbol": decision.get("symbol", ""),
                "action": decision.get("action", ""),
                "size_usd": decision.get("size_usd", 0),
                "confidence": decision.get("confidence", 0),
                "reasoning": decision.get("reasoning", ""),
                "market_price": market_data.get(decision.get("symbol", ""), {}).get("price", 0),
                "market_change_24h": market_data.get(decision.get("symbol", ""), {}).get("change_24h", 0),
            }
            
            # 3. 添加执行结果（如果有）
            if result:
                payload.update({
                    "executed": True,
                    "pnl": result.get("pnl", 0),
                    "status": result.get("status", ""),
                })
            else:
                payload["executed"] = False
            
            # 4. 生成唯一ID（使用decision_id的hash）
            point_id = int(hashlib.md5(decision_id.encode()).hexdigest()[:8], 16)
            
            # 5. 插入Qdrant
            self.client.upsert(
                collection_name=self.COLLECTION_NAME,
                points=[
                    PointStruct(
                        id=point_id,
                        vector=vector,
                        payload=payload
                    )
                ]
            )
            
            logger.info(f"存储决策到长期记忆: {decision_id}")
            return True
        
        except Exception as e:
            logger.error(f"存储决策到长期记忆失败: {e}")
            return False
    
    async def find_similar_situations(
        self,
        current_market_data: Dict[str, Any],
        current_decision: Dict[str, Any],
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        查找相似的历史场景
        
        Args:
            current_market_data: 当前市场数据
            current_decision: 当前决策
            limit: 返回数量
        
        Returns:
            相似场景列表（按相似度排序）
        """
        try:
            # 1. 向量化当前市场状态
            query_vector = self.vectorizer.extract_features(
                current_market_data,
                current_decision
            )
            
            # 2. 搜索相似向量
            search_result = self.client.search(
                collection_name=self.COLLECTION_NAME,
                query_vector=query_vector,
                limit=limit,
                with_payload=True
            )
            
            # 3. 格式化结果
            similar_situations = []
            for hit in search_result:
                similar_situations.append({
                    "score": hit.score,  # 相似度分数
                    "decision_id": hit.payload.get("decision_id"),
                    "timestamp": hit.payload.get("timestamp"),
                    "symbol": hit.payload.get("symbol"),
                    "action": hit.payload.get("action"),
                    "confidence": hit.payload.get("confidence"),
                    "reasoning": hit.payload.get("reasoning"),
                    "executed": hit.payload.get("executed"),
                    "pnl": hit.payload.get("pnl", 0),
                    "market_price": hit.payload.get("market_price"),
                    "market_change_24h": hit.payload.get("market_change_24h"),
                })
            
            logger.info(f"找到 {len(similar_situations)} 个相似场景")
            return similar_situations
        
        except Exception as e:
            logger.error(f"查找相似场景失败: {e}")
            return []
    
    async def get_pattern_statistics(
        self,
        symbol: str,
        action: str,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        获取特定交易模式的统计数据
        
        Args:
            symbol: 交易对
            action: 动作类型
            days: 时间范围（天）
        
        Returns:
            统计数据
        """
        try:
            # 计算时间范围
            cutoff_time = datetime.now() - timedelta(days=days)
            
            # 使用scroll获取所有相关记录
            from qdrant_client.models import Filter, FieldCondition, MatchValue
            
            filter_condition = Filter(
                must=[
                    FieldCondition(
                        key="symbol",
                        match=MatchValue(value=symbol)
                    ),
                    FieldCondition(
                        key="action",
                        match=MatchValue(value=action)
                    ),
                ]
            )
            
            # 滚动查询
            records, _ = self.client.scroll(
                collection_name=self.COLLECTION_NAME,
                scroll_filter=filter_condition,
                limit=1000
            )
            
            # 过滤时间范围
            recent_records = [
                r for r in records
                if datetime.fromisoformat(r.payload.get("timestamp", "1970-01-01")) > cutoff_time
            ]
            
            # 统计
            total_count = len(recent_records)
            executed_count = sum(1 for r in recent_records if r.payload.get("executed"))
            
            if executed_count == 0:
                return {
                    "symbol": symbol,
                    "action": action,
                    "total_count": total_count,
                    "executed_count": 0,
                    "success_rate": 0.0,
                    "avg_pnl": 0.0,
                }
            
            # 计算成功率和平均PnL
            pnl_list = [r.payload.get("pnl", 0) for r in recent_records if r.payload.get("executed")]
            success_count = sum(1 for pnl in pnl_list if pnl > 0)
            
            return {
                "symbol": symbol,
                "action": action,
                "total_count": total_count,
                "executed_count": executed_count,
                "success_rate": success_count / executed_count if executed_count > 0 else 0.0,
                "avg_pnl": sum(pnl_list) / len(pnl_list) if pnl_list else 0.0,
                "total_pnl": sum(pnl_list),
            }
        
        except Exception as e:
            logger.error(f"获取模式统计失败: {e}")
            return {}


from datetime import timedelta

