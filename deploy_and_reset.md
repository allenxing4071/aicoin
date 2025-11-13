# 部署和重置成本操作指南

## 当前状态

- ✅ 代码已推送到 GitHub
- ⚠️ 服务器需要拉取最新代码并重启

## 操作步骤

### 1. 登录服务器并部署

```bash
# SSH 登录（需要您的密钥）
ssh root@jifenpay.cc

# 进入项目目录
cd /root/aicoin

# 拉取最新代码
git pull origin main

# 重启后端服务
docker-compose restart backend

# 查看日志确认启动成功
docker-compose logs -f backend | head -50
```

### 2. 重置成本

部署完成后，执行以下命令：

```bash
# 获取管理员 Token
TOKEN=$(curl -s -X POST https://jifenpay.cc/api/v1/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  | grep -o '"token":"[^"]*' | cut -d'"' -f4)

# 重置所有平台成本
curl -X POST https://jifenpay.cc/api/v1/ai-cost/reset-costs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  | python3 -m json.tool
```

### 3. 验证结果

```bash
# 查看当前成本（应该都是 0）
curl -s https://jifenpay.cc/api/v1/ai-cost/summary | python3 -m json.tool
```

或者直接访问：https://jifenpay.cc/admin/ai-cost

应该看到：
- **总成本**: ¥0.00
- **本月成本**: ¥0.00
- **今日成本**: ¥0.00

## 预期结果

重置成功后会返回：

```json
{
  "success": true,
  "message": "已重置 X 个平台的成本",
  "data": {
    "reset_count": 5,
    "old_total_cost": 3.65
  }
}
```

## 后续

重置后，每次 AI 调用都会使用新的定价管理器计算成本：

- ✅ DeepSeek: ¥0.001/1K tokens (输入)
- ✅ Qwen Plus: ¥0.004/1K tokens (输入)
- ✅ 支持缓存价格
- ✅ 所有价格都是 2025-11-13 最新官方价格

## 如果遇到问题

1. **404 错误**：后端还没重启完成，等待 10-20 秒后重试
2. **401 错误**：Token 过期，重新获取
3. **403 错误**：权限不足，确认使用 admin 账号

## 一键脚本（需要 SSH 密钥配置）

如果您配置了 SSH 密钥，可以使用：

```bash
cd /Users/xinghailong/Documents/soft/AIcoin
./reset_costs.sh
```

