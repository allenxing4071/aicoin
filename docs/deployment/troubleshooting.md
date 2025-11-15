# 🔍 AIcoin 故障排查指南

> **常见问题诊断与解决** | 快速定位 | 解决方案

---

## 📋 目录

1. [部署问题](#1-部署问题)
2. [服务问题](#2-服务问题)
3. [数据库问题](#3-数据库问题)
4. [交易问题](#4-交易问题)
5. [性能问题](#5-性能问题)

---

## 1. 部署问题

### 问题 1.1: Docker 容器启动失败

**症状**:
```bash
docker-compose ps
# 显示容器状态为 Exited 或 Restarting
```

**诊断**:
```bash
# 查看容器日志
docker-compose logs backend
docker-compose logs postgres

# 查看容器详情
docker inspect aicoin-backend-1
```

**常见原因与解决**:

#### 原因 1: 端口被占用
```bash
# 检查端口占用
lsof -i :8000
lsof -i :3000
lsof -i :5432

# 解决方案 A: 停止占用进程
kill -9 <PID>

# 解决方案 B: 修改端口
nano docker-compose.yml
# 修改 ports: "8001:8000"
```

#### 原因 2: 环境变量缺失
```bash
# 检查 .env 文件
cat .env | grep -E "DEEPSEEK|HYPERLIQUID|SECRET_KEY"

# 解决方案: 补全环境变量
cp .env.example .env
nano .env  # 填写必需变量
```

#### 原因 3: 磁盘空间不足
```bash
# 检查磁盘空间
df -h

# 解决方案: 清理空间
docker system prune -a --volumes -f
rm -rf /var/log/*.log
```

---

### 问题 1.2: Docker 镜像构建失败

**症状**:
```bash
ERROR [backend 5/10] RUN pip install -r requirements.txt
```

**解决方案**:
```bash
# 方案 1: 清理缓存重新构建
docker-compose build --no-cache

# 方案 2: 使用国内镜像源
# 编辑 backend/Dockerfile
RUN pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple

# 方案 3: 增加构建超时
DOCKER_BUILDKIT=1 docker-compose build --build-arg BUILDKIT_TIMEOUT=600
```

---

### 问题 1.3: 数据库迁移失败

**症状**:
```bash
alembic upgrade head
# ERROR: relation "users" already exists
```

**解决方案**:
```bash
# 方案 1: 重置数据库
docker-compose down -v
docker-compose up -d postgres
sleep 5
cd backend && alembic upgrade head

# 方案 2: 标记当前版本
cd backend && alembic stamp head

# 方案 3: 手动删除冲突表
docker-compose exec postgres psql -U aicoin aicoin -c "DROP TABLE IF EXISTS users CASCADE;"
cd backend && alembic upgrade head
```

---

## 2. 服务问题

### 问题 2.1: 后端 API 无响应

**症状**:
```bash
curl http://localhost:8000/health
# curl: (7) Failed to connect to localhost port 8000: Connection refused
```

**诊断步骤**:
```bash
# 1. 检查容器状态
docker-compose ps backend

# 2. 查看后端日志
docker-compose logs --tail=50 backend

# 3. 检查进程
docker-compose exec backend ps aux | grep uvicorn
```

**常见原因与解决**:

#### 原因 1: 容器未启动
```bash
# 启动容器
docker-compose up -d backend

# 如果反复重启
docker-compose logs backend | grep "ERROR"
# 根据错误信息修复
```

#### 原因 2: 数据库连接失败
```bash
# 检查数据库
docker-compose exec postgres pg_isready -U aicoin

# 检查连接字符串
docker-compose exec backend env | grep DATABASE_URL

# 修复连接
nano .env
# DATABASE_URL=postgresql://aicoin:password@postgres:5432/aicoin
docker-compose restart backend
```

#### 原因 3: 依赖包缺失
```bash
# 重新安装依赖
docker-compose exec backend pip install -r requirements.txt

# 或重新构建
docker-compose up -d --build backend
```

---

### 问题 2.2: 前端页面无法访问

**症状**:
```bash
curl http://localhost:3000
# 无响应或 502 Bad Gateway
```

**解决方案**:
```bash
# 1. 检查前端容器
docker-compose ps frontend

# 2. 查看前端日志
docker-compose logs frontend

# 3. 检查后端连接
# 编辑 frontend/.env.local
NEXT_PUBLIC_API_URL=http://localhost:8000

# 4. 重启前端
docker-compose restart frontend

# 5. 清理缓存重新构建
docker-compose stop frontend
docker-compose rm -f frontend
docker-compose up -d --build frontend
```

---

### 问题 2.3: Redis 连接失败

**症状**:
```bash
docker-compose logs backend | grep "Redis"
# ERROR: Error connecting to Redis: Connection refused
```

**解决方案**:
```bash
# 1. 检查 Redis 容器
docker-compose ps redis

# 2. 测试 Redis 连接
docker-compose exec redis redis-cli ping
# 预期输出: PONG

# 3. 检查 Redis URL
docker-compose exec backend env | grep REDIS_URL

# 4. 重启 Redis
docker-compose restart redis

# 5. 如果数据损坏
docker-compose stop redis
docker volume rm aicoin_redis_data
docker-compose up -d redis
```

---

## 3. 数据库问题

### 问题 3.1: 数据库连接池耗尽

**症状**:
```bash
# 日志显示
FATAL: remaining connection slots are reserved for non-replication superuser connections
```

**解决方案**:
```bash
# 1. 查看当前连接数
docker-compose exec postgres psql -U aicoin -c "
SELECT count(*) FROM pg_stat_activity;
"

# 2. 杀死空闲连接
docker-compose exec postgres psql -U aicoin -c "
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'idle' 
AND state_change < NOW() - INTERVAL '5 minutes';
"

# 3. 增加最大连接数
# 编辑 docker-compose.yml
postgres:
  command: postgres -c max_connections=200

# 4. 重启数据库
docker-compose restart postgres
```

---

### 问题 3.2: 数据库性能慢

**症状**:
```bash
# API 响应慢，日志显示查询耗时长
```

**诊断**:
```bash
# 查看慢查询
docker-compose exec postgres psql -U aicoin aicoin -c "
SELECT query, calls, total_time, mean_time
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
"

# 查看表大小
docker-compose exec postgres psql -U aicoin aicoin -c "
SELECT schemaname, tablename, 
       pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
"
```

**解决方案**:
```bash
# 1. 重建索引
docker-compose exec postgres psql -U aicoin aicoin -c "REINDEX DATABASE aicoin;"

# 2. 更新统计信息
docker-compose exec postgres psql -U aicoin aicoin -c "ANALYZE;"

# 3. 清理旧数据
docker-compose exec postgres psql -U aicoin aicoin -c "
DELETE FROM decision_history WHERE created_at < NOW() - INTERVAL '30 days';
VACUUM FULL;
"

# 4. 增加内存配置
# 编辑 docker-compose.yml
postgres:
  command: postgres -c shared_buffers=256MB -c effective_cache_size=1GB
```

---

## 4. 交易问题

### 问题 4.1: AI 不执行交易

**症状**:
```bash
# 日志显示决策但不交易
docker-compose logs backend | grep "决策"
# 有决策记录但无交易记录
```

**诊断**:
```bash
# 1. 检查交易开关
curl http://localhost:8000/api/v1/admin/trading/status

# 2. 检查权限等级
curl http://localhost:8000/api/v1/permissions/current

# 3. 检查风控状态
curl http://localhost:8000/api/v1/admin/risk/status

# 4. 查看拒绝原因
docker-compose logs backend | grep "拒绝"
```

**常见原因与解决**:

#### 原因 1: 交易未启用
```bash
# 启用交易
curl -X POST http://localhost:8000/api/v1/admin/trading/enable

# 或修改环境变量
echo "ENABLE_TRADING=true" >> .env
docker-compose restart backend
```

#### 原因 2: 权限等级过低 (L0)
```bash
# 查看当前等级
curl http://localhost:8000/api/v1/permissions/current

# 手动升级到 L1
curl -X POST http://localhost:8000/api/v1/admin/permissions/upgrade-to/L1
```

#### 原因 3: 置信度不足
```bash
# 查看决策日志
docker-compose logs backend | grep "置信度"

# 降低置信度门槛 (谨慎)
curl -X PUT http://localhost:8000/api/v1/admin/permissions/levels/L1 \
  -H "Content-Type: application/json" \
  -d '{"trading_params": {"confidence_threshold": 0.70}}'
```

#### 原因 4: 达到交易频率限制
```bash
# 查看今日交易次数
curl http://localhost:8000/api/v1/trades/today/count

# 增加频率限制
curl -X PUT http://localhost:8000/api/v1/admin/permissions/levels/L1 \
  -H "Content-Type: application/json" \
  -d '{"trading_params": {"max_daily_trades": 5}}'
```

---

### 问题 4.2: 交易执行失败

**症状**:
```bash
# 日志显示交易失败
ERROR: Failed to execute trade: Insufficient balance
```

**解决方案**:
```bash
# 1. 检查账户余额
curl http://localhost:8000/api/v1/account/balance

# 2. 检查 Hyperliquid 连接
curl http://localhost:8000/api/v1/admin/exchange/test-connection

# 3. 检查 API 密钥
docker-compose exec backend env | grep HYPERLIQUID

# 4. 查看详细错误
docker-compose logs backend | grep "Hyperliquid" | tail -20
```

---

### 问题 4.3: AI 决策异常

**症状**:
```bash
# AI 返回无效决策或错误
ERROR: DeepSeek API error: Invalid response
```

**解决方案**:
```bash
# 1. 检查 API Key
docker-compose exec backend env | grep DEEPSEEK_API_KEY

# 2. 测试 API 连接
curl -X POST http://localhost:8000/api/v1/admin/ai/test-connection

# 3. 查看 API 配额
# 访问 https://platform.deepseek.com 查看余额

# 4. 检查 Prompt 模板
curl http://localhost:8000/api/v1/admin/prompts/current

# 5. 重启后端
docker-compose restart backend
```

---

## 5. 性能问题

### 问题 5.1: 系统响应慢

**诊断**:
```bash
# 1. 检查系统资源
docker stats --no-stream

# 2. 检查 CPU 使用
top -b -n 1 | head -20

# 3. 检查内存使用
free -h

# 4. 检查磁盘 I/O
iostat -x 1 5
```

**解决方案**:
```bash
# 1. 增加 Docker 资源限制
# 编辑 docker-compose.yml
backend:
  deploy:
    resources:
      limits:
        cpus: '2'
        memory: 2G

# 2. 启用 Redis 缓存
echo "ENABLE_CACHE=true" >> .env
docker-compose restart backend

# 3. 优化数据库查询
# 参考 "数据库问题" 章节

# 4. 升级服务器配置
# CPU: 2核 → 4核
# 内存: 4GB → 8GB
```

---

### 问题 5.2: 内存泄漏

**症状**:
```bash
# 容器内存持续增长
docker stats
# 内存使用率 > 80%
```

**解决方案**:
```bash
# 1. 重启容器 (临时)
docker-compose restart backend

# 2. 检查内存泄漏
docker-compose exec backend pip install memory_profiler
docker-compose exec backend python -m memory_profiler app/main.py

# 3. 限制内存使用
# 编辑 docker-compose.yml
backend:
  deploy:
    resources:
      limits:
        memory: 1G
      reservations:
        memory: 512M

# 4. 定期重启 (Cron)
0 3 * * * cd /root/AIcoin && docker-compose restart backend
```

---

## 📊 故障排查流程图

```
问题发生
    ↓
检查服务状态 (docker-compose ps)
    ↓
    ├─ 容器未运行 → 查看日志 (docker-compose logs)
    │                    ↓
    │              根据错误信息修复
    │
    ├─ 容器运行中 → 检查健康状态 (curl /health)
    │                    ↓
    │              ├─ 数据库问题 → 检查 PostgreSQL
    │              ├─ Redis 问题 → 检查 Redis
    │              └─ API 问题 → 检查后端日志
    │
    └─ 性能问题 → 检查资源使用 (docker stats)
                       ↓
                 优化配置或升级资源
```

---

## 🆘 紧急联系

如果以上方法都无法解决问题：

1. **收集诊断信息**:
```bash
# 生成诊断报告
./scripts/generate-diagnostic-report.sh > diagnostic_$(date +%Y%m%d_%H%M%S).txt
```

2. **提交 Issue**:
   - GitHub: https://github.com/allenxing4071/aicoin/issues
   - 附上诊断报告和错误日志

3. **联系技术支持**:
   - 提供详细的错误信息
   - 说明复现步骤
   - 附上系统环境信息

---

## 📚 相关文档

- [快速部署](./quick-deploy.md) - 部署指南
- [配置指南](./configuration.md) - 配置说明
- [运维操作](./operations.md) - 日常运维

---

**文档维护**: AIcoin Team  
**最后更新**: 2025-11-15  
**文档版本**: v2.0

