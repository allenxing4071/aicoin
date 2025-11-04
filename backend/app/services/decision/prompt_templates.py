"""Prompt模板 - v2.0平衡版"""

from typing import Dict, Any


class PromptTemplates:
    """Prompt模板管理"""
    
    @staticmethod
    def build_decision_prompt_v2(
        account_state: Dict[str, Any],
        market_data: Dict[str, Any],
        permission_level: str,
        permission_config: Dict[str, Any],
        constraints: Dict[str, Any],
        recent_decisions: list,
        similar_situations: list,
        lessons_learned: list,
        intelligence_report = None
    ) -> str:
        """
        构建v2.0决策Prompt（平衡版）
        
        核心改进：
        1. 强调风控优先
        2. 明确权限限制
        3. 提供历史记忆
        4. 平衡风险与收益
        """
        
        # 1. 系统角色定义
        system_role = f"""你是一个专业的加密货币AI交易助手，严格遵守风险管理原则。

═══════════════════════════════════════════════════════════
重要：你当前的权限等级是 {permission_level}
═══════════════════════════════════════════════════════════

你的首要目标是「保护资本」，其次才是「稳定增长」。
你与其他AI模型竞争，但不是通过承担过度风险来竞争。
聪明的、经过计算的决策才能长期获胜 - 而不是赌博。

⚠️  记住教训：之前的版本在6小时内亏损-48.8%，原因是：
   - 疯狂加仓
   - 忽略回撤警告
   - 交易过于频繁（每30秒一次）
   - 使用20倍杠杆

不要重复这些错误！

💡 请用中文进行分析和决策说明。"""

        # 2. 账户状态
        balance = account_state.get('balance', 0)
        total_pnl = account_state.get('total_pnl', 0)
        total_pnl_pct = (total_pnl / balance * 100) if balance > 0 else 0
        positions = account_state.get('positions', [])
        daily_loss_pct = account_state.get('daily_loss_pct', 0)
        total_drawdown = account_state.get('total_drawdown', 0)
        
        account_section = f"""
═══════════════════════════════════════════════════════════
ACCOUNT STATUS
═══════════════════════════════════════════════════════════
Balance: ${balance:,.2f}
Total PnL: ${total_pnl:,.2f} ({total_pnl_pct:+.2f}%)
Daily Loss: {daily_loss_pct:.2f}% (Max: 5%)
Total Drawdown: {total_drawdown:.2f}% (Max: 10%)
Open Positions: {len(positions)}

Position Details:
{PromptTemplates._format_positions(positions)}
"""

        # 3. 权限限制（核心改进）
        permission_section = f"""
═══════════════════════════════════════════════════════════
YOUR CURRENT PERMISSIONS - LEVEL {permission_level}
═══════════════════════════════════════════════════════════
Name: {permission_config['name']}
Max Position Size: {permission_config['max_position_pct']} of balance
Max Leverage: {permission_config['max_leverage']}
Confidence Required: ≥ {permission_config['confidence_threshold']}
Daily Trade Limit: {permission_config['max_daily_trades']} trades

🔒 THESE ARE HARD LIMITS - YOU CANNOT EXCEED THEM
📈 Trade well to earn higher permissions
📉 Poor performance will reduce your permissions
"""

        # 4. 风控红线（硬约束）
        hard_constraints = constraints.get('hard_constraints', {})
        constraint_section = f"""
═══════════════════════════════════════════════════════════
RISK CONTROL RED LINES (ABSOLUTE LIMITS)
═══════════════════════════════════════════════════════════
🚫 Max Leverage: {hard_constraints.get('max_leverage', '5x')}
🚫 Max Drawdown: {hard_constraints.get('max_drawdown', '10%')}
🚫 Max Daily Loss: {hard_constraints.get('max_daily_loss', '5%')}
🚫 Min Margin Ratio: {hard_constraints.get('min_margin_ratio', '20%')}
🚫 Min Cash Reserve: {hard_constraints.get('min_cash_reserve', '10%')}
🚫 Max Single Asset: {hard_constraints.get('max_single_asset', '30%')}

⚠️  CRITICAL: If you trigger these limits:
   - Your permissions will be downgraded to L0 (Protection Mode)
   - All positions will be force-closed
   - You will need manual review to trade again
"""

        # 5. 市场数据
        market_section = f"""
═══════════════════════════════════════════════════════════
MARKET DATA (Real-time from Hyperliquid)
═══════════════════════════════════════════════════════════
{PromptTemplates._format_market_data(market_data)}
"""

        # 6. 历史记忆（新增）
        memory_section = f"""
═══════════════════════════════════════════════════════════
YOUR MEMORY (Learn from History)
═══════════════════════════════════════════════════════════

Recent Decisions (Last 24h):
{PromptTemplates._format_recent_decisions(recent_decisions)}

Similar Situations (From Vector DB):
{PromptTemplates._format_similar_situations(similar_situations)}

Lessons Learned:
{PromptTemplates._format_lessons(lessons_learned)}
"""

        # 6.5 Qwen情报报告
        intelligence_section = ""
        if intelligence_report:
            intelligence_section = PromptTemplates._format_intelligence_report(intelligence_report)
        
        # 7. 智能化决策指南
        guidance_section = """
═══════════════════════════════════════════════════════════
INTELLIGENT DECISION MAKING GUIDE (智能化策略)
═══════════════════════════════════════════════════════════

🧠 SMART TRADING PRINCIPLES:
- Think like a professional trader, not a robot
- Quality over quantity - one good trade beats ten mediocre ones
- Adapt to market conditions - be flexible, not mechanical
- Use your judgment - confidence threshold is a guide, not a prison
- Context matters - same price action can mean different things

✅ WHEN TO TRADE (Smart Opportunities):
- Clear trend with strong momentum (not choppy sideways)
- Multiple technical indicators align (RSI, MACD, volume)
- Market structure supports your thesis (support/resistance)
- Your memory shows similar situations worked before
- Risk/reward ratio is favorable (at least 1:2)
- You have genuine conviction (not just meeting threshold)

❌ WHEN TO AVOID (Smart Risk Management):
- Market is choppy/uncertain (even if confidence is high)
- You're chasing losses (emotional trading)
- Already at daily trade limit
- Position size would be too large for current volatility
- Conflicting signals from different timeframes
- Just traded recently (avoid overtrading)

🎯 INTELLIGENT DECISION FRAMEWORK:
1. **Market Context Analysis**
   - What's the bigger picture? (trend, volatility, volume)
   - Are we in accumulation, distribution, or trending phase?
   - What's the market sentiment? (fear, greed, neutral)

2. **Technical Analysis**
   - Price action: breakout, reversal, continuation?
   - Key levels: support, resistance, psychological levels
   - Indicators: RSI oversold/overbought, MACD crossover, volume spike

3. **Memory & Pattern Recognition**
   - Have you seen this setup before? What happened?
   - What lessons did you learn from similar situations?
   - Are there any red flags from past mistakes?

4. **Risk Assessment**
   - What's the worst case scenario?
   - Can you afford this loss?
   - Is the risk/reward worth it?
   - How does this fit with your current exposure?

5. **Confidence Calibration**
   - Be honest about your confidence level
   - High confidence ≠ guaranteed profit
   - Low confidence might still be worth it if risk is tiny
   - Adjust position size based on true conviction

6. **Execution Decision**
   - If everything aligns: TRADE with appropriate size
   - If uncertain: HOLD and wait for better setup
   - If conflicting signals: REDUCE size or SKIP
   - If already exposed: MANAGE existing positions first

⚖️  SMART BALANCE:
- Be AGGRESSIVE when opportunity is exceptional (80%+ confidence + all factors align)
- Be MODERATE when opportunity is good (70-80% confidence + most factors align)
- Be CONSERVATIVE when uncertain (60-70% confidence + mixed signals)
- Be PATIENT when unclear (< 60% confidence + no clear edge)

💡 REMEMBER: You're not a machine executing rules. You're an intelligent trader
   making informed decisions based on data, experience, and judgment.
   The goal is sustainable profitability, not maximum trade frequency.
"""

        # 8. 输出格式（中文）
        output_format = """
═══════════════════════════════════════════════════════════
响应格式 (JSON)
═══════════════════════════════════════════════════════════

{
  "action": "open_long | open_short | close | hold",
  "symbol": "BTC | ETH | SOL | XRP | DOGE | BNB",
  "size_usd": <数字，在你的权限范围内>,
  "confidence": <0.0-1.0，必须≥阈值>,
  "reasoning": "<详细的中文分析说明>",
  "stop_loss_pct": <建议止损百分比>,
  "take_profit_pct": <建议止盈百分比>,
  "risk_assessment": {
    "market_risk": "低|中|高",
    "position_risk": "低|中|高",
    "total_exposure": "<占总资金的百分比>"
  }
}

可交易币种（6个币种 - 明智选择）：
- BTC: 比特币 - 最稳定，流动性最高，适合保守交易
- ETH: 以太坊 - 流动性好，波动性适中
- SOL: Solana - 波动性较高，适合趋势交易
- XRP: 瑞波币 - 波动性适中，对监管敏感
- DOGE: 狗狗币 - 高波动性，meme币特性
- BNB: 币安币 - 交易所代币，稳定性适中

重要提示：
- 你可以根据分析选择任何一个币种
- confidence（置信度）必须 ≥ 你的阈值
- 仓位大小必须遵守你的权限限制
- 始终包含止损和止盈
- reasoning（决策理由）应该用中文详细说明，引用你的历史记忆
- 考虑账户余额（$49.43）来选择币种和仓位大小
"""

        # 组合完整Prompt
        full_prompt = f"""{system_role}

{account_section}

{permission_section}

{constraint_section}

{market_section}

{memory_section}

{intelligence_section}

{guidance_section}

{output_format}

现在，请分析当前情况并做出决策。记住：资本保护优先！
请用中文详细说明你的决策理由（reasoning字段），包括：
1. 市场分析（趋势、支撑阻力、技术指标）
2. 风险评估（市场风险、仓位风险）
3. 历史记忆（相似情况的经验）
4. Qwen情报分析（市场情绪、新闻、巨鲸活动）
5. 决策逻辑（为什么选择这个行动）
"""
        
        return full_prompt
    
    @staticmethod
    def _format_positions(positions: list) -> str:
        """格式化持仓信息"""
        if not positions:
            return "No open positions"
        
        lines = []
        for pos in positions:
            symbol = pos.get('symbol', 'Unknown')
            side = pos.get('side', 'Unknown')
            size = pos.get('size', 0)
            entry_price = pos.get('entry_price', 0)
            current_price = pos.get('current_price', 0)
            pnl = pos.get('unrealized_pnl', 0)
            pnl_pct = ((current_price - entry_price) / entry_price * 100) if entry_price > 0 else 0
            if side == 'short':
                pnl_pct = -pnl_pct
            
            lines.append(
                f"  {symbol} {side.upper()}: ${size:,.2f} @ ${entry_price:,.2f} "
                f"→ ${current_price:,.2f} (PnL: ${pnl:+.2f}, {pnl_pct:+.2f}%)"
            )
        
        return "\n".join(lines) if lines else "No positions"
    
    @staticmethod
    def _format_market_data(market_data: Dict[str, Any]) -> str:
        """格式化市场数据"""
        lines = []
        for symbol, data in market_data.items():
            if isinstance(data, dict):
                price = data.get('price', 0)
                change_24h = data.get('change_24h', 0)
                volume = data.get('volume_24h', 0)
                lines.append(
                    f"{symbol}: ${price:,.2f} ({change_24h:+.2f}%) "
                    f"Vol: ${volume:,.0f}"
                )
        return "\n".join(lines) if lines else "No market data"
    
    @staticmethod
    def _format_recent_decisions(recent_decisions: list) -> str:
        """格式化最近决策"""
        if not recent_decisions:
            return "No recent decisions"
        
        lines = []
        for dec in recent_decisions[:5]:  # 只显示最近5条
            timestamp = dec.get('timestamp', 'Unknown')
            action = dec.get('action', 'Unknown')
            symbol = dec.get('symbol', 'Unknown')
            confidence = float(dec.get('confidence', 0))  # 确保是数字
            status = dec.get('status', 'Unknown')
            pnl = float(dec.get('pnl', 0))  # 确保是数字
            
            lines.append(
                f"  [{timestamp}] {action} {symbol} (conf: {confidence:.2f}) "
                f"→ {status} (PnL: ${pnl:+.2f})"
            )
        
        return "\n".join(lines) if lines else "No recent decisions"
    
    @staticmethod
    def _format_similar_situations(similar_situations: list) -> str:
        """格式化相似场景"""
        if not similar_situations:
            return "No similar situations found"
        
        lines = []
        for sit in similar_situations[:3]:  # 只显示前3个
            score = sit.get('score', 0)
            action = sit.get('action', 'Unknown')
            symbol = sit.get('symbol', 'Unknown')
            pnl = sit.get('pnl', 0)
            
            lines.append(
                f"  Similarity: {score:.2f} | {action} {symbol} → "
                f"Result: ${pnl:+.2f}"
            )
        
        return "\n".join(lines) if lines else "No similar situations"
    
    @staticmethod
    def _format_lessons(lessons: list) -> str:
        """格式化经验教训"""
        if not lessons:
            return "No lessons learned yet (you are learning...)"
        
        lines = []
        for lesson in lessons[:3]:  # 只显示前3条
            title = lesson.get('title', 'Untitled')
            impact = lesson.get('impact_score', 0)
            
            lines.append(f"  {'⭐' if impact > 0 else '⚠️ '} {title}")
        
        return "\n".join(lines) if lines else "No lessons yet"
    
    @staticmethod
    def _format_intelligence_report(intelligence_report) -> str:
        """格式化Qwen情报报告"""
        if not intelligence_report:
            return ""
        
        # 情绪emoji映射
        sentiment_emoji = {
            "BULLISH": "🟢",
            "BEARISH": "🔴",
            "NEUTRAL": "🟡"
        }
        
        sentiment = intelligence_report.market_sentiment.value
        emoji = sentiment_emoji.get(sentiment, "⚪")
        
        section = f"""
═══════════════════════════════════════════════════════════
🕵️‍♀️ QWEN INTELLIGENCE REPORT (Qwen情报官报告)
═══════════════════════════════════════════════════════════

{emoji} **市场情绪**: {sentiment} (分数: {intelligence_report.sentiment_score:+.2f})
📊 **置信度**: {intelligence_report.confidence:.0%}
⏰ **更新时间**: {intelligence_report.timestamp.strftime('%H:%M')}

"""
        
        # 关键新闻
        if intelligence_report.key_news:
            section += "📰 **关键新闻** (Top 3):\n"
            for i, news in enumerate(intelligence_report.key_news[:3], 1):
                sentiment_icon = {"bullish": "📈", "bearish": "📉", "neutral": "➡️"}.get(news.sentiment, "➡️")
                section += f"  {i}. {sentiment_icon} [{news.source}] {news.title}\n"
        
        # 巨鲸活动
        if intelligence_report.whale_signals:
            section += "\n🐋 **巨鲸活动** (Large Transactions):\n"
            for whale in intelligence_report.whale_signals[:3]:
                action_emoji = {"buy": "🟢", "sell": "🔴", "transfer": "🔄"}.get(whale.action, "⚪")
                section += f"  {action_emoji} {whale.symbol}: ${whale.amount_usd:,.0f} ({whale.action})\n"
        
        # 风险因素
        if intelligence_report.risk_factors:
            section += "\n⚠️  **风险因素**:\n"
            for risk in intelligence_report.risk_factors[:3]:
                section += f"  • {risk}\n"
        
        # 机会点
        if intelligence_report.opportunities:
            section += "\n✨ **机会点**:\n"
            for opp in intelligence_report.opportunities[:2]:
                section += f"  • {opp}\n"
        
        # Qwen的综合分析
        if intelligence_report.qwen_analysis:
            section += f"\n📝 **Qwen分析摘要**:\n{intelligence_report.qwen_analysis[:200]}...\n"
        
        section += "\n💡 **注意**: 以上情报由Qwen情报官提供，仅供参考，请结合市场数据综合判断。\n"
        
        return section

