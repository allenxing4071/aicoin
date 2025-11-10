# 🚀 AIcoin 远程服务器部署 - 快速开始

## 📋 服务器信息
- **IP地址**: 192.168.31.85
- **用户名**: allenxing07
- **部署目录**: /home/allenxing07/AIcoin

---

## ⚡ 一键部署（推荐）

在**本地终端**执行:

```bash
cd /Users/xinghailong/Documents/soft/AIcoin

# 1. 检查远程环境
./scripts/check_remote_env.sh

# 2. 自动部署
./scripts/deploy_to_remote.sh
```

**脚本会自动完成:**
- ✅ SSH连接检查
- ✅ 环境检查（Docker、内存、磁盘）
- ✅ 代码同步
- ✅ 环境配置
- ✅ Docker镜像构建
- ✅ 服务启动

---

## 📝 部署后必做事项

### 1. SSH到服务器编辑配置

```bash
ssh allenxing07@192.168.31.85
cd /home/allenxing07/AIcoin
nano .env
```

### 2. 填写必需配置

**必须修改的配置项:**

```bash
# AI API密钥（必需）
DEEPSEEK_API_KEY=sk-your-real-deepseek-api-key

# Hyperliquid钱包（必需）
HYPERLIQUID_WALLET_ADDRESS=0xYourRealWalletAddress
HYPERLIQUID_PRIVATE_KEY=0xYourRealPrivateKey

# 其他AI API（可选）
QWEN_API_KEY=sk-your-qwen-api-key
GROK_API_KEY=xai-your-grok-api-key
CLAUDE_API_KEY=sk-ant-your-claude-api-key
OPENAI_API_KEY=sk-your-openai-api-key
```

### 3. 重启服务使配置生效

```bash
cd /home/allenxing07/AIcoin
docker-compose -f deploy/docker-compose.prod.yml restart
```

---

## 🔍 验证部署

### 在浏览器中访问:

- **前端界面**: http://192.168.31.85:3000
- **后端API**: http://192.168.31.85:8000
- **API文档**: http://192.168.31.85:8000/docs
- **Qdrant**: http://192.168.31.85:6333/dashboard

### 检查服务状态:

```bash
ssh allenxing07@192.168.31.85
cd /home/allenxing07/AIcoin

# 查看所有服务
docker-compose -f deploy/docker-compose.prod.yml ps

# 查看日志
docker-compose -f deploy/docker-compose.prod.yml logs -f
```

---

## 📚 详细文档

完整部署文档: `docs/07-部署运维/06-远程服务器部署手册.md`

---

## 🛠️ 常用命令

```bash
# SSH连接
ssh allenxing07@192.168.31.85

# 进入项目目录
cd /home/allenxing07/AIcoin

# 查看服务状态
docker-compose -f deploy/docker-compose.prod.yml ps

# 查看日志
docker-compose -f deploy/docker-compose.prod.yml logs -f

# 重启服务
docker-compose -f deploy/docker-compose.prod.yml restart

# 停止服务
docker-compose -f deploy/docker-compose.prod.yml down

# 启动服务
docker-compose -f deploy/docker-compose.prod.yml up -d
```

---

## ⚠️ 重要提醒

1. **安全配置**
   - 立即修改.env中的API密钥和钱包信息
   - 不要在公共场合泄露私钥

2. **交易设置**
   - 默认交易功能关闭 (`TRADING_ENABLED=false`)
   - 启用交易前请充分测试
   - 建议先在测试网验证

3. **备份策略**
   - 定期备份数据库
   - 保存重要配置文件
   - 记录所有重要变更

---

## 🎯 部署流程图

```
本地电脑
    ↓
[1] 运行 check_remote_env.sh (检查环境)
    ↓
[2] 运行 deploy_to_remote.sh (自动部署)
    ↓
远程服务器 (192.168.31.85)
    ↓
[3] 代码同步完成
    ↓
[4] Docker镜像构建
    ↓
[5] 服务启动
    ↓
[6] 手动编辑 .env 文件
    ↓
[7] 重启服务
    ↓
[8] 访问 http://192.168.31.85:3000
    ↓
✅ 部署完成
```

---

## 📞 遇到问题？

1. 查看日志: `docker-compose logs -f`
2. 检查服务: `docker-compose ps`
3. 参考文档: `docs/07-部署运维/06-远程服务器部署手册.md`
4. 故障排查: 文档中有详细的故障排查章节

---

**准备好了吗？开始部署吧！🚀**

```bash
./scripts/deploy_to_remote.sh
```

