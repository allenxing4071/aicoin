# API设计规范

**文档编号**: AICOIN-ARCH-003  
**文档版本**: v1.0.0  
**文档状态**: ✅ 已批准  
**创建日期**: 2025-10-22  
**最后更新**: 2025-10-22  
**文档所有者**: 技术负责人  
**审阅人**: 产品经理  
**密级**: 内部公开

---

## 1. RESTful API规范

### 1.1 基础URL

```
开发环境: http://localhost:8000/api/v1
生产环境: https://api.aicoin.ai/api/v1
```

### 1.2 HTTP方法

| 方法 | 用途 | 幂等性 |
|------|------|--------|
| GET | 查询资源 | 是 |
| POST | 创建资源 | 否 |
| PUT | 完整更新 | 是 |
| PATCH | 部分更新 | 否 |
| DELETE | 删除资源 | 是 |

### 1.3 统一响应格式

```json
{
  "code": 200,
  "message": "success",
  "data": {},
  "timestamp": "2025-10-22T10:00:00Z"
}
```

---

## 2. 核心API端点

### 2.1 交易相关

```
POST /api/v1/trading/decision
- 触发AI决策
- Body: { "symbol": "BTC-PERP" }
- Response: { "action": "BUY", "size": 0.05 }

GET /api/v1/trading/trades
- 查询交易记录
- Query: ?symbol=BTC-PERP&limit=20

GET /api/v1/trading/trades/{id}
- 查询单个交易详情
```

### 2.2 市场数据

```
GET /api/v1/market/kline/{symbol}
- 获取K线数据
- Query: ?interval=1h&limit=100

GET /api/v1/market/orderbook/{symbol}
- 获取订单簿
- Query: ?depth=20

GET /api/v1/market/ticker/{symbol}
- 获取实时价格
```

### 2.3 账户相关

```
GET /api/v1/account/info
- 获取账户信息

GET /api/v1/account/positions
- 获取持仓列表

GET /api/v1/account/balance
- 获取账户余额
```

### 2.4 性能指标

```
GET /api/v1/performance/metrics
- 获取性能指标
- Response: { "sharpe_ratio": 1.5, "max_drawdown": 0.08 }

GET /api/v1/performance/history
- 获取历史绩效
```

---

## 3. WebSocket协议

### 3.1 连接

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
```

### 3.2 订阅频道

```json
{
  "action": "subscribe",
  "channels": ["ticker", "trades", "account"]
}
```

### 3.3 消息格式

```json
{
  "channel": "ticker",
  "symbol": "BTC-PERP",
  "data": {
    "price": 67500.00,
    "timestamp": "2025-10-22T10:00:00Z"
  }
}
```

---

## 4. 错误码

| 错误码 | 说明 | HTTP状态码 |
|--------|------|-----------|
| 0 | 成功 | 200 |
| 1001 | 参数错误 | 400 |
| 1002 | 未授权 | 401 |
| 1003 | 资源不存在 | 404 |
| 2001 | AI决策失败 | 500 |
| 2002 | 订单执行失败 | 500 |
| 3001 | 风控拒绝 | 403 |

---

**文档结束**

