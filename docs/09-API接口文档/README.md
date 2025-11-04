# 🔌 API接口文档

> AIcoin Trading System API Documentation  
> **Base URL**: `http://localhost:8000/api/v1`  
> **最后更新**: 2025-11-02

---

## 📚 文档目录

| 端点分类 | 说明 | 文档 |
|---------|------|------|
| 市场数据 | 价格、K线、订单簿 | [Market API](#1-市场数据-api) |
| 账户管理 | 余额、持仓 | [Account API](#2-账户管理-api) |
| 交易管理 | 交易历史、持仓 | [Trading API](#3-交易管理-api) |
| AI决策 | 决策历史、聊天 | [AI API](#4-ai决策-api) |
| 性能指标 | 收益、风险指标 | [Performance API](#5-性能指标-api) |
| 系统状态 | 健康检查、状态 | [System API](#6-系统状态-api) |
| 管理后台 | 数据库查看 | [Admin API](#7-管理后台-api) |

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

## 5. 性能指标 API

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

### 5.2 获取约束状态

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
      },
      {
        "name": "max_single_trade",
        "current": 0.10,
        "limit": 0.20,
        "passed": true
      },
      {
        "name": "daily_loss_limit",
        "current": 0.00,
        "limit": 0.05,
        "passed": true
      }
    ]
  },
  "soft_constraints": {
    "warnings": 1,
    "checks": [
      {
        "name": "trade_frequency",
        "status": "normal"
      },
      {
        "name": "confidence_threshold",
        "status": "warning"
      }
    ]
  }
}
```

---

## 6. 系统状态 API

### 6.1 健康检查

**端点**: `GET /health`

**描述**: 系统健康检查

**请求**:
```bash
curl http://localhost:8000/health
```

**响应**:
```json
{
  "status": "healthy",
  "timestamp": "2025-11-02T10:00:00Z",
  "version": "2.0.0"
}
```

---

### 6.2 获取系统状态

**端点**: `GET /status`

**描述**: 获取系统运行状态

**请求**:
```bash
curl http://localhost:8000/api/v1/status
```

**响应**:
```json
{
  "orchestrator_status": "active",
  "trade_count": 0,
  "last_decision": "2025-11-02T10:00:00Z",
  "uptime": 3600
}
```

---

## 7. 管理后台 API

### 7.1 获取系统统计

**端点**: `GET /admin/stats`

**描述**: 获取数据库统计信息

**请求**:
```bash
curl http://localhost:8000/api/v1/admin/stats
```

**响应**:
```json
{
  "success": true,
  "data": {
    "trades_count": 150,
    "orders_count": 300,
    "ai_decisions_count": 500,
    "risk_events_count": 10
  }
}
```

---

### 7.2 获取交易记录

**端点**: `GET /admin/trades`

**描述**: 获取数据库中的交易记录（分页）

**参数**:
- `page`: 页码（默认1）
- `page_size`: 每页数量（默认10）
- `symbol`: 币种筛选（可选）
- `side`: 方向筛选（可选）

**请求**:
```bash
curl "http://localhost:8000/api/v1/admin/trades?page=1&page_size=10"
```

**响应**:
```json
{
  "success": true,
  "data": [...],
  "meta": {
    "total": 150,
    "page": 1,
    "page_size": 10,
    "total_pages": 15
  }
}
```

---

## 8. 错误处理

### 8.1 错误响应格式

```json
{
  "detail": "Error message",
  "status_code": 400
}
```

### 8.2 HTTP状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 9. 速率限制

**当前版本**: 无速率限制

**计划版本**:
- 普通端点: 100次/分钟
- 市场数据: 300次/分钟
- 管理端点: 30次/分钟

---

## 10. 开发工具

### 10.1 Postman Collection

```bash
# 导入Postman Collection
# 文件位置: docs/09-API接口文档/postman_collection.json
```

### 10.2 Swagger UI

```bash
# 访问Swagger文档
http://localhost:8000/docs

# 访问ReDoc
http://localhost:8000/redoc
```

---

**文档版本**: v1.0  
**最后更新**: 2025-11-02  
**维护状态**: ✅ Active

