# ✅ AIcoin系统验证清单

## 🎯 快速验证步骤

按顺序执行以下步骤,验证系统是否正常运行:

---

## 步骤1: 配置检查 ✓

```bash
# 检查env.example文件存在
ls -la env.example

# 复制为.env
cp env.example .env

# 验证DeepSeek API密钥已配置
grep "DEEPSEEK_API_KEY=sk-4943" .env
```

**预期结果**: 看到API密钥配置

---

## 步骤2: Docker环境检查 ✓

```bash
# 检查Docker版本
docker --version
# 预期: Docker version 24.0+

# 检查Docker Compose
docker-compose --version
# 预期: Docker Compose version v2.0+

# 检查Docker正在运行
docker ps
# 预期: 显示当前运行的容器列表(可能为空)
```

**预期结果**: Docker环境正常

---

## 步骤3: 启动服务 ✓

```bash
# 进入项目目录
cd /Users/xinghailong/Documents/soft/AIcoin

# 启动所有Docker服务
docker-compose up -d

# 等待服务启动(约10秒)
sleep 10

# 检查所有服务状态
docker-compose ps
```

**预期结果**: 看到6个服务都是`Up`状态:
- aicoin-postgres (Up, healthy)
- aicoin-redis (Up, healthy)
- aicoin-backend (Up)
- aicoin-celery-worker (Up)
- aicoin-celery-beat (Up)
- aicoin-frontend (Up)

---

## 步骤4: 数据库初始化 ✓

```bash
# 方法1: 使用初始化脚本
docker-compose exec backend python scripts/init_db.py

# 方法2: 手动初始化
docker-compose exec backend python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"
```

**预期结果**: 
```
Initializing database...
✅ Database initialized successfully!
All tables created.
```

---

## 步骤5: 后端API验证 ✓

```bash
# 5.1 健康检查
curl http://localhost:8000/health
# 预期: {"status":"healthy","app":"AIcoin Trading System","version":"1.0.0"}

# 5.2 根端点
curl http://localhost:8000/
# 预期: {"app":"AIcoin Trading System","version":"1.0.0","status":"running","trading_enabled":false,"docs":"/docs"}

# 5.3 查看API文档
# 浏览器打开: http://localhost:8000/docs
# 预期: 看到Swagger UI界面
```

**预期结果**: 所有API端点响应正常

---

## 步骤6: AI决策测试 ✓

```bash
# 方法1: 使用测试脚本(推荐)
docker-compose exec backend python scripts/test_ai_decision.py

# 方法2: API调用
curl -X POST http://localhost:8000/api/v1/trading/decision \
  -H "Content-Type: application/json" \
  -d '{"symbol":"BTC-PERP","force":true}'
```

**预期结果**:
```
============================================================
AIcoin - Testing AI Decision Engine
============================================================

📊 Fetching market data for BTC-PERP...
✅ Current price: $67500

💰 Fetching account info...
✅ Balance: $10000

🤖 Making AI decision...

============================================================
AI DECISION RESULT
============================================================
Action:     BUY/SELL/HOLD
Size:       0.01-0.05
Confidence: 0.5-0.9
Reasoning:  (AI的决策理由)
Latency:    2000-3000ms
============================================================

✅ Test completed successfully!
```

---

## 步骤7: 前端界面验证 ✓

```bash
# 在浏览器中打开
open http://localhost:3000
```

**预期看到**:
1. ✅ AIcoin Trading System标题
2. ✅ API Status卡片(显示running)
3. ✅ System Info卡片
4. ✅ Quick Actions按钮
   - 📚 API Docs按钮可点击
   - 🤖 Test AI Decision按钮可测试
   - 💰 View Account按钮可查看

**测试前端功能**:
1. 点击"Test AI Decision" → 弹窗显示AI决策JSON
2. 点击"View Account" → 弹窗显示账户信息
3. 点击"API Docs" → 跳转到Swagger文档

---

## 步骤8: 数据库验证 ✓

```bash
# 进入PostgreSQL容器
docker-compose exec postgres psql -U admin -d aicoin

# 查看所有表
\dt

# 预期看到6张表:
# - trades
# - orders
# - ai_decisions
# - account_snapshots
# - market_data_kline
# - risk_events

# 退出
\q
```

**预期结果**: 所有表创建成功

---

## 步骤9: Redis验证 ✓

```bash
# 连接Redis
docker-compose exec redis redis-cli

# 测试连接
PING
# 预期: PONG

# 退出
exit
```

**预期结果**: Redis连接正常

---

## 步骤10: Celery任务验证 ✓

```bash
# 查看Celery Worker日志
docker-compose logs celery_worker | tail -20

# 查看Celery Beat日志
docker-compose logs celery_beat | tail -20
```

**预期看到**:
- Worker日志: `celery@... ready.`
- Beat日志: 定时任务调度信息

---

## 步骤11: 完整功能测试 ✓

### 11.1 查询交易记录
```bash
curl http://localhost:8000/api/v1/trading/trades?limit=10
```

### 11.2 查询市场数据
```bash
curl http://localhost:8000/api/v1/market/kline/BTC-PERP?interval=1h&limit=5
```

### 11.3 查询账户信息
```bash
curl http://localhost:8000/api/v1/account/info
```

### 11.4 查询性能指标
```bash
curl http://localhost:8000/api/v1/performance/metrics
```

**预期结果**: 所有API正常响应

---

## 步骤12: 日志查看 ✓

```bash
# 后端日志
docker-compose logs backend | tail -50

# Celery Worker日志
docker-compose logs celery_worker | tail -50

# 前端日志
docker-compose logs frontend | tail -20

# 实时查看后端日志
docker-compose logs -f backend
```

**预期看到**: 无ERROR级别日志,系统正常运行

---

## 🎉 验收标准

完成以上12个步骤后,系统应该满足:

- ✅ 所有6个Docker容器正常运行
- ✅ 数据库6张表创建成功
- ✅ 所有10个API端点响应正常
- ✅ AI决策功能完整可用
- ✅ 前端界面正常显示
- ✅ Celery定时任务正常调度
- ✅ 日志无ERROR级别错误

---

## 🐛 常见问题排查

### 问题1: Docker服务启动失败

```bash
# 查看具体错误
docker-compose logs [服务名]

# 重启服务
docker-compose restart [服务名]

# 完全重启
docker-compose down && docker-compose up -d
```

### 问题2: 端口被占用

```bash
# 检查端口占用
lsof -i :8000  # 后端
lsof -i :3000  # 前端
lsof -i :5432  # PostgreSQL
lsof -i :6379  # Redis

# 停止占用进程或修改docker-compose.yml中的端口映射
```

### 问题3: AI决策失败

```bash
# 检查API密钥
docker-compose exec backend printenv | grep DEEPSEEK

# 查看详细错误
docker-compose logs backend | grep -i "deepseek\|error"

# 测试DeepSeek API连通性
docker-compose exec backend python -c "
from openai import OpenAI
client = OpenAI(api_key='sk-494388a93f714088ba870436de7176d7', base_url='https://api.deepseek.com')
print('API Key Valid!')
"
```

### 问题4: 数据库连接失败

```bash
# 检查PostgreSQL状态
docker-compose ps postgres

# 查看PostgreSQL日志
docker-compose logs postgres

# 重启PostgreSQL
docker-compose restart postgres

# 等待健康检查通过
docker-compose ps postgres  # 应该显示(healthy)
```

---

## 📊 性能基准

首次运行时,正常的性能指标:

| 指标 | 预期值 | 说明 |
|------|--------|------|
| API响应时间 | < 200ms | /health端点 |
| AI决策延迟 | 2-5秒 | DeepSeek API调用 |
| 数据库查询 | < 50ms | 简单查询 |
| 前端加载时间 | < 2秒 | 首屏加载 |
| Docker内存占用 | ~1-2GB | 所有6个容器总和 |
| Docker CPU占用 | < 10% | 空闲状态 |

---

## ✅ 最终确认

如果所有12个步骤都通过,恭喜!您的AIcoin量化交易系统已成功运行!

**下一步建议**:
1. 阅读 `QUICKSTART.md` 了解更多功能
2. 测试多次AI决策,观察结果
3. 查看API文档,探索更多端点
4. 考虑启用Testnet进行长期验证

---

**验证完成时间**: _______  
**验证人**: _______  
**验证结果**: ✅ 通过 / ❌ 失败  
**备注**: _______

