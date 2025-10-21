# WebSocket协议

**文档编号**: AICOIN-API-002  
**文档版本**: v1.0.0  
**创建日期**: 2025-10-22

---

## 1. 连接

```javascript
const ws = new WebSocket('ws://localhost:8000/ws');
```

---

## 2. 订阅频道

```json
{
  "action": "subscribe",
  "channels": ["ticker", "trades", "account", "ai_decision"]
}
```

---

## 3. 数据格式

### 3.1 实时价格 (ticker)
```json
{
  "channel": "ticker",
  "symbol": "BTC-PERP",
  "data": {
    "price": 67500.00,
    "change_24h": 0.025,
    "timestamp": "2025-10-22T10:00:00Z"
  }
}
```

### 3.2 交易推送 (trades)
```json
{
  "channel": "trades",
  "data": {
    "id": 123,
    "symbol": "BTC-PERP",
    "side": "BUY",
    "price": 67500.00,
    "size": 0.05,
    "pnl": 125.50,
    "timestamp": "2025-10-22T10:00:00Z"
  }
}
```

### 3.3 账户更新 (account)
```json
{
  "channel": "account",
  "data": {
    "balance": 10125.50,
    "unrealized_pnl": 125.50,
    "timestamp": "2025-10-22T10:00:00Z"
  }
}
```

### 3.4 AI决策 (ai_decision)
```json
{
  "channel": "ai_decision",
  "data": {
    "symbol": "BTC-PERP",
    "action": "BUY",
    "size": 0.05,
    "confidence": 0.85,
    "reasoning": "市场出现上涨信号",
    "executed": true,
    "timestamp": "2025-10-22T10:00:00Z"
  }
}
```

---

## 4. 心跳机制

```json
// 客户端发送 (每30秒)
{"action": "ping"}

// 服务端响应
{"action": "pong", "timestamp": "2025-10-22T10:00:00Z"}
```

---

## 5. 断线重连

```javascript
function connectWebSocket() {
  const ws = new WebSocket('ws://localhost:8000/ws');
  
  ws.onclose = () => {
    console.log('Connection closed, reconnecting in 3s...');
    setTimeout(connectWebSocket, 3000);
  };
  
  return ws;
}
```

---

**文档结束**

