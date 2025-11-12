# 🚀 Git 自动化部署方案

## 📦 文件说明

本目录包含基于 Git 的自动化部署方案，适合生产环境使用。

### 核心脚本

| 脚本 | 用途 | 耗时 | 适用场景 |
|------|------|------|---------|
| **deploy-git.sh** | 标准部署（重新构建） | 5-10分钟 | 功能更新、代码变更 |
| **deploy-git-quick.sh** | 快速部署（仅重启） | 30秒 | 配置修改、脚本更新 |
| **deploy-git-rollback.sh** | 版本回滚 | 5-10分钟 | 紧急回滚 |
| **test-deploy-git.sh** | 环境测试 | 10秒 | 部署前检查 |

### 辅助文件

- **DEPLOY_CHEATSHEET.md** - 部署命令速查表
- **部署脚本使用说明.md** - 中文使用说明

---

## 🎯 快速开始

### 1️⃣ 首次部署前测试

```bash
# 测试环境是否就绪
./scripts/test-deploy-git.sh
```

**测试内容：**
- ✅ 本地环境（Git、SSH密钥）
- ✅ 服务器连接
- ✅ 服务器环境（Git、Docker、Docker Compose）
- ✅ Git 仓库访问权限

---

### 2️⃣ 执行部署

```bash
# 标准部署（推荐）
./scripts/deploy-git.sh

# 快速部署（配置修改时）
./scripts/deploy-git-quick.sh
```

---

### 3️⃣ 紧急回滚（如需要）

```bash
# 查看可用版本
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166 \
  'cd /root/AIcoin && git log --oneline -10'

# 回滚到指定版本
./scripts/deploy-git-rollback.sh <commit-hash>
```

---

## 📊 部署流程图

```
┌─────────────────────────────────────────────────────────────┐
│                     部署流程                                  │
└─────────────────────────────────────────────────────────────┘

  本地开发
     │
     ├─► git add . 
     ├─► git commit -m "描述"
     ├─► git push origin main
     │
     ▼
  执行部署脚本
     │
     ├─► ./scripts/deploy-git.sh
     │
     ▼
  服务器操作（自动）
     │
     ├─► 1. 拉取最新代码 (git pull)
     ├─► 2. 停止容器 (docker compose down)
     ├─► 3. 构建镜像 (docker compose build)
     ├─► 4. 启动服务 (docker compose up -d)
     ├─► 5. 健康检查
     │
     ▼
  验证部署
     │
     ├─► 访问 https://jifenpay.cc
     ├─► 检查日志
     ├─► 测试核心功能
     │
     ▼
  ✅ 部署完成


  如果出现问题 ──► 执行回滚
     │
     ├─► ./scripts/deploy-git-rollback.sh HEAD~1
     │
     ▼
  ✅ 恢复正常
```

---

## 🔄 版本管理最佳实践

### 提交规范

```bash
# 功能更新
git commit -m "feat: 新增用户权限管理功能"

# Bug 修复
git commit -m "fix: 修复登录超时问题"

# 配置更新
git commit -m "config: 更新数据库连接池大小"

# 文档更新
git commit -m "docs: 更新部署文档"
```

### 版本标签

```bash
# 创建版本标签
git tag -a v3.3.0 -m "v3.3.0: RBAC权限系统发布"
git push origin v3.3.0

# 部署指定标签
./scripts/deploy-git-rollback.sh v3.3.0
```

---

## 🛡️ 安全配置

### 服务器 Git 访问配置

#### 方式 1: SSH Key（推荐）

```bash
# 1. 服务器生成 SSH Key
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166
ssh-keygen -t ed25519 -C "deploy@aicoin.com"

# 2. 查看公钥
cat ~/.ssh/id_ed25519.pub

# 3. 添加到 GitHub
# GitHub 仓库 → Settings → Deploy keys → Add deploy key
# 粘贴公钥，勾选 "Allow write access" (如果需要推送)
```

#### 方式 2: Personal Access Token

```bash
# 1. 生成 Token
# GitHub → Settings → Developer settings → Personal access tokens → Generate new token
# 权限: repo (Full control of private repositories)

# 2. 在服务器上配置
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166
git config --global credential.helper store
echo "https://YOUR_TOKEN@github.com" > ~/.git-credentials
```

---

## 📋 部署检查清单

### 部署前 ✓

- [ ] 代码已提交并推送到 Git
- [ ] 本地测试通过
- [ ] 数据库备份已创建
- [ ] 环境变量已检查
- [ ] 团队成员已通知

### 部署中 ✓

- [ ] 脚本执行无错误
- [ ] 镜像构建成功
- [ ] 容器正常启动
- [ ] 日志无严重错误

### 部署后 ✓

- [ ] 网站可访问
- [ ] 核心功能正常
- [ ] API 响应正常
- [ ] 数据库连接正常

---

## 🆘 常见问题

### Q1: Git pull 失败 - Permission denied

**原因：** 服务器没有仓库访问权限

**解决：**
```bash
# 配置 SSH Key 或 Token（参考"安全配置"章节）
```

---

### Q2: Docker 构建慢

**原因：** 网络问题或镜像大

**解决：**
```bash
# 使用国内镜像源
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166
vi /etc/docker/daemon.json

# 添加:
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}

# 重启 Docker
systemctl restart docker
```

---

### Q3: 回滚后数据库不兼容

**原因：** 新版本执行了数据库迁移

**解决：**
```bash
# 恢复数据库备份（推荐）
# 参考 docs/07-部署运维/08-数据备份与清理指南.md

# 或手动回滚迁移
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166
cd /root/AIcoin
docker compose exec backend alembic downgrade -1
```

---

## 📚 相关文档

- [完整部署指南](../docs/07-部署运维/10-Git自动化部署指南.md)
- [部署命令速查](./DEPLOY_CHEATSHEET.md)
- [数据备份指南](../docs/07-部署运维/08-数据备份与清理指南.md)
- [日志管理系统](../docs/07-部署运维/09-日志管理系统.md)

---

## 🎓 对比：Git vs rsync 部署

| 特性 | Git 部署 | rsync 部署 |
|------|----------|-----------|
| **版本控制** | ✅ 完整历史 | ❌ 无 |
| **回滚能力** | ✅ 一键回滚 | ⚠️ 需重新同步 |
| **团队协作** | ✅ 多人可独立部署 | ⚠️ 依赖本地环境 |
| **审计追踪** | ✅ 完整日志 | ⚠️ 较弱 |
| **生产环境** | ✅✅✅ 推荐 | ❌ 不推荐 |
| **开发环境** | ✅ 可用 | ✅ 快速 |
| **部署速度** | ⚠️ 5-10分钟 | ✅ 1-2分钟 |

**推荐：**
- 🏭 **生产环境** → 使用 Git 部署
- 🛠️ **开发环境** → 使用 rsync 快速迭代

---

## 📞 技术支持

如遇问题，请按顺序排查：

1. **运行测试脚本** → `./scripts/test-deploy-git.sh`
2. **查看脚本输出** → 错误信息通常很明确
3. **检查服务器日志** → `docker compose logs -f`
4. **参考文档** → 本 README 和完整部署指南
5. **联系技术团队** → 提供完整错误信息

---

**最后更新:** 2024-11-12  
**版本:** v1.0  
**维护者:** AIcoin 团队

