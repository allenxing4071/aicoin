"""Decision Data Collector - DeepSeek训练数据收集器"""

from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import json
import logging

logger = logging.getLogger(__name__)


class DecisionDataCollector:
    """
    决策数据收集器
    
    职责：
    1. 从PostgreSQL收集历史决策数据
    2. 从Redis提取市场快照
    3. 从Qdrant获取向量化特征
    4. 标注决策结果（盈利/亏损/准确度）
    5. 生成训练数据集
    
    数据格式：
    {
        "input": {
            "prompt": "完整的决策Prompt",
            "market_data": {...},
            "intelligence_report": {...},
            "memory_context": {...}
        },
        "output": {
            "decision": {...},
            "expected_action": "...",
            "expected_confidence": 0.0
        },
        "result": {
            "actual_outcome": "success/failure",
            "pnl": 0.0,
            "duration_hours": 0.0,
            "accuracy_score": 0.0
        }
    }
    """
    
    def __init__(
        self,
        redis_client,
        db_session,
        qdrant_client=None
    ):
        """
        初始化数据收集器
        
        Args:
            redis_client: Redis客户端
            db_session: 数据库会话
            qdrant_client: Qdrant客户端（可选）
        """
        self.redis = redis_client
        self.db = db_session
        self.qdrant = qdrant_client
        
        logger.info("✅ 决策数据收集器初始化完成")
    
    async def collect_training_data(
        self,
        start_date: datetime,
        end_date: datetime,
        min_samples: int = 100,
        only_completed: bool = True
    ) -> List[Dict[str, Any]]:
        """
        收集训练数据
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            min_samples: 最小样本数
            only_completed: 只收集已完成的交易
        
        Returns:
            训练样本列表
        """
        try:
            logger.info(
                f"📦 开始收集训练数据: "
                f"{start_date.date()} 到 {end_date.date()}, "
                f"目标样本数 >= {min_samples}"
            )
            
            # 1. 从数据库获取决策记录
            decisions = await self._fetch_decisions_from_db(
                start_date, end_date, only_completed
            )
            
            logger.info(f"✓ 从数据库获取 {len(decisions)} 条决策记录")
            
            # 2. 为每条决策收集完整数据
            training_samples = []
            for decision in decisions:
                sample = await self._build_training_sample(decision)
                if sample:
                    training_samples.append(sample)
            
            logger.info(f"✓ 成功构建 {len(training_samples)} 个训练样本")
            
            # 3. 数据质量检查
            valid_samples = self._validate_samples(training_samples)
            
            logger.info(f"✓ 质量检查后剩余 {len(valid_samples)} 个有效样本")
            
            # 4. 检查是否满足最小样本数
            if len(valid_samples) < min_samples:
                logger.warning(
                    f"⚠️ 样本数不足: {len(valid_samples)} < {min_samples}, "
                    f"建议扩大时间范围或降低质量要求"
                )
            
            return valid_samples
            
        except Exception as e:
            logger.error(f"❌ 收集训练数据失败: {e}", exc_info=True)
            return []
    
    async def _fetch_decisions_from_db(
        self,
        start_date: datetime,
        end_date: datetime,
        only_completed: bool
    ) -> List[Dict[str, Any]]:
        """从数据库获取决策"""
        try:
            query = f"""
            SELECT 
                d.id,
                d.timestamp,
                d.symbol,
                d.market_data,
                d.decision,
                d.executed,
                d.reject_reason,
                d.model_name,
                t.id as trade_id,
                t.pnl,
                t.closed_at,
                t.status as trade_status
            FROM ai_decisions d
            LEFT JOIN trades t ON t.decision_id = d.id
            WHERE d.timestamp >= '{start_date.isoformat()}'
              AND d.timestamp <= '{end_date.isoformat()}'
            """
            
            if only_completed:
                query += " AND t.status = 'closed'"
            
            query += " ORDER BY d.timestamp DESC"
            
            result = await self.db.execute(query)
            rows = result.fetchall()
            
            decisions = []
            for row in rows:
                decisions.append({
                    "decision_id": row[0],
                    "timestamp": row[1],
                    "symbol": row[2],
                    "market_data": row[3],  # JSON
                    "decision": row[4],  # JSON
                    "executed": row[5],
                    "reject_reason": row[6],
                    "model_name": row[7],
                    "trade_id": row[8],
                    "pnl": float(row[9]) if row[9] else None,
                    "closed_at": row[10],
                    "trade_status": row[11]
                })
            
            return decisions
            
        except Exception as e:
            logger.error(f"从数据库获取决策失败: {e}")
            return []
    
    async def _build_training_sample(
        self,
        decision: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """构建单个训练样本"""
        try:
            decision_id = decision["decision_id"]
            
            # 构建输入部分
            input_data = {
                "prompt": await self._reconstruct_prompt(decision),
                "market_data": decision["market_data"],
                "intelligence_report": await self._get_intelligence_context(decision),
                "memory_context": await self._get_memory_context(decision)
            }
            
            # 构建输出部分
            output_data = {
                "decision": decision["decision"],
                "expected_action": decision["decision"].get("action", "hold"),
                "expected_confidence": decision["decision"].get("confidence", 0.0)
            }
            
            # 构建结果部分
            result_data = self._build_result_data(decision)
            
            sample = {
                "sample_id": f"train_{decision_id}",
                "timestamp": decision["timestamp"].isoformat(),
                "input": input_data,
                "output": output_data,
                "result": result_data,
                "metadata": {
                    "symbol": decision["symbol"],
                    "model_name": decision["model_name"],
                    "executed": decision["executed"]
                }
            }
            
            return sample
            
        except Exception as e:
            logger.error(f"构建训练样本失败 (decision_id={decision.get('decision_id')}): {e}")
            return None
    
    async def _reconstruct_prompt(self, decision: Dict[str, Any]) -> str:
        """重构决策时的Prompt"""
        # 简化版：实际应该从日志或记录中恢复完整Prompt
        market_data = decision["market_data"]
        
        prompt = f"""你是专业的加密货币交易AI。

【市场数据】
币种: {decision['symbol']}
价格: ${market_data.get('price', 'N/A')}
24h涨跌: {market_data.get('change_24h', 'N/A')}

【任务】
请基于以上信息做出交易决策，返回JSON格式。

注：这是训练数据重构的简化Prompt，实际应该包含完整的约束、权限、记忆等信息。
"""
        return prompt
    
    async def _get_intelligence_context(
        self,
        decision: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """获取情报上下文"""
        # TODO: 从Redis获取当时的情报报告
        return None
    
    async def _get_memory_context(
        self,
        decision: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """获取记忆上下文"""
        # TODO: 从Qdrant获取当时的记忆向量
        return None
    
    def _build_result_data(self, decision: Dict[str, Any]) -> Dict[str, Any]:
        """构建结果数据"""
        pnl = decision.get("pnl")
        closed_at = decision.get("closed_at")
        timestamp = decision.get("timestamp")
        
        # 计算持续时间
        duration_hours = 0.0
        if closed_at and timestamp:
            duration = closed_at - timestamp
            duration_hours = duration.total_seconds() / 3600
        
        # 判断结果
        actual_outcome = "unknown"
        accuracy_score = 0.5
        
        if pnl is not None:
            if pnl > 0:
                actual_outcome = "success"
                accuracy_score = min(1.0, 0.5 + (pnl / 100))  # 简化评分
            elif pnl < 0:
                actual_outcome = "failure"
                accuracy_score = max(0.0, 0.5 - (abs(pnl) / 100))
            else:
                actual_outcome = "neutral"
                accuracy_score = 0.5
        
        return {
            "actual_outcome": actual_outcome,
            "pnl": pnl if pnl is not None else 0.0,
            "duration_hours": duration_hours,
            "accuracy_score": accuracy_score
        }
    
    def _validate_samples(
        self,
        samples: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """验证样本质量"""
        valid_samples = []
        
        for sample in samples:
            # 检查必要字段
            if not sample.get("input") or not sample.get("output"):
                continue
            
            # 检查结果
            result = sample.get("result", {})
            if result.get("actual_outcome") == "unknown":
                continue  # 跳过未知结果的样本
            
            # 检查Prompt长度
            prompt = sample["input"].get("prompt", "")
            if len(prompt) < 50:  # Prompt太短
                continue
            
            valid_samples.append(sample)
        
        return valid_samples
    
    async def export_to_jsonl(
        self,
        samples: List[Dict[str, Any]],
        output_path: str
    ) -> bool:
        """
        导出为JSONL格式（训练数据标准格式）
        
        Args:
            samples: 训练样本列表
            output_path: 输出文件路径
        
        Returns:
            是否导出成功
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                for sample in samples:
                    # 转换为训练格式
                    training_item = {
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a professional cryptocurrency trading AI."
                            },
                            {
                                "role": "user",
                                "content": sample["input"]["prompt"]
                            },
                            {
                                "role": "assistant",
                                "content": json.dumps(sample["output"]["decision"], ensure_ascii=False)
                            }
                        ],
                        "metadata": sample.get("metadata", {})
                    }
                    
                    f.write(json.dumps(training_item, ensure_ascii=False) + '\n')
            
            logger.info(f"✅ 训练数据已导出: {output_path} ({len(samples)} 样本)")
            return True
            
        except Exception as e:
            logger.error(f"❌ 导出训练数据失败: {e}")
            return False
    
    async def get_collection_stats(
        self,
        start_date: datetime,
        end_date: datetime
    ) -> Dict[str, Any]:
        """
        获取数据收集统计
        
        Returns:
            统计信息
        """
        try:
            query = f"""
            SELECT 
                COUNT(*) as total_decisions,
                SUM(CASE WHEN executed THEN 1 ELSE 0 END) as executed_count,
                COUNT(t.id) as completed_trades,
                AVG(t.pnl) as avg_pnl,
                SUM(CASE WHEN t.pnl > 0 THEN 1 ELSE 0 END) as profitable_trades
            FROM ai_decisions d
            LEFT JOIN trades t ON t.decision_id = d.id AND t.status = 'closed'
            WHERE d.timestamp >= '{start_date.isoformat()}'
              AND d.timestamp <= '{end_date.isoformat()}'
            """
            
            result = await self.db.execute(query)
            row = result.first()
            
            if row:
                total_decisions = row[0] or 0
                completed_trades = row[2] or 0
                profitable_trades = row[4] or 0
                
                return {
                    "date_range": {
                        "start": start_date.isoformat(),
                        "end": end_date.isoformat()
                    },
                    "total_decisions": total_decisions,
                    "executed_count": row[1] or 0,
                    "completed_trades": completed_trades,
                    "avg_pnl": float(row[3]) if row[3] else 0.0,
                    "profitable_trades": profitable_trades,
                    "win_rate": (
                        (profitable_trades / completed_trades * 100)
                        if completed_trades > 0
                        else 0.0
                    )
                }
            
            return {}
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {e}")
            return {}

