# AIcoin 项目部署脚本使用指南

## 📁 脚本概览

本目录提供了三种部署方式，适用于不同场景：

| 脚本文件 | 适用场景 | 速度 | 推荐度 |
|---------|---------|------|--------|
| `deploy-rsync.sh` | 开发阶段快速迭代 | ⚡⚡⚡ | ⭐⭐⭐⭐⭐ |
| `deploy-git.sh` | 生产环境正式发布 | ⚡⚡ | ⭐⭐⭐⭐ |
| `deploy-quick.sh` | 仅修改配置文件时 | ⚡⚡⚡⚡ | ⭐⭐⭐ |

---

## 🚀 快速开始

### 1️⃣ 赋予脚本执行权限（首次使用）

```bash
chmod +x scripts/deploy-*.sh
```

### 2️⃣ 选择合适的脚本执行

#### 方式 A：rsync 快速部署（推荐开发环境）

```bash
./scripts/deploy-rsync.sh
```

**优点：**
- ✅ 速度最快（增量传输）
- ✅ 无需 git commit
- ✅ 适合频繁修改代码

**缺点：**
- ⚠️ 不记录版本历史
- ⚠️ 需要确保本地代码可靠

---

#### 方式 B：Git 标准部署（推荐生产环境）

```bash
./scripts/deploy-git.sh
```

**优点：**
- ✅ 有版本控制
- ✅ 可追踪每次部署
- ✅ 便于回滚

**缺点：**
- ⚠️ 需要先 commit
- ⚠️ 速度稍慢

**注意事项：**
- 会自动检测未提交的更改并提示
- 会自动推送到远程仓库
- 需要配置 Git 远程仓库

---

#### 方式 C：快速重启（仅重启服务）

```bash
./scripts/deploy-quick.sh
```

**适用场景：**
- ✅ 修改了 `.env` 环境变量
- ✅ 修改了 `docker-compose.yml`
- ✅ 服务异常需要重启

**注意：**
- ⚠️ 不会同步代码
- ⚠️ 不会重新构建镜像

---

## 🔧 高级配置

### 修改服务器地址

编辑脚本开头的配置区域：

```bash
SERVER_USER="root"
SERVER_HOST="47.250.132.166"
SERVER_PATH="/root/AIcoin"
SSH_KEY="/path/to/your/ssh-key.pem"
```

### 修改 Git 分支

在 `deploy-git.sh` 中修改：

```bash
GIT_BRANCH="main"  # 改为你的目标分支
GIT_REMOTE="origin"
```

### 自定义 rsync 排除规则

在 `deploy-rsync.sh` 中修改 `--exclude` 参数：

```bash
rsync -avz --delete \
    --exclude='node_modules/' \
    --exclude='your-custom-folder/' \
    ...
```

---

## 📝 部署流程详解

### rsync 部署流程

```
1️⃣ 检查本地环境
    ↓
2️⃣ 测试服务器连接
    ↓
3️⃣ rsync 同步代码（增量）
    ↓
4️⃣ 服务器上重新构建 Docker 镜像
    ↓
5️⃣ 重启所有服务
    ↓
6️⃣ 验证部署状态
```

### Git 部署流程

```
1️⃣ 检查本地 Git 状态
    ↓
2️⃣ 提交并推送代码到远程仓库
    ↓
3️⃣ 服务器上 git pull 最新代码
    ↓
4️⃣ 服务器上重新构建 Docker 镜像
    ↓
5️⃣ 重启所有服务
    ↓
6️⃣ 验证部署状态
```

---

## ⚠️ 常见问题

### Q1: SSH 连接失败

**解决方案：**
```bash
# 检查 SSH 密钥权限
chmod 400 ssh-configs/cloud-servers/AIcoin.pem

# 手动测试连接
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166
```

### Q2: rsync 速度慢

**原因：** 可能是首次同步或网络问题

**解决方案：**
- 首次同步会较慢（需要传输所有文件）
- 后续同步会很快（仅传输修改的文件）
- 检查网络连接质量

### Q3: Docker 构建失败

**解决方案：**
```bash
# SSH 到服务器手动查看日志
ssh -i ssh-configs/cloud-servers/AIcoin.pem root@47.250.132.166

cd /root/AIcoin
docker compose logs backend
docker compose logs frontend
```

### Q4: 服务启动失败

**解决方案：**
```bash
# 查看容器状态
docker compose ps

# 查看具体错误
docker compose logs --tail=100

# 手动重启
docker compose restart
```

---

## 🔐 安全性说明

### rsync 安全性

- ✅ 使用 SSH 加密传输
- ✅ 使用私钥认证
- ✅ 自动跳过敏感文件（.env.local）
- ⚠️ 确保 SSH 密钥权限正确（400）

### Git 安全性

- ✅ 有版本追踪和审计日志
- ✅ 可以回滚到任意版本
- ⚠️ 敏感文件需要添加到 `.gitignore`
- ⚠️ 不要将 SSH 密钥提交到 Git

---

## 📊 性能对比

### 传输速度测试（参考）

| 方法 | 首次部署 | 增量部署 | 优势 |
|------|---------|---------|------|
| rsync | ~30秒 | ~5秒 | 仅传输修改文件 |
| Git | ~45秒 | ~10秒 | 有版本控制 |
| Docker Hub | ~3分钟 | ~3分钟 | 不依赖网络带宽 |

---

## 🎯 推荐使用策略

### 开发阶段（推荐 rsync）

```bash
# 修改代码后
./scripts/deploy-rsync.sh

# 仅修改配置
./scripts/deploy-quick.sh
```

### 测试/预发布阶段（推荐 Git）

```bash
# 提交代码
git add .
git commit -m "feature: 新功能"

# 部署
./scripts/deploy-git.sh
```

### 生产环境（推荐 Git + Tag）

```bash
# 打标签
git tag -a v1.0.0 -m "Release v1.0.0"
git push origin v1.0.0

# 部署
./scripts/deploy-git.sh
```

---

## 📞 技术支持

如有问题，请联系技术团队或查看项目文档。
