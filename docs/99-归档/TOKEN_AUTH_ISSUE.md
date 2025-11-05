# JWT Token 验证问题报告

## 🐛 问题描述

用户管理页面 (`/admin/users`) 一直返回 `401 Unauthorized` 错误，提示"无效的令牌"。

## 🔍 问题分析

经过详细调查，发现以下问题：

1. **症状**: 登录API返回200和token，但使用该token访问`/api/v1/admin/users`时返回401
2. **错误日志**: `Token verification failed: InvalidSignatureError: Signature verification failed`
3. **根本原因**: Token创建和验证使用的`JWT_SECRET_KEY`不一致

## 📋 已尝试的修复方案

### 1. 统一KEY设置 ✅
- 在`.env`中添加了`JWT_SECRET_KEY=your-secret-key-here-change-in-production`
- 确保`SECRET_KEY`和`JWT_SECRET_KEY`使用相同的值

### 2. 更新代码使用JWT_SECRET_KEY ✅
- 将`auth.py`中所有`settings.SECRET_KEY`改为`settings.JWT_SECRET_KEY`
- 在`create_access_token`和`verify_admin_token`中统一使用`JWT_SECRET_KEY`

### 3. 禁用uvicorn的--reload模式 ✅
- 从`docker-compose.yml`中移除`--reload`参数
- 避免热重载导致的模块重复初始化问题

### 4. 完全重启Docker容器 ✅
- 执行`docker-compose down`和`docker-compose up -d`
- 确保所有配置重新加载

## 🔧 容器内验证结果

```python
# 在容器内部测试
settings.SECRET_KEY     : your-secret-key-here-change-in-production
settings.JWT_SECRET_KEY : your-secret-key-here-change-in-production
是否相同? True

# 但是...
使用JWT_SECRET_KEY验证新生成的token: ❌ 失败 (Signature verification failed)
```

## 🤔 可能的原因

1. **FastAPI/uvicorn的模块缓存问题**: 即使重启容器，某些模块可能still使用旧的KEY值
2. **pydantic-settings的延迟加载**: `settings`对象可能在不同的请求中被重新初始化
3. **JWT库的缓存**: jwt.encode/decode内部可能有某种KEY缓存机制

## 💡 建议的解决方案

### 方案A: 使用环境变量强制重新初始化
在`docker-compose.yml`中添加一个新的环境变量强制刷新：
```yaml
environment:
  - FORCE_KEY_REFRESH=true
  - SECRET_KEY=...
  - JWT_SECRET_KEY=...
```

### 方案B: 简化KEY管理
只使用一个`SECRET_KEY`，删除`JWT_SECRET_KEY`：
```python
# auth.py
encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)
payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
```

### 方案C: 重新构建Docker镜像
```bash
cd deploy
docker-compose down
docker-compose build --no-cache backend
docker-compose up -d
```

## 📝 下一步行动

建议明天：
1. 尝试方案B（最简单）
2. 如果不行，尝试方案C（完全重建）
3. 添加更详细的debug logging来追踪KEY的实际值

## ⚠️ 临时解决方案

作为临时措施，可以考虑：
1. 暂时禁用JWT验证（仅用于开发环境）
2. 使用固定的、hard-coded的KEY值进行测试
3. 直接在数据库中手动创建admin_token

---

**创建时间**: 2025-11-05 00:55  
**状态**: 未解决  
**优先级**: P0 (阻塞用户管理功能)


