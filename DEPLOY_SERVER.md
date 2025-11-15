# 🚀 AIcoin v3.1 服务器部署指南

## 快速部署（推荐）

### 方式1：使用部署脚本（最简单）

在服务器上执行：

```bash
# 进入项目目录
cd /root/AIcoin  # 或你的实际项目路径

# 拉取最新代码
git pull origin main

# 运行部署脚本
bash scripts/deploy_to_server.sh
```

### 方式2：手动部署

```bash
# 1. 进入项目目录
cd /root/AIcoin

# 2. 拉取最新代码
git pull origin main

# 3. 进入deploy目录
cd deploy

# 4. 停止现有服务
docker-compose down

# 5. 重新构建并启动
docker-compose up -d --build

# 6. 运行数据库迁移
docker-compose exec backend alembic upgrade head

# 7. 运行自检
docker-compose exec backend python scripts/self_check.py
```

## 📋 部署前检查清单

- [ ] 服务器已安装Docker和Docker Compose
- [ ] `.env`文件已配置（包含所有必要的API密钥）
- [ ] 域名DNS已正确解析到服务器IP
- [ ] SSL证书已配置（如使用HTTPS）
- [ ] 防火墙已开放80和443端口

## 🔧 环境要求

### 系统要求
- **操作系统**: Ubuntu 20.04+ / CentOS 7+ / Debian 10+
- **内存**: 最少4GB，推荐8GB+
- **磁盘**: 最少20GB可用空间
- **CPU**: 2核心+

### 软件要求
- **Docker**: 20.10+
- **Docker Compose**: 2.0+
- **Git**: 2.0+

### 安装Docker（如未安装）

```bash
# Ubuntu/Debian
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo systemctl enable docker
sudo systemctl start docker

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
```

## 🌐 域名配置

### 1. DNS配置
确保域名解析到服务器IP：
```
A记录: jifenpay.cc -> 你的服务器IP
A记录: www.jifenpay.cc -> 你的服务器IP
```

### 2. Nginx配置
Nginx配置文件位于：`deploy/nginx/nginx.conf`

已配置的域名：
- `jifenpay.cc`
- `www.jifenpay.cc`

### 3. SSL证书（HTTPS）

如使用Let's Encrypt：
```bash
# 安装certbot
sudo apt install certbot

# 获取证书
sudo certbot certonly --standalone -d jifenpay.cc -d www.jifenpay.cc

# 证书会保存在
# /etc/letsencrypt/live/jifenpay.cc/fullchain.pem
# /etc/letsencrypt/live/jifenpay.cc/privkey.pem

# 复制到项目目录
sudo cp /etc/letsencrypt/live/jifenpay.cc/fullchain.pem deploy/nginx/ssl/
sudo cp /etc/letsencrypt/live/jifenpay.cc/privkey.pem deploy/nginx/ssl/
```

## 🔐 环境变量配置

确保`.env`文件包含以下关键配置：

```bash
# 数据库
POSTGRES_USER=aicoin
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=aicoin

# Redis
REDIS_URL=redis://redis:6379/0

# Qdrant
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# API密钥
DEEPSEEK_API_KEY=your_deepseek_key
QWEN_API_KEY=your_qwen_key
OPENAI_API_KEY=your_openai_key

# 交易所
HYPERLIQUID_WALLET_ADDRESS=your_wallet
HYPERLIQUID_PRIVATE_KEY=your_private_key
HYPERLIQUID_TESTNET=false

# 安全
SECRET_KEY=your_secret_key_change_in_production
JWT_SECRET_KEY=your_jwt_secret_key

# 交易开关
TRADING_ENABLED=true
```

## 📊 部署后验证

### 1. 检查服务状态
```bash
cd /root/AIcoin/deploy
docker-compose ps
```

所有服务应显示"Up"状态。

### 2. 检查日志
```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f frontend
```

### 3. 访问测试
- **主站**: http://jifenpay.cc
- **API文档**: http://jifenpay.cc/docs
- **管理后台**: http://jifenpay.cc/admin

### 4. 运行自检
```bash
docker-compose exec backend python scripts/self_check.py
```

应该看到：
```
✅ 模块导入 - 通过
✅ IntelligenceCoordinator - 通过
✅ 四层存储 - 通过
✅ 配置检查 - 通过
✅ API端点 - 通过
```

### 5. 运行功能测试
```bash
docker-compose exec backend python scripts/test_v3.1_features.py
```

## 🔄 常用运维命令

### 查看服务状态
```bash
docker-compose ps
```

### 查看实时日志
```bash
docker-compose logs -f
```

### 重启服务
```bash
# 重启所有服务
docker-compose restart

# 重启特定服务
docker-compose restart backend
docker-compose restart frontend
```

### 停止服务
```bash
docker-compose down
```

### 进入容器
```bash
# 进入后端容器
docker-compose exec backend bash

# 进入数据库容器
docker-compose exec postgres psql -U aicoin
```

### 查看资源使用
```bash
docker stats
```

### 清理日志
```bash
docker-compose logs --tail=0 -f
```

## 🐛 故障排查

### 问题1：服务无法启动
```bash
# 查看详细日志
docker-compose logs backend

# 检查端口占用
sudo netstat -tlnp | grep :8000
```

### 问题2：数据库连接失败
```bash
# 检查数据库状态
docker-compose exec postgres pg_isready -U aicoin

# 查看数据库日志
docker-compose logs postgres
```

### 问题3：Redis连接失败
```bash
# 检查Redis状态
docker-compose exec redis redis-cli ping

# 查看Redis日志
docker-compose logs redis
```

### 问题4：前端无法访问
```bash
# 检查Nginx配置
docker-compose exec nginx nginx -t

# 重启Nginx
docker-compose restart nginx
```

## 📈 性能优化建议

1. **数据库优化**
   - 定期备份数据库
   - 配置合适的连接池大小
   - 添加必要的索引

2. **Redis优化**
   - 配置持久化策略
   - 设置合理的内存限制
   - 定期清理过期键

3. **Nginx优化**
   - 启用Gzip压缩
   - 配置缓存策略
   - 使用CDN加速静态资源

4. **Docker优化**
   - 定期清理未使用的镜像和容器
   - 限制容器资源使用
   - 使用Docker卷进行数据持久化

## 🔒 安全建议

1. **更改默认密码**
   - 数据库密码
   - Redis密码（如启用）
   - JWT密钥

2. **配置防火墙**
   ```bash
   # 只开放必要端口
   sudo ufw allow 80/tcp
   sudo ufw allow 443/tcp
   sudo ufw allow 22/tcp
   sudo ufw enable
   ```

3. **定期更新**
   - 定期更新系统包
   - 定期更新Docker镜像
   - 定期更新依赖包

4. **备份策略**
   - 每日自动备份数据库
   - 备份.env文件
   - 备份SSL证书

## 📞 技术支持

如遇到问题，请查看：
1. 项目文档：`docs/`目录
2. 部署日志：`logs/`目录
3. Docker日志：`docker-compose logs`

## 🎉 部署成功！

恭喜！AIcoin v3.1 已成功部署到服务器。

访问地址：
- **主站**: http://jifenpay.cc
- **API文档**: http://jifenpay.cc/docs
- **管理后台**: http://jifenpay.cc/admin

祝交易顺利！🚀

