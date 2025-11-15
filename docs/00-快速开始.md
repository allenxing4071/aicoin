# 🚀 AIcoin 5分钟快速开始

> **最快的方式体验 AIcoin** | 从零到运行只需 5 分钟

---

## 📋 前置要求

- ✅ Docker & Docker Compose 已安装
- ✅ 已获取 DeepSeek API Key
- ✅ 已获取 Hyperliquid 钱包地址和私钥

---

## ⚡ 三步启动

### 步骤 1: 克隆项目

```bash
git clone https://github.com/allenxing4071/aicoin.git
cd aicoin
```

### 步骤 2: 配置环境变量

```bash
# 复制配置模板
cp .env.example .env

# 编辑配置文件
nano .env
```

**最小配置 (必填):**

```bash
# AI 平台
DEEPSEEK_API_KEY=sk-your-deepseek-key

# 交易所
HYPERLIQUID_WALLET_ADDRESS=0xYourAddress
HYPERLIQUID_PRIVATE_KEY=0xYourPrivateKey
HYPERLIQUID_TESTNET=true  # 建议先用测试网

# 安全密钥
SECRET_KEY=your-secret-key-change-this
JWT_SECRET_KEY=your-jwt-secret-key
```

### 步骤 3: 启动服务

```bash
# 一键启动
docker-compose up -d

# 查看状态
docker-compose ps
```

---

## 🎯 访问系统

启动成功后，访问以下地址:

- **前端界面**: http://localhost:3000
- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health

---

## ✅ 验证运行

```bash
# 检查后端健康状态
curl http://localhost:8000/health

# 预期输出
{
  "status": "healthy",
  "version": "4.1.0",
  "ai_orchestrator": true
}
```

---

## 🔍 查看日志

```bash
# 查看所有日志
docker-compose logs -f

# 只看后端
docker-compose logs -f backend

# 只看 AI 决策
docker-compose logs backend | grep "决策"
```

---

## ⚠️ 常见问题

### 容器启动失败

```bash
# 检查端口占用
lsof -i :8000
lsof -i :3000

# 重新启动
docker-compose down
docker-compose up -d --build
```

### 数据库连接失败

```bash
# 检查 PostgreSQL
docker-compose logs postgres

# 重启数据库
docker-compose restart postgres
```

### 前端无法访问

```bash
# 检查后端是否运行
curl http://localhost:8000/health

# 重启前端
docker-compose restart frontend
```

---

## 📚 下一步

- **用户指南**: 查看 [01-用户指南/user-guide.md](01-用户指南/user-guide.md) 了解核心功能
- **配置优化**: 查看 [02-部署运维/configuration.md](02-部署运维/configuration.md) 调整参数
- **开发文档**: 查看 [03-开发文档/architecture.md](03-开发文档/architecture.md) 了解架构

---

## 🆘 获取帮助

- **文档中心**: [docs/README.md](README.md)
- **GitHub Issues**: https://github.com/allenxing4071/aicoin/issues
- **API 文档**: http://localhost:8000/docs

---

**祝你使用愉快！** 🎉

如有问题，请查看完整的 [用户指南](01-用户指南/user-guide.md) 或 [故障排查](02-部署运维/troubleshooting.md)。

