# 🐳 Docker快速启动指南

## 🚀 5分钟快速部署

### 步骤1: 配置环境变量
```bash
# 测试网
cp .env.testnet.example .env.testnet
nano .env.testnet

# 或生产环境
cp .env.prod.example .env.prod
nano .env.prod
```

### 步骤2: 填写必需配置
```bash
DEEPSEEK_API_KEY=sk-your-key
HYPERLIQUID_WALLET_ADDRESS=0xYourAddress
HYPERLIQUID_PRIVATE_KEY=0xYourPrivateKey
```

### 步骤3: 一键部署
```bash
# 测试网
./scripts/start_testnet.sh

# 或生产环境
./scripts/deploy_prod.sh
```

### 步骤4: 访问系统
- **前端**: http://localhost:3000
- **API**: http://localhost:8000/docs

---

## 📦 常用命令

### 构建镜像
```bash
./scripts/build_docker.sh
```

### 启动服务
```bash
# 测试网
docker-compose -f deploy/docker-compose.testnet.yml up -d

# 生产环境
docker-compose -f deploy/docker-compose.prod.yml up -d
```

### 停止服务
```bash
# 测试网
docker-compose -f deploy/docker-compose.testnet.yml down

# 生产环境
docker-compose -f deploy/docker-compose.prod.yml down
```

### 查看日志
```bash
docker-compose logs -f backend
```

### 查看状态
```bash
docker-compose ps
```

---

## 🔍 健康检查

```bash
# Backend
curl http://localhost:8000/health

# Frontend
curl http://localhost:3000

# 系统状态
curl http://localhost:8000/api/v1/status
```

---

## 📊 监控

```bash
# 资源使用
docker stats

# 实时日志
docker-compose logs -f backend | grep -E '(🔄|✅|❌|⚠️)'
```

---

## 🛠️ 故障排查

### 端口冲突
```bash
# 检查端口占用
lsof -i :8000
lsof -i :3000

# 修改端口映射（根据实际使用的文件）
nano deploy/docker-compose.testnet.yml
# 或
nano deploy/docker-compose.prod.yml
```

### 容器无法启动
```bash
# 查看日志
docker-compose logs backend

# 重启服务
docker-compose restart backend
```

### 数据库连接失败
```bash
# 检查PostgreSQL
docker-compose logs postgres

# 重启PostgreSQL
docker-compose restart postgres
```

---

## 📚 完整文档

详细文档请查看: [docs/07-部署运维/部署指南.md](../07-部署运维/部署指南.md)

---

**快速支持**: 查看日志 → 检查配置 → 重启服务

