# 🔌 API接口文档

> AIcoin Trading System API Documentation  
> **Base URL**: `http://localhost:8000/api/v1`  
> **版本**: v2.1  
> **最后更新**: 2025-11-04

---

## 📚 文档目录

| 端点分类 | 说明 | 文档 |
|---------|------|------|
| 市场数据 | 价格、K线、订单簿 | [Market API](#1-市场数据-api) |
| 账户管理 | 余额、持仓 | [Account API](#2-账户管理-api) |
| 交易管理 | 交易历史、统计 | [Trading API](#3-交易管理-api) |
| AI决策 | 决策历史、聊天、状态 | [AI API](#4-ai决策-api) |
| 权限管理 | 权限等级、配置 | [Permission API](#5-权限管理-api) |
| 约束系统 | 约束状态、控制 | [Constraints API](#6-约束系统-api) |
| 情报系统 | Qwen情报、数据源 | [Intelligence API](#7-情报系统-api) |
| 性能指标 | 收益、风险指标 | [Performance API](#8-性能指标-api) |
| 管理后台 | 数据库、权限、情报、记忆 | [Admin API](#9-管理后台-api) |

---

## 🚀 快速开始

### 基础信息

```bash
# Base URL
http://localhost:8000/api/v1

# Health Check
GET /health

# API Version
v1
```

### 认证

```bash
# 当前版本：无需认证
# 计划版本：Bearer Token
Authorization: Bearer <token>
```

### 响应格式

```json
{
  "success": true,
  "data": {},
  "message": "Success"
}
```

---

## 1. 市场数据 API

### 1.1 获取多个币种价格

**端点**: `GET /market/tickers`

**描述**: 获取BTC、ETH、SOL、BNB、DOGE、XRP的实时价格

**请求**:
```bash
curl http://localhost:8000/api/v1/market/tickers
```

**响应**:
```json
[
  {
    "symbol": "BTC",
    "price": "110010.5",
    "change_24h": "0.12",
    "volume_24h": "0.00",
    "timestamp": "2025-11-02T10:32:33Z"
  },
  {
    "symbol": "ETH",
    "price": "3874.25",
    "change_24h": "0.80",
    "volume_24h": "0.00",
    "timestamp": "2025-11-02T10:32:33Z"
  }
]
```

**字段说明**:
- `symbol`: 币种符号
- `price`: 当前价格（字符串）
- `change_24h`: 24小时涨跌幅（%）
- `volume_24h`: 24小时交易量（暂未实现）
- `timestamp`: 时间戳（ISO 8601）

---

### 1.2 获取单个币种价格

**端点**: `GET /market/ticker/{symbol}`

**描述**: 获取指定币种的实时价格

**请求**:
```bash
curl http://localhost:8000/api/v1/market/ticker/BTC
```

**响应**:
```json
{
  "symbol": "BTC",
  "price": "110010.5",
  "change_24h": "0.12",
  "volume_24h": "0.00",
  "timestamp": "2025-11-02T10:32:33Z"
}
```

---

### 1.3 获取K线数据

**端点**: `GET /market/kline/{symbol}`

**描述**: 获取K线数据

**参数**:
- `interval`: K线间隔（1m, 5m, 15m, 1h, 4h, 1d）
- `limit`: 返回数量（默认100）

**请求**:
```bash
curl "http://localhost:8000/api/v1/market/kline/BTC?interval=1h&limit=100"
```

**响应**:
```json
[
  {
    "time": 1730534400,
    "open": 110000.0,
    "high": 110500.0,
    "low": 109800.0,
    "close": 110010.5,
    "volume": 1234.56
  }
]
```

---

### 1.4 获取订单簿

**端点**: `GET /market/orderbook/{symbol}`

**描述**: 获取订单簿数据

**参数**:
- `depth`: 深度（默认20）

**请求**:
```bash
curl "http://localhost:8000/api/v1/market/orderbook/BTC?depth=20"
```

**响应**:
```json
{
  "bids": [
    ["110000.0", "1.5"],
    ["109999.0", "2.3"]
  ],
  "asks": [
    ["110001.0", "1.8"],
    ["110002.0", "2.1"]
  ],
  "timestamp": "2025-11-02T10:32:33Z"
}
```

---

## 2. 账户管理 API

### 2.1 获取账户信息

**端点**: `GET /account/info`

**描述**: 获取账户余额和权益

**请求**:
```bash
curl http://localhost:8000/api/v1/account/info
```

**响应**:
```json
{
  "balance": 0.000772,
  "equity": 0.000772,
  "unrealizedPnl": 0.0,
  "marginUsed": 0.0,
  "availableMargin": 0.000772,
  "leverage": 1.0
}
```

**字段说明**:
- `balance`: 账户余额
- `equity`: 账户权益（余额 + 未实现盈亏）
- `unrealizedPnl`: 未实现盈亏
- `marginUsed`: 已用保证金
- `availableMargin`: 可用保证金
- `leverage`: 杠杆倍数

---

### 2.2 获取账户总价值

**端点**: `GET /account/value`

**描述**: 获取账户总价值、现金和未实现盈亏

**请求**:
```bash
curl http://localhost:8000/api/v1/account/value
```

**响应**:
```json
{
  "total_value": 0.000772,
  "cash": 0.000772,
  "unrealized_pnl": 0.0
}
```

---

### 2.3 获取持仓列表

**端点**: `GET /account/positions`

**描述**: 获取当前所有持仓

**请求**:
```bash
curl http://localhost:8000/api/v1/account/positions
```

**响应**:
```json
[
  {
    "symbol": "BTC-PERP",
    "side": "long",
    "size": 0.01,
    "entry_price": 110000.0,
    "mark_price": 110010.5,
    "unrealized_pnl": 0.105,
    "leverage": 1.0
  }
]
```

---

## 3. 交易管理 API

### 3.1 获取交易历史

**端点**: `GET /trading/trades`

**描述**: 获取历史交易记录

**参数**:
- `model`: 模型名称筛选（可选）
- `symbol`: 币种筛选（可选）
- `limit`: 返回数量（默认100，最大500）

**请求**:
```bash
curl "http://localhost:8000/api/v1/trading/trades?limit=10"
```

**响应**:
```json
{
  "success": true,
  "trades": [
    {
      "id": "order_123",
      "model": "deepseek-chat-v3.1",
      "side": "buy",
      "symbol": "BTC",
      "price": "110000.0",
      "size": "0.01",
      "timestamp": "2025-11-02T10:00:00Z",
      "fee": "0.55",
      "closed_pnl": "10.5"
    }
  ],
  "count": 1
}
```

**字段说明**:
- `id`: 订单ID
- `model`: AI模型名称
- `side`: 方向（buy/sell）
- `symbol`: 币种
- `price`: 成交价格
- `size`: 成交数量
- `timestamp`: 时间戳
- `fee`: 手续费
- `closed_pnl`: 已实现盈亏

---

### 3.2 获取交易统计

**端点**: `GET /trading/trades/stats`

**描述**: 获取交易统计数据

**参数**:
- `model`: 模型名称筛选（可选）
- `days`: 统计天数（默认30，最大365）

**请求**:
```bash
curl "http://localhost:8000/api/v1/trading/trades/stats?days=30"
```

**响应**:
```json
{
  "success": true,
  "stats": {
    "total_trades": 150,
    "winning_trades": 93,
    "losing_trades": 57,
    "win_rate": 62.0,
    "total_pnl": 1550.0,
    "avg_pnl_per_trade": 10.33
  }
}
```

---

### 3.3 获取当前持仓

**端点**: `GET /trading/positions`

**描述**: 获取当前所有持仓

**请求**:
```bash
curl http://localhost:8000/api/v1/trading/positions
```

**响应**:
```json
{
  "success": true,
  "positions": [
    {
      "coin": "BTC",
      "side": "long",
      "size": 0.01,
      "entry_price": 110000.0,
      "current_price": 110010.5,
      "unrealized_pnl": 0.105,
      "realized_pnl": 0.0,
      "leverage": 1.0,
      "liquidation_price": null,
      "margin_used": 1100.0
    }
  ],
  "count": 1
}
```

---

## 4. AI决策 API

### 4.1 获取AI聊天历史

**端点**: `GET /ai/chat/history`

**描述**: 获取AI决策聊天历史

**参数**:
- `model`: 模型名称筛选（可选）
- `limit`: 返回数量（默认50，最大200）

**请求**:
```bash
curl "http://localhost:8000/api/v1/ai/chat/history?limit=10"
```

**响应**:
```json
{
  "success": true,
  "messages": [
    {
      "model": "DEEPSEEK",
      "timestamp": "2025-11-02T10:00:00Z",
      "action": "— HOLD",
      "symbol": "BTC-PERP",
      "confidence": 30,
      "reasoning": "Market volatility is high, waiting for clear signal..."
    }
  ],
  "count": 1
}
```

**action类型**:
- `— HOLD`: 持有
- `↗ BUY`: 做多
- `↘ SELL`: 做空

---

### 4.2 获取AI决策历史

**端点**: `GET /ai/decisions`

**描述**: 获取AI决策历史（详细版）

**参数**:
- `model`: 模型名称筛选（可选）
- `limit`: 返回数量（默认50）

**请求**:
```bash
curl "http://localhost:8000/api/v1/ai/decisions?limit=10"
```

**响应**:
```json
{
  "decisions": [
    {
      "id": 1,
      "timestamp": "2025-11-02T10:00:00Z",
      "symbol": "BTC-PERP",
      "action": "HOLD",
      "confidence": 0.3,
      "reasoning": "Market volatility is high...",
      "executed": false,
      "reject_reason": "Confidence below threshold"
    }
  ],
  "count": 1
}
```

---

### 4.3 获取AI权限状态

**端点**: `GET /ai/permission`

**描述**: 获取当前AI权限等级

**请求**:
```bash
curl http://localhost:8000/api/v1/ai/permission
```

**响应**:
```json
{
  "level": "L2",
  "description": "Cautious Trader",
  "max_position_size": 0.15,
  "max_leverage": 2.0,
  "confidence_threshold": 0.70,
  "max_trades_per_day": 5
}
```

---

### 4.4 获取AI健康状态

**端点**: `GET /ai/health`

**描述**: 获取AI系统健康状态

**请求**:
```bash
curl http://localhost:8000/api/v1/ai/health
```

**响应**:
```json
{
  "status": "healthy",
  "orchestrator": "active",
  "decision_engine": "ready",
  "memory_system": "connected",
  "last_decision": "2025-11-02T10:00:00Z"
}
```

---

### 4.5 获取AI完整状态

**端点**: `GET /ai/status`

**描述**: 获取AI编排器完整状态（v2.1新增）

**请求**:
```bash
curl http://localhost:8000/api/v1/ai/status
```

**响应**:
```json
{
  "running": true,
  "current_level": "L3",
  "last_decision_time": "2025-11-04T10:00:00Z",
  "uptime_seconds": 3600,
  "total_decisions": 150,
  "qwen_intelligence": {
    "enabled": true,
    "last_collection": "2025-11-04T09:30:00Z",
    "market_sentiment": "BULLISH",
    "confidence": 0.75
  },
  "memory_status": {
    "short_term": "active",
    "long_term": "connected",
    "knowledge_base": "loaded"
  }
}
```

---

## 5. 权限管理 API

### 5.1 获取所有权限等级

**端点**: `GET /permissions/levels`

**描述**: 获取所有权限等级配置

**请求**:
```bash
curl http://localhost:8000/api/v1/permissions/levels
```

**响应**:
```json
[
  {
    "level": "L0",
    "name": "观察模式",
    "risk_level": "无风险",
    "is_default": false,
    "max_position_pct": 0.0,
    "max_leverage": 1.0,
    "confidence_threshold": 1.0,
    "max_daily_trades": 0,
    "stop_loss_pct": 0.0,
    "take_profit_pct": 0.0,
    "upgrade_conditions": {
      "win_rate_7d": 0.0,
      "win_rate_30d": 0.0,
      "sharpe_ratio": 0.0,
      "min_trades": 0,
      "min_days": 0
    }
  },
  {
    "level": "L3",
    "name": "稳定级",
    "risk_level": "中等",
    "is_default": true,
    "max_position_pct": 0.4,
    "max_leverage": 3.0,
    "confidence_threshold": 0.7,
    "max_daily_trades": 6,
    "stop_loss_pct": 0.03,
    "take_profit_pct": 0.06
  }
]
```

---

### 5.2 获取单个权限等级

**端点**: `GET /permissions/levels/{level}`

**描述**: 获取指定权限等级详情

**请求**:
```bash
curl http://localhost:8000/api/v1/permissions/levels/L3
```

---

### 5.3 获取升级条件

**端点**: `GET /permissions/upgrade-conditions`

**描述**: 获取权限升级条件

**请求**:
```bash
curl http://localhost:8000/api/v1/permissions/upgrade-conditions
```

**响应**:
```json
{
  "current_level": "L3",
  "next_level": "L4",
  "conditions": {
    "win_rate_7d": {"required": 0.65, "current": 0.62},
    "win_rate_30d": {"required": 0.60, "current": 0.58},
    "sharpe_ratio": {"required": 1.8, "current": 1.5},
    "min_trades": {"required": 30, "current": 25},
    "min_days": {"required": 14, "current": 10}
  },
  "can_upgrade": false
}
```

---

## 6. 约束系统 API

### 6.1 获取约束状态

**端点**: `GET /constraints/status`

**描述**: 获取约束系统状态

**请求**:
```bash
curl http://localhost:8000/api/v1/constraints/status
```

**响应**:
```json
{
  "hard_constraints": {
    "passed": true,
    "checks": [
      {
        "name": "max_position_size",
        "current": 0.50,
        "limit": 0.80,
        "passed": true
      }
    ]
  },
  "soft_constraints": {
    "warnings": 1,
    "checks": []
  }
}
```

---

### 6.2 获取违规记录

**端点**: `GET /constraints/violations`

**描述**: 获取约束违规历史

**请求**:
```bash
curl http://localhost:8000/api/v1/constraints/violations
```

**响应**:
```json
{
  "violations": [
    {
      "timestamp": "2025-11-04T10:00:00Z",
      "type": "position_size_exceeded",
      "severity": "high",
      "details": "Position size 0.85 exceeded limit 0.80"
    }
  ],
  "count": 1
}
```

---

### 6.3 获取交易控制状态

**端点**: `GET /constraints/trading-control`

**描述**: 获取交易启停状态

**请求**:
```bash
curl http://localhost:8000/api/v1/constraints/trading-control
```

**响应**:
```json
{
  "trading_enabled": true,
  "can_open_positions": true,
  "can_close_positions": true,
  "emergency_stop": false
}
```

---

### 6.4 控制交易启停

**端点**: `POST /constraints/trading-control`

**描述**: 启动或停止交易

**请求**:
```bash
curl -X POST http://localhost:8000/api/v1/constraints/trading-control \
  -H "Content-Type: application/json" \
  -d '{"action": "start", "level": "L3"}'
```

**参数**:
- `action`: "start" 或 "stop"
- `level`: 权限等级（仅在start时需要）

**响应**:
```json
{
  "success": true,
  "message": "交易已启动",
  "new_level": "L3"
}
```

---

## 7. 情报系统 API

### 7.1 获取最新情报

**端点**: `GET /intelligence/reports/latest`

**描述**: 获取最新的Qwen情报报告

**请求**:
```bash
curl http://localhost:8000/api/v1/intelligence/reports/latest
```

**响应**:
```json
{
  "success": true,
  "data": {
    "timestamp": "2025-11-04T10:00:00Z",
    "market_sentiment": "BULLISH",
    "sentiment_score": 0.65,
    "confidence": 0.80,
    "key_news": [
      {
        "title": "Bitcoin ETF approval news",
        "sentiment": "positive",
        "impact": "high"
      }
    ],
    "whale_signals": [
      {
        "type": "large_buy",
        "amount": "100 BTC",
        "impact": "bullish"
      }
    ],
    "on_chain_metrics": {
      "exchange_netflow": "-500 BTC",
      "active_addresses": "+15%"
    },
    "risk_factors": ["High volatility", "Regulatory uncertainty"],
    "opportunities": ["Momentum breakout", "Support level hold"],
    "qwen_analysis": "市场情绪积极，建议保持多头..."
  }
}
```

---

### 7.2 获取历史情报

**端点**: `GET /intelligence/reports/history`

**描述**: 获取历史情报列表

**参数**:
- `limit`: 返回数量（默认10）
- `offset`: 偏移量（默认0）
- `start_date`: 开始日期（可选）
- `end_date`: 结束日期（可选）
- `sentiment`: 情绪筛选（BULLISH/BEARISH/NEUTRAL）
- `min_confidence`: 最小置信度（0.0-1.0）

**请求**:
```bash
curl "http://localhost:8000/api/v1/intelligence/reports/history?limit=10&sentiment=BULLISH"
```

**响应**:
```json
{
  "success": true,
  "data": [...],
  "total": 100,
  "limit": 10,
  "offset": 0
}
```

---

### 7.3 获取情报分析摘要

**端点**: `GET /intelligence/analytics/summary`

**描述**: 获取情报统计摘要

**参数**:
- `days`: 统计天数（默认7）

**请求**:
```bash
curl "http://localhost:8000/api/v1/intelligence/analytics/summary?days=7"
```

**响应**:
```json
{
  "success": true,
  "data": {
    "total_reports": 48,
    "sentiment_distribution": {
      "BULLISH": 28,
      "BEARISH": 12,
      "NEUTRAL": 8
    },
    "average_confidence": 0.75,
    "data_sources_active": 12
  }
}
```

---

### 7.4 获取情绪趋势

**端点**: `GET /intelligence/analytics/sentiment-trend`

**描述**: 获取市场情绪趋势

**参数**:
- `days`: 统计天数（默认30）

**请求**:
```bash
curl "http://localhost:8000/api/v1/intelligence/analytics/sentiment-trend?days=30"
```

**响应**:
```json
{
  "success": true,
  "data": {
    "trend": [
      {
        "date": "2025-11-04",
        "sentiment": "BULLISH",
        "score": 0.65
      }
    ]
  }
}
```

---

## 8. 性能指标 API

### 5.1 获取性能指标

**端点**: `GET /performance/metrics`

**描述**: 获取系统性能指标

**请求**:
```bash
curl http://localhost:8000/api/v1/performance/metrics
```

**响应**:
```json
{
  "total_return": 0.155,
  "annual_return": 0.452,
  "sharpe_ratio": 1.85,
  "sortino_ratio": 2.31,
  "max_drawdown": 0.085,
  "win_rate": 0.62,
  "total_trades": 150,
  "avg_profit": 15.20,
  "avg_loss": -8.50,
  "profit_factor": 1.79
}
```

**字段说明**:
- `total_return`: 总收益率
- `annual_return`: 年化收益率
- `sharpe_ratio`: 夏普比率
- `sortino_ratio`: 索提诺比率
- `max_drawdown`: 最大回撤
- `win_rate`: 胜率
- `total_trades`: 总交易数
- `avg_profit`: 平均盈利
- `avg_loss`: 平均亏损
- `profit_factor`: 盈亏比

---

### 8.2 获取性能摘要

**端点**: `GET /performance/summary`

**描述**: 获取性能摘要信息

**请求**:
```bash
curl http://localhost:8000/api/v1/performance/summary
```

---

### 8.3 获取历史性能

**端点**: `GET /performance/history`

**描述**: 获取历史性能数据

**参数**:
- `days`: 统计天数（默认30）

**请求**:
```bash
curl "http://localhost:8000/api/v1/performance/history?days=30"
```

---

## 9. 管理后台 API

### 9.1 数据库管理

#### 9.1.1 获取数据库统计

**端点**: `GET /admin/database/stats`

**描述**: 获取数据库统计信息

**请求**:
```bash
curl http://localhost:8000/api/v1/admin/database/stats
```

**响应**:
```json
{
  "trades": 150,
  "orders": 300,
  "ai_decisions": 500,
  "account_snapshots": 1000,
  "risk_events": 10,
  "intelligence_reports": 48
}
```

---

#### 9.1.2 获取所有表信息

**端点**: `GET /admin/database/tables`

**描述**: 获取数据库所有表的信息

**请求**:
```bash
curl http://localhost:8000/api/v1/admin/database/tables
```

---

#### 9.1.3 获取表数据

**端点**: `GET /admin/database/tables/{table_name}/data`

**描述**: 获取指定表的数据

**参数**:
- `limit`: 返回数量（默认100）
- `offset`: 偏移量（默认0）

**请求**:
```bash
curl "http://localhost:8000/api/v1/admin/database/tables/trades/data?limit=10"
```

---

### 9.2 权限管理

#### 9.2.1 获取所有权限等级

**端点**: `GET /admin/permissions/levels`

**描述**: 获取所有权限等级配置

**请求**:
```bash
curl http://localhost:8000/api/v1/admin/permissions/levels
```

---

#### 9.2.2 更新权限等级

**端点**: `PUT /admin/permissions/levels/{level}`

**描述**: 更新指定权限等级的配置

**请求**:
```bash
curl -X PUT http://localhost:8000/api/v1/admin/permissions/levels/L3 \
  -H "Content-Type: application/json" \
  -d '{
    "max_position_pct": 0.5,
    "max_leverage": 3.0,
    "confidence_threshold": 0.75
  }'
```

---

#### 9.2.3 设置默认权限

**端点**: `POST /admin/permissions/levels/{level}/set-default`

**描述**: 设置指定等级为默认权限

**请求**:
```bash
curl -X POST http://localhost:8000/api/v1/admin/permissions/levels/L3/set-default
```

---

#### 9.2.4 初始化默认配置

**端点**: `POST /admin/permissions/levels/init-defaults`

**描述**: 初始化L0-L5的默认配置

**请求**:
```bash
curl -X POST http://localhost:8000/api/v1/admin/permissions/levels/init-defaults
```

---

### 9.3 情报系统管理

#### 9.3.1 获取情报系统状态

**端点**: `GET /admin/intelligence/status`

**描述**: 获取Qwen情报系统状态

**请求**:
```bash
curl http://localhost:8000/api/v1/admin/intelligence/status
```

**响应**:
```json
{
  "qwen_enabled": true,
  "collection_interval": 1800,
  "last_collection_time": "2025-11-04T10:00:00Z",
  "next_collection_time": "2025-11-04T10:30:00Z",
  "latest_report": {
    "market_sentiment": "BULLISH",
    "confidence": 0.75
  },
  "data_sources": {
    "news": {"total": 5, "enabled": 4},
    "whale": {"total": 5, "enabled": 3},
    "onchain": {"total": 5, "enabled": 5}
  }
}
```

---

#### 9.3.2 获取数据源配置

**端点**: `GET /admin/intelligence/config`

**描述**: 获取数据源配置

**请求**:
```bash
curl http://localhost:8000/api/v1/admin/intelligence/config
```

---

#### 9.3.3 更新数据源配置

**端点**: `POST /admin/intelligence/config`

**描述**: 更新数据源配置

**请求**:
```bash
curl -X POST http://localhost:8000/api/v1/admin/intelligence/config \
  -H "Content-Type: application/json" \
  -d '{
    "data_sources": {
      "news": {
        "CoinDesk": {
          "enabled": true,
          "api_key": "your-api-key"
        }
      }
    }
  }'
```

---

#### 9.3.4 测试数据源连接

**端点**: `POST /admin/intelligence/data-sources/{source_name}/test-connection`

**描述**: 测试指定数据源的连接

**请求**:
```bash
curl -X POST http://localhost:8000/api/v1/admin/intelligence/data-sources/CoinDesk/test-connection
```

**响应**:
```json
{
  "success": true,
  "message": "连接测试成功",
  "response_time_ms": 250
}
```

---

#### 9.3.5 启用/禁用数据源

**端点**: `POST /admin/intelligence/data-sources/{source_name}/toggle`

**描述**: 切换数据源的启用状态

**请求**:
```bash
curl -X POST http://localhost:8000/api/v1/admin/intelligence/data-sources/CoinDesk/toggle \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```

---

#### 9.3.6 触发情报收集

**端点**: `POST /admin/intelligence/test-collection`

**描述**: 手动触发一次情报收集

**请求**:
```bash
curl -X POST http://localhost:8000/api/v1/admin/intelligence/test-collection
```

---

### 9.4 记忆系统管理

#### 9.4.1 获取记忆系统概览

**端点**: `GET /admin/memory/overview`

**描述**: 获取记忆系统状态概览

**请求**:
```bash
curl http://localhost:8000/api/v1/admin/memory/overview
```

**响应**:
```json
{
  "short_term_memory": {
    "status": "active",
    "recent_decisions": 10,
    "cache_size": 50
  },
  "long_term_memory": {
    "status": "connected",
    "provider": "qwen",
    "vector_dim": 1024,
    "total_vectors": 150,
    "qdrant_status": "healthy"
  },
  "knowledge_base": {
    "status": "loaded",
    "patterns": 25,
    "lessons": 40,
    "strategies": 15
  }
}
```

---

### 9.5 旧版管理API（兼容性）

#### 9.5.1 获取系统统计

**端点**: `GET /admin/stats`

**描述**: 获取数据库统计信息（旧版）

**请求**:
```bash
curl http://localhost:8000/api/v1/admin/stats
```

---

#### 9.5.2 获取交易记录

**端点**: `GET /admin/trades`

**描述**: 获取交易记录（旧版，分页）

**参数**:
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认10）

**请求**:
```bash
curl "http://localhost:8000/api/v1/admin/trades?page=1&page_size=10"
```

---

## 10. 决策历史 API

### 10.1 获取决策列表

**端点**: `GET /decisions`

**描述**: 获取AI决策历史列表

**参数**:
- `limit`: 返回数量（默认50）
- `symbol`: 币种筛选（可选）
- `action`: 行为筛选（可选）

**请求**:
```bash
curl "http://localhost:8000/api/v1/decisions?limit=20"
```

---

### 10.2 获取决策详情

**端点**: `GET /decisions/{decision_id}`

**描述**: 获取指定决策的详细信息

**请求**:
```bash
curl http://localhost:8000/api/v1/decisions/123
```

---

### 10.3 获取决策统计

**端点**: `GET /decisions/stats/summary`

**描述**: 获取决策统计摘要

**请求**:
```bash
curl http://localhost:8000/api/v1/decisions/stats/summary
```

**响应**:
```json
{
  "total_decisions": 500,
  "executed_decisions": 150,
  "rejected_decisions": 350,
  "execution_rate": 0.30,
  "avg_confidence": 0.65,
  "by_action": {
    "HOLD": 250,
    "BUY": 125,
    "SELL": 125
  }
}
```

---

## 11. 持仓管理 API

### 11.1 获取当前持仓

**端点**: `GET /positions`

**描述**: 获取当前所有持仓

**请求**:
```bash
curl http://localhost:8000/api/v1/positions
```

**响应**:
```json
{
  "positions": [
    {
      "symbol": "BTC-PERP",
      "side": "long",
      "size": 0.01,
      "entry_price": 110000.0,
      "mark_price": 110010.5,
      "unrealized_pnl": 0.105,
      "leverage": 1.0,
      "margin_used": 1100.0
    }
  ],
  "count": 1
}
```

---

## 12. 错误处理

### 12.1 错误响应格式

```json
{
  "detail": "Error message",
  "status_code": 400
}
```

### 12.2 HTTP状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 201 | 创建成功 |
| 204 | 删除成功（无内容） |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 12.3 常见错误

| 错误信息 | 原因 | 解决方案 |
|---------|------|---------|
| `Permission level not found` | 权限等级不存在 | 检查权限等级是否正确 (L0-L5) |
| `Trading is not enabled` | 交易未启动 | 使用 `/constraints/trading-control` 启动交易 |
| `Confidence below threshold` | 置信度不足 | 降低权限等级或提高模型置信度 |
| `Intelligence service not available` | 情报服务未启用 | 检查Qwen配置和API Key |
| `Vector database not connected` | 向量数据库未连接 | 检查Qdrant服务状态 |

---

## 13. 速率限制

**当前版本**: 无速率限制

**计划版本**:
- 普通端点: 100次/分钟
- 市场数据: 300次/分钟
- 管理端点: 30次/分钟
- 情报API: 60次/分钟

---

## 14. 开发工具

### 14.1 Swagger UI

访问交互式API文档：

```bash
# Swagger UI (推荐)
http://localhost:8000/docs

# ReDoc (阅读友好)
http://localhost:8000/redoc

# OpenAPI JSON
http://localhost:8000/openapi.json
```

### 14.2 测试工具

```bash
# 使用httpie测试API
http GET localhost:8000/api/v1/market/tickers

# 使用jq格式化JSON响应
curl http://localhost:8000/api/v1/market/tickers | jq '.'

# WebSocket测试
wscat -c ws://localhost:8000/ws
```

---

## 15. API变更记录

### v2.1 (2025-11-04)

**新增**:
- ✅ 情报系统API (7个端点)
- ✅ 权限管理API (4个端点)
- ✅ 约束控制API (4个端点)
- ✅ 决策历史API (3个端点)
- ✅ 管理后台API (15+个端点)
- ✅ AI状态详情API

**增强**:
- ✅ AI决策API增加Qwen情报支持
- ✅ 性能API增加历史数据查询
- ✅ 数据库API增加表详情查询

**废弃**:
- ⚠️ `/trading/trades` → 使用 `/trades` (v3.0将移除)
- ⚠️ `/trading/positions` → 使用 `/positions` (v3.0将移除)

### v2.0 (2025-11-03)

**新增**:
- AI编排器v2.0
- 权限系统基础API
- 约束系统API
- 管理后台基础API

---

## 16. 最佳实践

### 16.1 API调用建议

1. **轮询频率**: 
   - 市场数据: 最快1秒/次
   - AI决策: 10秒/次
   - 情报数据: 30秒/次
   - 性能指标: 60秒/次

2. **错误处理**:
   ```python
   try:
       response = requests.get(f"{API_BASE}/market/tickers")
       response.raise_for_status()
       data = response.json()
   except requests.exceptions.RequestException as e:
       logger.error(f"API call failed: {e}")
   ```

3. **超时设置**:
   ```python
   requests.get(url, timeout=10)  # 10秒超时
   ```

### 16.2 性能优化

1. **批量查询**: 优先使用批量端点 (`/market/tickers` 而非多次调用 `/market/ticker/{symbol}`)
2. **缓存**: 合理缓存市场数据和性能指标
3. **WebSocket**: 对于实时数据，使用WebSocket而非轮询

---

## 17. 常见问题

### Q1: 为什么没有认证？
A: v2.1为开发版本，v3.0将添加JWT认证。

### Q2: 如何获取历史K线数据？
A: 使用 `/market/kline/{symbol}?interval=1h&limit=1000`

### Q3: 情报系统多久更新一次？
A: 默认30分钟，可在管理后台配置。

### Q4: 如何重置权限配置？
A: 调用 `/admin/permissions/levels/init-defaults`

### Q5: 长期记忆使用哪个embedding服务？
A: 自动选择：Qwen > DeepSeek > OpenAI，可在环境变量中配置。

---

**文档版本**: v2.1  
**最后更新**: 2025-11-04  
**维护状态**: ✅ Active  
**维护者**: AIcoin Team

---

## 📞 技术支持

- **GitHub Issues**: [报告问题](https://github.com/your-repo/issues)
- **文档反馈**: 提交Pull Request
- **API状态**: http://localhost:8000/health

