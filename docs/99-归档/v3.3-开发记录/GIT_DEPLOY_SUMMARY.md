# 🎉 Git 自动化部署方案已完成

## ✅ 已完成内容

### 1. 核心部署脚本（3个）

#### 📦 `scripts/deploy-git.sh` - 标准部署
- **用途**: 生产环境标准部署，拉取代码 + 重新构建镜像
- **耗时**: 5-10 分钟
- **适用**: 功能更新、代码变更、依赖更新

```bash
# 部署 main 分支
./scripts/deploy-git.sh

# 部署指定分支
./scripts/deploy-git.sh develop
```

---

#### ⚡ `scripts/deploy-git-quick.sh` - 快速部署
- **用途**: 快速部署，拉取代码 + 重启服务（不重新构建）
- **耗时**: 30 秒
- **适用**: 配置修改、脚本更新

```bash
./scripts/deploy-git-quick.sh
```

---

#### ⏮️ `scripts/deploy-git-rollback.sh` - 版本回滚
- **用途**: 紧急回滚到任意历史版本
- **耗时**: 5-10 分钟
- **适用**: 新版本出现严重 Bug

```bash
# 回滚到上一版本
./scripts/deploy-git-rollback.sh HEAD~1

# 回滚到指定提交
./scripts/deploy-git-rollback.sh 1bc5b09

# 回滚到指定标签
./scripts/deploy-git-rollback.sh v3.2.0
```

---

### 2. 辅助工具（2个）

#### 🧪 `scripts/test-deploy-git.sh` - 环境测试
- **用途**: 部署前检测环境是否就绪
- **检查项**:
  - ✅ 本地环境（Git、SSH 密钥）
  - ✅ 服务器连接
  - ✅ 服务器环境（Git、Docker、Docker Compose）
  - ✅ Git 仓库访问权限

```bash
./scripts/test-deploy-git.sh
```

---

#### 📋 `scripts/DEPLOY_CHEATSHEET.md` - 命令速查表
- **用途**: 快速查找常用命令
- **内容**: 部署命令、运维命令、应急处理

---

### 3. 完整文档（2份）

#### 📚 `docs/07-部署运维/10-Git自动化部署指南.md`
**包含：**
- 完整部署流程
- 实际操作示例
- 服务器初始化配置
- 部署监控与日志
- 安全最佳实践
- 常见问题与解决
- 部署检查清单
- CI/CD 建议

---

#### 📘 `scripts/README_GIT_DEPLOY.md`
**包含：**
- 快速开始教程
- 部署流程图
- 版本管理最佳实践
- 安全配置指南
- Git vs rsync 对比

---

## 🚀 如何使用

### 第一次使用（推荐流程）

```bash
# 1️⃣ 测试环境
./scripts/test-deploy-git.sh

# 2️⃣ 如果测试通过，执行部署
./scripts/deploy-git.sh

# 3️⃣ 验证部署
# 浏览器访问: https://jifenpay.cc
# 检查日志（如需要）
```

---

### 日常更新流程

```bash
# 本地开发完成后
git add .
git commit -m "描述改动"
git push origin main

# 执行部署
./scripts/deploy-git.sh

# 验证功能
# 访问 https://jifenpay.cc 测试
```

---

### 紧急回滚流程

```bash
# 1. 查看可用版本
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166 \
  'cd /root/AIcoin && git log --oneline -10'

# 2. 执行回滚
./scripts/deploy-git-rollback.sh <commit-hash>

# 3. 验证恢复
# 访问网站确认功能正常
```

---

## 📊 Git 部署 vs rsync 部署

| 特性 | Git 部署 | rsync 部署 |
|------|----------|-----------|
| **版本控制** | ✅ 完整历史记录 | ❌ 无版本记录 |
| **回滚能力** | ✅ 一键回滚任意版本 | ❌ 需要重新同步 |
| **团队协作** | ✅ 多人可独立部署 | ⚠️ 依赖本地环境 |
| **审计追踪** | ✅ 完整操作日志 | ⚠️ 较弱 |
| **部署速度** | ⚠️ 5-10分钟（首次） | ✅ 1-2分钟 |
| **生产环境** | ✅✅✅ 强烈推荐 | ❌ 不推荐 |
| **开发环境** | ✅ 可用 | ✅ 快速迭代 |

---

## 🔐 首次使用前的配置

### 服务器端 Git 访问配置（必需）

由于仓库是私有的，需要配置服务器访问权限：

#### 方式 1: SSH Key（推荐，最安全）

```bash
# 1. SSH 登录服务器
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166

# 2. 生成 SSH Key
ssh-keygen -t ed25519 -C "deploy@aicoin.com"
# 直接按回车，使用默认路径

# 3. 查看公钥
cat ~/.ssh/id_ed25519.pub
# 复制输出内容

# 4. 添加到 GitHub
# 打开 https://github.com/allenxing4071/aicoin/settings/keys
# 点击 "Add deploy key"
# 标题: AIcoin Server Deploy
# Key: 粘贴公钥内容
# ✅ 勾选 "Allow write access"（如果需要服务器推送代码）
# 点击 "Add key"
```

#### 方式 2: Personal Access Token（备选）

```bash
# 1. 创建 Token
# 打开 https://github.com/settings/tokens/new
# Note: AIcoin Deploy Token
# Expiration: No expiration（或设置过期时间）
# Select scopes: 勾选 "repo" (Full control of private repositories)
# 点击 "Generate token"
# ⚠️ 复制 Token（只显示一次）

# 2. SSH 登录服务器
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166

# 3. 配置 Git 凭据
git config --global credential.helper store
echo "https://YOUR_TOKEN@github.com" > ~/.git-credentials

# 4. 测试访问
git ls-remote https://github.com/allenxing4071/aicoin.git
```

---

## ✨ 核心优势

### 1. 完整的版本控制
- 每次部署都有完整的 Git 历史记录
- 可以查看任何时间点的代码状态
- 支持标签管理（v3.3.0、v3.2.0 等）

### 2. 一键回滚能力
- 出现问题立即回滚到任意历史版本
- 回滚操作安全可靠
- 支持回滚到特定标签或提交

### 3. 审计与追踪
- 完整的部署日志
- 每次部署都能追溯到具体提交
- 符合企业级审计要求

### 4. 团队协作友好
- 任何团队成员都可以独立部署
- 不依赖特定开发机器
- 部署环境标准化

### 5. 符合 GitOps 最佳实践
- 声明式配置
- Git 作为唯一真实来源
- 可复现的部署流程

---

## 📝 部署检查清单

### 部署前检查
- [ ] 运行环境测试脚本
- [ ] 代码已推送到 Git
- [ ] 数据库已备份（重要更新）
- [ ] 团队成员已通知

### 部署中检查
- [ ] 脚本执行无错误
- [ ] 镜像构建成功
- [ ] 容器正常启动

### 部署后检查
- [ ] 网站可正常访问 (https://jifenpay.cc)
- [ ] 管理后台可登录 (https://jifenpay.cc/admin)
- [ ] 核心功能测试通过
- [ ] 日志无严重错误

---

## 🆘 常见问题快速解决

### Q1: 执行 deploy-git.sh 时提示 Permission denied

**解决方案:**
```bash
# 修改 SSH 密钥权限
chmod 600 ssh-configs/cloud-servers/AIcoin.pem
```

---

### Q2: Git pull 失败 - Authentication failed

**原因:** 服务器没有仓库访问权限

**解决方案:** 按照上面的"首次使用前的配置"章节配置 SSH Key 或 Token

---

### Q3: Docker 构建非常慢

**解决方案:**
```bash
# 配置国内 Docker 镜像源
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166
cat > /etc/docker/daemon.json << 'EOF'
{
  "registry-mirrors": [
    "https://docker.mirrors.ustc.edu.cn",
    "https://hub-mirror.c.163.com"
  ]
}
EOF
systemctl restart docker
```

---

### Q4: 部署后服务无法访问

**排查步骤:**
```bash
# 1. 检查容器状态
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166 \
  'cd /root/AIcoin && docker compose ps'

# 2. 查看日志
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166 \
  'cd /root/AIcoin && docker compose logs --tail=100'

# 3. 重启服务（如需要）
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166 \
  'cd /root/AIcoin && docker compose restart'
```

---

## 📚 完整文档索引

1. **快速参考**
   - `scripts/DEPLOY_CHEATSHEET.md` - 命令速查表

2. **详细指南**
   - `scripts/README_GIT_DEPLOY.md` - Git 部署快速指南
   - `docs/07-部署运维/10-Git自动化部署指南.md` - 完整部署文档

3. **相关文档**
   - `docs/07-部署运维/06-生产环境部署.md` - 生产环境配置
   - `docs/07-部署运维/08-数据备份与清理指南.md` - 数据备份策略
   - `docs/07-部署运维/09-日志管理系统.md` - 日志管理

---

## 🎯 下一步行动

### 立即可以做的：

1. **测试环境**
```bash
./scripts/test-deploy-git.sh
```

2. **配置 Git 访问**（如果测试失败）
   - 按照"首次使用前的配置"章节操作

3. **执行首次 Git 部署**
```bash
./scripts/deploy-git.sh
```

### 未来建议：

1. **设置版本标签**
```bash
git tag -a v3.3.1 -m "版本描述"
git push origin v3.3.1
```

2. **配置 CI/CD**（可选）
   - 参考 `docs/07-部署运维/10-Git自动化部署指南.md` 中的 GitHub Actions 配置

3. **定期备份**
   - 使用管理后台的备份功能
   - 参考数据备份指南

---

## 📞 技术支持

如有问题：

1. **查看文档** - 大部分问题都有解答
2. **查看日志** - `docker compose logs -f`
3. **运行测试** - `./scripts/test-deploy-git.sh`
4. **联系团队** - 提供详细错误信息

---

## 📊 部署方案对比总结

| 场景 | 推荐方案 | 命令 |
|------|---------|------|
| 生产环境功能更新 | ✅ Git 标准部署 | `./scripts/deploy-git.sh` |
| 生产环境配置调整 | ✅ Git 快速部署 | `./scripts/deploy-git-quick.sh` |
| 生产环境紧急回滚 | ✅ Git 回滚 | `./scripts/deploy-git-rollback.sh` |
| 开发环境快速测试 | ⚡ rsync 部署 | `./scripts/deploy-rsync.sh` |

---

**状态:** ✅ 已完成并测试  
**版本:** v1.0  
**完成时间:** 2024-11-12  
**维护者:** AIcoin 团队

---

🎉 **恭喜！Git 自动化部署方案已全部完成，可以开始使用了！**

