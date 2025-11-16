# 🚨 紧急：504 超时问题 - 立即修复指南

**生产环境**: jifenpay.cc  
**问题时间**: 2025-11-16  
**影响**: 多个管理后台 API 无法访问

---

## ⚡ 立即执行（5分钟内）

### 步骤 1: SSH 登录生产服务器

```bash
# 使用你的 SSH 密钥登录
ssh -i /path/to/your/key.pem user@your-server-ip
```

### 步骤 2: 快速检查服务状态

```bash
# 进入项目目录
cd /path/to/AIcoin

# 查看容器状态
docker ps | grep aicoin
```

**检查点**:
- ✅ 所有容器都应该显示 "Up"
- ❌ 如果 aicoin-backend 显示 "Restarting" 或不存在 → **执行步骤 3**

### 步骤 3: 查看后端日志（关键！）

```bash
# 查看最近 100 行日志
docker logs aicoin-backend --tail 100

# 或者实时查看
docker logs aicoin-backend -f
```

**常见错误模式**:

1. **数据库连接错误**
   ```
   sqlalchemy.exc.OperationalError: could not connect to server
   ```
   → 执行【解决方案 A】

2. **内存不足**
   ```
   MemoryError / Killed
   ```
   → 执行【解决方案 B】

3. **代码异常**
   ```
   Exception / Traceback
   ```
   → 执行【解决方案 C】

---

## 🔧 解决方案

### 【解决方案 A】数据库连接问题

```bash
# 1. 检查数据库是否运行
docker ps | grep postgres

# 2. 测试数据库连接
docker exec aicoin-postgres pg_isready -U aicoin

# 3. 如果失败，重启数据库
docker-compose restart postgres

# 4. 等待 10 秒后重启后端
sleep 10
docker-compose restart backend

# 5. 验证（应该在 1 秒内响应）
curl -I http://localhost:8000/api/v1/status
```

### 【解决方案 B】资源不足问题

```bash
# 1. 检查内存
free -h

# 2. 检查磁盘
df -h

# 3. 如果磁盘满了，清理 Docker
docker system prune -a --volumes -f

# 4. 清理日志文件
cd /path/to/AIcoin
find ./logs -name "*.log.*" -mtime +7 -delete
find ./deploy/logs -name "*.log.*" -mtime +7 -delete

# 5. 重启服务
docker-compose restart backend
```

### 【解决方案 C】代码异常（通用重启）

```bash
# 完整重启（推荐）
cd /path/to/AIcoin
docker-compose down
docker-compose up -d

# 等待服务启动（约 30 秒）
sleep 30

# 验证
curl http://localhost:8000/api/v1/status
```

---

## ✅ 验证修复

在浏览器中测试以下页面：

1. **后端健康检查**
   - 直接访问: `https://jifenpay.cc/api/v1/status`
   - 预期: 返回 JSON，包含系统状态

2. **管理后台登录**
   - 访问: `https://jifenpay.cc/admin`
   - 登录后检查是否能正常加载

3. **情报平台接口**
   - 打开浏览器开发者工具 (F12)
   - 访问: `https://jifenpay.cc/admin`
   - 查看 Network 标签，确认没有 504 错误

---

## 🔍 深度诊断（如果快速修复无效）

### 使用自动化诊断脚本

```bash
cd /path/to/AIcoin

# 拉取最新代码（包含诊断工具）
git pull origin main

# 运行诊断
./scripts/diagnose_504.sh
```

脚本会自动检查并生成报告。

### 手动深度检查

#### 1. 检查数据库连接池

```bash
docker exec aicoin-postgres psql -U aicoin -d aicoin -c "
  SELECT 
    count(*) FILTER (WHERE state = 'active') AS active,
    count(*) FILTER (WHERE state = 'idle') AS idle,
    count(*) AS total
  FROM pg_stat_activity 
  WHERE datname = 'aicoin';
"
```

**正常情况**: 
- active: 0-10
- idle: 5-20
- **异常**: active > 50 或 total > 100

**解决**: 
```bash
# 杀掉闲置连接
docker exec aicoin-postgres psql -U aicoin -d aicoin -c "
  SELECT pg_terminate_backend(pid) 
  FROM pg_stat_activity 
  WHERE state = 'idle' 
  AND state_change < now() - interval '5 minutes';
"
```

#### 2. 检查慢查询

```bash
# 查看当前正在执行的慢查询
docker exec aicoin-postgres psql -U aicoin -d aicoin -c "
  SELECT 
    pid,
    now() - query_start AS duration,
    query
  FROM pg_stat_activity
  WHERE state = 'active'
  AND now() - query_start > interval '5 seconds'
  ORDER BY duration DESC;
"
```

**如果发现慢查询**: 记录下来，稍后优化。现在先杀掉：

```bash
# 替换 <PID> 为实际的进程ID
docker exec aicoin-postgres psql -U aicoin -d aicoin -c "
  SELECT pg_terminate_backend(<PID>);
"
```

#### 3. 检查 Nginx 上游状态

```bash
# 查看 Nginx 错误日志
tail -50 /path/to/AIcoin/deploy/logs/error.log

# 测试 Nginx 到后端的连接
docker exec aicoin-nginx wget -O- --timeout=5 http://backend:8000/api/v1/status
```

---

## 🎯 临时扩容方案（如果需要）

### 增加超时时间（临时）

```bash
# 编辑 Nginx 配置
vim /path/to/AIcoin/deploy/nginx/nginx.conf

# 找到 location /api/ 块，修改超时时间
location /api/ {
    proxy_pass http://backend;
    
    # 临时增加到 180 秒
    proxy_connect_timeout 180s;
    proxy_send_timeout 180s;
    proxy_read_timeout 180s;
    
    # ... 其他配置保持不变
}

# 重新加载 Nginx
docker exec aicoin-nginx nginx -s reload
```

### 增加后端资源（如果可能）

编辑 `docker-compose.yml`:

```yaml
backend:
  # ... 其他配置
  deploy:
    resources:
      limits:
        cpus: '2.0'      # 增加到 2 核
        memory: 4G       # 增加到 4GB
```

然后重启：

```bash
docker-compose up -d --force-recreate backend
```

---

## 📊 实时监控

### 终端 1: 后端日志

```bash
docker logs aicoin-backend -f --tail 100
```

### 终端 2: Nginx 访问日志

```bash
tail -f /path/to/AIcoin/deploy/logs/access.log | grep 504
```

### 终端 3: 系统资源

```bash
watch -n 2 'docker stats --no-stream aicoin-backend'
```

---

## 📝 修复后记录

修复完成后，请填写：

```markdown
## 问题记录

**修复时间**: _________
**采用方案**: A / B / C / 其他
**根本原因**: _________
**是否需要后续优化**: 是 / 否

如需后续优化：
- [ ] 优化慢查询
- [ ] 添加数据库索引
- [ ] 增加服务器资源
- [ ] 添加缓存层
- [ ] 代码重构

**备注**: _________
```

---

## 📞 紧急联系

如果以上方案都无效：

1. **检查服务器负载**
   ```bash
   top -bn1 | head -20
   iostat -x 2 10
   ```

2. **保存现场日志**
   ```bash
   docker logs aicoin-backend > /tmp/backend-$(date +%s).log
   docker logs aicoin-postgres > /tmp/postgres-$(date +%s).log
   ```

3. **联系运维人员**
   - 提供日志文件
   - 说明已执行的步骤
   - 描述当前状态

---

**最后提醒**: 
- ⚠️ 生产环境操作请谨慎
- ⚠️ 重启前确认是否有正在执行的交易
- ⚠️ 必要时通知用户系统维护

**详细文档**: `docs/03-开发文档/504超时问题诊断.md`

