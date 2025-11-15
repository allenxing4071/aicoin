# 🔧 AIcoin 运维操作手册

> **日常运维指南** | 监控 | 备份 | 日志 | 版本管理

---

## 📋 目录

1. [日常监控](#1-日常监控)
2. [数据备份与恢复](#2-数据备份与恢复)
3. [日志管理](#3-日志管理)
4. [版本管理](#4-版本管理)
5. [性能优化](#5-性能优化)

---

## 1. 日常监控

### 1.1 服务状态检查

```bash
# 检查所有服务
docker-compose ps

# 检查特定服务
docker-compose ps backend
docker-compose ps postgres

# 查看资源使用
docker stats --no-stream

# 预期输出:
# CONTAINER           CPU %     MEM USAGE / LIMIT     MEM %
# aicoin-backend-1    5.23%     512MiB / 8GiB        6.25%
# aicoin-postgres-1   1.45%     256MiB / 8GiB        3.13%
```

### 1.2 健康检查

```bash
# 后端健康检查
curl http://localhost:8000/health

# 预期输出:
# {
#   "status": "healthy",
#   "version": "4.1.0",
#   "ai_orchestrator": true,
#   "database": "connected",
#   "redis": "connected",
#   "qdrant": "connected"
# }

# 前端检查
curl http://localhost:3000

# 数据库检查
docker-compose exec postgres pg_isready -U aicoin
```

### 1.3 交易监控

```bash
# 查看今日交易
curl http://localhost:8000/api/v1/trades/today

# 查看当前仓位
curl http://localhost:8000/api/v1/positions/current

# 查看账户余额
curl http://localhost:8000/api/v1/account/balance

# 查看权限等级
curl http://localhost:8000/api/v1/permissions/current
```

### 1.4 AI 性能监控

```bash
# 查看 AI 调用统计
curl http://localhost:8000/api/v1/admin/ai/usage-stats

# 查看决策历史
curl http://localhost:8000/api/v1/decisions/recent?limit=10

# 查看成功率
curl http://localhost:8000/api/v1/admin/ai/success-rate
```

---

## 2. 数据备份与恢复

### 2.1 数据库备份

#### 手动备份
```bash
# 完整备份
docker-compose exec postgres pg_dump -U aicoin aicoin > backup_$(date +%Y%m%d_%H%M%S).sql

# 压缩备份
docker-compose exec postgres pg_dump -U aicoin aicoin | gzip > backup_$(date +%Y%m%d_%H%M%S).sql.gz

# 仅备份数据 (不含结构)
docker-compose exec postgres pg_dump -U aicoin --data-only aicoin > data_backup.sql

# 仅备份结构 (不含数据)
docker-compose exec postgres pg_dump -U aicoin --schema-only aicoin > schema_backup.sql
```

#### 自动备份 (Cron)
```bash
# 编辑 crontab
crontab -e

# 添加每日备份任务 (凌晨 2 点)
0 2 * * * cd /root/AIcoin && docker-compose exec -T postgres pg_dump -U aicoin aicoin | gzip > /root/backups/aicoin_$(date +\%Y\%m\%d).sql.gz

# 添加每周完整备份 (周日凌晨 3 点)
0 3 * * 0 cd /root/AIcoin && docker-compose exec -T postgres pg_dump -U aicoin aicoin > /root/backups/aicoin_weekly_$(date +\%Y\%m\%d).sql

# 清理 30 天前的备份
0 4 * * * find /root/backups -name "aicoin_*.sql*" -mtime +30 -delete
```

### 2.2 数据库恢复

```bash
# 从备份恢复
docker-compose exec -T postgres psql -U aicoin aicoin < backup.sql

# 从压缩备份恢复
gunzip < backup.sql.gz | docker-compose exec -T postgres psql -U aicoin aicoin

# 恢复前先删除现有数据库
docker-compose exec postgres psql -U aicoin -c "DROP DATABASE IF EXISTS aicoin;"
docker-compose exec postgres psql -U aicoin -c "CREATE DATABASE aicoin;"
docker-compose exec -T postgres psql -U aicoin aicoin < backup.sql
```

### 2.3 数据清理

```bash
# 清理 30 天前的决策记录
docker-compose exec postgres psql -U aicoin aicoin -c "
DELETE FROM decision_history 
WHERE created_at < NOW() - INTERVAL '30 days';
"

# 清理旧的 AI 使用日志
docker-compose exec postgres psql -U aicoin aicoin -c "
DELETE FROM ai_model_usage_log 
WHERE timestamp < NOW() - INTERVAL '90 days';
"

# 清理已关闭的仓位 (保留 90 天)
docker-compose exec postgres psql -U aicoin aicoin -c "
DELETE FROM positions 
WHERE status = 'closed' 
AND closed_at < NOW() - INTERVAL '90 days';
"

# 真空清理 (回收空间)
docker-compose exec postgres psql -U aicoin aicoin -c "VACUUM FULL;"
```

### 2.4 Redis 备份

```bash
# 手动保存快照
docker-compose exec redis redis-cli SAVE

# 导出 RDB 文件
docker cp aicoin-redis-1:/data/dump.rdb ./redis_backup_$(date +%Y%m%d).rdb

# 恢复 Redis 数据
docker cp redis_backup.rdb aicoin-redis-1:/data/dump.rdb
docker-compose restart redis
```

---

## 3. 日志管理

### 3.1 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f postgres

# 查看最近 100 行
docker-compose logs --tail=100 backend

# 查看特定时间范围
docker-compose logs --since 2025-11-15T10:00:00 backend
docker-compose logs --until 2025-11-15T12:00:00 backend

# 搜索关键词
docker-compose logs backend | grep "ERROR"
docker-compose logs backend | grep "决策"
docker-compose logs backend | grep "交易"
```

### 3.2 日志文件位置

```bash
# 后端日志
tail -f backend/logs/aicoin.log
tail -f backend/logs/error.log

# 前端日志
tail -f frontend/.next/server.log

# Nginx 日志 (如果使用)
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### 3.3 日志分析

```bash
# 统计错误数量
docker-compose logs backend | grep "ERROR" | wc -l

# 统计今日交易次数
docker-compose logs backend | grep "执行交易" | grep $(date +%Y-%m-%d) | wc -l

# 查看 AI 决策日志
docker-compose logs backend | grep "AI决策"

# 查看风控触发日志
docker-compose logs backend | grep "风控"
```

### 3.4 日志清理

```bash
# 手动清理日志
rm -f backend/logs/*.log
docker-compose restart backend

# 清理 Docker 日志
docker-compose down
rm -rf /var/lib/docker/containers/*/*-json.log
docker-compose up -d

# 配置日志轮转 (logrotate)
sudo nano /etc/logrotate.d/aicoin

# 添加配置:
/root/AIcoin/backend/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0644 root root
    sharedscripts
    postrotate
        docker-compose -f /root/AIcoin/docker-compose.yml restart backend
    endscript
}
```

---

## 4. 版本管理

### 4.1 查看当前版本

```bash
# 查看系统版本
cat VERSION

# 查看 Git 版本
git log -1 --oneline

# 查看后端版本
curl http://localhost:8000/health | jq '.version'

# 查看前端版本
curl http://localhost:3000/api/version
```

### 4.2 版本更新

```bash
# 方式一: Git 自动化部署
./scripts/deploy-git.sh

# 方式二: 手动更新
git pull origin main
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 方式三: 快速更新 (不重新构建)
git pull origin main
docker-compose restart
```

### 4.3 版本回滚

```bash
# 查看可回滚版本
git log --oneline -10

# 回滚到指定版本
./scripts/deploy-git-rollback.sh <commit-hash>

# 或手动回滚
git reset --hard <commit-hash>
docker-compose down
docker-compose up -d --build
```

### 4.4 版本发布流程

```bash
# 1. 更新版本号
echo "4.2.0" > VERSION

# 2. 更新 CHANGELOG
nano CHANGELOG.md

# 3. 提交变更
git add VERSION CHANGELOG.md
git commit -m "chore: bump version to 4.2.0"

# 4. 创建标签
git tag -a v4.2.0 -m "Release v4.2.0"

# 5. 推送到远程
git push origin main
git push origin v4.2.0

# 6. 部署到生产
./scripts/deploy-git.sh
```

---

## 5. 性能优化

### 5.1 数据库优化

```bash
# 分析查询性能
docker-compose exec postgres psql -U aicoin aicoin -c "
EXPLAIN ANALYZE 
SELECT * FROM trades 
WHERE created_at > NOW() - INTERVAL '7 days';
"

# 重建索引
docker-compose exec postgres psql -U aicoin aicoin -c "
REINDEX DATABASE aicoin;
"

# 更新统计信息
docker-compose exec postgres psql -U aicoin aicoin -c "
ANALYZE;
"

# 查看慢查询
docker-compose exec postgres psql -U aicoin aicoin -c "
SELECT query, calls, total_time, mean_time 
FROM pg_stat_statements 
ORDER BY mean_time DESC 
LIMIT 10;
"
```

### 5.2 Redis 优化

```bash
# 查看 Redis 信息
docker-compose exec redis redis-cli INFO

# 查看内存使用
docker-compose exec redis redis-cli INFO memory

# 查看键数量
docker-compose exec redis redis-cli DBSIZE

# 清理过期键
docker-compose exec redis redis-cli --scan --pattern "*" | xargs docker-compose exec redis redis-cli DEL
```

### 5.3 Docker 优化

```bash
# 清理未使用的镜像
docker image prune -a -f

# 清理未使用的容器
docker container prune -f

# 清理未使用的卷
docker volume prune -f

# 完整清理
docker system prune -a --volumes -f

# 查看磁盘使用
docker system df
```

### 5.4 系统资源监控

```bash
# CPU 使用率
top -b -n 1 | head -20

# 内存使用
free -h

# 磁盘使用
df -h

# 网络连接
netstat -tulnp | grep -E "8000|3000|5432|6379"

# 进程监控
ps aux | grep -E "python|node|postgres|redis"
```

---

## 📊 运维检查清单

### 每日检查
- [ ] 服务状态正常
- [ ] 健康检查通过
- [ ] 无严重错误日志
- [ ] 交易执行正常
- [ ] 账户余额正常

### 每周检查
- [ ] 数据库备份成功
- [ ] 磁盘空间充足
- [ ] 日志文件大小正常
- [ ] 性能指标正常
- [ ] 版本是否需要更新

### 每月检查
- [ ] 清理旧数据
- [ ] 优化数据库索引
- [ ] 审查安全日志
- [ ] 更新依赖包
- [ ] 性能压测

---

## 🆘 紧急操作

### 紧急停止交易
```bash
# 方式一: 环境变量
docker-compose exec backend sh -c "echo 'ENABLE_TRADING=false' >> .env"
docker-compose restart backend

# 方式二: API
curl -X POST http://localhost:8000/api/v1/admin/trading/disable

# 方式三: 停止服务
docker-compose stop backend
```

### 紧急平仓
```bash
# 平掉所有仓位
curl -X POST http://localhost:8000/api/v1/admin/positions/close-all
```

### 紧急回滚
```bash
# 回滚到上一个版本
./scripts/deploy-git-rollback.sh HEAD~1

# 恢复数据库
gunzip < backup_latest.sql.gz | docker-compose exec -T postgres psql -U aicoin aicoin
```

---

## 📚 相关文档

- [快速部署](./quick-deploy.md) - 部署指南
- [配置指南](./configuration.md) - 配置说明
- [故障排查](./troubleshooting.md) - 问题诊断

---

**文档维护**: AIcoin Team  
**最后更新**: 2025-11-15  
**文档版本**: v2.0

