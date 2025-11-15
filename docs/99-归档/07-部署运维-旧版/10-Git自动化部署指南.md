# Git 自动化部署指南

## 📋 概述

本文档介绍基于 Git 的自动化部署方案，相比 rsync 方式更加专业、可控、符合 GitOps 最佳实践。

### 优势对比

| 特性 | Git 部署 | rsync 部署 |
|------|---------|-----------|
| **版本控制** | ✅ 完整的版本历史 | ❌ 无版本记录 |
| **回滚能力** | ✅ 一键回滚任意版本 | ❌ 需要重新同步 |
| **团队协作** | ✅ 多人可独立部署 | ⚠️ 依赖本地环境 |
| **审计追踪** | ✅ 完整的操作日志 | ⚠️ 较弱 |
| **部署速度** | ⚠️ 首次较慢 | ✅ 快速 |
| **生产环境** | ✅ 推荐 | ⚠️ 仅适合开发 |

---

## 🛠️ 部署脚本说明

### 1️⃣ 标准部署脚本 `deploy-git.sh`

**用途：** 生产环境标准部署，拉取最新代码并重新构建 Docker 镜像。

**使用场景：**
- ✅ 功能更新
- ✅ 代码变更
- ✅ 依赖更新
- ✅ 首次部署

**基本用法：**

```bash
# 部署 main 分支（默认）
./scripts/deploy-git.sh

# 部署指定分支
./scripts/deploy-git.sh develop
./scripts/deploy-git.sh feature/new-feature
```

**执行流程：**
1. 检查本地环境（SSH 密钥）
2. 测试服务器连接
3. 在服务器上拉取/更新 Git 仓库
4. 检查环境配置（.env、Docker）
5. 停止现有容器
6. 重新构建前后端镜像（--no-cache）
7. 启动所有服务
8. 验证部署状态

**预计耗时：** 5-10 分钟（取决于网络速度和镜像大小）

---

### 2️⃣ 快速部署脚本 `deploy-git-quick.sh`

**用途：** 快速更新，仅拉取代码并重启服务，不重新构建镜像。

**使用场景：**
- ✅ 配置文件修改
- ✅ 数据库迁移脚本
- ✅ 环境变量调整
- ✅ 文档更新
- ❌ 代码逻辑变更（需用标准部署）

**基本用法：**

```bash
# 快速部署 main 分支
./scripts/deploy-git-quick.sh

# 快速部署指定分支
./scripts/deploy-git-quick.sh develop
```

**执行流程：**
1. 拉取最新代码
2. 重启 Docker 容器（不重新构建）
3. 验证服务状态

**预计耗时：** 30 秒 - 1 分钟

---

### 3️⃣ 回滚脚本 `deploy-git-rollback.sh`

**用途：** 紧急回滚到指定版本。

**使用场景：**
- ⚠️ 新版本出现严重 Bug
- ⚠️ 性能问题需要紧急恢复
- ⚠️ 功能验证失败

**基本用法：**

```bash
# 回滚到上一个版本
./scripts/deploy-git-rollback.sh HEAD~1

# 回滚到指定提交
./scripts/deploy-git-rollback.sh 1bc5b09

# 回滚到指定标签
./scripts/deploy-git-rollback.sh v3.2.0
```

**查看可回滚版本：**

```bash
# 查看最近 10 次提交
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166 'cd /root/AIcoin && git log --oneline -10'

# 查看所有标签
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166 'cd /root/AIcoin && git tag'
```

**执行流程：**
1. 显示当前版本信息
2. 确认回滚操作（需输入 yes）
3. 停止服务
4. 回滚到指定版本
5. 重新构建镜像
6. 启动服务
7. 验证状态

**预计耗时：** 5-10 分钟

---

## 🚀 实际操作示例

### 场景 1：日常功能更新

```bash
# 1. 本地开发完成后，提交并推送代码
git add .
git commit -m "新增用户权限功能"
git push origin main

# 2. 执行标准部署
./scripts/deploy-git.sh

# 3. 验证部署
# 浏览器访问 https://jifenpay.cc 测试功能
```

---

### 场景 2：紧急配置修改

```bash
# 1. 修改配置文件（如 .env）
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166
vi /root/AIcoin/.env

# 2. 提交配置到 Git（可选但推荐）
cd /root/AIcoin
git add .env
git commit -m "更新数据库连接配置"
git push

# 3. 本地执行快速部署
./scripts/deploy-git-quick.sh
```

---

### 场景 3：发现 Bug 需要紧急回滚

```bash
# 1. 查看可用版本
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166 'cd /root/AIcoin && git log --oneline -5'

# 输出示例：
# 1bc5b09 (HEAD -> main) v3.3.0: RBAC权限系统完整实现
# d18925f 更新前端认证逻辑
# a7e8f3c 修复登录 Bug
# 9c2d1a0 优化性能
# 6b5e4f2 v3.2.0 稳定版本

# 2. 回滚到上一个版本
./scripts/deploy-git-rollback.sh d18925f

# 3. 或回滚到稳定版本
./scripts/deploy-git-rollback.sh v3.2.0
```

---

## 🔧 服务器端初始化配置

### 首次使用前需要在服务器上配置 Git

```bash
# 1. SSH 登录服务器
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166

# 2. 配置 Git 用户信息（用于提交记录）
git config --global user.name "AIcoin Deploy Bot"
git config --global user.email "deploy@aicoin.com"

# 3. 配置 Git 凭据（如果仓库是私有的）
# 方式 1: Personal Access Token
git config --global credential.helper store
echo "https://YOUR_TOKEN@github.com" > ~/.git-credentials

# 方式 2: SSH Key（推荐）
ssh-keygen -t ed25519 -C "deploy@aicoin.com"
cat ~/.ssh/id_ed25519.pub
# 将公钥添加到 GitHub 仓库的 Deploy Keys

# 4. 首次部署
# 本地运行标准部署脚本即可
```

---

## 📊 部署监控与日志

### 查看实时日志

```bash
# 所有服务日志
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166 'cd /root/AIcoin && docker compose logs -f'

# 仅查看后端日志
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166 'cd /root/AIcoin && docker compose logs -f backend'

# 仅查看前端日志
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166 'cd /root/AIcoin && docker compose logs -f frontend'

# 最近 100 行日志
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166 'cd /root/AIcoin && docker compose logs --tail=100'
```

### 检查容器状态

```bash
# 容器运行状态
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166 'cd /root/AIcoin && docker compose ps'

# 容器资源使用情况
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166 'docker stats --no-stream'
```

### 查看 Git 版本信息

```bash
# 当前部署版本
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166 'cd /root/AIcoin && git log -1 --oneline'

# 最近 5 次提交
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166 'cd /root/AIcoin && git log -5 --oneline --decorate'

# 查看当前分支
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166 'cd /root/AIcoin && git branch --show-current'
```

---

## 🔐 安全最佳实践

### 1. SSH 密钥权限

```bash
# 确保 SSH 密钥权限正确
chmod 600 ssh-configs/cloud-servers/AIcoin.pem
```

### 2. Git 仓库访问

**推荐：使用 SSH Key 方式（最安全）**

```bash
# 服务器生成 SSH Key
ssh-keygen -t ed25519 -C "deploy@aicoin.com"

# 添加到 GitHub Deploy Keys (只读权限)
# Settings → Deploy Keys → Add deploy key
```

**备选：使用 Personal Access Token**

```bash
# 创建 Token: GitHub → Settings → Developer settings → Personal access tokens
# 权限：repo (full control)

# 在服务器上配置
git config --global credential.helper store
git clone https://YOUR_TOKEN@github.com/allenxing4071/aicoin.git
```

### 3. 环境变量保护

```bash
# .env 文件不要提交到 Git
echo ".env" >> .gitignore

# 在服务器上单独维护 .env
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166
vi /root/AIcoin/.env
```

---

## ⚠️ 常见问题与解决

### 问题 1：Git 拉取失败 - Permission denied

**原因：** 服务器无权访问 Git 仓库

**解决：**

```bash
# 检查 Git 配置
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166 'git config --list'

# 如果仓库是私有的，需要配置访问凭据
# 推荐使用 SSH Key（参考"安全最佳实践"章节）
```

---

### 问题 2：Docker 构建失败 - 磁盘空间不足

**原因：** 旧镜像和容器占用空间

**解决：**

```bash
# 清理未使用的镜像和容器
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166 << 'EOF'
docker system prune -a -f
docker volume prune -f
EOF
```

---

### 问题 3：服务启动后无法访问

**排查步骤：**

```bash
# 1. 检查容器状态
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166 'cd /root/AIcoin && docker compose ps'

# 2. 查看日志
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166 'cd /root/AIcoin && docker compose logs --tail=50'

# 3. 检查端口占用
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166 'netstat -tulnp | grep -E "80|443|8000|3000"'

# 4. 检查防火墙
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166 'ufw status'
```

---

### 问题 4：回滚后数据库不兼容

**原因：** 新版本执行了数据库迁移，回滚代码后数据库结构不匹配

**解决：**

```bash
# 方案 1: 恢复数据库备份（推荐）
# 参考 "08-数据备份与清理指南.md"

# 方案 2: 手动回滚数据库迁移
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166
cd /root/AIcoin
docker compose exec backend alembic downgrade -1
```

**预防措施：**
- 部署前备份数据库
- 使用可逆的数据库迁移
- 在测试环境先验证回滚流程

---

## 📅 部署检查清单

### 部署前检查

- [ ] 代码已通过本地测试
- [ ] 已提交并推送到 Git 仓库
- [ ] 版本号已更新（如 VERSION 文件）
- [ ] 数据库迁移脚本已准备
- [ ] 重要数据已备份
- [ ] 团队成员已通知

### 部署中检查

- [ ] 脚本执行无错误
- [ ] Docker 镜像构建成功
- [ ] 所有容器正常启动
- [ ] 日志无严重错误

### 部署后检查

- [ ] 网站可正常访问
- [ ] 核心功能测试通过
- [ ] API 接口响应正常
- [ ] 管理后台可登录
- [ ] 数据库连接正常
- [ ] 监控指标正常

---

## 🔄 持续集成/部署（CI/CD）建议

### GitHub Actions 自动部署（高级）

创建 `.github/workflows/deploy.yml`:

```yaml
name: Deploy to Production

on:
  push:
    branches:
      - main
    tags:
      - 'v*'

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Setup SSH
        run: |
          mkdir -p ~/.ssh
          echo "${{ secrets.SSH_PRIVATE_KEY }}" > ~/.ssh/id_rsa
          chmod 600 ~/.ssh/id_rsa
          ssh-keyscan -H 47.250.132.166 >> ~/.ssh/known_hosts

      - name: Deploy to server
        run: |
          ssh root@47.250.132.166 << 'EOF'
            cd /root/AIcoin
            git pull origin main
            docker compose down
            docker compose build --no-cache
            docker compose up -d
          EOF

      - name: Verify deployment
        run: |
          sleep 30
          curl -f https://jifenpay.cc || exit 1
```

**配置方法：**
1. GitHub 仓库 → Settings → Secrets
2. 添加 `SSH_PRIVATE_KEY`（服务器 SSH 私钥）
3. 推送代码到 main 分支自动触发部署

---

## 📚 相关文档

- [01-快速开始.md](../01-快速入门/01-快速开始.md) - 项目基本介绍
- [06-生产环境部署.md](./06-生产环境部署.md) - 生产环境详细配置
- [08-数据备份与清理指南.md](./08-数据备份与清理指南.md) - 数据备份策略
- [09-日志管理系统.md](./09-日志管理系统.md) - 日志查看与分析

---

## 📞 支持与反馈

如遇到部署问题，请按以下顺序排查：

1. **查看脚本输出** - 错误信息通常很明确
2. **检查服务器日志** - `docker compose logs -f`
3. **参考常见问题** - 本文档"常见问题与解决"章节
4. **联系技术负责人** - 提供详细错误信息

---

**版本记录：**
- v1.0 (2024-11-12) - 初始版本，添加 Git 部署方案

