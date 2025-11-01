# 前端硬编码清单 - 需连接真实API

**生成时间**: 2025-10-31  
**状态**: ⚠️ 大量组件使用模拟数据

---

## 📋 需要替换为真实API的组件

### 1. ✅ **已实现真实API的组件**

| 组件 | 文件路径 | API端点 | 状态 |
|------|---------|---------|------|
| AIStatusPanel | `components/ai/AIStatusPanel.tsx` | `/api/v1/constraints/status` | ✅ 已连接 |
| PermissionIndicator | `components/ai/PermissionIndicator.tsx` | `/api/v1/ai/permission` | ✅ 已连接 |
| DecisionTimeline | `components/ai/DecisionTimeline.tsx` | `/api/v1/ai/decisions` | ✅ 已连接 |
| PerformanceDashboard | `components/performance/PerformanceDashboard.tsx` | `/api/v1/performance/metrics` | ✅ 已连接 |

---

### 2. ❌ **仍使用硬编码数据的组件**

#### 🔴 **P0 - 核心功能（必须优先实现）**

| 组件 | 文件路径 | 问题描述 | 需要的API |
|------|---------|---------|-----------|
| **PriceTicker** | `components/ticker/PriceTicker.tsx` | 🔴 **硬编码价格数据** | `/api/v1/market/tickers` |
| | | - BTC: $95,000.00 (+2.50%) | 需要实时WebSocket |
| | | - ETH: $3,500.00 (+1.80%) | |
| | | - SOL, BNB, DOGE, XRP等 | |
| **AIDecisionChat** | `components/chat/AIDecisionChat.tsx` | 🔴 **硬编码聊天记录** | `/api/v1/ai/chat/history` |
| | | - GPT 5: "HOLD ETH-PERP..." | |
| | | - GROK 4: "HOLD SOL-PERP..." | |
| | | - 所有消息都是假数据 | |
| **TradeListComplete** | `components/trades/TradeListComplete.tsx` | 🔴 **空交易列表**（猜测） | `/api/v1/trades/history` |
| | | - 需要显示历史交易 | 参数: model, limit |
| **PositionsList** | `components/positions/PositionsList.tsx` | 🔴 **空持仓列表**（猜测） | `/api/v1/positions/current` |
| | | - 需要显示当前持仓 | 参数: model |

#### 🟠 **P1 - 重要图表（影响用户体验）**

| 组件 | 文件路径 | 问题描述 | 需要的API |
|------|---------|---------|-----------|
| **MultiModelChart** | `components/charts/MultiModelChart.tsx` | 🟠 **使用模拟曲线数据** | `/api/v1/account/equity_curve` |
| | | - 账户价值曲线 | 参数: models, period |
| | | - 已注释掉原API调用 | |
| **LightweightChart** | `components/charts/LightweightChart.tsx` | 🟠 **使用模拟K线数据** | `/api/v1/market/klines` |
| | | - 生成100根假K线 | 参数: symbol, interval |
| | | - `generateMockCandlestickData()` | |
| **EquityCurveMulti** | `components/charts/EquityCurveMulti.tsx` | 🟠 **使用模拟权益曲线** | `/api/v1/models/equity_curves` |
| | | - 多模型对比曲线 | |

#### 🟡 **P2 - 细节优化（可后续实现）**

| 组件 | 文件路径 | 问题描述 | 需要的API |
|------|---------|---------|-----------|
| **page.tsx (主页)** | `app/page.tsx` | 🟡 **部分硬编码** | 多个API |
| | | - `totalValue = 100` | `/api/v1/account/value` |
| | | - 模型列表硬编码 | `/api/v1/models/list` |
| | | - AI健康状态部分模拟 | 已有 `/health` |

---

## 🛠️ 需要实现的后端API清单

### 📊 **市场数据API**

```typescript
// 1. 实时价格行情
GET /api/v1/market/tickers
Response: {
  tickers: [
    { symbol: "BTC-PERP", price: 95234.50, change_24h: 2.34, volume_24h: 1234567890 },
    ...
  ]
}

// 2. K线数据
GET /api/v1/market/klines?symbol=BTC-PERP&interval=1h&limit=100
Response: {
  klines: [
    { time: 1730000000, open: 95000, high: 95500, low: 94500, close: 95234, volume: 12345 },
    ...
  ]
}
```

### 💬 **AI对话API**

```typescript
// 3. AI决策聊天历史
GET /api/v1/ai/chat/history?model=all&limit=50
Response: {
  messages: [
    {
      id: "msg_123",
      model: "deepseek-chat-v3.1",
      timestamp: "2025-10-31T10:30:00Z",
      action: "HOLD" | "BUY" | "SELL",
      symbol: "ETH-PERP",
      confidence: 85,
      reasoning: "市场处于盘整阶段，等待突破信号..."
    },
    ...
  ]
}
```

### 📈 **交易历史API**

```typescript
// 4. 交易历史
GET /api/v1/trades/history?model=all&limit=100
Response: {
  trades: [
    {
      id: "trade_456",
      model: "deepseek-chat-v3.1",
      timestamp: "2025-10-31T10:25:00Z",
      side: "BUY" | "SELL",
      symbol: "BTC-PERP",
      size: 0.1,
      price: 95234.50,
      pnl: 123.45,
      pnl_percent: 2.34
    },
    ...
  ]
}
```

### 📌 **持仓API**

```typescript
// 5. 当前持仓
GET /api/v1/positions/current?model=all
Response: {
  positions: [
    {
      symbol: "ETH-PERP",
      side: "LONG" | "SHORT",
      size: 1.5,
      entry_price: 3450.00,
      current_price: 3500.00,
      unrealized_pnl: 75.00,
      leverage: 2.0
    },
    ...
  ]
}
```

### 💰 **账户数据API**

```typescript
// 6. 账户价值
GET /api/v1/account/value
Response: {
  total_value: 300.50,
  cash: 150.25,
  unrealized_pnl: 50.25
}

// 7. 账户权益曲线
GET /api/v1/account/equity_curve?period_days=30
Response: {
  equity_curve: [
    { timestamp: "2025-10-01T00:00:00Z", value: 300.00 },
    { timestamp: "2025-10-02T00:00:00Z", value: 305.50 },
    ...
  ]
}

// 8. 模型列表
GET /api/v1/models/list
Response: {
  models: [
    {
      slug: "deepseek-chat-v3.1",
      name: "DEEPSEEK CHAT V3.1",
      icon: "🧠",
      status: "running" | "stopped",
      value: 100.50,
      pnl_percent: 0.50
    },
    ...
  ]
}

// 9. 多模型权益曲线
GET /api/v1/models/equity_curves?period_days=30
Response: {
  curves: {
    "deepseek-chat-v3.1": [
      { timestamp: "2025-10-01T00:00:00Z", value: 100.00 },
      ...
    ],
    ...
  }
}
```

---

## 🔥 **WebSocket实时数据（推荐）**

```typescript
// 实时价格推送
ws://localhost:8000/ws/market/tickers
Message: {
  type: "ticker_update",
  data: {
    symbol: "BTC-PERP",
    price: 95234.50,
    change_24h: 2.34
  }
}

// 实时交易推送
ws://localhost:8000/ws/trades
Message: {
  type: "trade_executed",
  data: { ... }
}

// 实时AI决策推送
ws://localhost:8000/ws/ai/decisions
Message: {
  type: "decision_made",
  data: { ... }
}
```

---

## 📝 优先级建议

### 🔴 **第一阶段（核心功能 - 1周）**
1. ✅ 实现市场数据API (`/api/v1/market/tickers`, `/api/v1/market/klines`)
2. ✅ 实现交易历史API (`/api/v1/trades/history`)
3. ✅ 实现持仓API (`/api/v1/positions/current`)
4. ✅ 实现账户价值API (`/api/v1/account/value`)

### 🟠 **第二阶段（增强体验 - 3天）**
5. ✅ 实现AI聊天历史API (`/api/v1/ai/chat/history`)
6. ✅ 实现权益曲线API (`/api/v1/account/equity_curve`)
7. ✅ 实现模型列表API (`/api/v1/models/list`)

### 🟡 **第三阶段（实时功能 - 3天）**
8. ✅ 实现WebSocket实时价格推送
9. ✅ 实现WebSocket实时交易推送
10. ✅ 实现WebSocket实时AI决策推送

---

## ✅ 完成标准

| 组件 | 完成标准 |
|------|---------|
| PriceTicker | 显示真实市场价格，每秒更新 |
| AIDecisionChat | 显示真实AI决策记录，按时间倒序 |
| TradeListComplete | 显示真实交易历史，支持分页 |
| PositionsList | 显示真实持仓，实时更新PnL |
| MultiModelChart | 显示真实账户权益曲线 |
| LightweightChart | 显示真实K线数据 |
| page.tsx | 所有数据来自API，无硬编码 |

---

## 🎯 最终目标

**100% 数据真实化，0 硬编码**

- [x] AI状态监控 ✅
- [x] 权限指示器 ✅
- [x] 决策历史 ✅
- [x] 性能仪表盘 ✅
- [ ] 价格行情 ❌
- [ ] AI对话 ❌
- [ ] 交易列表 ❌
- [ ] 持仓列表 ❌
- [ ] 权益曲线 ❌
- [ ] K线图 ❌

**当前完成度: 40% (4/10)**

---

© 2025 AIcoin Trading System | 硬编码清单

