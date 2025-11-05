"""Cloud Platform Coordinator - 云平台并行协调器

核心设计：三大云平台同时调用，交叉验证信息准确性
类似DeepSeek的双模型投票思想，但应用于情报收集
"""

from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import logging
import asyncio
from collections import Counter

from app.core.config import settings
from .platforms.cloud_adapters import (
    BaiduQwenAdapter,
    TencentQwenAdapter,
    VolcanoQwenAdapter,
    AWSQwenAdapter
)

logger = logging.getLogger(__name__)


class CloudPlatformCoordinator:
    """
    云平台并行协调器
    
    核心功能：
    1. 同时调用三大云平台（百度+腾讯+火山）
    2. 汇总和对比三个平台的搜索结果
    3. 交叉验证信息准确性
    4. 计算置信度评分（基于平台共识度）
    
    工作流程：
    ┌─────────────────┐
    │   收到情报需求   │
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │  同时调用三平台  │
    │ ├─ 百度智能云   │
    │ ├─ 腾讯云       │
    │ └─ 火山引擎     │
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │  汇总三份结果    │
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │ 交叉验证与融合   │
    │ ├─ 共同信息     │
    │ ├─ 部分信息     │
    │ └─ 单源信息     │
    └────────┬────────┘
             │
    ┌────────▼────────┐
    │ 输出综合情报报告 │
    │ (含置信度评分)  │
    └─────────────────┘
    """
    
    def __init__(self):
        """初始化云平台协调器"""
        self.platforms: Dict[str, Any] = {}
        self._initialize_platforms()
        logger.info(f"✅ 云平台协调器初始化完成，已加载 {len(self.platforms)} 个平台")
    
    def _initialize_platforms(self):
        """初始化云平台适配器"""
        # 百度智能云
        if settings.ENABLE_BAIDU_QWEN and settings.BAIDU_QWEN_API_KEY:
            self.platforms["baidu"] = BaiduQwenAdapter(
                api_key=settings.BAIDU_QWEN_API_KEY,
                base_url=settings.BAIDU_QWEN_BASE_URL,
                enabled=settings.ENABLE_BAIDU_QWEN
            )
            logger.info("✓ 百度智能云平台已加载")
        
        # 腾讯云
        if settings.ENABLE_TENCENT_QWEN and settings.TENCENT_QWEN_API_KEY:
            self.platforms["tencent"] = TencentQwenAdapter(
                api_key=settings.TENCENT_QWEN_API_KEY,
                base_url=settings.TENCENT_QWEN_BASE_URL,
                enabled=settings.ENABLE_TENCENT_QWEN
            )
            logger.info("✓ 腾讯云平台已加载")
        
        # 火山引擎
        if settings.ENABLE_VOLCANO_QWEN and settings.VOLCANO_QWEN_API_KEY:
            self.platforms["volcano"] = VolcanoQwenAdapter(
                api_key=settings.VOLCANO_QWEN_API_KEY,
                base_url=settings.VOLCANO_QWEN_BASE_URL,
                enabled=settings.ENABLE_VOLCANO_QWEN
            )
            logger.info("✓ 火山引擎平台已加载")
        
        # AWS（可选）
        if settings.ENABLE_AWS_QWEN and settings.AWS_QWEN_API_KEY:
            self.platforms["aws"] = AWSQwenAdapter(
                api_key=settings.AWS_QWEN_API_KEY,
                base_url=settings.AWS_QWEN_BASE_URL,
                enabled=settings.ENABLE_AWS_QWEN
            )
            logger.info("✓ AWS平台已加载")
    
    async def parallel_search_and_verify(
        self,
        data_sources: Dict[str, Any],
        query_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        并行搜索与交叉验证（核心方法）
        
        Args:
            data_sources: 原始数据源
            query_context: 查询上下文
        
        Returns:
            综合情报报告（含置信度评分）
        """
        start_time = datetime.now()
        
        if len(self.platforms) < 2:
            logger.warning("⚠️  可用平台少于2个，无法进行交叉验证！")
            return self._fallback_response("可用平台不足")
        
        logger.info(f"🎯 开始并行调用 {len(self.platforms)} 个云平台进行交叉验证...")
        
        # === 步骤1: 同时调用所有平台 ===
        platform_results = await self._call_platforms_parallel(data_sources, query_context)
        
        if not platform_results:
            logger.error("❌ 所有平台调用失败！")
            return self._fallback_response("所有平台失败")
        
        logger.info(f"✓ 成功获取 {len(platform_results)} 个平台的结果")
        
        # === 步骤2: 交叉验证与信息融合 ===
        verified_intelligence = self._cross_verify_results(platform_results)
        
        # === 步骤3: 计算综合置信度 ===
        confidence_score = self._calculate_confidence(platform_results, verified_intelligence)
        
        # === 步骤4: 构建最终报告 ===
        final_report = {
            "intelligence_summary": verified_intelligence["summary"],
            "key_findings": verified_intelligence["high_confidence_findings"],
            "risk_warnings": verified_intelligence["risk_warnings"],
            "confidence": confidence_score,
            "verification_metadata": {
                "total_platforms_called": len(self.platforms),
                "successful_platforms": len(platform_results),
                "platform_consensus": verified_intelligence["consensus_rate"],
                "high_confidence_items": len(verified_intelligence["high_confidence_findings"]),
                "medium_confidence_items": len(verified_intelligence["medium_confidence_findings"]),
                "low_confidence_items": len(verified_intelligence["low_confidence_findings"]),
                "processing_time_seconds": (datetime.now() - start_time).total_seconds(),
                "timestamp": datetime.now().isoformat()
            },
            "platform_details": [
                {
                    "platform": name,
                    "success": True,
                    "key_findings_count": len(result.get("key_findings", [])),
                    "confidence": result.get("confidence", 0)
                }
                for name, result in platform_results.items()
            ]
        }
        
        logger.info(f"✅ 并行验证完成: 置信度={confidence_score:.2f}, 平台共识度={verified_intelligence['consensus_rate']:.1%}")
        
        return final_report
    
    async def _call_platforms_parallel(
        self,
        data_sources: Dict[str, Any],
        query_context: Optional[Dict[str, Any]]
    ) -> Dict[str, Dict[str, Any]]:
        """
        并行调用所有平台
        
        Returns:
            {platform_name: result_dict}
        """
        tasks = []
        platform_names = []
        
        for name, platform in self.platforms.items():
            if platform.enabled:
                tasks.append(platform.analyze(data_sources, query_context))
                platform_names.append(name)
        
        if not tasks:
            return {}
        
        logger.info(f"📡 同时调用 {len(tasks)} 个平台: {', '.join(platform_names)}")
        
        # 使用asyncio.gather并行执行，return_exceptions=True避免一个失败影响其他
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 收集成功的结果
        successful_results = {}
        for name, result in zip(platform_names, results):
            if isinstance(result, Exception):
                logger.warning(f"⚠️  {name} 平台调用失败: {result}")
            elif isinstance(result, dict) and not result.get("error"):
                successful_results[name] = result
                logger.info(f"✓ {name} 平台返回成功")
            else:
                logger.warning(f"⚠️  {name} 平台返回错误: {result.get('error', 'Unknown')}")
        
        return successful_results
    
    def _cross_verify_results(
        self,
        platform_results: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """
        交叉验证结果
        
        核心逻辑：
        1. 提取所有平台的key_findings
        2. 对比相似度，识别共同信息
        3. 分类：高置信度（多平台共识）、中置信度（部分共识）、低置信度（单源独有）
        
        Returns:
            验证后的情报（分置信度等级）
        """
        all_findings = []
        platform_analyses = []
        
        # 收集所有平台的发现和分析
        for platform_name, result in platform_results.items():
            findings = result.get("key_findings", [])
            analysis = result.get("analysis", "")
            
            for finding in findings:
                all_findings.append({
                    "content": finding,
                    "source": platform_name,
                    "original_confidence": result.get("confidence", 0.5)
                })
            
            if analysis:
                platform_analyses.append({
                    "platform": platform_name,
                    "analysis": analysis
                })
        
        # 简单的相似度匹配（可以后续优化为向量相似度）
        finding_groups = self._group_similar_findings(all_findings)
        
        # 分类
        high_confidence_findings = []  # 3个或更多平台共识
        medium_confidence_findings = []  # 2个平台共识
        low_confidence_findings = []  # 单平台独有
        
        total_platforms = len(platform_results)
        
        for group in finding_groups:
            source_count = len(set([f["source"] for f in group]))
            consensus_rate = source_count / total_platforms
            
            # 合并内容
            merged_content = self._merge_findings(group)
            
            if source_count >= 3 or (source_count == 2 and total_platforms == 2):
                # 高置信度：多平台共识
                high_confidence_findings.append({
                    "content": merged_content,
                    "consensus_platforms": source_count,
                    "total_platforms": total_platforms,
                    "sources": list(set([f["source"] for f in group]))
                })
            elif source_count == 2:
                # 中置信度：部分共识
                medium_confidence_findings.append({
                    "content": merged_content,
                    "consensus_platforms": source_count,
                    "sources": list(set([f["source"] for f in group]))
                })
            else:
                # 低置信度：单源独有
                low_confidence_findings.append({
                    "content": merged_content,
                    "source": group[0]["source"]
                })
        
        # 生成综合摘要
        summary = self._generate_summary(
            high_confidence_findings,
            medium_confidence_findings,
            platform_analyses
        )
        
        # 提取风险警告（高置信度中的负面信息）
        risk_warnings = self._extract_risk_warnings(high_confidence_findings, medium_confidence_findings)
        
        # 计算共识度
        total_findings = len(all_findings)
        high_conf_count = sum([f["consensus_platforms"] for f in high_confidence_findings])
        consensus_rate = high_conf_count / total_findings if total_findings > 0 else 0
        
        return {
            "summary": summary,
            "high_confidence_findings": high_confidence_findings,
            "medium_confidence_findings": medium_confidence_findings,
            "low_confidence_findings": low_confidence_findings,
            "risk_warnings": risk_warnings,
            "consensus_rate": consensus_rate
        }
    
    def _group_similar_findings(
        self,
        findings: List[Dict[str, Any]]
    ) -> List[List[Dict[str, Any]]]:
        """
        将相似的发现分组
        
        简化版：基于关键词匹配
        TODO: 后续可以升级为向量相似度匹配
        """
        groups = []
        used_indices = set()
        
        for i, finding1 in enumerate(findings):
            if i in used_indices:
                continue
            
            group = [finding1]
            used_indices.add(i)
            
            content1 = finding1["content"].lower()
            
            for j, finding2 in enumerate(findings):
                if j <= i or j in used_indices:
                    continue
                
                content2 = finding2["content"].lower()
                
                # 简单的关键词重叠检测
                words1 = set(content1.split())
                words2 = set(content2.split())
                
                overlap = len(words1 & words2) / max(len(words1), len(words2))
                
                if overlap > 0.3:  # 30%的词重叠认为相似
                    group.append(finding2)
                    used_indices.add(j)
            
            groups.append(group)
        
        return groups
    
    def _merge_findings(self, findings: List[Dict[str, Any]]) -> str:
        """合并相似发现的内容"""
        if len(findings) == 1:
            return findings[0]["content"]
        
        # 选择最详细的那个
        longest = max(findings, key=lambda f: len(f["content"]))
        return longest["content"]
    
    def _generate_summary(
        self,
        high_confidence: List[Dict],
        medium_confidence: List[Dict],
        platform_analyses: List[Dict]
    ) -> str:
        """生成综合摘要"""
        summary_parts = []
        
        if high_confidence:
            summary_parts.append(f"【高置信度情报】({len(high_confidence)}条，多平台共识):")
            for i, item in enumerate(high_confidence[:5], 1):  # 最多显示5条
                summary_parts.append(f"{i}. {item['content']}")
        
        if medium_confidence:
            summary_parts.append(f"\n【中置信度情报】({len(medium_confidence)}条，部分平台共识):")
            for i, item in enumerate(medium_confidence[:3], 1):  # 最多显示3条
                summary_parts.append(f"{i}. {item['content']}")
        
        return "\n".join(summary_parts)
    
    def _extract_risk_warnings(
        self,
        high_confidence: List[Dict],
        medium_confidence: List[Dict]
    ) -> List[str]:
        """提取风险警告（识别负面关键词）"""
        risk_keywords = ["下跌", "暴跌", "风险", "警告", "监管", "禁止", "崩盘", "抛售", 
                        "bearish", "dump", "crash", "ban", "regulation", "risk"]
        
        warnings = []
        
        for item in high_confidence + medium_confidence:
            content = item["content"].lower()
            if any(keyword in content for keyword in risk_keywords):
                warnings.append(item["content"])
        
        return warnings[:5]  # 最多返回5条
    
    def _calculate_confidence(
        self,
        platform_results: Dict[str, Dict[str, Any]],
        verified_intelligence: Dict[str, Any]
    ) -> float:
        """
        计算综合置信度
        
        考虑因素：
        1. 平台数量（更多平台 = 更高置信度）
        2. 共识率（更多共识 = 更高置信度）
        3. 单平台的置信度
        """
        if not platform_results:
            return 0.0
        
        # 因素1: 平台数量加成
        platform_count = len(platform_results)
        platform_factor = min(1.0, platform_count / 3)  # 3个平台满分
        
        # 因素2: 共识率
        consensus_rate = verified_intelligence["consensus_rate"]
        
        # 因素3: 平均单平台置信度
        avg_platform_confidence = sum([
            r.get("confidence", 0.5) for r in platform_results.values()
        ]) / len(platform_results)
        
        # 综合计算
        final_confidence = (
            platform_factor * 0.3 +
            consensus_rate * 0.4 +
            avg_platform_confidence * 0.3
        )
        
        return min(1.0, max(0.0, final_confidence))
    
    def _fallback_response(self, reason: str) -> Dict[str, Any]:
        """降级响应"""
        return {
            "intelligence_summary": f"情报收集失败: {reason}",
            "key_findings": [],
            "risk_warnings": [],
            "confidence": 0.0,
            "verification_metadata": {
                "total_platforms_called": len(self.platforms),
                "successful_platforms": 0,
                "error": reason,
                "timestamp": datetime.now().isoformat()
            },
            "platform_details": []
        }

