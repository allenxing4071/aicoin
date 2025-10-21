# 后端API参考

**文档编号**: AICOIN-API-001  
**文档版本**: v1.0.0  
**创建日期**: 2025-10-22

---

## 1. 基础信息

- **Base URL**: `http://localhost:8000/api/v1`
- **认证方式**: JWT Bearer Token
- **数据格式**: JSON

---

## 2. 交易相关API

### 2.1 触发AI决策
```http
POST /trading/decision
Content-Type: application/json

{
  "symbol": "BTC-PERP"
}

Response:
{
  "code": 200,
  "data": {
    "action": "BUY",
    "size": 0.05,
    "confidence": 0.85,
    "reasoning": "市场出现上涨信号"
  }
}
```

### 2.2 获取交易记录
```http
GET /trading/trades?symbol=BTC-PERP&limit=20

Response:
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "symbol": "BTC-PERP",
      "side": "BUY",
      "price": 67500.00,
      "size": 0.05,
      "pnl": 125.50,
      "timestamp": "2025-10-22T10:00:00Z"
    }
  ]
}
```

---

## 3. 市场数据API

### 3.1 获取K线
```http
GET /market/kline/BTC-PERP?interval=1h&limit=100

Response:
{
  "code": 200,
  "data": [
    {
      "open_time": "2025-10-22T10:00:00Z",
      "open": 67000.00,
      "high": 67800.00,
      "low": 66500.00,
      "close": 67500.00,
      "volume": 1250.50
    }
  ]
}
```

### 3.2 获取订单簿
```http
GET /market/orderbook/BTC-PERP?depth=20

Response:
{
  "code": 200,
  "data": {
    "bids": [[67490.00, 10.5], [67480.00, 5.2]],
    "asks": [[67510.00, 8.3], [67520.00, 12.1]]
  }
}
```

---

## 4. 账户API

### 4.1 获取账户信息
```http
GET /account/info

Response:
{
  "code": 200,
  "data": {
    "balance": 10000.00,
    "equity": 10125.50,
    "unrealized_pnl": 125.50
  }
}
```

### 4.2 获取持仓
```http
GET /account/positions

Response:
{
  "code": 200,
  "data": [
    {
      "symbol": "BTC-PERP",
      "size": 0.5,
      "entry_price": 67000.00,
      "unrealized_pnl": 250.00
    }
  ]
}
```

---

## 5. 性能指标API

### 5.1 获取性能指标
```http
GET /performance/metrics

Response:
{
  "code": 200,
  "data": {
    "total_return": 0.125,
    "sharpe_ratio": 1.8,
    "max_drawdown": 0.08,
    "win_rate": 0.72,
    "total_trades": 18
  }
}
```

---

## 6. 错误码

| 错误码 | 说明 |
|--------|------|
| 1001 | 参数错误 |
| 1002 | 未授权 |
| 2001 | AI决策失败 |
| 2002 | 订单执行失败 |
| 3001 | 风控拒绝 |

---

**完整API文档**: http://localhost:8000/docs

**文档结束**

