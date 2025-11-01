#!/bin/bash

echo "=========================================="
echo "🚀 AIcoin v2.0 生产环境部署脚本"
echo "=========================================="
echo ""

# 检查.env.prod文件
if [ ! -f .env.prod ]; then
    echo "❌ .env.prod 文件不存在"
    echo ""
    echo "请执行以下步骤："
    echo "1. 复制示例配置："
    echo "   cp .env.prod.example .env.prod"
    echo ""
    echo "2. 编辑 .env.prod 并填入生产环境配置"
    echo ""
    exit 1
fi

echo "✅ 找到 .env.prod 配置文件"
echo ""

# 加载环境变量
export $(cat .env.prod | grep -v '^#' | xargs)

echo "📋 当前配置："
echo "   - APP_VERSION: ${APP_VERSION:-2.0.0}"
echo "   - HYPERLIQUID_TESTNET: ${HYPERLIQUID_TESTNET:-false}"
echo "   - TRADING_ENABLED: ${TRADING_ENABLED:-false}"
echo "   - DECISION_INTERVAL: ${DECISION_INTERVAL:-300}秒"
echo "   - INITIAL_PERMISSION_LEVEL: ${INITIAL_PERMISSION_LEVEL:-L1}"
echo ""

# 检查必需的环境变量
missing_vars=()

if [ -z "$DEEPSEEK_API_KEY" ] || [ "$DEEPSEEK_API_KEY" = "sk-your-deepseek-api-key" ]; then
    missing_vars+=("DEEPSEEK_API_KEY")
fi

if [ -z "$HYPERLIQUID_WALLET_ADDRESS" ] || [ "$HYPERLIQUID_WALLET_ADDRESS" = "0xYourMainnetWalletAddress" ]; then
    missing_vars+=("HYPERLIQUID_WALLET_ADDRESS")
fi

if [ -z "$HYPERLIQUID_PRIVATE_KEY" ] || [ "$HYPERLIQUID_PRIVATE_KEY" = "0xYourMainnetPrivateKey" ]; then
    missing_vars+=("HYPERLIQUID_PRIVATE_KEY")
fi

if [ -z "$POSTGRES_PASSWORD" ] || [ "$POSTGRES_PASSWORD" = "your-strong-postgres-password" ]; then
    missing_vars+=("POSTGRES_PASSWORD")
fi

if [ -z "$REDIS_PASSWORD" ] || [ "$REDIS_PASSWORD" = "your-strong-redis-password" ]; then
    missing_vars+=("REDIS_PASSWORD")
fi

if [ -z "$SECRET_KEY" ] || [ "$SECRET_KEY" = "your-super-secret-key-change-this-in-production" ]; then
    missing_vars+=("SECRET_KEY")
fi

if [ ${#missing_vars[@]} -gt 0 ]; then
    echo "❌ 以下必需的环境变量未配置："
    for var in "${missing_vars[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "请编辑 .env.prod 文件并填入正确的值"
    exit 1
fi

echo "✅ 环境变量检查通过"
echo ""

# 确认部署
echo "⚠️  警告：这将部署到生产环境！"
echo ""
read -p "确认继续部署？(yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ 部署已取消"
    exit 0
fi

echo ""
echo "🛑 停止旧容器（如果有）..."
docker-compose -f docker-compose.prod.yml down

echo ""
echo "🏗️  构建Docker镜像..."
docker-compose -f docker-compose.prod.yml build --no-cache

echo ""
echo "🚀 启动所有服务..."
docker-compose -f docker-compose.prod.yml up -d

echo ""
echo "⏳ 等待服务启动..."
sleep 20

# 检查服务状态
echo ""
echo "📊 检查服务状态..."
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "⏳ 等待Backend初始化..."
sleep 15

# 检查健康状态
echo ""
echo "🏥 检查服务健康状态..."
echo ""

# 检查Backend
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend: 健康"
else
    echo "❌ Backend: 不健康"
fi

# 检查Frontend
if curl -s http://localhost:3000 > /dev/null; then
    echo "✅ Frontend: 健康"
else
    echo "❌ Frontend: 不健康"
fi

# 检查Nginx
if curl -s http://localhost/health > /dev/null; then
    echo "✅ Nginx: 健康"
else
    echo "❌ Nginx: 不健康"
fi

echo ""
echo "=========================================="
echo "✅ AIcoin v2.0 生产环境部署完成！"
echo "=========================================="
echo ""
echo "📊 访问地址："
echo "   - 前端:      http://localhost"
echo "   - API文档:   http://localhost/api/docs"
echo "   - 健康检查:  http://localhost/health"
echo "   - 系统状态:  http://localhost/api/v1/status"
echo "   - Qdrant:    http://localhost:6333/dashboard"
echo ""
echo "📋 查看日志："
echo "   docker-compose -f docker-compose.prod.yml logs -f backend"
echo ""
echo "🔍 监控命令："
echo "   # 实时日志"
echo "   docker-compose -f docker-compose.prod.yml logs -f backend | grep -E '(🔄|✅|❌|⚠️)'"
echo ""
echo "   # 查看决策"
echo "   docker-compose -f docker-compose.prod.yml logs backend | grep '决策'"
echo ""
echo "   # 查看权限"
echo "   docker-compose -f docker-compose.prod.yml logs backend | grep '权限'"
echo ""
echo "🛑 停止系统："
echo "   docker-compose -f docker-compose.prod.yml down"
echo ""
echo "=========================================="
echo "⚠️  重要提醒："
echo "=========================================="
echo ""
if [ "$TRADING_ENABLED" = "true" ]; then
    echo "🚨 交易已启用！系统将自动执行交易"
    echo "   - 当前在生产环境（主网）"
    echo "   - 请密切监控系统运行"
    echo "   - 发现问题立即停止（docker-compose down）"
else
    echo "✅ 交易未启用（观察模式）"
    echo "   - 系统会给出决策建议"
    echo "   - 但不会实际执行交易"
    echo "   - 确认系统正常后，修改 TRADING_ENABLED=true"
fi
echo ""
echo "📖 查看文档："
echo "   cat docs/部署指南.md"
echo ""
echo "Happy trading! 🚀"
echo ""

