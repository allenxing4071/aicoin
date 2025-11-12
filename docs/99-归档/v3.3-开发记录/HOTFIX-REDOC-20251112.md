# 🔥 HOTFIX: Redoc 页面无法访问

**日期**：2025-11-12  
**优先级**：中等  
**影响**：API 文档页面 `/docs` 和 `/redoc` 无法访问

## ⚡ 快速修复（1分钟）

```bash
# SSH 登录到服务器后执行
cd /path/to/AIcoin
sudo bash scripts/update-nginx-config.sh
```

**就这么简单！** 脚本会自动完成所有操作。

## 📋 问题说明

- **现象**：访问 `https://jifenpay.cc/redoc` 返回 404
- **原因**：Nginx 将 `/docs` 和 `/redoc` 路由到了前端而不是后端
- **修复**：更新 Nginx 配置，将文档路由正确代理到后端

## 🔍 验证修复

```bash
# 应该都返回 200 OK
curl -I https://jifenpay.cc/docs
curl -I https://jifenpay.cc/redoc
curl -I https://jifenpay.cc/openapi.json
```

## 📚 详细文档

完整的技术分析和修复说明见：`docs/故障修复-Redoc页面无法访问.md`

## 🔄 回滚方案

如果出现问题，脚本会自动创建备份，可以手动回滚：

```bash
# 查看备份目录（脚本执行时会显示路径）
BACKUP_DIR="/var/backups/nginx-YYYYMMDD-HHMMSS"

# 恢复备份
docker cp $BACKUP_DIR/nginx.conf nginx:/etc/nginx/nginx.conf
docker exec nginx nginx -s reload
```

## ✅ 变更清单

- ✅ `deploy/nginx/nginx.conf` - 生产 HTTPS 配置
- ✅ `deploy/nginx/nginx-http-only.conf` - 临时 HTTP 配置
- ✅ `nginx/nginx.conf` - 本地开发配置
- ✅ `scripts/update-nginx-config.sh` - 自动化部署脚本
- ✅ `docs/故障修复-Redoc页面无法访问.md` - 详细技术文档

## 📝 Git 提交

```bash
git add .
git commit -m "fix(nginx): 修复 /docs 和 /redoc 路由无法访问的问题

- 添加 API 文档路由规则到所有 Nginx 配置
- 创建自动化更新脚本
- 添加详细的故障修复文档

Issue: /redoc 和 /docs 返回 404
Root Cause: Nginx 配置将这些路由代理到前端而非后端
Solution: 添加正则 location 规则匹配 docs/redoc/openapi.json"
```

---

**需要帮助？** 请查看详细文档或联系技术负责人。

