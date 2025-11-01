# 管理后台快速启动指南

## 🚀 快速开始

### 1. 启动后端服务

```bash
cd /Users/xinghailong/Documents/soft/AIcoin/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 2. 启动前端服务

```bash
cd /Users/xinghailong/Documents/soft/AIcoin/frontend
npm run dev
```

### 3. 访问管理后台

打开浏览器访问以下地址:

- **API 文档 (Swagger)**: http://localhost:8000/docs
- **API 文档 (ReDoc)**: http://localhost:8000/redoc
- **管理后台界面**: http://localhost:3000/admin

---

## 📋 功能清单

### API 文档页面 (Swagger UI)

访问 `http://localhost:8000/docs` 可以:

✅ 查看所有 API 接口文档  
✅ 在线测试 API 接口  
✅ 查看请求/响应示例  
✅ 按模块浏览接口  

**新增的管理后台 API 模块**:
- `Admin - Database Viewer` - 包含 8 个数据查看接口

---

### 管理后台界面

访问 `http://localhost:3000/admin` 可以:

#### 📊 概览页 (`/admin`)
- 查看系统统计 (总交易数、订单数、AI决策数、风控事件数)
- 查看最新账户余额和净值
- 快速访问各数据表
- 跳转到 API 文档

#### 💰 交易记录 (`/admin/trades`)
- 查看所有交易记录
- 筛选: 交易品种、方向、AI模型、时间范围
- 显示: 价格、数量、盈亏、置信度等

#### 📝 订单记录 (`/admin/orders`)
- 查看所有订单记录
- 筛选: 交易品种、方向、订单状态、时间范围
- 显示: 订单类型、价格、成交量、状态等

#### 💼 账户快照 (`/admin/accounts`)
- 查看账户历史快照
- 筛选: 时间范围
- 显示: 余额、净值、盈亏、夏普比率、最大回撤、胜率等

#### 🤖 AI决策日志 (`/admin/ai-decisions`)
- 查看所有 AI 决策记录
- 筛选: 交易品种、模型名称、是否执行、时间范围
- 显示: 决策内容、执行状态、拒绝原因、延迟等

#### 📈 K线数据 (`/admin/market-data`)
- 查看市场 K线数据
- 筛选: 交易品种、K线周期、时间范围
- 显示: OHLCV (开高低收量)

#### ⚠️ 风控事件 (`/admin/risk-events`)
- 查看所有风控事件
- 筛选: 事件类型、严重程度、是否解决、时间范围
- 显示: 事件描述、处理措施、解决状态等

---

## 🎯 核心功能

### 所有数据查看页面都支持:

- ✅ **分页浏览**: 10/25/50/100 条/页可选
- ✅ **多维度筛选**: 根据不同字段筛选数据
- ✅ **时间范围筛选**: 查看特定时间段的数据
- ✅ **排序功能**: 点击列标题排序 (升序/降序)
- ✅ **数据格式化**: 金额、百分比、日期自动格式化
- ✅ **状态标识**: 使用颜色区分不同状态
- ✅ **只读模式**: 仅查看,不可修改

---

## 📡 API 使用示例

### 查询交易记录

```bash
# 查询 BTC-PERP 的交易记录
curl "http://localhost:8000/api/v1/admin/trades?symbol=BTC-PERP&page=1&page_size=10"

# 查询买入方向的交易
curl "http://localhost:8000/api/v1/admin/trades?side=BUY"

# 查询特定模型的交易
curl "http://localhost:8000/api/v1/admin/trades?model=deepseek-chat"
```

### 查询系统统计

```bash
curl "http://localhost:8000/api/v1/admin/stats"
```

### 查询 AI 决策

```bash
# 查询已执行的决策
curl "http://localhost:8000/api/v1/admin/ai-decisions?executed=true"

# 查询特定模型的决策
curl "http://localhost:8000/api/v1/admin/ai-decisions?model_name=deepseek"
```

### 查询风控事件

```bash
# 查询严重级别为 HIGH 的事件
curl "http://localhost:8000/api/v1/admin/risk-events?severity=HIGH"

# 查询未解决的事件
curl "http://localhost:8000/api/v1/admin/risk-events?resolved=false"
```

---

## 🔍 数据表说明

系统包含 6 个核心数据表:

| 表名 | 说明 | 主要字段 |
|------|------|---------|
| **trades** | 交易记录 | symbol, side, price, size, pnl, model |
| **orders** | 订单记录 | symbol, side, type, status, price, size |
| **account_snapshots** | 账户快照 | balance, equity, pnl, sharpe_ratio, max_drawdown |
| **ai_decisions** | AI决策日志 | symbol, decision, executed, reject_reason, model_name |
| **market_data_kline** | K线数据 | symbol, interval, open, high, low, close, volume |
| **risk_events** | 风控事件 | event_type, severity, description, action_taken |

---

## 💡 使用技巧

### 1. 快速查看最新数据
- 默认按时间倒序排列,最新数据在最前面
- 可以调整每页显示数量 (建议 50 条)

### 2. 精确筛选
- 使用筛选栏可以快速定位特定数据
- 支持多个筛选条件组合使用
- 点击"重置"清除所有筛选

### 3. 时间范围查询
- 使用日期时间选择器选择时间范围
- 格式: `YYYY-MM-DDTHH:mm` (如: 2025-11-01T10:00)

### 4. 数据导出
- 通过 API 接口可以获取 JSON 格式数据
- 可以使用 `page_size=500` 获取更多数据

### 5. API 测试
- 在 Swagger UI 页面可以直接测试 API
- 点击 "Try it out" 按钮输入参数测试

---

## 🛠️ 故障排查

### 后端无法启动
```bash
# 检查 Python 环境
python --version  # 需要 Python 3.8+

# 安装依赖
pip install -r backend/requirements.txt

# 检查数据库连接
# 确保 PostgreSQL 正在运行
```

### 前端无法启动
```bash
# 检查 Node.js 版本
node --version  # 需要 Node.js 16+

# 安装依赖
npm install

# 清除缓存重新启动
rm -rf .next
npm run dev
```

### API 返回 500 错误
- 检查数据库是否正常运行
- 查看后端日志: `backend/backend.log`
- 确认数据表是否已创建

### 前端显示空数据
- 检查后端是否正常运行 (http://localhost:8000)
- 打开浏览器开发者工具查看网络请求
- 确认 CORS 配置正确

---

## 📞 需要帮助?

1. 查看完整实施报告: `admin-backend-implementation-report.md`
2. 查看 API 文档: http://localhost:8000/docs
3. 查看系统日志: `backend/backend.log`

---

## ✨ 特性亮点

- 🎨 **现代化 UI**: 使用 Tailwind CSS,简洁美观
- 📱 **响应式设计**: 适配桌面和移动设备
- ⚡ **高性能**: 分页查询,快速响应
- 🔒 **只读模式**: 安全的数据查看
- 📊 **数据可视化**: 状态标签、颜色区分
- 🔍 **强大筛选**: 多维度筛选和排序

---

**祝使用愉快!** 🎉

