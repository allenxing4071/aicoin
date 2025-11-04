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
    """
    市场状态向量化器
    
    支持多种Embedding服务:
    - OpenAI (text-embedding-ada-002)
    - DeepSeek (deepseek-chat with custom embedding)
    - Qwen (text-embedding-v2/v3)
    """
    
    def __init__(
        self, 
        api_key: Optional[str] = None,
        provider: str = "auto",  # auto, openai, deepseek, qwen
        model: Optional[str] = None
    ):
        """
        初始化向量化器
        
        Args:
            api_key: API密钥（如果为None，自动从settings获取）
            provider: embedding服务提供商 (auto会自动选择可用的)
            model: 模型名称（如果为None，使用默认值）
        """
        self.provider = provider
        self.enabled = False
        self.client = None
        self.model = None
        self.vector_dim = 1536  # 默认维度
        
        # 自动选择provider
        if provider == "auto":
            if settings.QWEN_API_KEY:
                provider = "qwen"
                api_key = api_key or settings.QWEN_API_KEY
                logger.info("🔍 使用Qwen Embedding服务")
            elif settings.DEEPSEEK_API_KEY:
                provider = "deepseek"
                api_key = api_key or settings.DEEPSEEK_API_KEY
                logger.info("🔍 使用DeepSeek Embedding服务")
            elif settings.OPENAI_API_KEY:
                provider = "openai"
                api_key = api_key or settings.OPENAI_API_KEY
                logger.info("🔍 使用OpenAI Embedding服务")
            else:
                logger.warning("⚠️ 未配置任何Embedding API Key，长期记忆功能已禁用")
                return
        
        # 验证API Key
        if not api_key or api_key.startswith("sk-your-") or api_key == "your-key-here":
            logger.warning(f"⚠️ {provider.upper()} API Key未配置或无效，长期记忆功能已禁用")
            return
        
        # 初始化对应的客户端
        try:
            if provider == "qwen":
                self.client = openai.OpenAI(
                    api_key=api_key,
                    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1"
                )
                self.model = model or "text-embedding-v3"
                self.vector_dim = 1024  # Qwen embedding维度
                self.enabled = True
                logger.info(f"✅ Qwen Embedding已启用 (模型: {self.model}, 维度: {self.vector_dim})")
                
            elif provider == "deepseek":
                # DeepSeek暂不直接支持embedding，使用chat模型生成特征
                self.client = openai.OpenAI(
                    api_key=api_key,
                    base_url="https://api.deepseek.com/v1"
                )
                self.model = model or "deepseek-chat"
                self.vector_dim = 768  # 使用较小维度
                self.enabled = True
                logger.info(f"✅ DeepSeek特征提取已启用 (模型: {self.model}, 维度: {self.vector_dim})")
                logger.warning("⚠️ DeepSeek暂无专用embedding接口，使用特征哈希方法")
                
            elif provider == "openai":
                self.client = openai.OpenAI(api_key=api_key)
                self.model = model or "text-embedding-ada-002"
                self.vector_dim = 1536
                self.enabled = True
                logger.info(f"✅ OpenAI Embedding已启用 (模型: {self.model}, 维度: {self.vector_dim})")
            
            else:
                logger.error(f"❌ 不支持的provider: {provider}")
                
        except Exception as e:
            logger.error(f"❌ 初始化{provider}客户端失败: {e}")
            self.enabled = False
        
        self.provider = provider
    
    def extract_features(self, market_data: Dict[str, Any], decision: Dict[str, Any]) -> List[float]:
        """
        提取市场特征并转换为向量
        
        Returns:
            特征向量
        """
        # 如果未启用，返回零向量
        if not self.enabled:
            return [0.0] * self.vector_dim
        
        # 1. 构建文本描述
        text_description = self._build_text_description(market_data, decision)
        
        # 2. 根据provider调用相应的向量化方法
        try:
            if self.provider in ["qwen", "openai"]:
                # Qwen和OpenAI都支持标准的embeddings接口
                response = self.client.embeddings.create(
                    model=self.model,
                    input=text_description
                )
                return response.data[0].embedding
            
            elif self.provider == "deepseek":
                # DeepSeek使用特征哈希方法
                # 提取关键特征并生成固定维度向量
                return self._deepseek_feature_hash(text_description, market_data, decision)
            
            else:
                logger.error(f"不支持的provider: {self.provider}")
                return [0.0] * self.vector_dim
        
        except Exception as e:
            logger.error(f"向量化失败 ({self.provider}): {e}")
            # 返回零向量
            return [0.0] * self.vector_dim
    
    def _deepseek_feature_hash(
        self, 
        text_description: str, 
        market_data: Dict[str, Any], 
        decision: Dict[str, Any]
    ) -> List[float]:
        """
        DeepSeek特征哈希方法
        
        由于DeepSeek暂无embedding接口，使用数值特征组合生成向量
        """
        import hashlib
        import struct
        
        # 提取数值特征
        symbol = decision.get("symbol", "BTC")
        action = decision.get("action", "hold")
        confidence = decision.get("confidence", 0.0)
        
        price = market_data.get(symbol, {}).get("price", 0)
        change_24h = market_data.get(symbol, {}).get("change_24h", 0)
        volume = market_data.get(symbol, {}).get("volume_24h", 0)
        
        # 归一化数值特征
        features = []
        
        # 价格相关特征 (256维)
        price_hash = hashlib.sha256(str(price).encode()).digest()
        features.extend([b / 255.0 for b in price_hash])
        
        # 变化相关特征 (256维)
        change_hash = hashlib.sha256(str(change_24h).encode()).digest()
        features.extend([b / 255.0 for b in change_hash])
        
        # 决策相关特征 (256维)
        decision_str = f"{symbol}_{action}_{confidence}"
        decision_hash = hashlib.sha256(decision_str.encode()).digest()
        features.extend([b / 255.0 for b in decision_hash])
        
        # 确保维度正确 (768维)
        if len(features) < self.vector_dim:
            features.extend([0.0] * (self.vector_dim - len(features)))
        else:
            features = features[:self.vector_dim]
        
        return features
    
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
    
    支持多种embedding服务:
    - Qwen (推荐): 性价比高，中文支持好
    - DeepSeek: 使用特征哈希，无需额外费用
    - OpenAI: 效果好，但需要额外费用
    """
    
    COLLECTION_NAME = "trading_memories"
    
    def __init__(
        self,
        qdrant_host: str = "localhost",
        qdrant_port: int = 6333,
        api_key: Optional[str] = None,
        embedding_provider: str = "auto"  # auto, qwen, deepseek, openai
    ):
        """
        初始化长期记忆服务
        
        Args:
            qdrant_host: Qdrant服务器地址
            qdrant_port: Qdrant端口
            api_key: Embedding API密钥（如果为None，自动选择）
            embedding_provider: embedding服务提供商
        """
        self.client = QdrantClient(host=qdrant_host, port=qdrant_port)
        
        # 初始化向量化器（自动选择provider）
        self.vectorizer = MarketStateVectorizer(
            api_key=api_key,
            provider=embedding_provider
        )
        
        # 使用向量化器的维度
        self.VECTOR_DIM = self.vectorizer.vector_dim
        
        # 初始化collection
        self._init_collection()
    
    def _init_collection(self):
        """初始化Qdrant collection"""
        try:
            # 检查collection是否存在
            collections = self.client.get_collections().collections
            exists = any(c.name == self.COLLECTION_NAME for c in collections)
            
            if not exists:
                # 使用实际的向量维度创建collection
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

