# Prompt工程实践

**文档编号**: AICOIN-RESEARCH-004  
**文档版本**: v1.0.0  
**创建日期**: 2025-10-22

---

## 1. 核心Prompt模板

### 1.1 完整Prompt

```python
TRADING_PROMPT_TEMPLATE = """
你是一位专业的加密货币量化交易AI,目标是最大化风险调整后收益(夏普比率)。

=== 当前市场数据 ===
交易对: {symbol}
当前价格: ${current_price}
24小时涨跌: {price_change_24h}%

最近24根1小时K线摘要:
- 最高价: ${high_24h}
- 最低价: ${low_24h}
- 平均价: ${avg_price_24h}
- 总成交量: {volume_24h} {symbol}
- 趋势: {trend} (上涨/下跌/震荡)

订单簿分析:
- 前20档买单总量: {bid_depth} {symbol} ({bid_depth_usd} USD)
- 前20档卖单总量: {ask_depth} {symbol} ({ask_depth_usd} USD)
- 买卖压力比: {pressure_ratio} (>1.5看涨, <0.67看跌)
- 买卖价差: {spread}% 

技术指标:
- MA5: ${ma5}, MA20: ${ma20}, MA60: ${ma60}
- MACD: {macd_value} ({macd_signal})
- RSI: {rsi} (>70超买, <30超卖)

=== 账户状态 ===
可用余额: ${available_balance} USDC
当前持仓: {position_size} {symbol} @ ${entry_price} (成本价)
未实现盈亏: ${unrealized_pnl} ({unrealized_pnl_pct}%)
今日已实现盈亏: ${realized_pnl_today} ({realized_pnl_today_pct}%)
今日交易次数: {trades_today}

=== 交易规则 (严格遵守) ===
1. **低频策略**: 优先HOLD,只在高确定性机会时交易(参考DeepSeek: 18笔/月)
2. **仓位控制**: 单笔交易 ≤ 20%总资金 (可用余额 * 0.20 = ${max_order_size})
3. **止损严格**: 每笔交易亏损 ≤ 3% 立即离场
4. **趋势优先**: 关注明确趋势,避免震荡市频繁交易
5. **风控第一**: 达到单日亏损5%时,必须HOLD

=== 决策指南 ===
**BUY信号** (至少满足3条):
□ MA5 > MA20 (短期均线上穿长期)
□ MACD金叉 (DIF上穿DEA)
□ RSI > 50 且未超买(<70)
□ 订单簿买压强 (压力比 > 1.5)
□ 价格突破关键阻力位
□ 成交量放大

**SELL信号** (至少满足3条):
□ MA5 < MA20 (死叉)
□ MACD死叉
□ RSI < 50 或超买(>70)
□ 订单簿卖压强 (压力比 < 0.67)
□ 价格跌破关键支撑位
□ 持仓盈利 >5% (止盈)

**HOLD条件**:
□ 信号不明确
□ 震荡行情
□ 单日亏损接近5%
□ 今日已交易≥2次

=== 输出格式 (严格JSON) ===
请深度分析市场后,返回以下JSON格式决策:

{{
    "action": "BUY" | "SELL" | "HOLD",
    "size": 交易数量(如果HOLD则为0),
    "confidence": 0.0-1.0的信心水平,
    "reasoning": "决策理由(简明扼要,50字内)"
}}

示例:
{{
    "action": "BUY",
    "size": 0.05,
    "confidence": 0.85,
    "reasoning": "MA5上穿MA20,MACD金叉,订单簿买压1.8倍,明确上涨趋势"
}}

现在请分析并决策:
"""
```

---

## 2. Prompt优化技巧

### 2.1 结构化数据

**优化前**:
```
价格:67500,MA5:67200,MA20:66800,MACD:250,RSI:62
```

**优化后**:
```
技术指标:
- MA5: $67,200 (✓ > MA20)
- MA20: $66,800
- MACD: 250 (金叉)
- RSI: 62 (中性,未超买)
```

### 2.2 明确约束

**关键约束前置**:
```
=== 交易规则 (严格遵守) ===
1. 仓位控制: ≤ 20%
2. 止损: ≤ -3%
3. 单日亏损限制: ≤ -5%
```

---

## 3. 常见问题修复

### 3.1 输出格式不稳定

**问题**: LLM有时返回markdown而非JSON

**解决**:
```python
def parse_llm_output(text: str):
    # 1. 尝试直接解析
    try:
        return json.loads(text)
    except:
        pass
    
    # 2. 提取JSON代码块
    import re
    match = re.search(r'```json\n(.*?)\n```', text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    
    # 3. 重新请求
    raise ValueError("Invalid JSON format")
```

### 3.2 决策过于激进

**问题**: LLM频繁交易

**解决**:
在Prompt中强调:
```
低频策略: 参考DeepSeek成功经验,月交易18笔,日均<1笔
优先HOLD,只在极高确定性时交易
```

---

## 4. A/B测试

### 4.1 测试维度

| 变量 | 版本A | 版本B | 胜者 |
|------|-------|-------|------|
| 温度参数 | 0.7 | 0.3 | ? |
| 决策信号 | 3/6 | 4/6 | ? |
| Prompt长度 | 1500 tokens | 800 tokens | ? |

### 4.2 评估指标

- 夏普比率
- 交易次数
- 胜率
- 最大回撤

---

**文档结束**

