# 🚀 AIcoin 部署速查表

## 快速命令

### 标准部署（推荐生产环境）
```bash
# 部署 main 分支（重新构建镜像）
./scripts/deploy-git.sh

# 部署指定分支
./scripts/deploy-git.sh develop
```
⏱️ **耗时**: 5-10 分钟  
📦 **适用**: 代码更新、功能发布、依赖更新

---

### 快速部署（仅重启服务）
```bash
# 拉取代码 + 重启（不重新构建）
./scripts/deploy-git-quick.sh
```
⏱️ **耗时**: 30 秒  
📦 **适用**: 配置修改、脚本更新

---

### 紧急回滚
```bash
# 查看可用版本
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166 \
  'cd /root/AIcoin && git log --oneline -10'

# 回滚到上一版本
./scripts/deploy-git-rollback.sh HEAD~1

# 回滚到指定提交
./scripts/deploy-git-rollback.sh 1bc5b09
```
⏱️ **耗时**: 5-10 分钟  
⚠️ **注意**: 需要确认操作（输入 yes）

---

## 部署方式对比

| 方式 | 脚本 | 速度 | 安全性 | 推荐场景 |
|------|------|------|--------|---------|
| **Git 标准部署** | `deploy-git.sh` | ⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 🔥 生产环境 |
| **Git 快速部署** | `deploy-git-quick.sh` | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | 配置调整 |
| **rsync 部署** | `deploy-rsync.sh` | ⭐⭐⭐⭐ | ⭐⭐⭐ | 开发测试 |

---

## 常用运维命令

### 查看日志
```bash
# 实时日志
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166 \
  'cd /root/AIcoin && docker compose logs -f'

# 仅后端日志
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166 \
  'cd /root/AIcoin && docker compose logs -f backend'
```

### 检查状态
```bash
# 容器状态
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166 \
  'cd /root/AIcoin && docker compose ps'

# 资源使用
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166 \
  'docker stats --no-stream'
```

### 重启服务
```bash
# 重启所有服务
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166 \
  'cd /root/AIcoin && docker compose restart'

# 重启指定服务
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166 \
  'cd /root/AIcoin && docker compose restart backend'
```

### 清理资源
```bash
# 清理未使用的镜像和容器
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166 \
  'docker system prune -a -f'
```

---

## 完整部署流程

### 1️⃣ 开发阶段（本地）
```bash
# 开发 → 测试 → 提交
git add .
git commit -m "描述改动"
git push origin main
```

### 2️⃣ 部署阶段（远程）
```bash
# 执行部署脚本
./scripts/deploy-git.sh

# 或快速部署
./scripts/deploy-git-quick.sh
```

### 3️⃣ 验证阶段
```bash
# 浏览器访问
https://jifenpay.cc

# 查看日志
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166 \
  'cd /root/AIcoin && docker compose logs --tail=50'
```

---

## 🆘 应急处理

### 服务无响应
```bash
# 1. 重启服务
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166 \
  'cd /root/AIcoin && docker compose restart'

# 2. 查看日志
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166 \
  'cd /root/AIcoin && docker compose logs --tail=100'
```

### 新版本有 Bug
```bash
# 紧急回滚到上一版本
./scripts/deploy-git-rollback.sh HEAD~1
```

### 磁盘空间不足
```bash
# 清理 Docker 资源
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166 << 'EOF'
docker system prune -a -f
docker volume prune -f
df -h
EOF
```

---

## 📚 详细文档

- **完整指南**: `docs/07-部署运维/10-Git自动化部署指南.md`
- **生产部署**: `docs/07-部署运维/06-生产环境部署.md`
- **数据备份**: `docs/07-部署运维/08-数据备份与清理指南.md`

---

**访问地址**:  
🌐 前台: https://jifenpay.cc  
🔐 管理后台: https://jifenpay.cc/admin

