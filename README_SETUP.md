# AIcoin Trading System - 快速启动指南

## 🚀 快速开始

### 1. 环境配置

创建 `.env` 文件(复制env.example):

```bash
cp env.example .env
```

编辑`.env`文件,填入您的API密钥:

```env
# 必填项
DEEPSEEK_API_KEY=sk-494388a93f714088ba870436de7176d7

# 可选项(Testnet模拟交易)
HYPERLIQUID_TESTNET=true
TRADING_ENABLED=false

# 数据库密码(可保持默认)
DB_PASSWORD=changeme123
```

### 2. 启动系统

使用Docker Compose一键启动:

```bash
# 启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f backend

# 查看所有服务状态
docker-compose ps
```

### 3. 初始化数据库

```bash
# 进入backend容器
docker-compose exec backend bash

# 创建数据库表
python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"

# 退出容器
exit
```

### 4. 访问服务

- **前端界面**: http://localhost:3000
- **API文档**: http://localhost:8000/docs
- **后端API**: http://localhost:8000/api/v1

### 5. 测试AI决策

在前端页面点击"Test AI Decision"按钮,或使用curl:

```bash
curl -X POST http://localhost:8000/api/v1/trading/decision \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BTC-PERP","force":true}'
```

## 📊 系统架构

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Frontend   │────▶│   Backend   │────▶│  Hyperliquid│
│  (Next.js)  │     │  (FastAPI)  │     │  (Exchange) │
└─────────────┘     └─────────────┘     └─────────────┘
                           │
                    ┌──────┴──────┐
                    ▼             ▼
              ┌──────────┐  ┌──────────┐
              │PostgreSQL│  │  Redis   │
              └──────────┘  └──────────┘
                    ▲
                    │
              ┌─────────────┐
              │   Celery    │
              │ (定时任务)   │
              └─────────────┘
```

## 🔧 服务说明

| 服务 | 端口 | 说明 |
|------|------|------|
| frontend | 3000 | Next.js前端界面 |
| backend | 8000 | FastAPI后端API |
| postgres | 5432 | PostgreSQL数据库 |
| redis | 6379 | Redis缓存 |
| celery_worker | - | Celery工作进程 |
| celery_beat | - | Celery定时任务调度 |

## 📝 核心功能

### 1. AI决策引擎
- ✅ DeepSeek API集成
- ✅ 智能Prompt工程
- ✅ 决策置信度评分
- ✅ 市场数据分析

### 2. 风控系统
- ✅ 单笔仓位限制(≤20%)
- ✅ 单日亏损限制(≤5%)
- ✅ 最大回撤限制(≤10%)
- ✅ 连续亏损保护(≤3笔)

### 3. 交易执行
- ✅ Hyperliquid集成(模拟模式)
- ✅ 订单管理
- ✅ 持仓跟踪
- ✅ PnL计算

### 4. 数据管理
- ✅ PostgreSQL持久化存储
- ✅ Redis高速缓存
- ✅ 交易记录归档
- ✅ 性能指标计算

## 🎯 启用真实交易

**⚠️ 警告: 启用真实交易前请确保充分测试**

1. 配置Hyperliquid钱包:
```env
HYPERLIQUID_WALLET_ADDRESS=0x...
HYPERLIQUID_PRIVATE_KEY=0x...
HYPERLIQUID_TESTNET=false
```

2. 启用交易:
```env
TRADING_ENABLED=true
```

3. 重启服务:
```bash
docker-compose restart backend celery_worker celery_beat
```

## 📈 监控运行

### 查看AI决策日志
```bash
docker-compose logs -f celery_worker | grep "AI Decision"
```

### 查看交易记录
```bash
curl http://localhost:8000/api/v1/trading/trades?limit=10
```

### 查看账户信息
```bash
curl http://localhost:8000/api/v1/account/info
```

### 查看性能指标
```bash
curl http://localhost:8000/api/v1/performance/metrics
```

## 🛠️ 常见问题

### Q: 无法连接到数据库?
```bash
# 检查PostgreSQL容器状态
docker-compose ps postgres

# 重启PostgreSQL
docker-compose restart postgres
```

### Q: AI决策失败?
```bash
# 检查DeepSeek API密钥
echo $DEEPSEEK_API_KEY

# 查看错误日志
docker-compose logs backend | grep "DeepSeek"
```

### Q: 前端无法访问后端?
```bash
# 检查CORS配置
# 编辑 backend/app/core/config.py
# CORS_ORIGINS = ["http://localhost:3000"]
```

## 📚 更多文档

- [项目概述](docs/01-规划文档/01-项目概述.md)
- [系统架构设计](docs/02-架构设计/01-系统架构设计.md)
- [API文档](http://localhost:8000/docs)
- [开发指南](docs/03-开发指南/01-开发环境搭建.md)

## 🔗 参考资料

- **DeepSeek API**: https://platform.deepseek.com/api-docs
- **Hyperliquid Docs**: https://hyperliquid.xyz/docs
- **FastAPI**: https://fastapi.tiangolo.com
- **Next.js**: https://nextjs.org

## 📞 技术支持

如遇问题,请查看日志:

```bash
# 查看所有服务日志
docker-compose logs

# 查看特定服务
docker-compose logs backend
docker-compose logs celery_worker
docker-compose logs frontend
```

---

**开始交易,祝您盈利! 🚀**

