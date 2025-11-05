# 市场数据 API (扩展)

> **版本**: v3.1  
> **Base URL**: `/api/v1/market`  
> **新增功能**: 多时间周期分析、现货合约对比

## 新增端点

| 方法 | 路径 | 描述 | 版本 |
|------|------|------|------|
| GET | `/klines/multi` | 获取多时间周期K线数据 | v3.1 ✨ |
| GET | `/spot-futures-compare` | 现货合约价格对比 | v3.1 ✨ |

---

## 1. 获取多时间周期K线数据

一次请求获取多个时间周期的K线数据,用于多周期分析和趋势判断。

### 请求

```http
GET /api/v1/market/klines/multi?symbol=BTC&intervals=1m,5m,15m,1h
```

### Query Parameters

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `symbol` | string | ✅ | - | 交易对符号 (如 `BTC`, `ETH`) |
| `intervals` | string | ❌ | `1m,5m,15m,1h,4h,1d` | 时间周期(逗号分隔) |
| `limit` | integer | ❌ | `100` | 每个周期的K线数量 |

### 支持的时间周期

- `1m` - 1分钟
- `5m` - 5分钟
- `15m` - 15分钟
- `30m` - 30分钟
- `1h` - 1小时
- `4h` - 4小时
- `1d` - 1天
- `1w` - 1周

### 响应

**状态码**: `200 OK`

```json
{
  "success": true,
  "data": {
    "1m": [
      {
        "open_time": "2025-11-05T14:00:00Z",
        "open": "69500.00",
        "high": "69550.00",
        "low": "69480.00",
        "close": "69520.00",
        "volume": "125.45",
        "close_time": "2025-11-05T14:00:59Z",
        "quote_volume": "8724562.50",
        "trades": 1523,
        "taker_buy_volume": "65.23",
        "taker_buy_quote_volume": "4532145.20"
      }
      // ... more 1m klines
    ],
    "5m": [
      {
        "open_time": "2025-11-05T14:00:00Z",
        "open": "69450.00",
        "high": "69600.00",
        "low": "69420.00",
        "close": "69520.00",
        "volume": "542.12",
        "close_time": "2025-11-05T14:04:59Z",
        "quote_volume": "37654321.45",
        "trades": 7234,
        "taker_buy_volume": "285.67",
        "taker_buy_quote_volume": "19845632.10"
      }
      // ... more 5m klines
    ],
    "1h": [
      // ... 1h klines
    ]
  },
  "symbol": "BTC",
  "exchange": "binance",
  "market_type": "spot",
  "timestamp": "2025-11-05T14:30:00Z"
}
```

### K线数据字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `open_time` | datetime | K线开始时间 (UTC) |
| `open` | string | 开盘价 |
| `high` | string | 最高价 |
| `low` | string | 最低价 |
| `close` | string | 收盘价 |
| `volume` | string | 成交量 (基础货币) |
| `close_time` | datetime | K线结束时间 (UTC) |
| `quote_volume` | string | 成交额 (计价货币) |
| `trades` | integer | 成交笔数 |
| `taker_buy_volume` | string | 主动买入量 |
| `taker_buy_quote_volume` | string | 主动买入额 |

### 错误响应

**状态码**: `400 Bad Request`

```json
{
  "detail": "symbol参数缺失"
}
```

**状态码**: `500 Internal Server Error`

```json
{
  "detail": "获取多周期K线失败: Connection timeout"
}
```

### 使用场景

1. **多周期趋势分析**: 同时查看短期(1m, 5m)和长期(1h, 4h)趋势
2. **交易信号验证**: 跨周期确认买卖信号
3. **波动率评估**: 对比不同周期的价格波动
4. **量能分析**: 多周期成交量对比

---

## 2. 现货合约价格对比

对比同一交易对在现货和合约市场的价格差异,用于套利分析。

### 请求

```http
GET /api/v1/market/spot-futures-compare?symbol=BTC&interval=1h
```

### Query Parameters

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `symbol` | string | ✅ | - | 交易对符号 |
| `interval` | string | ❌ | `1h` | K线周期 |
| `limit` | integer | ❌ | `100` | K线数量 |

### 响应

**状态码**: `200 OK`

```json
{
  "success": true,
  "data": {
    "spot": [
      {
        "open_time": "2025-11-05T14:00:00Z",
        "open": "69500.00",
        "high": "69550.00",
        "low": "69480.00",
        "close": "69520.00",
        "volume": "125.45"
      }
      // ... more spot klines
    ],
    "futures": [
      {
        "open_time": "2025-11-05T14:00:00Z",
        "open": "69520.00",
        "high": "69570.00",
        "low": "69500.00",
        "close": "69540.00",
        "volume": "1523.67",
        "funding_rate": "0.0001",
        "open_interest": "1234567.89"
      }
      // ... more futures klines
    ],
    "comparison": {
      "current_spread": "20.00",           // 当前价差 (futures - spot)
      "spread_percentage": "0.029%",       // 价差百分比
      "average_spread": "15.50",           // 平均价差
      "max_spread": "45.00",               // 最大价差
      "min_spread": "-10.00",              // 最小价差
      "spread_volatility": "12.34",        // 价差波动率
      "funding_rate": "0.0001",            // 当前资金费率
      "next_funding_time": "2025-11-05T16:00:00Z",  // 下次资金费率时间
      "arbitrage_opportunity": false       // 是否有套利机会
    }
  },
  "symbol": "BTC",
  "exchange": "binance",
  "interval": "1h",
  "timestamp": "2025-11-05T14:30:00Z"
}
```

### 合约独有字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `funding_rate` | string | 资金费率 |
| `open_interest` | string | 未平仓合约量 |

### 对比分析字段

| 字段 | 类型 | 说明 |
|------|------|------|
| `current_spread` | string | 当前价差 (合约价 - 现货价) |
| `spread_percentage` | string | 价差百分比 |
| `average_spread` | string | 时间段内平均价差 |
| `max_spread` | string | 最大价差 |
| `min_spread` | string | 最小价差 |
| `spread_volatility` | string | 价差波动率 (标准差) |
| `funding_rate` | string | 当前资金费率 |
| `next_funding_time` | datetime | 下次资金费率结算时间 |
| `arbitrage_opportunity` | boolean | 是否存在套利机会 (价差 > 阈值) |

### 套利信号判断

系统自动判断套利机会的条件:

```python
arbitrage_opportunity = (
    abs(spread_percentage) > 0.5%  # 价差超过0.5%
    and funding_rate < 0.1%        # 资金费率较低
    and open_interest > threshold  # 足够的流动性
)
```

### 使用场景

1. **套利交易**: 发现现货-合约价差套利机会
2. **价格发现**: 判断市场定价是否合理
3. **趋势预判**: 合约价格往往领先现货
4. **风险对冲**: 制定对冲策略

---

## 代码示例

### Python

```python
import httpx
import asyncio

async def get_multi_timeframe_data():
    """获取多周期K线"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/api/v1/market/klines/multi",
            params={
                "symbol": "BTC",
                "intervals": "1m,5m,15m,1h,4h",
                "limit": 100
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"获取到 {len(data['data'])} 个时间周期的数据")
            
            # 分析1小时K线
            klines_1h = data['data']['1h']
            latest = klines_1h[-1]
            print(f"BTC 1h: {latest['close']}")

async def compare_spot_futures():
    """对比现货合约"""
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "http://localhost:8000/api/v1/market/spot-futures-compare",
            params={
                "symbol": "BTC",
                "interval": "1h",
                "limit": 24  # 最近24小时
            }
        )
        
        if response.status_code == 200:
            data = response.json()
            comparison = data['data']['comparison']
            
            print(f"当前价差: {comparison['current_spread']}")
            print(f"价差百分比: {comparison['spread_percentage']}")
            print(f"套利机会: {comparison['arbitrage_opportunity']}")

# 运行
asyncio.run(get_multi_timeframe_data())
asyncio.run(compare_spot_futures())
```

### JavaScript

```javascript
// 获取多周期K线
async function getMultiTimeframeKlines(symbol) {
  const response = await fetch(
    `http://localhost:8000/api/v1/market/klines/multi?symbol=${symbol}&intervals=1m,5m,1h`
  );
  
  const data = await response.json();
  
  if (data.success) {
    console.log('多周期数据:', data.data);
    
    // 分析趋势一致性
    const close_1m = parseFloat(data.data['1m'].slice(-1)[0].close);
    const close_5m = parseFloat(data.data['5m'].slice(-1)[0].close);
    const close_1h = parseFloat(data.data['1h'].slice(-1)[0].close);
    
    console.log('1m收盘:', close_1m);
    console.log('5m收盘:', close_5m);
    console.log('1h收盘:', close_1h);
    
    // 判断趋势
    if (close_1m > close_5m && close_5m > close_1h) {
      console.log('多周期上涨趋势一致 📈');
    }
  }
}

// 现货合约对比
async function compareSpotFutures(symbol) {
  const response = await fetch(
    `http://localhost:8000/api/v1/market/spot-futures-compare?symbol=${symbol}`
  );
  
  const data = await response.json();
  
  if (data.success) {
    const { comparison } = data.data;
    
    console.log(`价差: ${comparison.current_spread}`);
    console.log(`资金费率: ${comparison.funding_rate}`);
    
    if (comparison.arbitrage_opportunity) {
      console.log('🚨 发现套利机会!');
    }
  }
}

// 使用
getMultiTimeframeKlines('BTC');
compareSpotFutures('BTC');
```

### cURL

```bash
# 获取多周期K线
curl "http://localhost:8000/api/v1/market/klines/multi?symbol=BTC&intervals=1m,5m,15m,1h,4h&limit=50"

# 现货合约对比
curl "http://localhost:8000/api/v1/market/spot-futures-compare?symbol=ETH&interval=1h&limit=24"
```

---

## 性能优化

### 1. 并发请求

内部使用 `asyncio.gather()` 并发获取多个周期的数据:

```python
# 并发获取6个周期,总耗时 ≈ 单次请求耗时
tasks = [
    adapter.get_klines(symbol, "1m", 100),
    adapter.get_klines(symbol, "5m", 100),
    adapter.get_klines(symbol, "15m", 100),
    adapter.get_klines(symbol, "1h", 100),
    adapter.get_klines(symbol, "4h", 100),
    adapter.get_klines(symbol, "1d", 100),
]
results = await asyncio.gather(*tasks)
```

### 2. 响应时间

| 端点 | 平均响应时间 | 数据量 |
|------|------------|--------|
| `/klines/multi` (6周期) | ~300ms | ~600条K线 |
| `/spot-futures-compare` | ~250ms | ~200条K线 |

### 3. 缓存策略

```python
# 短期缓存 (1-5分钟周期)
CACHE_TTL_SHORT = 30  # 30秒

# 长期缓存 (1小时及以上)
CACHE_TTL_LONG = 300  # 5分钟
```

---

## 注意事项

1. **交易所限制**
   - 某些交易所可能不支持所有时间周期
   - 请求频率受交易所API限制

2. **数据一致性**
   - 不同周期的K线可能来自不同时间点
   - 建议以 `timestamp` 字段为准

3. **现货合约对比**
   - 仅Binance支持(Hyperliquid只有合约)
   - 需要同时配置现货和合约API

4. **套利判断**
   - 系统提供的套利信号仅供参考
   - 实际套利需考虑手续费、滑点等成本

---

## 相关文档

- [交易所管理API](./交易所管理API.md)
- [技术架构 - 多交易所集成](../03-技术架构/07-多交易所集成架构.md)
- [快速上手指南](../06-快速参考/v3.1快速上手指南.md)

---

## 更新记录

- **2025-11-05**: v3.1 新增
  - `/klines/multi` 多周期K线端点
  - `/spot-futures-compare` 现货合约对比端点
  - 并发优化,支持6个周期<300ms响应

