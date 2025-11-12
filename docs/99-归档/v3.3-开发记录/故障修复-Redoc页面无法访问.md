# 故障修复报告：Redoc 页面无法访问

## 一、问题概述

**问题描述**：访问 `https://jifenpay.cc/redoc` 返回 404 错误

**发现时间**：2025-11-12

**影响范围**：
- `/redoc` - ReDoc API 文档页面
- `/docs` - Swagger UI 文档页面（同样受影响）
- `/openapi.json` - OpenAPI 规范文件（正常访问）

## 二、问题根因分析

### 2.1 技术架构

系统采用三层代理架构：

```
用户请求
  ↓
Nginx (反向代理)
  ↓
  ├─→ /api/*      → Backend (FastAPI, port 8000)
  ├─→ /ws/*       → Backend (WebSocket)
  └─→ /*          → Frontend (Next.js, port 3000)
```

### 2.2 问题定位

通过以下测试确认问题：

```bash
# 测试 1: redoc 返回 404
$ curl -I https://jifenpay.cc/redoc
HTTP/1.1 404 Not Found
Server: nginx/1.18.0 (Ubuntu)

# 测试 2: docs 返回 HTML 但实际被路由到前端
$ curl https://jifenpay.cc/docs
返回前端 Next.js 的 404 页面

# 测试 3: openapi.json 正常访问
$ curl -I https://jifenpay.cc/openapi.json
HTTP/1.1 200 OK

# 测试 4: 后端确实定义了这些路由
$ grep -n "redoc\|docs" backend/app/main.py
528:@app.get("/redoc", response_class=HTMLResponse, include_in_schema=False)
515:@app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
```

### 2.3 根本原因

**Nginx 配置问题**：

原配置中，Nginx 的路由规则如下：

```nginx
location /api/ {
    proxy_pass http://backend;
}

location / {
    proxy_pass http://frontend;  # 所有其他请求都到前端
}
```

由于 Nginx 的 location 匹配规则：
1. `/redoc` 和 `/docs` 不匹配 `/api/` 前缀
2. 因此被 `location /` 规则捕获
3. 请求被代理到前端 Next.js
4. 前端没有定义这些路由，返回 404

**为什么 openapi.json 正常？**

因为在 `nginx-http-only.conf` 中有单独的 location 规则：

```nginx
location /openapi.json {
    proxy_pass http://backend/openapi.json;
}
```

但这个规则在 HTTPS 版本的 `nginx.conf` 中被遗漏了。

## 三、解决方案

### 3.1 修复方式

在所有 Nginx 配置文件中，添加 API 文档路由规则，放在 `/api/` 规则**之前**：

```nginx
# API 文档路由 - 代理到后端
location ~ ^/(docs|redoc|openapi.json)$ {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}
```

### 3.2 修改的文件

以下三个配置文件均已更新：

1. **`deploy/nginx/nginx.conf`** - 生产环境 HTTPS 配置
2. **`deploy/nginx/nginx-http-only.conf`** - 临时 HTTP-only 配置
3. **`nginx/nginx.conf`** - 本地开发环境配置

### 3.3 部署步骤

#### 方式 A：使用自动化脚本（推荐）

```bash
# 在服务器上执行
cd /path/to/AIcoin
sudo bash scripts/update-nginx-config.sh
```

脚本会自动完成：
- 备份当前配置
- 测试新配置语法
- 更新配置文件
- 重新加载 Nginx
- 验证修复结果

#### 方式 B：手动部署

```bash
# 1. 备份当前配置
docker exec nginx cp /etc/nginx/nginx.conf /etc/nginx/nginx.conf.backup

# 2. 测试新配置文件语法
docker run --rm -v $(pwd)/deploy/nginx/nginx.conf:/etc/nginx/nginx.conf:ro nginx nginx -t

# 3. 更新配置文件
docker cp deploy/nginx/nginx.conf nginx:/etc/nginx/nginx.conf

# 4. 在容器内测试配置
docker exec nginx nginx -t

# 5. 重新加载 Nginx
docker exec nginx nginx -s reload

# 6. 验证修复
curl -I https://jifenpay.cc/docs
curl -I https://jifenpay.cc/redoc
curl -I https://jifenpay.cc/openapi.json
```

## 四、验证测试

### 4.1 功能验证

```bash
# 测试 1: Swagger UI
curl -s https://jifenpay.cc/docs | grep -q "swagger-ui" && echo "✓ Swagger UI OK"

# 测试 2: ReDoc
curl -s https://jifenpay.cc/redoc | grep -q "redoc" && echo "✓ ReDoc OK"

# 测试 3: OpenAPI JSON
curl -s https://jifenpay.cc/openapi.json | grep -q "openapi" && echo "✓ OpenAPI OK"
```

### 4.2 预期结果

所有三个端点应该返回 200 OK，并且：
- `/docs` 显示 Swagger UI 界面
- `/redoc` 显示 ReDoc 界面
- `/openapi.json` 返回完整的 OpenAPI 规范 JSON

## 五、经验总结

### 5.1 Nginx location 匹配规则

优先级从高到低：
1. `location =` - 精确匹配
2. `location ^~` - 前缀匹配（匹配后不再正则）
3. `location ~` 或 `~*` - 正则匹配
4. `location /` - 前缀匹配

**关键点**：
- 我们使用正则匹配 `location ~ ^/(docs|redoc|openapi.json)$`
- 必须放在通用前缀 `location /` **之前**
- 否则会被 `location /` 先匹配并代理到前端

### 5.2 配置管理建议

1. **集中管理配置**：所有环境的 Nginx 配置应该在修改时同步更新
2. **测试驱动**：先在本地测试，再部署到生产
3. **版本控制**：所有配置变更必须提交 Git
4. **自动化部署**：使用脚本避免手动操作错误
5. **立即验证**：配置变更后立即进行功能验证

### 5.3 后续预防措施

1. **监控告警**：添加对 `/docs` 和 `/redoc` 端点的健康检查
2. **CI/CD 集成**：配置文件变更时自动运行语法检查
3. **文档完善**：更新运维文档，记录所有需要代理到后端的路由
4. **定期审计**：定期检查 Nginx 配置与后端路由的一致性

## 六、相关文件清单

### 修改的配置文件
- `deploy/nginx/nginx.conf`
- `deploy/nginx/nginx-http-only.conf`
- `nginx/nginx.conf`

### 新增的工具
- `scripts/update-nginx-config.sh` - Nginx 配置更新脚本

### 文档
- 本文件：`docs/故障修复-Redoc页面无法访问.md`

## 七、附录

### A. 完整的 Nginx Location 配置

```nginx
# API 文档路由 - 代理到后端（必须在 /api/ 之前）
location ~ ^/(docs|redoc|openapi.json)$ {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
}

# API 路由 - 代理到后端
location /api/ {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_cache_bypass $http_upgrade;
    
    # 超时设置
    proxy_connect_timeout 60s;
    proxy_send_timeout 60s;
    proxy_read_timeout 60s;
}

# WebSocket 支持
location /ws/ {
    proxy_pass http://backend;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection "upgrade";
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # WebSocket 超时设置
    proxy_connect_timeout 7d;
    proxy_send_timeout 7d;
    proxy_read_timeout 7d;
}

# 前端应用 - 代理到 Next.js（放在最后）
location / {
    proxy_pass http://frontend;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    proxy_cache_bypass $http_upgrade;
    
    # Next.js 特定设置
    proxy_buffering off;
    proxy_redirect off;
}
```

### B. FastAPI 路由定义

```python
# backend/app/main.py

@app.get("/docs", response_class=HTMLResponse, include_in_schema=False)
async def custom_swagger_ui():
    """Swagger UI - 公开访问（实际API调用仍需Token认证）"""
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui-bundle.js",
        swagger_css_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@5/swagger-ui.css",
    )

@app.get("/redoc", response_class=HTMLResponse, include_in_schema=False)
async def custom_redoc():
    """ReDoc - 公开访问（实际API调用仍需Token认证）"""
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=f"{app.title} - ReDoc",
        redoc_js_url="https://cdn.jsdelivr.net/npm/redoc@next/bundles/redoc.standalone.js",
    )
```

---

**报告编写时间**：2025-11-12  
**修复完成时间**：待部署  
**编写人员**：AI Assistant (Cursor)

