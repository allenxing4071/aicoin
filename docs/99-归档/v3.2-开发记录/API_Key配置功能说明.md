# API Key 配置功能说明

## 📋 功能概述

为**巨鲸监控**和**链上数据监控**页面添加了API Key配置功能，允许用户直接在前端界面配置和管理第三方数据源的API密钥。

---

## 🎯 涉及页面

### 1. 巨鲸监控 (`/admin/intelligence/whale`)

**需要配置的数据源**:
- **Whale Alert API** - 巨鲸交易监控服务
  - 官网: https://whale-alert.io
  - 注册获取Key: https://whale-alert.io/signup

### 2. 链上数据监控 (`/admin/intelligence/onchain`)

**需要配置的数据源**:
- **Etherscan API** - 以太坊链上数据
  - 官网: https://etherscan.io
  - 获取API Key: https://etherscan.io/myapikey
  
- **Glassnode API** - 链上指标分析
  - 官网: https://glassnode.com
  - 获取API Key: https://studio.glassnode.com/settings/api

---

## 🔧 功能特性

### 1. 配置按钮

每个数据源卡片上都有一个 **🔑 配置Key** 按钮：

```
┌─────────────────────────────────────────────────┐
│ Whale Alert API                    [✗ 禁用]    │
│ 巨鲸交易监控 - 需要API Key                      │
│ 更新间隔: 10分钟                                │
│                                                 │
│ [🔑 配置Key] [测试连接] [启用]                  │
└─────────────────────────────────────────────────┘
```

### 2. 配置模态框

点击"配置Key"按钮后，弹出配置模态框：

```
┌─────────────────────────────────────┐
│ 🔑 配置 API Key                     │
│                                     │
│ 数据源: Whale Alert API             │
│ 巨鲸交易监控 - 需要API Key          │
│                                     │
│ ┌─────────────────────────────────┐ │
│ │ [请输入 API Key]                │ │
│ └─────────────────────────────────┘ │
│                                     │
│ 💡 提示: API Key 将安全存储在服务器端│
│                                     │
│ 📝 获取 Whale Alert API Key:       │
│    https://whale-alert.io/signup   │
│                                     │
│ [保存]  [取消]                      │
└─────────────────────────────────────┘
```

### 3. 安全存储

- API Key 以 **密码输入框** 形式显示（`type="password"`）
- 保存后存储在服务器端 Redis 配置中
- 前端不会明文显示已保存的 API Key

### 4. 获取链接提示

配置模态框中会根据数据源类型显示对应的API Key获取链接：

| 数据源 | 获取链接 |
|--------|---------|
| Whale Alert | https://whale-alert.io/signup |
| Etherscan | https://etherscan.io/myapikey |
| Glassnode | https://studio.glassnode.com/settings/api |

---

## 🔄 使用流程

### 完整配置流程

```
1. 访问页面
   ↓
2. 点击 [🔑 配置Key] 按钮
   ↓
3. 在模态框中输入 API Key
   ↓
4. 点击 [保存]
   ↓
5. 系统保存配置到 Redis
   ↓
6. 页面自动刷新
   ↓
7. 点击 [测试连接] 验证 API Key
   ↓
8. 测试成功后，点击 [启用] 启动数据源
   ↓
9. 系统开始自动收集数据
```

### 示例操作

**配置 Whale Alert API**:

1. 访问 https://whale-alert.io/signup 注册账号
2. 获取 API Key（例如: `abc123xyz456...`）
3. 在巨鲸监控页面点击"配置Key"
4. 输入 API Key
5. 点击"保存"
6. 点击"测试连接"验证
7. 测试成功后点击"启用"

---

## 💻 技术实现

### 前端实现

**新增状态**:
```typescript
const [showConfigModal, setShowConfigModal] = useState(false);
const [selectedSource, setSelectedSource] = useState<DataSource | null>(null);
const [apiKeyInput, setApiKeyInput] = useState('');
```

**配置处理函数**:
```typescript
const handleConfigApiKey = (source: DataSource) => {
  setSelectedSource(source);
  setApiKeyInput(source.api_key || '');
  setShowConfigModal(true);
};

const handleSaveApiKey = async () => {
  // 1. 获取完整配置
  const configRes = await fetch('http://localhost:8000/api/v1/admin/intelligence/config');
  const configData = await configRes.json();
  
  // 2. 更新API Key
  const updatedSources = configData.data.data_sources.map((s: DataSource) => {
    if (s.name === selectedSource.name) {
      return { ...s, api_key: apiKeyInput };
    }
    return s;
  });

  // 3. 保存配置
  const saveRes = await fetch('http://localhost:8000/api/v1/admin/intelligence/config', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      ...configData.data,
      data_sources: updatedSources,
    }),
  });
  
  // 4. 刷新页面数据
  if (saveData.success) {
    alert('✅ API Key 保存成功');
    setShowConfigModal(false);
    fetchData();
  }
};
```

### 后端API

使用现有的情报配置管理API：

**获取配置**:
```
GET /api/v1/admin/intelligence/config
```

**保存配置**:
```
POST /api/v1/admin/intelligence/config
Content-Type: application/json

{
  "enabled": true,
  "update_interval": 1800,
  "qwen_model": "qwen-plus",
  "mock_mode": false,
  "data_sources": [
    {
      "type": "whale",
      "name": "Whale Alert API",
      "url": "https://api.whale-alert.io/v1/transactions",
      "api_key": "your-api-key-here",
      "enabled": true,
      "update_interval": 600,
      "description": "巨鲸交易监控 - 需要API Key"
    }
  ]
}
```

### 数据存储

API Key 存储在 Redis 中：

```
Key: intelligence:config
Value: {
  "enabled": true,
  "data_sources": [
    {
      "name": "Whale Alert API",
      "api_key": "encrypted-or-plain-key",
      ...
    }
  ]
}
TTL: 30天
```

---

## 🎨 UI设计

### 按钮样式

| 按钮 | 颜色 | 用途 |
|-----|------|------|
| 🔑 配置Key | Purple/Indigo | 打开配置模态框 |
| 测试连接 | Blue | 测试API连接 |
| 启用/禁用 | Green/Gray | 切换数据源状态 |

### 模态框样式

- **背景遮罩**: 黑色半透明 (`bg-black bg-opacity-50`)
- **模态框**: 白色圆角卡片 (`bg-white rounded-xl`)
- **输入框**: 密码类型，紫色/靛蓝色焦点环
- **提示框**: 蓝色背景（通用提示）、绿色背景（获取链接）

---

## ⚠️ 注意事项

### 1. API Key 安全

- ✅ 前端使用密码输入框（`type="password"`）
- ✅ 后端存储在 Redis（建议加密存储）
- ⚠️ 当前未实现加密，建议后续添加加密存储

### 2. 测试连接

- 必须先配置 API Key 才能测试连接
- 测试失败可能原因：
  - API Key 无效
  - API Key 配额已用完
  - 网络连接问题
  - API 服务暂时不可用

### 3. 数据采集

- 启用数据源后，系统会按照配置的更新间隔自动采集数据
- Whale Alert: 10分钟间隔
- Etherscan: 30分钟间隔
- Glassnode: 60分钟间隔

### 4. 成本考虑

- Whale Alert: 免费版有请求限制
- Etherscan: 免费版每秒5次请求
- Glassnode: 需要付费订阅

---

## 📊 功能对比

### 配置前 vs 配置后

| 功能 | 配置前 | 配置后 |
|-----|--------|--------|
| 数据源状态 | ❌ 禁用（无API Key） | ✅ 可启用 |
| 连接测试 | ❌ 无法测试 | ✅ 可以测试 |
| 数据采集 | ❌ 无法采集 | ✅ 自动采集 |
| 巨鲸活动 | ❌ 无数据 | ✅ 实时数据 |
| 链上指标 | ❌ 无数据 | ✅ 实时数据 |

---

## 🔮 未来优化

### P1 - 高优先级

1. **API Key 加密存储**
   - 使用 AES 加密存储 API Key
   - 仅在使用时解密

2. **API Key 验证**
   - 保存前自动测试连接
   - 验证 API Key 格式

### P2 - 中优先级

3. **配额监控**
   - 显示 API 调用次数
   - 配额预警

4. **多 Key 支持**
   - 支持配置多个 API Key
   - 自动轮换使用

### P3 - 低优先级

5. **Key 管理历史**
   - 记录 Key 更新历史
   - 支持回滚

---

## 📝 更新日志

### v1.0 (2025-11-09)

**新增功能**:
- ✅ 巨鲸监控页面添加 API Key 配置功能
- ✅ 链上数据监控页面添加 API Key 配置功能
- ✅ 配置模态框UI设计
- ✅ API Key 获取链接提示
- ✅ 密码输入框保护

**涉及文件**:
- `frontend/app/admin/intelligence/whale/page.tsx`
- `frontend/app/admin/intelligence/onchain/page.tsx`

**API依赖**:
- `GET /api/v1/admin/intelligence/config`
- `POST /api/v1/admin/intelligence/config`

---

## 🎯 总结

API Key 配置功能的添加使得巨鲸监控和链上数据监控功能更加完整和实用。用户现在可以：

1. ✅ 直接在前端配置 API Key
2. ✅ 测试连接验证 Key 有效性
3. ✅ 启用数据源开始采集数据
4. ✅ 获得实时的巨鲸活动和链上指标

这大大提升了系统的易用性和完整性！🚀

