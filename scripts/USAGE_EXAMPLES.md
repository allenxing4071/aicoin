# 📚 部署脚本实战示例

## 🎬 场景 1：修复前端 Bug

### 背景
前端页面有个按钮位置不对，需要快速修复并部署。

### 操作步骤

```bash
# 1. 修改代码
vim frontend/app/admin/layout.tsx

# 2. 快速部署（使用 rsync）
cd /Users/xinghailong/Documents/soft/AIcoin
./scripts/deploy-rsync.sh

# 3. 等待 3-5 分钟（构建镜像）
# 4. 浏览器测试：https://jifenpay.cc/admin

# 5. 如果没问题，提交代码
git add .
git commit -m "fix: 修复后台菜单按钮位置"
git push origin main
```

### 时间成本
- 修改代码：2 分钟
- rsync 传输：5 秒
- 构建镜像：3 分钟
- 测试验证：1 分钟
- **总计：~6 分钟**

### 关键优势
✅ 无需 git commit 就能快速验证  
✅ 如果有问题可以继续修改  
✅ 确认无误后再提交代码  

---

## 🎬 场景 2：添加新功能（后端 API）

### 背景
需要添加一个新的 API 端点，完整开发流程。

### 操作步骤

```bash
# 1. 创建新分支
git checkout -b feature/new-api

# 2. 开发阶段（多次迭代）
vim backend/app/api/v1/admin_new.py
./scripts/deploy-rsync.sh  # 第1次部署测试
# ... 发现问题 ...

vim backend/app/api/v1/admin_new.py
./scripts/deploy-rsync.sh  # 第2次部署测试
# ... 继续调试 ...

vim backend/app/api/v1/admin_new.py
./scripts/deploy-rsync.sh  # 第3次部署测试
# ✅ 功能完成

# 3. 功能完成后提交
git add .
git commit -m "feat: 添加新 API 端点"
git checkout main
git merge feature/new-api

# 4. 正式部署（使用 Git）
./scripts/deploy-git.sh

# 5. 打标签
git tag -a v3.3.1 -m "Release: 添加新 API"
git push origin main --tags
```

### 时间对比

| 方式 | 单次部署 | 3次迭代 | 总时间 |
|------|---------|---------|--------|
| **rsync** | 5秒 | 15秒 | ~20分钟 |
| **Git** | 15秒 | 45秒 | ~30分钟 |

**节省时间：10 分钟**

---

## 🎬 场景 3：修改环境变量

### 背景
需要调整 AI 决策间隔时间，只需修改 `.env` 文件。

### 操作步骤

```bash
# 1. 本地修改
vim .env
# 修改：AI_DECISION_INTERVAL=300

# 2. 同步到服务器
rsync -avz \
    -e "ssh -i ssh-configs/cloud-servers/AIcoin.pem" \
    .env root@47.250.132.166:/root/AIcoin/

# 3. 快速重启（不重新构建）
./scripts/deploy-quick.sh

# 4. 验证（3秒后生效）
curl https://jifenpay.cc/api/v1/dashboard/summary
```

### 时间成本
- 修改文件：30 秒
- 同步文件：2 秒
- 重启服务：3 秒
- **总计：~35 秒**

---

## 🎬 场景 4：紧急回滚

### 背景
新版本部署后发现严重 Bug，需要立即回滚。

### 操作步骤

```bash
# 1. SSH 到服务器
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166

# 2. 查看版本历史
cd /root/AIcoin
git log --oneline
# 输出：
# abc1234 (HEAD -> main) feat: 新功能（有 Bug）
# def5678 (tag: v3.3.0) fix: 上一个稳定版本

# 3. 回滚到上一个 tag
git checkout v3.3.0

# 4. 重新构建
docker compose down
docker compose build --no-cache
docker compose up -d

# 5. 验证
docker compose ps
curl http://localhost:8000/api/v1/health
```

### 时间成本
- 回滚代码：10 秒
- 重新构建：3 分钟
- **总计：~3 分钟**

### 关键提示
⚠️ 这就是为什么正式发布必须用 Git + Tag！

---

## 🎬 场景 5：多文件修改

### 背景
同时修改了前端和后端多个文件。

### 操作步骤

```bash
# 1. 批量修改
vim frontend/app/admin/users/page.tsx
vim frontend/app/admin/layout.tsx
vim backend/app/api/v1/admin_users.py
vim backend/app/core/permissions.py

# 2. 查看修改
git status
# 输出：
# modified:   frontend/app/admin/users/page.tsx
# modified:   frontend/app/admin/layout.tsx
# modified:   backend/app/api/v1/admin_users.py
# modified:   backend/app/core/permissions.py

# 3. 快速部署（rsync 自动传输所有修改）
./scripts/deploy-rsync.sh

# 4. 测试验证
# ...

# 5. 确认无误后提交
git add .
git commit -m "feat: 完善用户权限管理功能"
git push origin main
```

### rsync 优势
✅ 自动识别所有修改的文件  
✅ 只传输修改的部分（增量传输）  
✅ 无需手动指定文件列表  

---

## 🎬 场景 6：前后端独立部署

### 背景
只修改了前端，不想重新构建后端。

### 方式 A：使用 rsync（推荐）

```bash
# 修改前端
vim frontend/app/page.tsx

# rsync 会智能同步（只传输前端文件）
./scripts/deploy-rsync.sh
# 内部会重新构建前后端（保险起见）
```

### 方式 B：手动选择构建

```bash
# SSH 到服务器
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166

cd /root/AIcoin

# 只构建前端
docker compose build frontend --no-cache
docker compose up -d frontend

# 只构建后端
docker compose build backend --no-cache
docker compose up -d backend
```

---

## 🎬 场景 7：定时部署（自动化）

### 背景
希望每天凌晨自动部署最新代码。

### 创建定时任务

```bash
# 在服务器上设置 cron
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166

# 编辑 crontab
crontab -e

# 添加以下内容（每天凌晨 2 点）
0 2 * * * cd /root/AIcoin && git pull origin main && docker compose build --no-cache && docker compose up -d >> /var/log/aicoin-deploy.log 2>&1
```

---

## 🎬 场景 8：多服务器部署

### 背景
有开发、测试、生产三个环境。

### 方式 A：修改脚本配置

```bash
# 复制脚本
cp scripts/deploy-rsync.sh scripts/deploy-rsync-dev.sh
cp scripts/deploy-rsync.sh scripts/deploy-rsync-test.sh
cp scripts/deploy-rsync.sh scripts/deploy-rsync-prod.sh

# 修改每个脚本的服务器地址
# deploy-rsync-dev.sh
SERVER_HOST="dev.example.com"

# deploy-rsync-test.sh
SERVER_HOST="test.example.com"

# deploy-rsync-prod.sh
SERVER_HOST="prod.example.com"
```

### 方式 B：使用参数

```bash
# 修改脚本支持参数
./scripts/deploy-rsync.sh dev
./scripts/deploy-rsync.sh test
./scripts/deploy-rsync.sh prod
```

---

## 🎬 场景 9：检查部署状态

### 实时监控

```bash
# 方式 A：使用检查脚本
./scripts/check-deployment.sh

# 方式 B：手动检查
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166

# 查看容器状态
docker compose ps

# 查看实时日志
docker compose logs -f backend
docker compose logs -f frontend

# 查看最近 50 条日志
docker compose logs --tail=50 backend
```

---

## 🎬 场景 10：清理旧数据

### 背景
服务器磁盘空间不足，需要清理。

### 操作步骤

```bash
# SSH 到服务器
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166

# 1. 查看磁盘使用
df -h

# 2. 清理 Docker
docker system prune -a  # 清理所有未使用的镜像
docker volume prune     # 清理未使用的卷

# 3. 清理日志
cd /root/AIcoin
find logs/ -name "*.log" -mtime +7 -delete  # 删除 7 天前的日志

# 4. 清理备份
cd backups/
ls -lht  # 查看备份文件
rm aicoin_backup_2024-*.sql.gz  # 删除旧备份
```

---

## 📊 性能数据对比

### 场景：修改 1 个文件并部署

| 方式 | 传输时间 | 构建时间 | 重启时间 | 总时间 |
|------|---------|---------|---------|--------|
| **rsync** | 2秒 | 180秒 | 15秒 | **197秒** |
| **Git** | 5秒 | 180秒 | 15秒 | **200秒** |
| **差异** | -3秒 | 0秒 | 0秒 | **-3秒** |

### 场景：修改 10 个文件并部署

| 方式 | 传输时间 | 构建时间 | 重启时间 | 总时间 |
|------|---------|---------|---------|--------|
| **rsync** | 5秒 | 180秒 | 15秒 | **200秒** |
| **Git** | 10秒 | 180秒 | 15秒 | **205秒** |
| **差异** | -5秒 | 0秒 | 0秒 | **-5秒** |

### 场景：首次全量部署

| 方式 | 传输时间 | 构建时间 | 重启时间 | 总时间 |
|------|---------|---------|---------|--------|
| **rsync** | 30秒 | 240秒 | 15秒 | **285秒** |
| **Git** | 45秒 | 240秒 | 15秒 | **300秒** |
| **差异** | -15秒 | 0秒 | 0秒 | **-15秒** |

---

## 💡 经验总结

### ✅ 推荐做法

1. **开发阶段**：统一使用 `deploy-rsync.sh`
2. **每天结束**：`git commit` 保存进度
3. **功能完成**：`git push` + `deploy-git.sh`
4. **正式发布**：`git tag` + `deploy-git.sh`
5. **配置修改**：`deploy-quick.sh`

### ❌ 不推荐做法

1. ❌ 频繁 git commit 未完成的代码
2. ❌ 不提交代码就使用 `deploy-git.sh`
3. ❌ 在生产环境直接用 `deploy-rsync.sh`
4. ❌ 不打 tag 就正式发布
5. ❌ 修改代码后用 `deploy-quick.sh`

---

## 📞 需要帮助？

- 查看详细文档：`scripts/README.md`
- 查看使用指南：`scripts/部署脚本使用说明.md`
- 查看工具集文档：`docs/07-部署运维/部署脚本工具集.md`

---

**最后更新：** 2025-11-12

