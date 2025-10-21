# Hyperliquid集成

**文档编号**: AICOIN-API-003  
**文档版本**: v1.0.0  
**创建日期**: 2025-10-22

---

## 1. SDK安装

```bash
pip install hyperliquid-python-sdk
```

---

## 2. 初始化客户端

```python
from hyperliquid.exchange import Exchange
from hyperliquid.utils import constants

# Testnet
exchange = Exchange(
    wallet_address="0x...",
    private_key="0x...",
    base_url=constants.TESTNET_API_URL
)

# Mainnet
exchange = Exchange(
    wallet_address="0x...",
    private_key="0x...",
    base_url=constants.MAINNET_API_URL
)
```

---

## 3. 市场数据

### 3.1 获取K线
```python
klines = exchange.get_candles(
    symbol="BTC-PERP",
    interval="1h",
    limit=100
)
```

### 3.2 获取订单簿
```python
orderbook = exchange.get_order_book(symbol="BTC-PERP", depth=20)
```

---

## 4. 交易操作

### 4.1 下市价单
```python
order = exchange.market_order(
    symbol="BTC-PERP",
    side="BUY",
    size=0.05
)
```

### 4.2 下限价单
```python
order = exchange.limit_order(
    symbol="BTC-PERP",
    side="BUY",
    price=67500.00,
    size=0.05
)
```

### 4.3 撤销订单
```python
exchange.cancel_order(order_id="...")
```

---

## 5. 账户查询

```python
# 获取账户余额
balance = exchange.get_balance()

# 获取持仓
positions = exchange.get_positions()

# 获取订单历史
orders = exchange.get_order_history(limit=20)
```

---

## 6. WebSocket实时流

```python
from hyperliquid.websocket import WebSocket

ws = WebSocket()

# 订阅实时成交
ws.subscribe_trades("BTC-PERP", callback=on_trade)

# 订阅订单簿更新
ws.subscribe_order_book("BTC-PERP", callback=on_orderbook)
```

---

## 7. 错误处理

```python
from hyperliquid.exceptions import HyperliquidException

try:
    order = exchange.market_order(...)
except HyperliquidException as e:
    logger.error(f"Order failed: {e}")
    # 重试或告警
```

---

**官方文档**: https://hyperliquid.xyz/docs

**文档结束**

