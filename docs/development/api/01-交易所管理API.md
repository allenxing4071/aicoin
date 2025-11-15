# 交易所管理 API

> **版本**: v3.1  
> **Base URL**: `/api/v1/exchanges`  
> **认证**: 暂不需要 (后续版本将添加)

## 概述

交易所管理API提供多交易所配置、切换、查询功能,支持动态切换Binance、Hyperliquid等交易所。

## 端点列表

| 方法 | 路径 | 描述 | 状态 |
|------|------|------|------|
| GET | `/` | 获取所有交易所配置 | ✅ |
| GET | `/active` | 获取当前激活的交易所 | ✅ |
| GET | `/supported` | 获取支持的交易所列表 | ✅ |
| POST | `/switch` | 切换交易所 | ✅ |
| GET | `/{exchange_id}` | 获取指定交易所配置 | ✅ |
| PUT | `/{exchange_id}` | 更新交易所配置 | ✅ |
| POST | `/` | 创建交易所配置 | ✅ |
| DELETE | `/{exchange_id}` | 删除交易所配置 | ✅ |

---

## 1. 获取所有交易所配置

获取数据库中所有的交易所配置信息。

### 请求

```http
GET /api/v1/exchanges
```

### 响应

**状态码**: `200 OK`

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "name": "hyperliquid",
      "display_name": "Hyperliquid",
      "is_active": true,
      "market_type": "perpetual",
      "testnet": false,
      "config": {},
      "created_at": "2025-11-05T12:52:17.003600+00:00",
      "updated_at": "2025-11-05T12:52:17.003600+00:00"
    },
    {
      "id": 2,
      "name": "binance",
      "display_name": "Binance",
      "is_active": false,
      "market_type": "spot",
      "testnet": false,
      "config": {},
      "created_at": "2025-11-05T13:20:45.123456+00:00",
      "updated_at": "2025-11-05T13:20:45.123456+00:00"
    }
  ],
  "count": 2
}
```

### 字段说明

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | integer | 配置ID |
| `name` | string | 交易所标识 (`binance`, `hyperliquid`) |
| `display_name` | string | 显示名称 |
| `is_active` | boolean | 是否为当前激活的交易所 |
| `market_type` | string | 市场类型 (`spot`, `futures`, `perpetual`) |
| `testnet` | boolean | 是否为测试网 |
| `config` | object | 额外配置 (JSON) |
| `created_at` | datetime | 创建时间 (UTC) |
| `updated_at` | datetime | 更新时间 (UTC) |

---

## 2. 获取当前激活的交易所

获取当前系统正在使用的交易所信息。

### 请求

```http
GET /api/v1/exchanges/active
```

### 响应

**状态码**: `200 OK`

```json
{
  "success": true,
  "data": {
    "name": "hyperliquid",
    "market_type": "perpetual",
    "is_initialized": true,
    "supports_spot": false,
    "supports_futures": true
  }
}
```

### 错误响应

**状态码**: `500 Internal Server Error`

```json
{
  "detail": "获取当前交易所失败: Hyperliquid钱包凭证未配置"
}
```

---

## 3. 获取支持的交易所列表

获取系统支持的所有交易所及其功能特性。

### 请求

```http
GET /api/v1/exchanges/supported
```

### 响应

**状态码**: `200 OK`

```json
{
  "success": true,
  "data": [
    {
      "name": "binance",
      "display_name": "Binance",
      "supports_spot": true,
      "supports_futures": true
    },
    {
      "name": "hyperliquid",
      "display_name": "Hyperliquid",
      "supports_spot": false,
      "supports_futures": true
    }
  ]
}
```

---

## 4. 切换交易所

切换系统当前使用的交易所和市场类型。

### 请求

```http
POST /api/v1/exchanges/switch?exchange_name=binance&market_type=spot
```

### Query Parameters

| 参数 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `exchange_name` | string | ✅ | - | 交易所名称 (`binance`, `hyperliquid`) |
| `market_type` | string | ❌ | `spot` | 市场类型 (`spot`, `futures`, `perpetual`) |

### 响应

**状态码**: `200 OK`

```json
{
  "success": true,
  "message": "成功切换到 binance (spot)",
  "data": {
    "exchange": "binance",
    "market_type": "spot"
  }
}
```

### 错误响应

**1. 不支持的交易所**

**状态码**: `400 Bad Request`

```json
{
  "detail": "不支持的交易所: okx"
}
```

**2. 不支持的市场类型**

**状态码**: `400 Bad Request`

```json
{
  "detail": "不支持的市场类型: options"
}
```

**3. 交易所限制**

**状态码**: `400 Bad Request`

```json
{
  "detail": "Hyperliquid仅支持永续合约(perpetual)"
}
```

**4. 切换失败**

**状态码**: `500 Internal Server Error`

```json
{
  "detail": "切换交易所失败"
}
```

### 注意事项

- ⚠️ 切换交易所需要相应的API密钥配置
- ⚠️ Hyperliquid只支持 `perpetual` 市场类型
- ⚠️ 切换后会立即生效,影响所有后续交易操作

---

## 5. 获取指定交易所配置

根据ID获取单个交易所的配置详情。

### 请求

```http
GET /api/v1/exchanges/{exchange_id}
```

### Path Parameters

| 参数 | 类型 | 说明 |
|------|------|------|
| `exchange_id` | integer | 交易所配置ID |

### 响应

**状态码**: `200 OK`

```json
{
  "success": true,
  "data": {
    "id": 1,
    "name": "binance",
    "display_name": "Binance",
    "is_active": false,
    "market_type": "spot",
    "testnet": false,
    "config": {
      "leverage": 3,
      "min_notional": 10.0
    },
    "created_at": "2025-11-05T12:52:17.003600+00:00",
    "updated_at": "2025-11-05T12:52:17.003600+00:00"
  }
}
```

### 错误响应

**状态码**: `404 Not Found`

```json
{
  "detail": "交易所配置不存在"
}
```

---

## 6. 更新交易所配置

更新指定交易所的配置信息。

### 请求

```http
PUT /api/v1/exchanges/{exchange_id}
Content-Type: application/json
```

```json
{
  "display_name": "Binance Mainnet",
  "testnet": false,
  "config": {
    "leverage": 5,
    "min_notional": 20.0,
    "rate_limit": 1200
  }
}
```

### Request Body

| 字段 | 类型 | 必需 | 说明 |
|------|------|------|------|
| `display_name` | string | ❌ | 显示名称 |
| `testnet` | boolean | ❌ | 是否为测试网 |
| `config` | object | ❌ | 额外配置(JSON) |

### 响应

**状态码**: `200 OK`

```json
{
  "success": true,
  "message": "交易所配置已更新",
  "data": {
    "id": 1,
    "name": "binance",
    "display_name": "Binance Mainnet",
    "is_active": false,
    "market_type": "spot",
    "testnet": false,
    "config": {
      "leverage": 5,
      "min_notional": 20.0,
      "rate_limit": 1200
    },
    "created_at": "2025-11-05T12:52:17.003600+00:00",
    "updated_at": "2025-11-05T14:30:22.654321+00:00"
  }
}
```

### 错误响应

**状态码**: `404 Not Found`

```json
{
  "detail": "交易所配置不存在"
}
```

---

## 7. 创建交易所配置

创建新的交易所配置(通常由系统自动创建)。

### 请求

```http
POST /api/v1/exchanges
Content-Type: application/json
```

```json
{
  "name": "binance",
  "display_name": "Binance",
  "market_type": "spot",
  "testnet": false,
  "config": {
    "leverage": 3
  }
}
```

### Request Body

| 字段 | 类型 | 必需 | 默认值 | 说明 |
|------|------|------|--------|------|
| `name` | string | ✅ | - | 交易所标识 |
| `display_name` | string | ✅ | - | 显示名称 |
| `market_type` | string | ❌ | `perpetual` | 市场类型 |
| `testnet` | boolean | ❌ | `true` | 是否测试网 |
| `config` | object | ❌ | `{}` | 额外配置 |

### 响应

**状态码**: `201 Created`

```json
{
  "success": true,
  "message": "交易所配置已创建",
  "data": {
    "id": 3,
    "name": "binance",
    "display_name": "Binance",
    "is_active": false,
    "market_type": "spot",
    "testnet": false,
    "config": {
      "leverage": 3
    },
    "created_at": "2025-11-05T15:00:00.000000+00:00",
    "updated_at": "2025-11-05T15:00:00.000000+00:00"
  }
}
```

---

## 8. 删除交易所配置

删除指定的交易所配置(不能删除激活的交易所)。

### 请求

```http
DELETE /api/v1/exchanges/{exchange_id}
```

### 响应

**状态码**: `200 OK`

```json
{
  "success": true,
  "message": "交易所配置 binance 已删除"
}
```

### 错误响应

**1. 配置不存在**

**状态码**: `404 Not Found`

```json
{
  "detail": "交易所配置不存在"
}
```

**2. 删除激活的交易所**

**状态码**: `400 Bad Request`

```json
{
  "detail": "不能删除激活中的交易所,请先切换到其他交易所"
}
```

---

## 代码示例

### Python (httpx)

```python
import httpx
import asyncio

async def switch_exchange():
    async with httpx.AsyncClient() as client:
        # 切换到Binance现货
        response = await client.post(
            "http://localhost:8000/api/v1/exchanges/switch",
            params={
                "exchange_name": "binance",
                "market_type": "spot"
            }
        )
        
        if response.status_code == 200:
            print(f"切换成功: {response.json()}")
        else:
            print(f"切换失败: {response.json()}")

asyncio.run(switch_exchange())
```

### JavaScript (fetch)

```javascript
// 获取所有交易所配置
async function getAllExchanges() {
  const response = await fetch('http://localhost:8000/api/v1/exchanges');
  const data = await response.json();
  
  if (data.success) {
    console.log('交易所列表:', data.data);
  }
}

// 切换交易所
async function switchExchange(exchangeName, marketType) {
  const response = await fetch(
    `http://localhost:8000/api/v1/exchanges/switch?exchange_name=${exchangeName}&market_type=${marketType}`,
    { method: 'POST' }
  );
  
  const data = await response.json();
  
  if (data.success) {
    console.log('切换成功:', data.message);
  } else {
    console.error('切换失败:', data.detail);
  }
}

// 使用示例
getAllExchanges();
switchExchange('binance', 'spot');
```

### cURL

```bash
# 获取所有交易所
curl http://localhost:8000/api/v1/exchanges

# 获取当前激活的交易所
curl http://localhost:8000/api/v1/exchanges/active

# 切换到Binance现货
curl -X POST "http://localhost:8000/api/v1/exchanges/switch?exchange_name=binance&market_type=spot"

# 更新配置
curl -X PUT http://localhost:8000/api/v1/exchanges/1 \
  -H "Content-Type: application/json" \
  -d '{
    "display_name": "Binance Mainnet",
    "testnet": false
  }'
```

---

## 错误码

| HTTP状态码 | 说明 | 常见原因 |
|-----------|------|----------|
| 200 | 请求成功 | - |
| 201 | 创建成功 | - |
| 400 | 请求参数错误 | 无效的交易所名称/市场类型 |
| 404 | 资源不存在 | 交易所配置ID不存在 |
| 500 | 服务器内部错误 | API密钥未配置、网络异常等 |

---

## 相关文档

- [技术架构 - 多交易所集成](../03-技术架构/07-多交易所集成架构.md)
- [市场数据API](./市场数据API.md)
- [部署配置](../07-部署运维/交易所配置指南.md)

---

## 更新记录

- **2025-11-05**: v3.1 初始版本
  - 8个交易所管理端点
  - 支持Binance和Hyperliquid
  - 完整的错误处理

