"""
Debate System - 多空辩论机制
借鉴 TradingAgents 的辩论逻辑，适配 AIcoin

v2.0 更新：集成PromptManager，支持文件化Prompt管理
"""

import json
import time
import re
import asyncio
from typing import Dict, Any, Optional, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


def format_intelligence_with_verification(intelligence_report: Dict) -> str:
    """
    格式化情报报告，突出显示多平台验证信息（公共函数）
    
    Args:
        intelligence_report: 情报报告字典
        
    Returns:
        格式化的情报字符串
    """
    if not intelligence_report:
        return "Intelligence Report: No data available"
    
    output = "Intelligence Report (Multi-Platform Verified):\n"
    output += f"  Market Sentiment: {intelligence_report.get('market_sentiment', 'NEUTRAL')}\n"
    output += f"  Confidence: {intelligence_report.get('confidence', 0):.2f}\n"
    
    # 显示多平台验证信息
    platform_contributions = intelligence_report.get('platform_contributions', {})
    if platform_contributions:
        output += f"\n  📊 Multi-Platform Verification ({len(platform_contributions)} platforms):\n"
        for platform, contrib in platform_contributions.items():
            output += f"    - {platform}: {contrib.get('weight', 0):.1%} weight\n"
        
        # 显示共识度
        platform_consensus = intelligence_report.get('platform_consensus', 0)
        output += f"  🎯 Platform Consensus: {platform_consensus:.1%}\n"
    
    # 显示关键信息
    key_news = intelligence_report.get('key_news', [])
    if key_news:
        output += f"\n  📰 Key News ({len(key_news)}):\n"
        for news in key_news[:3]:
            output += f"    - {news.get('title', 'N/A')}\n"
    
    # 显示风险因素
    risk_factors = intelligence_report.get('risk_factors', [])
    if risk_factors:
        output += f"\n  ⚠️  Risk Factors: {', '.join(risk_factors[:3])}\n"
    
    # 显示机会
    opportunities = intelligence_report.get('opportunities', [])
    if opportunities:
        output += f"\n  💡 Opportunities: {', '.join(opportunities[:3])}\n"
    
    return output


class DebateState:
    """
    辩论状态管理
    借鉴 TradingAgents 的 InvestDebateState
    """
    
    def __init__(self):
        self.history: str = ""
        self.bull_history: str = ""
        self.bear_history: str = ""
        self.current_response: str = ""
        self.count: int = 0
        self.judge_decision: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "history": self.history,
            "bull_history": self.bull_history,
            "bear_history": self.bear_history,
            "current_response": self.current_response,
            "count": self.count,
            "judge_decision": self.judge_decision
        }


class BullAnalyst:
    """
    多头分析师
    完全复用 TradingAgents 的 Prompt 模板
    
    v2.0: 支持从文件加载Prompt（借鉴NOFX）
    """
    
    def __init__(self, llm_client, prompt_manager=None):
        self.client = llm_client
        self.prompt_manager = prompt_manager
    
    def _format_intelligence_with_verification(self, intelligence_report: Dict) -> str:
        """
        格式化情报报告，突出显示多平台验证信息
        
        Args:
            intelligence_report: 情报报告字典
            
        Returns:
            格式化的情报字符串
        """
        if not intelligence_report:
            return "Intelligence Report: No data available"
        
        output = "Intelligence Report (Multi-Platform Verified):\n"
        output += f"  Market Sentiment: {intelligence_report.get('market_sentiment', 'NEUTRAL')}\n"
        output += f"  Confidence: {intelligence_report.get('confidence', 0):.2f}\n"
        
        # 显示多平台验证信息
        platform_contributions = intelligence_report.get('platform_contributions', {})
        if platform_contributions:
            output += f"\n  📊 Multi-Platform Verification ({len(platform_contributions)} platforms):\n"
            for platform, contribution in platform_contributions.items():
                platform_conf = contribution.get('confidence', 0)
                output += f"    - {platform}: confidence={platform_conf:.2f}\n"
            
            platform_consensus = intelligence_report.get('platform_consensus', 0)
            if platform_consensus > 0:
                output += f"\n  🎯 Platform Consensus: {platform_consensus:.1%}\n"
                output += "  💡 Note: Higher consensus indicates stronger agreement across platforms.\n"
        
        # 显示摘要
        summary = intelligence_report.get('summary', '')
        if summary:
            output += f"\n  Summary: {summary}\n"
        
        return output
    
    async def analyze(
        self,
        market_data: Dict,
        intelligence_report: Dict,
        debate_state: DebateState,
        past_memories: List[Dict] = None
    ) -> str:
        """
        生成多头论点
        
        Args:
            market_data: 市场数据
            intelligence_report: 情报报告
            debate_state: 辩论状态
            past_memories: 历史记忆
        
        Returns:
            多头论点字符串
        """
        
        # 构建历史记忆字符串
        past_memory_str = ""
        if past_memories:
            for rec in past_memories:
                past_memory_str += rec.get("recommendation", "") + "\n\n"
        
        # 尝试从PromptManager加载模板（借鉴NOFX）
        if self.prompt_manager:
            try:
                template = self.prompt_manager.get_template("debate", "bull_analyst")
                base_prompt = template.content
                logger.debug("✅ 使用Bull Analyst文件模板")
            except Exception as e:
                logger.warning(f"⚠️  加载Bull Analyst模板失败: {e}，使用硬编码版本")
                base_prompt = """You are a Bull Analyst advocating for investing in the cryptocurrency. Your task is to build a strong, evidence-based case emphasizing growth potential, competitive advantages, and positive market indicators. Leverage the provided research and data to address concerns and counter bearish arguments effectively.

Key points to focus on:
- Growth Potential: Highlight the asset's market opportunities, price projections, and adoption trends.
- Competitive Advantages: Emphasize factors like unique technology, strong community, or dominant market positioning.
- Positive Indicators: Use technical analysis, on-chain data, and recent positive news as evidence.
- Bear Counterpoints: Critically analyze the bear argument with specific data and sound reasoning, addressing concerns thoroughly and showing why the bull perspective holds stronger merit.
- Engagement: Present your argument in a conversational style, engaging directly with the bear analyst's points and debating effectively rather than just listing data.

Use this information to deliver a compelling bull argument, refute the bear's concerns, and engage in a dynamic debate that demonstrates the strengths of the bull position. You must also address reflections and learn from lessons and mistakes you made in the past.
"""
        else:
            # 硬编码版本（fallback）
            base_prompt = """You are a Bull Analyst advocating for investing in the cryptocurrency. Your task is to build a strong, evidence-based case emphasizing growth potential, competitive advantages, and positive market indicators. Leverage the provided research and data to address concerns and counter bearish arguments effectively.

Key points to focus on:
- Growth Potential: Highlight the asset's market opportunities, price projections, and adoption trends.
- Competitive Advantages: Emphasize factors like unique technology, strong community, or dominant market positioning.
- Positive Indicators: Use technical analysis, on-chain data, and recent positive news as evidence.
- Bear Counterpoints: Critically analyze the bear argument with specific data and sound reasoning, addressing concerns thoroughly and showing why the bull perspective holds stronger merit.
- Engagement: Present your argument in a conversational style, engaging directly with the bear analyst's points and debating effectively rather than just listing data.

Use this information to deliver a compelling bull argument, refute the bear's concerns, and engage in a dynamic debate that demonstrates the strengths of the bull position. You must also address reflections and learn from lessons and mistakes you made in the past.
"""
        
        # 拼接动态数据（借鉴NOFX的buildUserPrompt）
        # 增强：展示多平台验证信息
        intelligence_summary = format_intelligence_with_verification(intelligence_report)
        
        prompt = f"""{base_prompt}

Resources available:
Market Data: {json.dumps(market_data, indent=2)}

{intelligence_summary}

Conversation history of the debate: {debate_state.history}

Last bear argument: {debate_state.current_response}

Reflections from similar situations and lessons learned: {past_memory_str}
"""
        
        try:
            # 调用 LLM（适配 AIcoin 的 OpenAI 客户端）
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            argument = f"Bull Analyst: {content}"
            
            # 更新辩论状态（完全复用 TradingAgents 的逻辑）
            debate_state.history += "\n" + argument
            debate_state.bull_history += "\n" + argument
            debate_state.current_response = argument
            debate_state.count += 1
            
            logger.info(f"🐂 Bull Analyst (Round {debate_state.count}): {content[:100]}...")
            
            return argument
            
        except Exception as e:
            logger.error(f"Bull Analyst 分析失败: {e}", exc_info=True)
            return f"Bull Analyst: [分析失败: {str(e)}]"


class BearAnalyst:
    """
    空头分析师
    完全复用 TradingAgents 的 Prompt 模板
    
    v2.0: 支持从文件加载Prompt（借鉴NOFX）
    """
    
    def __init__(self, llm_client, prompt_manager=None):
        self.client = llm_client
        self.prompt_manager = prompt_manager
    
    def _format_intelligence_with_verification(self, intelligence_report: Dict) -> str:
        """
        格式化情报报告，突出显示多平台验证信息
        
        Args:
            intelligence_report: 情报报告字典
            
        Returns:
            格式化的情报字符串
        """
        if not intelligence_report:
            return "Intelligence Report: No data available"
        
        output = "Intelligence Report (Multi-Platform Verified):\n"
        output += f"  Market Sentiment: {intelligence_report.get('market_sentiment', 'NEUTRAL')}\n"
        output += f"  Confidence: {intelligence_report.get('confidence', 0):.2f}\n"
        
        # 显示多平台验证信息
        platform_contributions = intelligence_report.get('platform_contributions', {})
        if platform_contributions:
            output += f"\n  📊 Multi-Platform Verification ({len(platform_contributions)} platforms):\n"
            for platform, contribution in platform_contributions.items():
                platform_conf = contribution.get('confidence', 0)
                output += f"    - {platform}: confidence={platform_conf:.2f}\n"
            
            platform_consensus = intelligence_report.get('platform_consensus', 0)
            if platform_consensus > 0:
                output += f"\n  🎯 Platform Consensus: {platform_consensus:.1%}\n"
                output += "  💡 Note: Higher consensus indicates stronger agreement across platforms.\n"
        
        # 显示摘要
        summary = intelligence_report.get('summary', '')
        if summary:
            output += f"\n  Summary: {summary}\n"
        
        return output
    
    async def analyze(
        self,
        market_data: Dict,
        intelligence_report: Dict,
        debate_state: DebateState,
        past_memories: List[Dict] = None
    ) -> str:
        """
        生成空头论点
        
        Args:
            market_data: 市场数据
            intelligence_report: 情报报告
            debate_state: 辩论状态
            past_memories: 历史记忆
        
        Returns:
            空头论点字符串
        """
        
        past_memory_str = ""
        if past_memories:
            for rec in past_memories:
                past_memory_str += rec.get("recommendation", "") + "\n\n"
        
        # 尝试从PromptManager加载模板（借鉴NOFX）
        if self.prompt_manager:
            try:
                template = self.prompt_manager.get_template("debate", "bear_analyst")
                base_prompt = template.content
                logger.debug("✅ 使用Bear Analyst文件模板")
            except Exception as e:
                logger.warning(f"⚠️  加载Bear Analyst模板失败: {e}，使用硬编码版本")
                base_prompt = """You are a Bear Analyst making the case against investing in the cryptocurrency. Your goal is to present a well-reasoned argument emphasizing risks, challenges, and negative indicators. Leverage the provided research and data to highlight potential downsides and counter bullish arguments effectively.

Key points to focus on:
- Risks and Challenges: Highlight factors like market saturation, regulatory threats, or macroeconomic headwinds that could hinder the asset's performance.
- Competitive Weaknesses: Emphasize vulnerabilities such as weaker technology, declining adoption, or threats from competitors.
- Negative Indicators: Use evidence from technical analysis, on-chain data, or recent adverse news to support your position.
- Bull Counterpoints: Critically analyze the bull argument with specific data and sound reasoning, exposing weaknesses or over-optimistic assumptions.
- Engagement: Present your argument in a conversational style, directly engaging with the bull analyst's points and debating effectively rather than simply listing facts.

Use this information to deliver a compelling bear argument, refute the bull's claims, and engage in a dynamic debate that demonstrates the risks and weaknesses of investing in the asset. You must also address reflections and learn from lessons and mistakes you made in the past.
"""
        else:
            base_prompt = """You are a Bear Analyst making the case against investing in the cryptocurrency. Your goal is to present a well-reasoned argument emphasizing risks, challenges, and negative indicators. Leverage the provided research and data to highlight potential downsides and counter bullish arguments effectively.

Key points to focus on:
- Risks and Challenges: Highlight factors like market saturation, regulatory threats, or macroeconomic headwinds that could hinder the asset's performance.
- Competitive Weaknesses: Emphasize vulnerabilities such as weaker technology, declining adoption, or threats from competitors.
- Negative Indicators: Use evidence from technical analysis, on-chain data, or recent adverse news to support your position.
- Bull Counterpoints: Critically analyze the bull argument with specific data and sound reasoning, exposing weaknesses or over-optimistic assumptions.
- Engagement: Present your argument in a conversational style, directly engaging with the bull analyst's points and debating effectively rather than simply listing facts.

Use this information to deliver a compelling bear argument, refute the bull's claims, and engage in a dynamic debate that demonstrates the risks and weaknesses of investing in the asset. You must also address reflections and learn from lessons and mistakes you made in the past.
"""
        
        # 拼接动态数据
        # 增强：展示多平台验证信息
        intelligence_summary = format_intelligence_with_verification(intelligence_report)
        
        prompt = f"""{base_prompt}

Resources available:
Market Data: {json.dumps(market_data, indent=2)}

{intelligence_summary}

Conversation history of the debate: {debate_state.history}

Last bull argument: {debate_state.current_response}

Reflections from similar situations and lessons learned: {past_memory_str}
"""
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.choices[0].message.content
            argument = f"Bear Analyst: {content}"
            
            debate_state.history += "\n" + argument
            debate_state.bear_history += "\n" + argument
            debate_state.current_response = argument
            debate_state.count += 1
            
            logger.info(f"🐻 Bear Analyst (Round {debate_state.count}): {content[:100]}...")
            
            return argument
            
        except Exception as e:
            logger.error(f"Bear Analyst 分析失败: {e}", exc_info=True)
            return f"Bear Analyst: [分析失败: {str(e)}]"


class ResearchManager:
    """
    研究经理
    完全复用 TradingAgents 的 Prompt 模板
    
    v2.0: 支持从文件加载Prompt（借鉴NOFX）
    """
    
    def __init__(self, llm_client, prompt_manager=None):
        self.client = llm_client
        self.prompt_manager = prompt_manager
    
    def _format_intelligence_with_verification(self, intelligence_report: Dict) -> str:
        """
        格式化情报报告，突出显示多平台验证信息
        
        Args:
            intelligence_report: 情报报告字典
            
        Returns:
            格式化的情报字符串
        """
        if not intelligence_report:
            return "Intelligence Report: No data available"
        
        output = "Intelligence Report (Multi-Platform Verified):\n"
        output += f"  Market Sentiment: {intelligence_report.get('market_sentiment', 'NEUTRAL')}\n"
        output += f"  Confidence: {intelligence_report.get('confidence', 0):.2f}\n"
        
        # 显示多平台验证信息
        platform_contributions = intelligence_report.get('platform_contributions', {})
        if platform_contributions:
            output += f"\n  📊 Multi-Platform Verification ({len(platform_contributions)} platforms):\n"
            for platform, contribution in platform_contributions.items():
                platform_conf = contribution.get('confidence', 0)
                output += f"    - {platform}: confidence={platform_conf:.2f}\n"
            
            platform_consensus = intelligence_report.get('platform_consensus', 0)
            if platform_consensus > 0:
                output += f"\n  🎯 Platform Consensus: {platform_consensus:.1%}\n"
                output += "  💡 Note: Higher consensus indicates stronger agreement across platforms.\n"
        
        # 显示摘要
        summary = intelligence_report.get('summary', '')
        if summary:
            output += f"\n  Summary: {summary}\n"
        
        return output
    
    async def summarize_debate(
        self,
        debate_state: DebateState,
        market_data: Dict,
        intelligence_report: Dict,
        past_memories: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        综合辩论结果，做出最终判断
        
        Args:
            debate_state: 辩论状态
            market_data: 市场数据
            intelligence_report: 情报报告
            past_memories: 历史记忆
        
        Returns:
            最终决策字典
        """
        
        past_memory_str = ""
        if past_memories:
            for rec in past_memories:
                past_memory_str += rec.get("recommendation", "") + "\n\n"
        
        # 尝试从PromptManager加载模板（借鉴NOFX）
        if self.prompt_manager:
            try:
                template = self.prompt_manager.get_template("debate", "research_manager")
                base_prompt = template.content
                logger.debug("✅ 使用Research Manager文件模板")
            except Exception as e:
                logger.warning(f"⚠️  加载Research Manager模板失败: {e}，使用硬编码版本")
                base_prompt = """As the portfolio manager and debate facilitator, your role is to critically evaluate this round of debate and make a definitive decision: align with the bear analyst, the bull analyst, or choose Hold only if it is strongly justified based on the arguments presented.

Summarize the key points from both sides concisely, focusing on the most compelling evidence or reasoning. Your recommendation—Buy, Sell, or Hold—must be clear and actionable. Avoid defaulting to Hold simply because both sides have valid points; commit to a stance grounded in the debate's strongest arguments.

Additionally, develop a detailed investment plan. This should include:

Your Recommendation: A decisive stance supported by the most convincing arguments.
Rationale: An explanation of why these arguments lead to your conclusion.
Strategic Actions: Concrete steps for implementing the recommendation.
Take into account your past mistakes on similar situations. Use these insights to refine your decision-making and ensure you are learning and improving. Present your analysis conversationally, as if speaking naturally, without special formatting.
"""
        else:
            base_prompt = """As the portfolio manager and debate facilitator, your role is to critically evaluate this round of debate and make a definitive decision: align with the bear analyst, the bull analyst, or choose Hold only if it is strongly justified based on the arguments presented.

Summarize the key points from both sides concisely, focusing on the most compelling evidence or reasoning. Your recommendation—Buy, Sell, or Hold—must be clear and actionable. Avoid defaulting to Hold simply because both sides have valid points; commit to a stance grounded in the debate's strongest arguments.

Additionally, develop a detailed investment plan. This should include:

Your Recommendation: A decisive stance supported by the most convincing arguments.
Rationale: An explanation of why these arguments lead to your conclusion.
Strategic Actions: Concrete steps for implementing the recommendation.
Take into account your past mistakes on similar situations. Use these insights to refine your decision-making and ensure you are learning and improving. Present your analysis conversationally, as if speaking naturally, without special formatting.
"""
        
        # 拼接动态数据
        # 增强：展示多平台验证信息
        intelligence_summary = format_intelligence_with_verification(intelligence_report)
        
        prompt = f"""{base_prompt}

Here are your past reflections on mistakes:
"{past_memory_str}"

Here is the debate:
Debate History:
{debate_state.history}

Market Data Context:
{json.dumps(market_data, indent=2)}

{intelligence_summary}
"""
        
        try:
            response = self.client.chat.completions.create(
                model="deepseek-chat",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            
            # 尝试解析 JSON（容错处理）
            decision = self._safe_parse_json(content)
            
            debate_state.judge_decision = json.dumps(decision, indent=2)
            
            logger.info(f"📊 Research Manager 决策: {decision.get('recommendation')} (置信度: {decision.get('confidence')})")
            
            return decision
            
        except Exception as e:
            logger.error(f"Research Manager 综合失败: {e}", exc_info=True)
            return {
                "recommendation": "HOLD",
                "confidence": 0.5,
                "rationale": f"综合失败: {str(e)}",
                "error": str(e)
            }
    
    def _safe_parse_json(self, response: str) -> Dict:
        """安全解析 LLM 响应（容错处理）"""
        try:
            # 尝试直接解析 JSON
            return json.loads(response)
        except json.JSONDecodeError:
            # 尝试提取 JSON 代码块
            json_match = re.search(r'```json\s*(.*?)\s*```', response, re.DOTALL)
            if json_match:
                try:
                    return json.loads(json_match.group(1))
                except:
                    pass
            
            # 如果都失败，返回默认结构
            logger.warning(f"无法解析 LLM 响应为 JSON，使用默认值: {response[:100]}")
            return {
                "recommendation": "HOLD",
                "confidence": 0.5,
                "rationale": response,
                "raw_response": response
            }


class DebateCoordinator:
    """
    辩论协调器
    借鉴 TradingAgents 的 conditional_logic.py 中的轮次控制
    """
    
    def __init__(self, llm_client, max_debate_rounds: int = 1, timeout_seconds: int = 60, prompt_manager=None):
        self.bull_analyst = BullAnalyst(llm_client, prompt_manager)
        self.bear_analyst = BearAnalyst(llm_client, prompt_manager)
        self.research_manager = ResearchManager(llm_client, prompt_manager)
        self.max_debate_rounds = max_debate_rounds
        self.timeout_seconds = timeout_seconds
    
    def should_continue_debate(self, debate_state: DebateState) -> str:
        """
        判断辩论是否继续
        完全复用 TradingAgents 的轮次控制逻辑
        
        Returns:
            "Research Manager" | "Bear Researcher" | "Bull Researcher"
        """
        if debate_state.count >= 2 * self.max_debate_rounds:
            return "Research Manager"
        
        if debate_state.current_response.startswith("Bull"):
            return "Bear Researcher"
        
        return "Bull Researcher"
    
    async def conduct_debate(
        self,
        market_data: Dict,
        intelligence_report: Dict,
        past_memories: List[Dict] = None
    ) -> Dict[str, Any]:
        """
        组织完整的辩论流程
        
        流程：Bull → Bear → Bull → Bear → ... → Research Manager
        
        Args:
            market_data: 市场数据
            intelligence_report: 情报报告
            past_memories: 历史记忆
        
        Returns:
            辩论结果字典
        """
        
        start_time = time.time()
        debate_state = DebateState()
        
        logger.info(f"⚔️  启动多空辩论（最大轮次: {self.max_debate_rounds}，超时: {self.timeout_seconds}秒）")
        
        try:
            # 辩论循环（借鉴 TradingAgents 的流程控制）
            while True:
                # 保护 1：最大轮次限制
                if debate_state.count >= self.max_debate_rounds * 2:
                    logger.info("✅ 达到最大轮次，结束辩论")
                    break
                
                # 保护 2：超时保护
                elapsed = time.time() - start_time
                if elapsed > self.timeout_seconds:
                    logger.warning(f"⏰ 辩论超时（{elapsed:.1f}秒），强制结束")
                    break
                
                # 判断下一步
                next_step = self.should_continue_debate(debate_state)
                
                if next_step == "Research Manager":
                    logger.info("📊 辩论结束，研究经理综合判断...")
                    break
                
                # 执行辩论
                if next_step == "Bull Researcher":
                    await self.bull_analyst.analyze(
                        market_data, intelligence_report, debate_state, past_memories
                    )
                
                elif next_step == "Bear Researcher":
                    await self.bear_analyst.analyze(
                        market_data, intelligence_report, debate_state, past_memories
                    )
            
            # 研究经理综合判断
            final_decision = await self.research_manager.summarize_debate(
                debate_state, market_data, intelligence_report, past_memories
            )
            
            duration = int(time.time() - start_time)
            
            return {
                "debate_history": debate_state.to_dict(),
                "final_decision": final_decision,
                "total_rounds": debate_state.count // 2,
                "consensus_level": self._calculate_consensus(debate_state),
                "duration_seconds": duration
            }
            
        except Exception as e:
            logger.error(f"❌ 辩论异常: {e}", exc_info=True)
            duration = int(time.time() - start_time)
            return {
                "debate_history": debate_state.to_dict(),
                "final_decision": {
                    "recommendation": "HOLD",
                    "confidence": 0.5,
                    "rationale": f"辩论异常: {str(e)}",
                    "error": str(e)
                },
                "total_rounds": debate_state.count // 2,
                "consensus_level": 0.5,
                "duration_seconds": duration,
                "error": str(e)
            }
    
    def _calculate_consensus(self, debate_state: DebateState) -> float:
        """
        计算共识度（简化版）
        
        共识度 = 1 - (实际轮次 / 最大轮次)
        轮次越多说明分歧越大，共识度越低
        """
        max_rounds = self.max_debate_rounds * 2
        actual_rounds = debate_state.count
        
        if max_rounds == 0:
            return 0.5
        
        consensus = 1.0 - (actual_rounds / max_rounds)
        
        return max(0.0, min(1.0, consensus))

