"""Multi-Platform Coordinator - 多平台协调器（AI顾问委员会协调中心）"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import logging
import asyncio

from .platforms import (
    BasePlatformAdapter,
    FreePlatformAdapter,
    QwenSearchAdapter,
    QwenDeepAdapter
)
from .cloud_platform_coordinator import CloudPlatformCoordinator

logger = logging.getLogger(__name__)


class MultiPlatformCoordinator:
    """
    多平台协调器 - AI顾问委员会协调中心
    
    职责：
    1. 管理多个AI平台适配器
    2. 协调平台间的协作流程
    3. 整合各平台的分析结果
    4. 优化平台调用策略
    
    工作流程：
    1. 免费平台（平台A）：快速筛选高价值信息
    2. Qwen联网搜索（平台B）：补充实时动态
    3. Qwen深度分析（平台C）：综合研判生成最终报告
    
    注意：所有搜索和分析都由Qwen负责，DeepSeek只负责交易决策
    """
    
    def __init__(
        self,
        free_platform: Optional[FreePlatformAdapter] = None,
        search_platform: Optional[QwenSearchAdapter] = None,
        deep_platform: Optional[QwenDeepAdapter] = None
    ):
        """
        初始化多平台协调器
        
        Args:
            free_platform: 免费平台适配器
            search_platform: 搜索平台适配器
            deep_platform: 深度分析平台适配器
        """
        self.platforms: Dict[str, BasePlatformAdapter] = {}
        
        if free_platform:
            self.platforms["free"] = free_platform
        if search_platform:
            self.platforms["search"] = search_platform
        if deep_platform:
            self.platforms["deep"] = deep_platform
        
        # 初始化云平台并行协调器（核心：三平台同时调用）
        self.cloud_coordinator = CloudPlatformCoordinator()
        
        self.coordination_history: List[Dict[str, Any]] = []
        
        logger.info(f"✅ 多平台协调器初始化完成，已注册 {len(self.platforms)} 个平台 + 云平台并行协调器")
    
    async def coordinate_analysis(
        self,
        data_sources: Dict[str, Any],
        query_context: Optional[Dict[str, Any]] = None,
        use_all_platforms: bool = True
    ) -> Dict[str, Any]:
        """
        协调多平台分析
        
        Args:
            data_sources: 原始数据源
            query_context: 查询上下文
            use_all_platforms: 是否使用所有平台（否则智能选择）
        
        Returns:
            整合后的综合分析报告
        """
        start_time = datetime.now()
        logger.info("🎯 多平台协调分析开始...")
        
        try:
            results = {}
            total_cost = 0.0
            
            # === 阶段1：免费平台快速筛选 ===
            if "free" in self.platforms and self.platforms["free"].enabled:
                logger.info("📊 阶段1: 免费平台快速筛选...")
                free_result = await self.platforms["free"].analyze(
                    data_sources=data_sources,
                    query_context=query_context
                )
                results["free_platform"] = free_result
                total_cost += free_result.get("cost", 0.0)
                
                logger.info(f"✓ 免费平台筛选完成，发现 {len(free_result.get('key_findings', []))} 个关键点")
            
            # === 阶段2：云平台并行搜索与交叉验证（核心升级）===
            should_search = self._should_use_search(results, query_context)
            
            if should_search:
                logger.info("🔍 阶段2: 云平台并行搜索与交叉验证...")
                
                # 使用云平台协调器：同时调用三大平台（百度+腾讯+火山）
                cloud_search_result = await self.cloud_coordinator.parallel_search_and_verify(
                    data_sources=data_sources,
                    query_context=query_context
                )
                results["cloud_platforms"] = cloud_search_result
                
                # 记录验证元数据
                metadata = cloud_search_result.get("verification_metadata", {})
                logger.info(
                    f"✓ 云平台并行验证完成: "
                    f"{metadata.get('successful_platforms', 0)}/{metadata.get('total_platforms_called', 0)} 个平台成功, "
                    f"共识度={metadata.get('platform_consensus', 0):.1%}, "
                    f"置信度={cloud_search_result.get('confidence', 0):.2f}"
                )
                
                # 如果还配置了原有的search平台，也调用（兼容性）
                if "search" in self.platforms and self.platforms["search"].enabled:
                    logger.info("🔍 补充: Qwen DashScope搜索...")
                    search_result = await self.platforms["search"].analyze(
                        data_sources=data_sources,
                        query_context=query_context
                    )
                    results["search_platform"] = search_result
                    total_cost += search_result.get("cost", 0.0)
            
            # === 阶段3：深度综合分析 ===
            if "deep" in self.platforms and self.platforms["deep"].enabled:
                logger.info("🧠 阶段3: Qwen深度综合分析...")
                
                # 构建深度分析的输入（包含云平台验证结果）
                deep_input = {
                    "raw_data": data_sources,
                    "free_platform_result": results.get("free_platform"),
                    "search_result": results.get("search_platform"),
                    "cloud_platforms_result": results.get("cloud_platforms")  # 新增：云平台验证结果
                }
                
                deep_result = await self.platforms["deep"].analyze(
                    data_sources=deep_input,
                    query_context=query_context
                )
                results["deep_platform"] = deep_result
                total_cost += deep_result.get("cost", 0.0)
                
                logger.info(f"✓ 深度分析完成，置信度 {deep_result.get('confidence', 0):.2f}")
            
            # === 整合最终报告 ===
            final_report = self._integrate_results(results, data_sources)
            final_report["coordination_metadata"] = {
                "platforms_used": list(results.keys()),
                "total_cost": total_cost,
                "processing_time_seconds": (datetime.now() - start_time).total_seconds(),
                "timestamp": datetime.now()
            }
            
            # 记录协调历史
            self._record_coordination(final_report)
            
            logger.info(
                f"✅ 多平台协调完成: "
                f"使用{len(results)}个平台, "
                f"耗时{final_report['coordination_metadata']['processing_time_seconds']:.2f}秒, "
                f"成本${total_cost:.4f}"
            )
            
            return final_report
        
        except Exception as e:
            logger.error(f"❌ 多平台协调失败: {e}", exc_info=True)
            
            return {
                "error": str(e),
                "platforms_attempted": list(self.platforms.keys()),
                "timestamp": datetime.now(),
                "success": False
            }
    
    def _should_use_search(
        self,
        preliminary_results: Dict[str, Any],
        query_context: Optional[Dict[str, Any]]
    ) -> bool:
        """
        判断是否需要使用实时搜索
        
        策略：
        1. 如果免费平台发现高影响力事件 -> 使用搜索
        2. 如果用户明确要求实时信息 -> 使用搜索
        3. 如果市场异常波动 -> 使用搜索
        4. 默认：不使用（节省成本）
        """
        # 策略1：检查免费平台结果
        free_result = preliminary_results.get("free_platform", {})
        high_impact_count = len([
            f for f in free_result.get("key_findings", [])
            if any(keyword in f for keyword in ["监管", "黑客", "重大", "突破"])
        ])
        
        if high_impact_count >= 2:
            logger.info("🎯 检测到重大事件，启用实时搜索")
            return True
        
        # 策略2：用户明确要求
        if query_context and query_context.get("require_realtime", False):
            logger.info("🎯 用户要求实时信息，启用搜索")
            return True
        
        # 策略3：市场异常（可以后续扩展）
        # TODO: 检查价格波动、交易量异常等
        
        # 默认不使用
        logger.info("💡 常规情况，跳过实时搜索以节省成本")
        return False
    
    def _integrate_results(
        self,
        platform_results: Dict[str, Any],
        original_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        整合各平台结果，生成最终报告
        
        整合策略：
        - 以Qwen深度分析为主体
        - 补充其他平台的关键发现
        - 聚合风险和机会
        """
        deep_result = platform_results.get("deep_platform", {})
        free_result = platform_results.get("free_platform", {})
        search_result = platform_results.get("search_platform", {})
        
        # 基础结构
        integrated = {
            "timestamp": datetime.now(),
            "platforms_used": list(platform_results.keys()),
            "success": True
        }
        
        # 主要分析（优先使用深度分析）
        if deep_result:
            integrated.update({
                "analysis": deep_result.get("analysis", ""),
                "market_sentiment": deep_result.get("market_sentiment", "neutral"),
                "sentiment_score": deep_result.get("sentiment_score", 0.0),
                "confidence": deep_result.get("confidence", 0.8)
            })
        elif free_result:
            integrated.update({
                "analysis": free_result.get("analysis", ""),
                "market_sentiment": "neutral",
                "sentiment_score": 0.0,
                "confidence": 0.6
            })
        
        # 聚合关键发现
        all_findings = []
        for platform_key, result in platform_results.items():
            findings = result.get("key_findings", [])
            for finding in findings:
                if finding not in all_findings:  # 去重
                    all_findings.append(finding)
        integrated["key_findings"] = all_findings[:10]  # 最多10个
        
        # 聚合风险因素
        all_risks = []
        if deep_result:
            all_risks.extend(deep_result.get("risk_factors", []))
        integrated["risk_factors"] = all_risks[:5]  # 最多5个
        
        # 聚合机会点
        all_opportunities = []
        if deep_result:
            all_opportunities.extend(deep_result.get("opportunities", []))
        integrated["opportunities"] = all_opportunities[:3]  # 最多3个
        
        # 平台贡献明细
        integrated["platform_contributions"] = {
            platform_key: {
                "role": result.get("role", ""),
                "confidence": result.get("confidence", 0.0),
                "cost": result.get("cost", 0.0),
                "findings_count": len(result.get("key_findings", []))
            }
            for platform_key, result in platform_results.items()
        }
        
        return integrated
    
    def _record_coordination(self, report: Dict[str, Any]):
        """记录协调历史"""
        self.coordination_history.append({
            "timestamp": report.get("timestamp"),
            "platforms_used": report.get("platforms_used", []),
            "total_cost": report.get("coordination_metadata", {}).get("total_cost", 0.0),
            "confidence": report.get("confidence", 0.0),
            "success": report.get("success", False)
        })
        
        # 只保留最近100条
        if len(self.coordination_history) > 100:
            self.coordination_history = self.coordination_history[-100:]
    
    async def health_check_all(self) -> Dict[str, bool]:
        """检查所有平台健康状态"""
        results = {}
        
        for platform_name, platform in self.platforms.items():
            try:
                results[platform_name] = await platform.health_check()
            except Exception as e:
                logger.error(f"平台 {platform_name} 健康检查失败: {e}")
                results[platform_name] = False
        
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """获取协调器统计信息"""
        return {
            "total_coordinations": len(self.coordination_history),
            "platforms": {
                name: platform.get_statistics()
                for name, platform in self.platforms.items()
            },
            "recent_coordinations": self.coordination_history[-10:]  # 最近10次
        }

