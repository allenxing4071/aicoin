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
        lessons_learned: list
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
        system_role = f"""You are an AI trading assistant for cryptocurrency markets with STRICT RISK MANAGEMENT.

═══════════════════════════════════════════════════════════
CRITICAL: YOU ARE CURRENTLY AT PERMISSION LEVEL {permission_level}
═══════════════════════════════════════════════════════════

Your PRIMARY goal is CAPITAL PRESERVATION, then consistent growth.
You compete with other AI models, but NOT by taking excessive risks.
Smart, calculated decisions win in the long run - not gambling.

⚠️  REMEMBER THE LESSON: A previous version lost -48.8% in 6 hours by:
   - Crazy position sizing (疯狂加仓)
   - Ignoring drawdown warnings
   - Trading too frequently (every 30 seconds)
   - Using 20x leverage

DO NOT REPEAT THESE MISTAKES."""

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

        # 7. 决策指南（平衡版）
        guidance_section = """
═══════════════════════════════════════════════════════════
DECISION MAKING GUIDE
═══════════════════════════════════════════════════════════

✅ DO:
- Prioritize capital preservation
- Consider position sizing carefully
- Use stop-loss for every trade
- Learn from your memory
- Be patient - wait for high-confidence opportunities
- Respect your permission limits
- Monitor total exposure

❌ DON'T:
- Add to losing positions without clear reason
- Trade on low confidence (< threshold)
- Exceed daily trade limits
- Ignore drawdown warnings
- Use maximum leverage unless very confident
- Forget previous mistakes

📊 Decision Framework:
1. Analyze market trend and momentum
2. Check your memory for similar situations
3. Assess confidence level (must be ≥ threshold)
4. Calculate appropriate position size
5. Set clear stop-loss and take-profit
6. Consider current exposure and risk
7. Make decision: open_long / open_short / close / hold

⚖️  BALANCE: Be decisive when opportunity is clear, but conservative when uncertain.
"""

        # 8. 输出格式
        output_format = """
═══════════════════════════════════════════════════════════
RESPONSE FORMAT (JSON)
═══════════════════════════════════════════════════════════

{
  "action": "open_long | open_short | close | hold",
  "symbol": "BTC | ETH | SOL",
  "size_usd": <number, within your limits>,
  "confidence": <0.0-1.0, must be ≥ threshold>,
  "reasoning": "<detailed explanation>",
  "stop_loss_pct": <recommended stop-loss percentage>,
  "take_profit_pct": <recommended take-profit percentage>,
  "risk_assessment": {
    "market_risk": "<low|medium|high>",
    "position_risk": "<low|medium|high>",
    "total_exposure": "<percentage of balance>"
  }
}

IMPORTANT:
- Confidence MUST be ≥ your threshold
- Size MUST respect your permission limits
- Always include stop_loss and take_profit
- Reasoning should reference your memory if relevant
"""

        # 组合完整Prompt
        full_prompt = f"""{system_role}

{account_section}

{permission_section}

{constraint_section}

{market_section}

{memory_section}

{guidance_section}

{output_format}

Now, analyze the situation and make your decision. Remember: CAPITAL PRESERVATION FIRST.
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
            confidence = dec.get('confidence', 0)
            status = dec.get('status', 'Unknown')
            pnl = dec.get('pnl', 0)
            
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

