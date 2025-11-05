#!/bin/bash

# AIcoin 系统完整停止脚本

echo "🛑 停止 AIcoin 系统..."

# 1. 停止前端
echo "  🎨 停止前端服务..."
lsof -ti:3000 | xargs kill -9 2>/dev/null
echo "  ✅ 前端已停止"

# 2. 停止后端
echo "  🔧 停止后端服务..."
docker stop aicoin-backend-prod-v2 > /dev/null 2>&1
echo "  ✅ 后端已停止"

# 3. 停止数据库服务（可选，如果需要完全关闭）
read -p "是否停止数据库服务？(y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "  📦 停止数据库服务..."
    docker stop aicoin-postgres-prod aicoin-redis-prod aicoin-qdrant-prod > /dev/null 2>&1
    echo "  ✅ 数据库服务已停止"
fi

echo ""
echo "✅ AIcoin 系统已停止"
echo ""
echo "📊 当前运行的容器："
docker ps --format "table {{.Names}}\t{{.Status}}" | grep -E "NAMES|aicoin"
echo ""

