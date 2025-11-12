# 🚀 部署检查清单 - Redoc 路由修复

## 📝 变更摘要

**修复项目**：API 文档页面 `/docs` 和 `/redoc` 无法访问  
**修复日期**：2025-11-12  
**紧急程度**：中等（不影响核心功能，仅影响开发者体验）

## ✅ 部署前检查

### 1. 代码审查
- [ ] 确认所有 Nginx 配置文件已更新
  - [ ] `deploy/nginx/nginx.conf`
  - [ ] `deploy/nginx/nginx-http-only.conf`
  - [ ] `nginx/nginx.conf`
- [ ] 确认自动化脚本已创建：`scripts/update-nginx-config.sh`
- [ ] 确认文档已完善

### 2. 本地测试（可选）
```bash
# 如果你有本地环境，可以先测试
docker-compose restart nginx
curl http://localhost/docs
curl http://localhost/redoc
```

### 3. Git 提交
```bash
# 查看变更
git status
git diff

# 添加所有变更
git add deploy/nginx/*.conf
git add nginx/nginx.conf
git add scripts/update-nginx-config.sh
git add docs/故障修复-Redoc页面无法访问.md
git add HOTFIX-REDOC-20251112.md
git add DEPLOYMENT-CHECKLIST.md

# 提交
git commit -m "fix(nginx): 修复 /docs 和 /redoc 路由无法访问的问题

问题描述:
- 访问 https://jifenpay.cc/redoc 返回 404
- 访问 https://jifenpay.cc/docs 返回前端 404 页面

根本原因:
- Nginx 配置中缺少对 /docs 和 /redoc 的路由规则
- 所有非 /api/ 和 /ws/ 的请求都被代理到前端
- 前端没有定义这些路由，导致 404

解决方案:
- 在 Nginx 配置中添加正则 location 规则
- 将 /docs、/redoc、/openapi.json 代理到后端
- 规则必须放在通用 / 规则之前

变更文件:
- deploy/nginx/nginx.conf
- deploy/nginx/nginx-http-only.conf
- nginx/nginx.conf
- scripts/update-nginx-config.sh (新增)
- docs/故障修复-Redoc页面无法访问.md (新增)
- HOTFIX-REDOC-20251112.md (新增)

测试方法:
curl -I https://jifenpay.cc/docs
curl -I https://jifenpay.cc/redoc
curl -I https://jifenpay.cc/openapi.json

预期结果: 所有端点返回 200 OK"

# 推送到远程
git push origin main  # 或你的分支名
```

## 🚀 部署步骤

### 方式 A：自动化部署（推荐）⭐

```bash
# 1. SSH 登录到服务器
ssh user@jifenpay.cc

# 2. 进入项目目录
cd /path/to/AIcoin

# 3. 拉取最新代码
git pull origin main

# 4. 运行自动化脚本
sudo bash scripts/update-nginx-config.sh

# 5. 查看输出，确认所有步骤都成功
# 脚本会自动完成：
#   - 备份当前配置
#   - 验证新配置语法
#   - 更新配置文件
#   - 重新加载 Nginx
#   - 验证修复结果
```

### 方式 B：手动部署

```bash
# 1-3. 同方式 A

# 4. 备份当前配置
docker exec nginx mkdir -p /tmp/nginx-backup
docker exec nginx cp /etc/nginx/nginx.conf /tmp/nginx-backup/
docker cp nginx:/tmp/nginx-backup /var/backups/nginx-$(date +%Y%m%d-%H%M%S)

# 5. 测试新配置语法（在主机上）
docker run --rm \
  -v $(pwd)/deploy/nginx/nginx.conf:/etc/nginx/nginx.conf:ro \
  nginx nginx -t

# 6. 如果测试通过，复制到容器
docker cp deploy/nginx/nginx.conf nginx:/etc/nginx/nginx.conf

# 7. 在容器内再次测试
docker exec nginx nginx -t

# 8. 重新加载 Nginx
docker exec nginx nginx -s reload

# 9. 等待服务稳定
sleep 2

# 10. 验证修复
curl -I https://jifenpay.cc/docs
curl -I https://jifenpay.cc/redoc
curl -I https://jifenpay.cc/openapi.json
```

## ✅ 部署后验证

### 1. 基本功能测试
```bash
# 测试 Swagger UI
curl -s https://jifenpay.cc/docs | grep -q "swagger-ui" && echo "✓ Swagger UI 正常"

# 测试 ReDoc
curl -s https://jifenpay.cc/redoc | grep -q "redoc" && echo "✓ ReDoc 正常"

# 测试 OpenAPI JSON
curl -s https://jifenpay.cc/openapi.json | jq '.openapi' && echo "✓ OpenAPI JSON 正常"
```

### 2. HTTP 状态码检查
```bash
# 应该都返回 200
curl -I https://jifenpay.cc/docs | grep "HTTP"
curl -I https://jifenpay.cc/redoc | grep "HTTP"
curl -I https://jifenpay.cc/openapi.json | grep "HTTP"
```

### 3. 浏览器验证
- [ ] 访问 https://jifenpay.cc/docs 查看 Swagger UI
- [ ] 访问 https://jifenpay.cc/redoc 查看 ReDoc
- [ ] 验证 API 文档可以正常浏览和交互

### 4. 原有功能验证（回归测试）
```bash
# 确保修改没有影响其他功能
curl -I https://jifenpay.cc/api/v1/health
curl -I https://jifenpay.cc/  # 前端首页
```

## 🔄 回滚方案

如果部署后出现问题：

### 快速回滚
```bash
# 1. 恢复备份（自动化脚本会显示备份路径）
BACKUP_DIR="/var/backups/nginx-YYYYMMDD-HHMMSS"
docker cp $BACKUP_DIR/nginx.conf nginx:/etc/nginx/nginx.conf

# 2. 重新加载
docker exec nginx nginx -s reload

# 3. 验证
curl -I https://jifenpay.cc/
```

### 完全回滚（Git）
```bash
# 回滚到上一个提交
git revert HEAD
git push origin main

# 然后重新部署旧配置
docker cp deploy/nginx/nginx.conf nginx:/etc/nginx/nginx.conf
docker exec nginx nginx -s reload
```

## 📊 监控和观察

部署后请监控以下指标（至少 1 小时）：

- [ ] Nginx 访问日志：查看 `/docs` 和 `/redoc` 的访问情况
  ```bash
  docker logs -f nginx | grep -E "(docs|redoc)"
  ```

- [ ] Nginx 错误日志：确认没有新的错误
  ```bash
  docker logs -f nginx | grep -i error
  ```

- [ ] 后端服务状态：确认后端服务正常
  ```bash
  docker logs -f backend | tail -50
  ```

- [ ] 系统资源：确认没有异常的 CPU/内存占用
  ```bash
  docker stats
  ```

## 📝 已知限制

1. **认证状态**：当前 `/docs` 和 `/redoc` 配置为公开访问，但实际的 API 调用仍需 Token 认证
2. **缓存**：浏览器可能缓存了旧的 404 页面，需要强制刷新（Ctrl+F5）
3. **CDN**：如果使用 CDN，可能需要清除缓存

## 🎯 成功标准

以下所有条件都满足才算部署成功：

- [x] Git 提交完成并推送
- [ ] 服务器代码已更新（git pull）
- [ ] Nginx 配置已更新
- [ ] Nginx 成功重新加载（无错误）
- [ ] `/docs` 返回 200 并显示 Swagger UI
- [ ] `/redoc` 返回 200 并显示 ReDoc
- [ ] `/openapi.json` 返回 200 并包含有效 JSON
- [ ] 原有功能（前端、API）仍然正常工作
- [ ] 无新的错误日志产生
- [ ] 持续监控 1 小时无异常

## 📞 紧急联系

如果部署过程中遇到问题：

1. **不要慌**：配置已备份，可以随时回滚
2. **记录错误**：保存错误日志和截图
3. **回滚优先**：如果影响生产，立即回滚
4. **事后分析**：回滚后再分析问题原因

## 📚 相关文档

- 详细技术文档：`docs/故障修复-Redoc页面无法访问.md`
- 快速参考：`HOTFIX-REDOC-20251112.md`
- 自动化脚本：`scripts/update-nginx-config.sh`

---

**检查清单完成时间**：________________  
**部署执行人员**：________________  
**部署完成时间**：________________  
**验证人员**：________________

