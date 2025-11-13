#!/bin/bash

# AIcoin 自动部署和重置成本脚本
# 用途: 在服务器上执行此脚本完成部署和成本重置

set -e  # 遇到错误立即退出

echo "🚀 开始 AIcoin 部署流程..."
echo "================================"

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# 1. 拉取最新代码
echo ""
echo "📦 步骤 1/5: 拉取最新代码..."
git fetch origin
git pull origin main
CURRENT_COMMIT=$(git log -1 --oneline)
echo "✅ 当前版本: $CURRENT_COMMIT"

# 2. 重启后端服务
echo ""
echo "🔄 步骤 2/5: 重启后端服务..."
docker-compose restart backend
echo "✅ 后端服务重启完成"

# 3. 等待服务启动
echo ""
echo "⏳ 步骤 3/5: 等待服务启动 (20秒)..."
sleep 20

# 4. 测试 API 可用性
echo ""
echo "🔍 步骤 4/5: 测试 API 可用性..."
API_TEST=$(curl -s -o /dev/null -w "%{http_code}" https://jifenpay.cc/api/v1/ai-cost/summary)
if [ "$API_TEST" = "200" ]; then
    echo "✅ API 服务正常"
else
    echo "⚠️  API 返回状态码: $API_TEST"
    echo "等待额外 10 秒..."
    sleep 10
fi

# 5. 执行重置成本
echo ""
echo "💰 步骤 5/5: 重置平台成本..."

# 获取管理员 Token
echo "   - 获取管理员 Token..."
TOKEN=$(curl -s -X POST https://jifenpay.cc/api/v1/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}' \
  | grep -o '"token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo "❌ 获取 Token 失败"
    exit 1
fi

echo "   - Token 获取成功"

# 执行重置
echo "   - 执行重置操作..."
RESET_RESULT=$(curl -s -X POST https://jifenpay.cc/api/v1/ai-cost/reset-costs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

echo ""
echo "📊 重置结果:"
echo "$RESET_RESULT" | python3 -m json.tool 2>/dev/null || echo "$RESET_RESULT"

# 6. 验证结果
echo ""
echo "✅ 验证结果..."
SUMMARY=$(curl -s https://jifenpay.cc/api/v1/ai-cost/summary)
echo "$SUMMARY" | python3 -m json.tool 2>/dev/null | head -20

echo ""
echo "================================"
echo "🎉 部署完成！"
echo ""
echo "请访问以下地址验证:"
echo "  - 管理后台: https://jifenpay.cc/admin/ai-cost"
echo "  - 价格管理: https://jifenpay.cc/admin/ai-pricing"
echo ""
echo "预期结果: 所有成本显示为 ¥0.00"
echo "================================"

