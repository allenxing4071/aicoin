"""短期记忆服务 - Redis实现"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from decimal import Decimal
import json
import logging

from app.core.redis_client import RedisClient

logger = logging.getLogger(__name__)


class ShortTermMemory:
    """
    短期记忆服务（Redis）
    存储最近的决策、交易和当天性能指标
    """
    
    # Redis Key前缀
    KEY_PREFIX_DECISIONS = "stm:decisions"  # Sorted Set
    KEY_PREFIX_DECISION_DETAIL = "stm:decision:"  # Hash
    KEY_TODAY_TRADE_COUNT = "stm:today:trade_count"  # String
    KEY_PERFORMANCE_METRICS = "stm:performance"  # Hash
    
    # 数据保留时间
    DECISION_TTL = 86400 * 7  # 7天
    PERFORMANCE_TTL = 86400 * 1  # 1天（每日重置）
    
    def __init__(self, redis_client: RedisClient):
        self.redis = redis_client
    
    async def record_decision(
        self,
        decision_id: str,
        timestamp: datetime,
        symbol: str,
        action: str,
        size_usd: float,
        confidence: float,
        reasoning: str,
        market_data: Dict[str, Any]
    ) -> bool:
        """
        记录AI决策
        
        Args:
            decision_id: 决策ID
            timestamp: 时间戳
            symbol: 交易对
            action: 动作（open_long/open_short/close/hold）
            size_usd: 仓位大小（美元）
            confidence: 置信度
            reasoning: 推理过程
            market_data: 市场数据
        
        Returns:
            是否成功
        """
        try:
            # 1. 添加到Sorted Set（按时间排序）
            score = timestamp.timestamp()
            await self.redis.zadd(
                self.KEY_PREFIX_DECISIONS,
                {decision_id: score}
            )
            
            # 2. 存储决策详情到Hash
            decision_key = f"{self.KEY_PREFIX_DECISION_DETAIL}{decision_id}"
            decision_data = {
                "decision_id": decision_id,
                "timestamp": timestamp.isoformat(),
                "symbol": symbol,
                "action": action,
                "size_usd": str(size_usd),
                "confidence": str(confidence),
                "reasoning": reasoning,
                "market_data": json.dumps(market_data),
                "status": "PENDING",  # PENDING/EXECUTED/REJECTED
                "result": "",
                "pnl": "0",
            }
            
            await self.redis.hset(decision_key, decision_data)
            await self.redis.expire(decision_key, self.DECISION_TTL)
            
            logger.info(f"记录决策: {decision_id} - {action} {symbol} {size_usd}USD")
            return True
            
        except Exception as e:
            logger.error(f"记录决策失败: {e}")
            return False
    
    async def update_decision_result(
        self,
        decision_id: str,
        status: str,
        result: str,
        pnl: float = 0.0
    ) -> bool:
        """
        更新决策执行结果
        
        Args:
            decision_id: 决策ID
            status: 状态（EXECUTED/REJECTED）
            result: 结果描述
            pnl: 盈亏（如果已平仓）
        
        Returns:
            是否成功
        """
        try:
            decision_key = f"{self.KEY_PREFIX_DECISION_DETAIL}{decision_id}"
            
            await self.redis.hset(decision_key, {
                "status": status,
                "result": result,
                "pnl": str(pnl),
                "updated_at": datetime.now().isoformat()
            })
            
            logger.info(f"更新决策结果: {decision_id} - {status} PnL:{pnl}")
            return True
            
        except Exception as e:
            logger.error(f"更新决策结果失败: {e}")
            return False
    
    async def get_recent_decisions(
        self,
        count: int = 10,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """
        获取最近的决策
        
        Args:
            count: 最多返回数量
            hours: 时间范围（小时）
        
        Returns:
            决策列表
        """
        try:
            # 计算时间范围
            min_score = (datetime.now() - timedelta(hours=hours)).timestamp()
            max_score = datetime.now().timestamp()
            
            # 从Sorted Set获取决策ID
            decision_ids = await self.redis.zrevrangebyscore(
                self.KEY_PREFIX_DECISIONS,
                max_score,
                min_score,
                start=0,
                num=count
            )
            
            # 获取每个决策的详情
            decisions = []
            for decision_id in decision_ids:
                decision_key = f"{self.KEY_PREFIX_DECISION_DETAIL}{decision_id}"
                decision_data = await self.redis.hgetall(decision_key)
                
                if decision_data:
                    # 解析market_data（JSON字符串）
                    if "market_data" in decision_data:
                        try:
                            decision_data["market_data"] = json.loads(decision_data["market_data"])
                        except:
                            decision_data["market_data"] = {}
                    
                    decisions.append(decision_data)
            
            return decisions
            
        except Exception as e:
            logger.error(f"获取最近决策失败: {e}")
            return []
    
    async def get_today_trade_count(self) -> int:
        """获取今日交易次数"""
        try:
            count = await self.redis.get(self.KEY_TODAY_TRADE_COUNT)
            return int(count) if count else 0
        except Exception as e:
            logger.error(f"获取今日交易次数失败: {e}")
            return 0
    
    async def increment_today_trade_count(self) -> int:
        """递增今日交易次数"""
        try:
            count = await self.redis.incr(self.KEY_TODAY_TRADE_COUNT)
            
            # 设置过期时间为今日结束
            now = datetime.now()
            midnight = datetime(now.year, now.month, now.day) + timedelta(days=1)
            ttl = int((midnight - now).total_seconds())
            await self.redis.expire(self.KEY_TODAY_TRADE_COUNT, ttl)
            
            return count
        except Exception as e:
            logger.error(f"递增今日交易次数失败: {e}")
            return 0
    
    async def update_performance_metrics(
        self,
        metrics: Dict[str, Any]
    ) -> bool:
        """
        更新性能指标
        
        Args:
            metrics: 性能指标字典
                - total_trades: int
                - win_trades: int
                - total_pnl: float
                - sharpe_ratio: float
                - max_drawdown: float
                - etc.
        
        Returns:
            是否成功
        """
        try:
            # 转换所有值为字符串
            metrics_str = {k: str(v) for k, v in metrics.items()}
            metrics_str["updated_at"] = datetime.now().isoformat()
            
            await self.redis.hset(self.KEY_PERFORMANCE_METRICS, metrics_str)
            await self.redis.expire(self.KEY_PERFORMANCE_METRICS, self.PERFORMANCE_TTL)
            
            logger.debug(f"更新性能指标: {metrics_str}")
            return True
            
        except Exception as e:
            logger.error(f"更新性能指标失败: {e}")
            return False
    
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        try:
            metrics = await self.redis.hgetall(self.KEY_PERFORMANCE_METRICS)
            
            # 转换数值类型
            if metrics:
                for key in ['total_trades', 'win_trades']:
                    if key in metrics:
                        metrics[key] = int(metrics[key])
                
                for key in ['total_pnl', 'sharpe_ratio', 'max_drawdown', 'win_rate']:
                    if key in metrics:
                        metrics[key] = float(metrics[key])
            
            return metrics or {}
            
        except Exception as e:
            logger.error(f"获取性能指标失败: {e}")
            return {}
    
    async def clear_old_decisions(self, days: int = 7):
        """清理旧决策"""
        try:
            cutoff = (datetime.now() - timedelta(days=days)).timestamp()
            
            # 删除旧的决策ID
            removed = await self.redis.zremrangebyscore(
                self.KEY_PREFIX_DECISIONS,
                0,
                cutoff
            )
            
            logger.info(f"清理了 {removed} 条旧决策")
            return removed
            
        except Exception as e:
            logger.error(f"清理旧决策失败: {e}")
            return 0

