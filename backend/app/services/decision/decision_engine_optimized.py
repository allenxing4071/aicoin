"""
DecisionEngine性能优化扩展

优化内容：
1. DeepSeek流式响应
2. 批量决策处理
3. 性能监控指标
"""

import asyncio
import time
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime

import openai

logger = logging.getLogger(__name__)


class DecisionEnginePerformanceOptimizer:
    """
    决策引擎性能优化器
    
    提供以下优化：
    1. 流式响应（降低感知延迟）
    2. 批量决策（提高吞吐量）
    3. 性能监控（追踪瓶颈）
    """
    
    def __init__(self, client: openai.OpenAI):
        self.client = client
        self.metrics = {
            "total_decisions": 0,
            "stream_decisions": 0,
            "batch_decisions": 0,
            "avg_response_time": 0,
            "cache_hits": 0,
            "cache_misses": 0
        }
    
    async def call_llm_stream(
        self,
        prompt: str,
        model: str = "deepseek-chat"
    ) -> Dict[str, Any]:
        """
        调用LLM（流式响应）
        
        优势：
        - 降低感知延迟（边接收边处理）
        - 更好的用户体验
        - 可以提前中断
        
        Args:
            prompt: Prompt内容
            model: 模型名称
            
        Returns:
            解析后的决策
        """
        start_time = time.time()
        
        try:
            response = await self.client.chat.completions.create(
                model=model,
                messages=[{"role": "user", "content": prompt}],
                stream=True,  # 启用流式
                temperature=0.7
            )
            
            # 收集流式响应
            full_content = ""
            async for chunk in response:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_content += content
                    
                    # 可以在这里实时处理部分内容
                    # 例如：提前识别决策类型
            
            elapsed = time.time() - start_time
            
            # 更新指标
            self.metrics["stream_decisions"] += 1
            self.metrics["total_decisions"] += 1
            self._update_avg_response_time(elapsed)
            
            logger.info(f"✅ 流式响应完成，耗时: {elapsed:.2f}秒")
            
            return {
                "content": full_content,
                "elapsed_time": elapsed,
                "stream": True
            }
            
        except Exception as e:
            logger.error(f"流式调用失败: {e}")
            raise
    
    async def batch_decisions(
        self,
        prompts: List[str],
        model: str = "deepseek-chat"
    ) -> List[Dict[str, Any]]:
        """
        批量处理决策（并发调用）
        
        优势：
        - 提高吞吐量
        - 降低平均延迟
        - 更好的资源利用
        
        Args:
            prompts: Prompt列表
            model: 模型名称
            
        Returns:
            决策列表
        """
        start_time = time.time()
        
        try:
            # 并发调用
            tasks = [
                self.client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                for prompt in prompts
            ]
            
            responses = await asyncio.gather(*tasks, return_exceptions=True)
            
            results = []
            for i, response in enumerate(responses):
                if isinstance(response, Exception):
                    logger.error(f"批量决策#{i}失败: {response}")
                    results.append({"error": str(response)})
                else:
                    results.append({
                        "content": response.choices[0].message.content,
                        "index": i
                    })
            
            elapsed = time.time() - start_time
            
            # 更新指标
            self.metrics["batch_decisions"] += len(prompts)
            self.metrics["total_decisions"] += len(prompts)
            
            logger.info(f"✅ 批量决策完成，{len(prompts)}个决策，耗时: {elapsed:.2f}秒")
            
            return results
            
        except Exception as e:
            logger.error(f"批量决策失败: {e}")
            raise
    
    def _update_avg_response_time(self, elapsed: float):
        """更新平均响应时间"""
        total = self.metrics["total_decisions"]
        if total == 1:
            self.metrics["avg_response_time"] = elapsed
        else:
            current_avg = self.metrics["avg_response_time"]
            self.metrics["avg_response_time"] = (current_avg * (total - 1) + elapsed) / total
    
    def get_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        return {
            **self.metrics,
            "cache_hit_rate": (
                self.metrics["cache_hits"] / 
                (self.metrics["cache_hits"] + self.metrics["cache_misses"])
                if (self.metrics["cache_hits"] + self.metrics["cache_misses"]) > 0
                else 0
            ),
            "timestamp": datetime.now().isoformat()
        }
    
    def record_cache_hit(self):
        """记录缓存命中"""
        self.metrics["cache_hits"] += 1
    
    def record_cache_miss(self):
        """记录缓存未命中"""
        self.metrics["cache_misses"] += 1


class PerformanceMonitor:
    """
    性能监控器
    
    追踪各个环节的耗时：
    - 数据库查询
    - Qdrant检索
    - Prompt渲染
    - LLM调用
    """
    
    def __init__(self):
        self.timings = {
            "db_query": [],
            "qdrant_search": [],
            "prompt_render": [],
            "llm_call": [],
            "total": []
        }
    
    def record(self, operation: str, elapsed: float):
        """记录操作耗时"""
        if operation in self.timings:
            self.timings[operation].append(elapsed)
    
    def get_stats(self) -> Dict[str, Any]:
        """获取统计信息"""
        stats = {}
        
        for operation, times in self.timings.items():
            if times:
                stats[operation] = {
                    "count": len(times),
                    "avg": sum(times) / len(times),
                    "min": min(times),
                    "max": max(times),
                    "p50": self._percentile(times, 50),
                    "p95": self._percentile(times, 95),
                    "p99": self._percentile(times, 99)
                }
            else:
                stats[operation] = {"count": 0}
        
        return stats
    
    def _percentile(self, data: List[float], percentile: int) -> float:
        """计算百分位数"""
        if not data:
            return 0
        
        sorted_data = sorted(data)
        index = int(len(sorted_data) * percentile / 100)
        return sorted_data[min(index, len(sorted_data) - 1)]
    
    def reset(self):
        """重置统计"""
        for key in self.timings:
            self.timings[key].clear()
    
    def print_report(self):
        """打印性能报告"""
        stats = self.get_stats()
        
        print("\n" + "="*60)
        print("性能监控报告")
        print("="*60)
        
        for operation, data in stats.items():
            if data.get("count", 0) > 0:
                print(f"\n{operation}:")
                print(f"  调用次数: {data['count']}")
                print(f"  平均耗时: {data['avg']*1000:.2f}ms")
                print(f"  最小耗时: {data['min']*1000:.2f}ms")
                print(f"  最大耗时: {data['max']*1000:.2f}ms")
                print(f"  P50: {data['p50']*1000:.2f}ms")
                print(f"  P95: {data['p95']*1000:.2f}ms")
                print(f"  P99: {data['p99']*1000:.2f}ms")
        
        print("\n" + "="*60)


# 全局性能监控器
performance_monitor = PerformanceMonitor()

