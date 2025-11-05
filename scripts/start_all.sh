#!/bin/bash

# AIcoin 系统完整启动脚本
# 用途：一键启动整个系统（数据库、后端、前端）

echo "🚀 开始启动 AIcoin 系统..."

# 1. 检查并启动 Docker
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker 未运行，请先启动 Docker Desktop"
    exit 1
fi

echo "✅ Docker 已运行"

# 2. 启动数据库服务（PostgreSQL, Redis, Qdrant）
echo "📦 启动数据库服务..."

# PostgreSQL
if ! docker ps | grep -q aicoin-postgres-prod; then
    if docker ps -a | grep -q aicoin-postgres-prod; then
        echo "  ▶️ 启动现有 PostgreSQL 容器..."
        docker start aicoin-postgres-prod
    else
        echo "  🆕 创建新的 PostgreSQL 容器..."
        docker run -d \
          --name aicoin-postgres-prod \
          --network deploy_aicoin-network \
          -e POSTGRES_USER=aicoin \
          -e POSTGRES_PASSWORD=aicoin_secure_password_2024 \
          -e POSTGRES_DB=aicoin \
          -p 5432:5432 \
          -v aicoin-postgres-data:/var/lib/postgresql/data \
          postgres:15
    fi
fi

# Redis
if ! docker ps | grep -q aicoin-redis-prod; then
    if docker ps -a | grep -q aicoin-redis-prod; then
        echo "  ▶️ 启动现有 Redis 容器..."
        docker start aicoin-redis-prod
    else
        echo "  🆕 创建新的 Redis 容器..."
        docker run -d \
          --name aicoin-redis-prod \
          --network deploy_aicoin-network \
          -p 6379:6379 \
          redis:7-alpine
    fi
fi

# Qdrant
if ! docker ps | grep -q aicoin-qdrant-prod; then
    if docker ps -a | grep -q aicoin-qdrant-prod; then
        echo "  ▶️ 启动现有 Qdrant 容器..."
        docker start aicoin-qdrant-prod
    else
        echo "  🆕 创建新的 Qdrant 容器..."
        docker run -d \
          --name aicoin-qdrant-prod \
          --network deploy_aicoin-network \
          -p 6333:6333 \
          -p 6334:6334 \
          -v aicoin-qdrant-data:/qdrant/storage \
          qdrant/qdrant:latest
    fi
fi

echo "✅ 数据库服务已启动"
echo "⏳ 等待数据库服务就绪..."
sleep 5

# 3. 构建并启动后端
echo "🔧 构建后端 Docker 镜像..."
cd backend
docker build -t deploy-backend . > /dev/null 2>&1

echo "🚀 启动后端服务..."

# 停止并删除旧的后端容器
docker stop aicoin-backend-prod-v2 > /dev/null 2>&1
docker rm aicoin-backend-prod-v2 > /dev/null 2>&1

# 启动新的后端容器
docker run -d \
  --name aicoin-backend-prod-v2 \
  --network deploy_aicoin-network \
  -p 8000:8000 \
  -e DATABASE_URL="postgresql+asyncpg://aicoin:aicoin_secure_password_2024@aicoin-postgres-prod:5432/aicoin" \
  -e REDIS_URL="redis://aicoin-redis-prod:6379/0" \
  -e QDRANT_HOST="aicoin-qdrant-prod" \
  -e QDRANT_PORT="6333" \
  -e DEEPSEEK_API_KEY="sk-c5a42c7110f047daa04e38e9d4fc3f5d" \
  -e HYPERLIQUID_PRIVATE_KEY="0xc67f5e32a46ddb85881d2f3785640dca83e01f74efeb1cd2c171b415e60e2d0f" \
  -e HYPERLIQUID_WALLET_ADDRESS="0x5Be3c6B0AC337ed37f93297b7Fe0233e8bb3E741" \
  -e ENVIRONMENT="testnet" \
  deploy-backend

echo "✅ 后端服务已启动"
echo "⏳ 等待后端服务就绪..."
sleep 8

# 测试后端是否正常
if curl -s http://localhost:8000/api/v1/ai/status > /dev/null 2>&1; then
    echo "✅ 后端 API 响应正常"
else
    echo "⚠️ 后端 API 可能还未完全就绪，请稍后再试"
fi

# 4. 启动前端
cd ../frontend
echo "🎨 启动前端服务..."

# 停止现有的前端进程
lsof -ti:3000 | xargs kill -9 2>/dev/null

# 启动前端（后台运行）
nohup npm run dev > /tmp/frontend.log 2>&1 &

echo "✅ 前端服务已启动"
echo "⏳ 等待前端服务就绪..."
sleep 5

# 测试前端是否正常
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ 前端页面响应正常"
else
    echo "⚠️ 前端页面可能还未完全就绪，请稍后再试"
fi

# 5. 显示系统状态
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎉 AIcoin 系统启动完成！"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 访问地址："
echo "  前端页面: http://localhost:3000"
echo "  后端 API: http://localhost:8000"
echo "  API 文档: http://localhost:8000/docs"
echo ""
echo "📊 服务状态："
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep -E "NAMES|aicoin"
echo ""
echo "📝 查看日志："
echo "  后端日志: docker logs -f aicoin-backend-prod-v2"
echo "  前端日志: tail -f /tmp/frontend.log"
echo ""
echo "🛑 停止系统: ./stop_all.sh"
echo ""

