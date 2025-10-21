# 🚀 AIcoin 量化交易系统 - 快速启动

## ✅ 系统已完成

恭喜!您的AIcoin量化交易系统第一个版本已经完成,包含以下核心功能:

### 已实现功能

- ✅ **后端系统(FastAPI)**
  - AI决策引擎(DeepSeek集成)
  - 交易执行系统
  - 风控管理系统
  - Hyperliquid API集成(模拟模式)
  - PostgreSQL数据库
  - Redis缓存
  - Celery定时任务

- ✅ **前端系统(Next.js)**
  - 实时监控界面
  - API状态展示
  - 快速操作按钮

- ✅ **Docker容器化**
  - 一键启动所有服务
  - 自动化部署

---

## 📋 启动步骤

### 第一步:配置API密钥

编辑项目根目录的 `env.example` 文件,将您的DeepSeek API密钥填入(已包含):

```env
DEEPSEEK_API_KEY=sk-494388a93f714088ba870436de7176d7
```

然后复制为`.env`:

```bash
cp env.example .env
```

### 第二步:启动Docker服务

```bash
# 确保Docker正在运行
docker --version

# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps
```

### 第三步:初始化数据库

```bash
# 等待服务启动(约10秒)
sleep 10

# 初始化数据库表
docker-compose exec backend python scripts/init_db.py
```

或者手动:

```bash
docker-compose exec backend python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"
```

### 第四步:访问系统

- **前端界面**: http://localhost:3000
- **API文档**: http://localhost:8000/docs
- **后端健康检查**: http://localhost:8000/health

---

## 🧪 测试AI决策

### 方法1:通过前端界面

1. 打开浏览器访问 http://localhost:3000
2. 点击"Test AI Decision"按钮
3. 查看AI决策结果弹窗

### 方法2:使用测试脚本

```bash
docker-compose exec backend python scripts/test_ai_decision.py
```

### 方法3:直接调用API

```bash
curl -X POST http://localhost:8000/api/v1/trading/decision \
  -H "Content-Type: application/json" \
  -d '{
    "symbol": "BTC-PERP",
    "force": true
  }'
```

预期响应:

```json
{
  "symbol": "BTC-PERP",
  "decision": {
    "action": "BUY" | "SELL" | "HOLD",
    "size": "0.05",
    "confidence": "0.85",
    "reasoning": "AI决策理由..."
  },
  "executed": false,
  "reject_reason": null,
  "latency_ms": 2300,
  "model_name": "deepseek"
}
```

---

## 📊 查看系统状态

### 查看日志

```bash
# 查看后端日志
docker-compose logs -f backend

# 查看Celery工作进程日志
docker-compose logs -f celery_worker

# 查看所有服务日志
docker-compose logs -f
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

---

## ⚙️ 系统配置

### 当前默认配置

```env
TRADING_ENABLED=false          # 交易默认关闭(安全)
HYPERLIQUID_TESTNET=true       # 使用Testnet(模拟交易)
DEFAULT_SYMBOL=BTC-PERP        # 默认交易品种
DECISION_INTERVAL=300          # AI决策间隔(5分钟)

# 风控参数
MAX_POSITION_PCT=0.20          # 单笔仓位≤20%
MAX_DAILY_LOSS_PCT=0.05        # 单日亏损≤5%
MAX_DRAWDOWN_PCT=0.10          # 最大回撤≤10%
```

### 修改配置

编辑 `.env` 文件后,重启服务:

```bash
docker-compose restart backend celery_worker celery_beat
```

---

## 🔧 常用命令

### 启动/停止服务

```bash
# 启动所有服务
docker-compose up -d

# 停止所有服务
docker-compose down

# 重启某个服务
docker-compose restart backend

# 查看服务状态
docker-compose ps
```

### 进入容器

```bash
# 进入后端容器
docker-compose exec backend bash

# 进入数据库容器
docker-compose exec postgres psql -U admin -d aicoin
```

### 清理系统

```bash
# 停止并删除容器(保留数据)
docker-compose down

# 完全清理(包括数据卷)
docker-compose down -v

# 重新构建
docker-compose build --no-cache
```

---

## 🎯 启用真实交易(可选)

**⚠️ 警告:仅在充分测试后启用真实交易!**

### 1. 配置Hyperliquid钱包

在 `.env` 文件中添加:

```env
HYPERLIQUID_WALLET_ADDRESS=0x你的钱包地址
HYPERLIQUID_PRIVATE_KEY=0x你的私钥
HYPERLIQUID_TESTNET=false
```

### 2. 启用交易

```env
TRADING_ENABLED=true
```

### 3. 重启服务

```bash
docker-compose restart backend celery_worker celery_beat
```

### 4. 监控运行

```bash
# 实时查看AI决策
docker-compose logs -f celery_worker | grep "AI Decision"

# 查看风控事件
docker-compose logs -f backend | grep "Risk"
```

---

## 📚 API文档

访问 http://localhost:8000/docs 查看完整的交互式API文档

主要端点:

- `POST /api/v1/trading/decision` - 触发AI决策
- `GET /api/v1/trading/trades` - 查询交易记录
- `GET /api/v1/market/kline/{symbol}` - 获取K线数据
- `GET /api/v1/market/orderbook/{symbol}` - 获取订单簿
- `GET /api/v1/account/info` - 获取账户信息
- `GET /api/v1/performance/metrics` - 获取性能指标

---

## 🐛 故障排查

### 问题1:无法启动服务

```bash
# 检查Docker是否运行
docker ps

# 查看错误日志
docker-compose logs backend
```

### 问题2:数据库连接失败

```bash
# 检查PostgreSQL状态
docker-compose ps postgres

# 重启数据库
docker-compose restart postgres
```

### 问题3:AI决策失败

```bash
# 检查DeepSeek API密钥
docker-compose exec backend printenv | grep DEEPSEEK

# 查看详细错误
docker-compose logs backend | grep "DeepSeek"
```

### 问题4:前端无法访问后端

检查CORS配置:

```bash
# 编辑 backend/app/core/config.py
# 确保 CORS_ORIGINS 包含 http://localhost:3000
```

---

## 📈 下一步

### 短期目标

1. **测试AI决策质量**
   - 观察多次AI决策结果
   - 评估决策合理性
   - 调整Prompt优化策略

2. **Testnet验证**
   - 在Testnet运行24-48小时
   - 记录所有决策和结果
   - 验证风控系统有效性

3. **性能优化**
   - 监控API响应时间
   - 优化数据库查询
   - 调整决策频率

### 长期目标

1. **扩展功能**
   - 添加更多交易品种
   - 实现WebSocket实时推送
   - 完善可视化图表

2. **策略优化**
   - 参考DeepSeek成功经验
   - 实现多策略切换
   - 回测历史数据

3. **生产部署**
   - VPS部署
   - 域名和SSL配置
   - 监控告警系统

---

## 📞 获取帮助

- **项目文档**: `docs/` 目录
- **API文档**: http://localhost:8000/docs
- **技术参考**: README_SETUP.md

---

## 🎉 完成状态

✅ **Phase 1-3已完成:**
- 基础架构 ✅
- 数据层开发 ✅
- AI决策引擎 ✅
- 交易执行系统 ✅
- Celery任务调度 ✅
- 前端界面 ✅

⏳ **Phase 4待验证:**
- Testnet验证
- 实盘运行
- 性能监控

---

**系统已就绪,开始您的量化交易之旅! 🚀💰**

```
                  🤖 AIcoin Trading System
                  Powered by DeepSeek AI
                  ────────────────────────
                  Status: ✅ Ready to Trade
```

