# 🔌 API集成文档

> 前端如何对接后端API  
> **最后更新**: 2025-11-02

---

## 📚 API集成概述

AIcoin前端通过**Axios**与后端API通信，所有API请求都遵循统一的模式。

### 基础配置

```typescript
// API Base URL
const API_BASE = 'http://localhost:8000/api/v1';

// 完整URL示例
const url = `${API_BASE}/market/tickers`;
```

---

## 🔗 API端点映射

### 1. 市场数据API

| 前端组件 | API端点 | 更新频率 | 说明 |
|---------|---------|----------|------|
| PriceTicker | `/market/tickers` | 5秒 | 多个币种价格 |
| LightweightChart | `/market/kline/{symbol}` | 手动 | K线数据 |

**示例代码**:
```typescript
// PriceTicker.tsx
const fetchRealPrices = async () => {
  try {
    const response = await axios.get(`${API_BASE}/market/tickers`);
    if (response.data && Array.isArray(response.data)) {
      const realTickers = response.data
        .filter((ticker: any) => ticker && ticker.symbol)
        .map((ticker: any) => ({
          symbol: ticker.symbol,
          price: parseFloat(ticker.price || 0),
          change24h: parseFloat(ticker.change_24h || 0),
          timestamp: ticker.timestamp
        }));
      setTickers(realTickers);
      setLoading(false);
    }
  } catch (error) {
    console.error('Failed to fetch real prices:', error);
    setLoading(true);
  }
};

// 5秒自动刷新
useEffect(() => {
  fetchRealPrices();
  const interval = setInterval(fetchRealPrices, 5000);
  return () => clearInterval(interval);
}, []);
```

---

### 2. 账户管理API

| 前端组件 | API端点 | 更新频率 | 说明 |
|---------|---------|----------|------|
| ModelCard | `/account/info` | 10秒 | 账户余额 |
| page.tsx | `/account/value` | 10秒 | 账户总价值 |

**示例代码**:
```typescript
// page.tsx
const fetchModelsData = async () => {
  try {
    const accountResponse = await axios.get(`${API_BASE}/account/info`);
    const realBalance = parseFloat(
      accountResponse.data.equity || 
      accountResponse.data.balance || 
      0
    );
    
    setModelsData([
      { 
        name: 'DEEPSEEK CHAT V3.1', 
        slug: 'deepseek-chat-v3.1', 
        value: realBalance,
        change: 0,  // TODO: 实现历史记录
        color: '#3b82f6', 
        icon: 'deepseek'
      },
    ]);
    setLoadingModels(false);
  } catch (error) {
    console.log('Failed to fetch models data:', error);
    setLoadingModels(true);
  }
};
```

---

### 3. 交易管理API

| 前端组件 | API端点 | 更新频率 | 说明 |
|---------|---------|----------|------|
| TradeListComplete | `/trading/trades` | 30秒 | 交易历史 |
| PositionsList | `/trading/positions` | 10秒 | 当前持仓 |

**示例代码**:
```typescript
// TradeListComplete.tsx
const fetchRealTrades = async () => {
  try {
    const response = await axios.get(`${API_BASE}/trading/trades?limit=100`);
    
    if (response.data && response.data.trades) {
      const realTrades = response.data.trades.map((trade: any, index: number) => {
        const modelData = models.find(m => m.slug === trade.model) || models[0];
        
        return {
          id: trade.id || index,
          model: modelData.name,
          modelIcon: modelData.icon || '🤖',
          type: trade.side.toLowerCase() === 'buy' ? 'long' as const : 'short' as const,
          symbol: trade.symbol,
          price: `$${parseFloat(trade.price || 0).toFixed(4)}`,
          quantity: parseFloat(trade.size || 0).toFixed(4),
          notional: `$${(parseFloat(trade.size || 0) * parseFloat(trade.price || 0) / 1000).toFixed(3)}k`,
          holdingTime: formatHoldingTime(trade.timestamp),
          pnl: parseFloat(trade.closed_pnl || trade.pnl || 0),
          timestamp: formatTimestamp(trade.timestamp)
        };
      });
      
      setTrades(realTrades);
      setLoading(false);
    } else {
      setTrades([]);
      setLoading(true);
    }
  } catch (error) {
    console.error('Failed to fetch trades:', error);
    setTrades([]);
    setLoading(true);
  }
};

// 30秒自动刷新
useEffect(() => {
  fetchRealTrades();
  const interval = setInterval(fetchRealTrades, 30000);
  return () => clearInterval(interval);
}, [models]);
```

---

### 4. AI决策API

| 前端组件 | API端点 | 更新频率 | 说明 |
|---------|---------|----------|------|
| AIDecisionChat | `/ai/chat/history` | 手动 | AI聊天历史 |
| DecisionTimeline | `/ai/decisions` | 手动 | 决策历史 |
| PermissionIndicator | `/ai/permission` | 手动 | 权限状态 |

**示例代码**:
```typescript
// AIDecisionChat.tsx
const fetchChatHistory = async () => {
  try {
    const response = await axios.get(
      `${API_BASE}/ai/chat/history?limit=50&model=${selectedModel}`
    );
    
    if (response.data && response.data.messages && response.data.messages.length > 0) {
      setMessages(response.data.messages);
      setLoading(false);
    } else {
      setMessages([]);
      setLoading(false);
    }
  } catch (error) {
    console.error('Failed to fetch chat history:', error);
    setMessages([]);
    setLoading(true);
  }
};
```

---

### 5. 性能指标API

| 前端组件 | API端点 | 更新频率 | 说明 |
|---------|---------|----------|------|
| PerformanceDashboard | `/performance/metrics` | 手动 | 性能指标 |
| AIStatusPanel | `/constraints/status` | 手动 | 约束状态 |

**示例代码**:
```typescript
// PerformanceDashboard.tsx
const fetchPerformanceMetrics = async () => {
  try {
    const response = await axios.get(
      `${API_BASE}/performance/metrics`,
      { timeout: 10000 }
    );
    
    if (response.data) {
      setMetrics(response.data);
      setLoading(false);
      setRetryCount(0);
    }
  } catch (error) {
    console.error('Failed to fetch performance metrics:', error);
    
    // 自动重试机制
    if (retryCount < 3) {
      setTimeout(() => {
        setRetryCount(retryCount + 1);
        fetchPerformanceMetrics();
      }, 2000);
    } else {
      setLoading(true);
    }
  }
};
```

---

### 6. 系统状态API

| 前端组件 | API端点 | 更新频率 | 说明 |
|---------|---------|----------|------|
| page.tsx (Footer) | `/status` | 10秒 | 系统状态 |
| - | `/health` | 手动 | 健康检查 |

**示例代码**:
```typescript
// page.tsx
const fetchAiHealth = async () => {
  try {
    const response = await axios.get(`${API_BASE}/status`);
    setAiHealth({
      status: response.data.orchestrator_status || 'unknown',
      tradeCount: response.data.trade_count || 0
    });
  } catch (error) {
    console.error('Failed to fetch AI health:', error);
  }
};

// 10秒自动刷新
useEffect(() => {
  fetchAiHealth();
  const interval = setInterval(fetchAiHealth, 10000);
  return () => clearInterval(interval);
}, []);
```

---

## 🔧 API集成模式

### 1. 基础请求模式

```typescript
const fetchData = async () => {
  try {
    const response = await axios.get(`${API_BASE}/endpoint`);
    setData(response.data);
    setLoading(false);
  } catch (error) {
    console.error('Failed to fetch:', error);
    setLoading(true);
  }
};
```

### 2. 带参数请求

```typescript
const fetchDataWithParams = async (params: any) => {
  try {
    const response = await axios.get(`${API_BASE}/endpoint`, {
      params: {
        limit: params.limit,
        page: params.page
      }
    });
    setData(response.data);
  } catch (error) {
    console.error('Failed to fetch:', error);
  }
};
```

### 3. 自动刷新模式

```typescript
useEffect(() => {
  fetchData();
  const interval = setInterval(fetchData, 5000);  // 5秒刷新
  return () => clearInterval(interval);
}, []);
```

### 4. 重试机制

```typescript
const [retryCount, setRetryCount] = useState(0);

const fetchDataWithRetry = async () => {
  try {
    const response = await axios.get(`${API_BASE}/endpoint`, {
      timeout: 10000
    });
    setData(response.data);
    setRetryCount(0);
  } catch (error) {
    if (retryCount < 3) {
      setTimeout(() => {
        setRetryCount(retryCount + 1);
        fetchDataWithRetry();
      }, 2000);
    }
  }
};
```

---

## 🎯 数据转换

### 1. 价格格式化

```typescript
// 后端返回: "110010.5"
// 前端显示: "$110,010.50"

const formatPrice = (price: string | number): string => {
  return `$${parseFloat(price).toLocaleString('en-US', {
    minimumFractionDigits: 2,
    maximumFractionDigits: 2
  })}`;
};
```

### 2. 百分比格式化

```typescript
// 后端返回: 0.155
// 前端显示: "+15.5%"

const formatPercent = (value: number): string => {
  const sign = value >= 0 ? '+' : '';
  return `${sign}${(value * 100).toFixed(2)}%`;
};
```

### 3. 时间格式化

```typescript
// 后端返回: "2025-11-02T10:00:00Z"
// 前端显示: "2小时前"

const formatTimeAgo = (timestamp: string): string => {
  const now = new Date();
  const time = new Date(timestamp);
  const diff = now.getTime() - time.getTime();
  
  const minutes = Math.floor(diff / 60000);
  const hours = Math.floor(diff / 3600000);
  const days = Math.floor(diff / 86400000);
  
  if (minutes < 60) return `${minutes}分钟前`;
  if (hours < 24) return `${hours}小时前`;
  return `${days}天前`;
};
```

---

## ⚠️ 错误处理

### 1. 网络错误

```typescript
try {
  const response = await axios.get(url);
} catch (error) {
  if (axios.isAxiosError(error)) {
    if (error.code === 'ECONNABORTED') {
      console.error('Request timeout');
    } else if (error.response) {
      console.error('Server error:', error.response.status);
    } else if (error.request) {
      console.error('Network error');
    }
  }
}
```

### 2. 数据验证

```typescript
const response = await axios.get(url);

// 验证响应结构
if (!response.data) {
  throw new Error('Invalid response');
}

// 验证数据类型
if (!Array.isArray(response.data.trades)) {
  throw new Error('Invalid data format');
}

// 过滤无效数据
const validData = response.data.trades.filter(
  (item: any) => item && item.id && item.symbol
);
```

### 3. 用户反馈

```typescript
// 加载状态
if (loading) {
  return <LoadingSkeleton type="card" />;
}

// 错误状态
if (error) {
  return (
    <div className="error">
      <p>加载失败</p>
      <button onClick={retry}>重试</button>
    </div>
  );
}

// 空数据
if (data.length === 0) {
  return <div>暂无数据</div>;
}
```

---

## 🚀 性能优化

### 1. 请求去重

```typescript
let requestInProgress = false;

const fetchData = async () => {
  if (requestInProgress) return;
  
  requestInProgress = true;
  try {
    const response = await axios.get(url);
    setData(response.data);
  } finally {
    requestInProgress = false;
  }
};
```

### 2. 请求取消

```typescript
useEffect(() => {
  const controller = new AbortController();
  
  const fetchData = async () => {
    try {
      const response = await axios.get(url, {
        signal: controller.signal
      });
      setData(response.data);
    } catch (error) {
      if (axios.isCancel(error)) {
        console.log('Request canceled');
      }
    }
  };
  
  fetchData();
  
  return () => {
    controller.abort();
  };
}, []);
```

### 3. 数据缓存

```typescript
const cache = new Map();

const fetchDataWithCache = async (key: string) => {
  if (cache.has(key)) {
    return cache.get(key);
  }
  
  const response = await axios.get(url);
  cache.set(key, response.data);
  
  // 5分钟后清除缓存
  setTimeout(() => cache.delete(key), 300000);
  
  return response.data;
};
```

---

## 📊 API状态管理

### 1. 全局状态

```typescript
// 使用Context API
const ApiContext = createContext(null);

export const ApiProvider = ({ children }) => {
  const [apiStatus, setApiStatus] = useState('idle');
  
  return (
    <ApiContext.Provider value={{ apiStatus, setApiStatus }}>
      {children}
    </ApiContext.Provider>
  );
};
```

### 2. React Query（推荐）

```typescript
import { useQuery } from '@tanstack/react-query';

const { data, isLoading, error } = useQuery({
  queryKey: ['trades'],
  queryFn: () => axios.get(`${API_BASE}/trading/trades`),
  refetchInterval: 30000  // 30秒自动刷新
});
```

---

## 🔐 安全考虑

### 1. API认证（计划中）

```typescript
// 添加认证头
const response = await axios.get(url, {
  headers: {
    'Authorization': `Bearer ${token}`
  }
});
```

### 2. CORS处理

```typescript
// 后端已配置CORS
// 前端无需额外处理
```

### 3. 数据验证

```typescript
// 验证响应数据
const validateResponse = (data: any): boolean => {
  if (!data) return false;
  if (typeof data !== 'object') return false;
  // 更多验证...
  return true;
};
```

---

## 📝 最佳实践

### 1. 统一API配置

```typescript
// api/config.ts
export const API_CONFIG = {
  BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:8000/api/v1',
  TIMEOUT: 10000,
  RETRY_COUNT: 3,
  RETRY_DELAY: 2000
};
```

### 2. API封装

```typescript
// api/client.ts
import axios from 'axios';
import { API_CONFIG } from './config';

const apiClient = axios.create({
  baseURL: API_CONFIG.BASE_URL,
  timeout: API_CONFIG.TIMEOUT
});

// 请求拦截器
apiClient.interceptors.request.use(
  (config) => {
    // 添加认证头等
    return config;
  },
  (error) => Promise.reject(error)
);

// 响应拦截器
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    // 统一错误处理
    return Promise.reject(error);
  }
);

export default apiClient;
```

### 3. 类型定义

```typescript
// types/api.ts
export interface ApiResponse<T> {
  success: boolean;
  data: T;
  message?: string;
}

export interface Trade {
  id: string;
  symbol: string;
  side: 'buy' | 'sell';
  price: string;
  size: string;
  timestamp: string;
}

// 使用
const response: ApiResponse<Trade[]> = await apiClient.get('/trading/trades');
```

---

## 🐛 调试技巧

### 1. 请求日志

```typescript
const fetchData = async () => {
  console.log('🔄 Fetching data from:', url);
  
  try {
    const response = await axios.get(url);
    console.log('✅ Response:', response.data);
  } catch (error) {
    console.error('❌ Error:', error);
  }
};
```

### 2. Network Tab

- 打开Chrome DevTools
- 切换到Network标签
- 筛选XHR请求
- 查看请求/响应详情

### 3. React DevTools

- 查看组件状态
- 追踪状态更新
- 性能分析

---

**文档版本**: v1.0  
**最后更新**: 2025-11-02  
**维护状态**: ✅ Active

