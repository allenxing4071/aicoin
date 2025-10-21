"""Prompt templates for AI trading decisions"""

from typing import Dict, Any
from decimal import Decimal


TRADING_SYSTEM_PROMPT = """你是一个专业的加密货币交易AI助手,目标是通过低频高胜率策略最大化夏普比率。

你的核心策略参考:
- DeepSeek在nof1.ai竞赛中的表现: 18笔交易，40%+收益率，胜率>70%
- 低频交易: 避免频繁交易，只在高确定性机会时出手
- 风险控制: 严格遵守仓位和止损规则

你必须返回JSON格式的决策，格式如下:
{
    "action": "BUY" | "SELL" | "HOLD",
    "size": 交易数量（Decimal，0表示HOLD）,
    "confidence": 0到1之间的信心水平（Decimal）,
    "reasoning": "简明决策理由（不超过200字）"
}
"""


def build_trading_prompt(
    symbol: str,
    current_price: Decimal,
    kline_data: list,
    orderbook: Dict[str, Any],
    account_balance: Decimal,
    position_info: Dict[str, Any]
) -> str:
    """构建交易决策Prompt"""
    
    # 简化K线数据
    if kline_data and len(kline_data) > 0:
        recent_klines = kline_data[-10:]  # 最近10根K线
        kline_summary = "\n".join([
            f"  时间: {k.get('open_time', 'N/A')}, "
            f"开: {k.get('open', 0)}, "
            f"高: {k.get('high', 0)}, "
            f"低: {k.get('low', 0)}, "
            f"收: {k.get('close', 0)}, "
            f"量: {k.get('volume', 0)}"
            for k in recent_klines
        ])
    else:
        kline_summary = "无K线数据"
    
    # 订单簿压力分析
    if orderbook and 'bids' in orderbook and 'asks' in orderbook:
        bid_volume = sum(float(b.get('size', 0)) for b in orderbook['bids'][:10])
        ask_volume = sum(float(a.get('size', 0)) for a in orderbook['asks'][:10])
        total_volume = bid_volume + ask_volume
        
        if total_volume > 0:
            bid_strength = (bid_volume / total_volume) * 100
            ask_strength = (ask_volume / total_volume) * 100
        else:
            bid_strength = 50
            ask_strength = 50
    else:
        bid_strength = 50
        ask_strength = 50
    
    # 持仓信息
    if position_info and position_info.get('size', 0) != 0:
        position_text = f"""
当前持仓:
- 持仓量: {position_info.get('size', 0)} {symbol}
- 开仓价: ${position_info.get('entry_price', 0)}
- 未实现盈亏: ${position_info.get('unrealized_pnl', 0)} ({position_info.get('unrealized_pnl_pct', 0)}%)
"""
    else:
        position_text = "当前无持仓"
    
    # 构建完整Prompt
    prompt = f"""
当前市场数据:
交易对: {symbol}
当前价格: ${current_price}

最近10根K线数据:
{kline_summary}

订单簿压力分析 (前10档):
- 买盘压力: {bid_strength:.1f}%
- 卖盘压力: {ask_strength:.1f}%

账户状态:
- 可用余额: ${account_balance} USDC
{position_text}

交易规则与风控:
1. 单笔仓位 ≤ 20%总资金 (最大 ${account_balance * Decimal('0.2')} USDC)
2. 单日最大亏损 ≤ 5%
3. 最大回撤限制 ≤ 10%
4. 优先低频高胜率策略
5. 避免频繁交易，只在高确定性机会时交易

请分析当前市场状况，做出交易决策。
如果没有明确的交易机会或市场不确定，请选择HOLD。
只在有高确定性(confidence > 0.7)时才建议交易。

返回JSON格式决策(不要有其他文字):
"""
    
    return prompt


def build_simple_prompt(symbol: str, current_price: Decimal) -> str:
    """构建简化版Prompt (用于测试)"""
    return f"""
针对 {symbol} 当前价格 ${current_price}，请做出交易决策。

返回JSON格式:
{{
    "action": "BUY" | "SELL" | "HOLD",
    "size": 0.01,
    "confidence": 0.5,
    "reasoning": "测试决策"
}}
"""

