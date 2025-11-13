#!/bin/bash

# 重置 AI 平台成本脚本

echo "🚀 开始部署和重置成本..."
echo ""

# 服务器信息
SERVER="root@jifenpay.cc"
PROJECT_DIR="/root/aicoin"

echo "📦 步骤 1/4: 拉取最新代码..."
ssh -o StrictHostKeyChecking=no $SERVER "cd $PROJECT_DIR && git pull origin main"

echo ""
echo "🔄 步骤 2/4: 重启后端服务..."
ssh -o StrictHostKeyChecking=no $SERVER "cd $PROJECT_DIR && docker-compose restart backend"

echo ""
echo "⏳ 步骤 3/4: 等待服务启动..."
sleep 15

echo ""
echo "🔧 步骤 4/4: 重置平台成本..."

# 先尝试登录获取 token
echo "正在获取管理员 token..."
TOKEN_RESPONSE=$(curl -s -X POST https://jifenpay.cc/api/v1/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin123"}')

TOKEN=$(echo $TOKEN_RESPONSE | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
  echo "❌ 获取 token 失败，请手动执行："
  echo ""
  echo "curl -X POST https://jifenpay.cc/api/v1/ai-cost/reset-costs \\"
  echo "  -H \"Authorization: Bearer YOUR_TOKEN\" \\"
  echo "  -H \"Content-Type: application/json\""
  exit 1
fi

echo "✅ Token 获取成功"
echo ""

# 执行重置
echo "正在重置成本..."
RESET_RESPONSE=$(curl -s -X POST https://jifenpay.cc/api/v1/ai-cost/reset-costs \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

echo ""
echo "📊 重置结果:"
echo $RESET_RESPONSE | python3 -m json.tool 2>/dev/null || echo $RESET_RESPONSE

echo ""
echo "✅ 操作完成！"
echo ""
echo "请访问 https://jifenpay.cc/admin/ai-cost 查看结果"

