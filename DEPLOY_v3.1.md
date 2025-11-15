# 🚀 AIcoin v3.1 部署指令

## 📋 快速开始

### 在服务器上执行以下命令：

```bash
# 1. 进入项目目录
cd /path/to/AIcoin

# 2. 拉取最新代码
git pull origin main

# 3. 运行一键部署脚本
./scripts/deploy_and_test_v3.1.sh
```

脚本会自动完成：
- ✅ 数据库备份
- ✅ 更新依赖
- ✅ 运行迁移
- ✅ 自检测试
- ✅ 重启服务
- ✅ 健康检查

## 📊 验证部署

### 1. 检查服务状态

```bash
pm2 list
pm2 logs aicoin-backend --lines 20
```

### 2. 测试API端点

```bash
# 健康检查
curl http://localhost:8000/api/v1/intelligence/storage/system/health

# 系统指标
curl http://localhost:8000/api/v1/intelligence/storage/system/metrics

# 手动触发情报收集
curl -X POST http://localhost:8000/api/v1/intelligence/refresh
```

### 3. 访问前端

```
http://your-server-ip:3000
http://your-server-ip:3000/admin/intelligence/monitoring
```

## ✅ 成功标准

部署成功的标志：

- [ ] 后端服务返回 HTTP 200
- [ ] 前端页面可访问
- [ ] 情报收集功能正常
- [ ] 监控页面显示数据
- [ ] 无Critical级别错误

## 🔧 如果遇到问题

### 问题1: 服务启动失败

```bash
# 查看详细日志
pm2 logs aicoin-backend --err --lines 50

# 检查端口占用
lsof -i :8000
lsof -i :3000

# 手动启动测试
cd backend
uvicorn app.main:app --reload
```

### 问题2: 数据库连接失败

```bash
# 检查PostgreSQL状态
sudo systemctl status postgresql

# 检查Redis状态
redis-cli ping

# 检查Qdrant状态
curl http://localhost:6333
```

### 问题3: 依赖安装失败

```bash
# 清理缓存重新安装
cd backend
pip cache purge
pip install -r requirements.txt --upgrade --force-reinstall

cd ../frontend
rm -rf node_modules package-lock.json
npm install
```

## 📞 获取帮助

如遇到无法解决的问题，请提供：

1. 错误日志（`pm2 logs`）
2. 系统信息（`uname -a`, `python --version`, `node --version`）
3. Git版本（`git rev-parse HEAD`）
4. 环境变量（隐藏敏感信息）

## 🎯 v3.1 新特性

### 已优化的功能

1. **异步任务追踪** - 带重试机制（3次，指数退避）
2. **超时控制** - 多平台调用30秒超时
3. **OpenAI Embedding** - 真实向量化（text-embedding-3-small）
4. **代码重构** - 消除重复代码，提升可维护性
5. **完整测试** - 自检脚本和功能测试套件

### 新增文件

- `scripts/deploy_and_test_v3.1.sh` - 一键部署脚本
- `backend/scripts/self_check.py` - 基础自检
- `backend/scripts/test_v3.1_features.py` - 完整功能测试
- `docs/10-版本更新/v3.1_*.md` - 详细文档

## 📚 相关文档

- [v3.1 优化完成清单](docs/10-版本更新/v3.1_优化完成清单.md)
- [v3.1 最终部署报告](docs/10-版本更新/v3.1_最终部署报告.md)
- [v3.1 自检摘要](docs/10-版本更新/v3.1_自检摘要.md)

---

**版本**: v3.1.0  
**发布日期**: 2025-11-15  
**Git Commit**: 966195b  
**状态**: ✅ 已完成，等待部署验证

**开始部署吧！🚀**

