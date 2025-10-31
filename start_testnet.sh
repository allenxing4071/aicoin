#!/bin/bash

echo "=========================================="
echo "🧪 AIcoin v2.0 测试网启动脚本"
echo "=========================================="
echo ""

# 检查.env.testnet文件
if [ ! -f .env.testnet ]; then
    echo "⚠️  .env.testnet 文件不存在"
    echo ""
    echo "请执行以下步骤："
    echo "1. 复制示例配置："
    echo "   cp .env.testnet.example .env.testnet"
    echo ""
    echo "2. 编辑 .env.testnet 并填入您的配置："
    echo "   - DEEPSEEK_API_KEY"
    echo "   - OPENAI_API_KEY (可选，用于向量化)"
    echo "   - HYPERLIQUID_WALLET_ADDRESS (测试网地址)"
    echo "   - HYPERLIQUID_PRIVATE_KEY (测试网私钥)"
    echo ""
    echo "3. 确认以下设置："
    echo "   - HYPERLIQUID_TESTNET=true"
    echo "   - TRADING_ENABLED=false (先观察模式)"
    echo ""
    read -p "按Enter继续创建配置文件..." 
    cp .env.testnet.example .env.testnet
    echo "✅ 已创建 .env.testnet，请编辑后重新运行此脚本"
    exit 1
fi

echo "✅ 找到 .env.testnet 配置文件"
echo ""

# 加载环境变量
export $(cat .env.testnet | grep -v '^#' | xargs)

echo "📋 当前配置："
echo "   - APP_VERSION: ${APP_VERSION:-2.0.0}"
echo "   - HYPERLIQUID_TESTNET: ${HYPERLIQUID_TESTNET:-true}"
echo "   - TRADING_ENABLED: ${TRADING_ENABLED:-false}"
echo "   - DECISION_INTERVAL: ${DECISION_INTERVAL:-300}秒"
echo "   - INITIAL_PERMISSION_LEVEL: ${INITIAL_PERMISSION_LEVEL:-L1}"
echo ""

# 检查必需的环境变量
missing_vars=()

if [ -z "$DEEPSEEK_API_KEY" ] || [ "$DEEPSEEK_API_KEY" = "sk-your-deepseek-api-key-here" ]; then
    missing_vars+=("DEEPSEEK_API_KEY")
fi

if [ -z "$HYPERLIQUID_WALLET_ADDRESS" ] || [ "$HYPERLIQUID_WALLET_ADDRESS" = "0xYourTestnetWalletAddress" ]; then
    missing_vars+=("HYPERLIQUID_WALLET_ADDRESS")
fi

if [ -z "$HYPERLIQUID_PRIVATE_KEY" ] || [ "$HYPERLIQUID_PRIVATE_KEY" = "0xYourTestnetPrivateKey" ]; then
    missing_vars+=("HYPERLIQUID_PRIVATE_KEY")
fi

if [ ${#missing_vars[@]} -gt 0 ]; then
    echo "❌ 以下必需的环境变量未配置："
    for var in "${missing_vars[@]}"; do
        echo "   - $var"
    done
    echo ""
    echo "请编辑 .env.testnet 文件并填入正确的值"
    exit 1
fi

echo "✅ 环境变量检查通过"
echo ""

# 停止旧容器
echo "🛑 停止旧容器（如果有）..."
docker-compose -f docker-compose.testnet.yml down

echo ""
echo "🚀 启动Docker服务（测试网专用配置）..."
echo ""

# 使用测试网专用配置启动所有服务
docker-compose -f docker-compose.testnet.yml up -d

echo ""
echo "⏳ 等待服务启动..."
sleep 15

# 检查服务状态
echo ""
echo "📊 检查服务状态..."
docker-compose -f docker-compose.testnet.yml ps

echo ""
echo "⏳ 等待Backend初始化..."
sleep 15

echo ""
echo "=========================================="
echo "✅ AIcoin v2.0 测试网已启动！"
echo "=========================================="
echo ""
echo "📊 访问地址："
echo "   - API文档:  http://localhost:8000/docs"
echo "   - 健康检查: http://localhost:8000/health"
echo "   - 系统状态: http://localhost:8000/api/v1/status"
echo "   - Qdrant:   http://localhost:6333/dashboard"
echo ""
echo "📋 查看日志："
echo "   docker-compose -f docker-compose.testnet.yml logs -f backend"
echo ""
echo "🔍 监控命令："
echo "   # 实时日志"
echo "   docker-compose -f docker-compose.testnet.yml logs -f backend | grep -E '(🔄|✅|❌|⚠️)'"
echo ""
echo "   # 查看决策"
echo "   docker-compose -f docker-compose.testnet.yml logs backend | grep '决策'"
echo ""
echo "   # 查看权限"
echo "   docker-compose -f docker-compose.testnet.yml logs backend | grep '权限'"
echo ""
echo "🛑 停止系统："
echo "   docker-compose -f docker-compose.testnet.yml down"
echo ""
echo "=========================================="
echo "⚠️  重要提醒："
echo "=========================================="
echo ""
if [ "$TRADING_ENABLED" = "true" ]; then
    echo "🚨 交易已启用！系统将自动执行交易"
    echo "   - 当前在测试网环境"
    echo "   - 请密切监控系统运行"
    echo "   - 发现问题立即停止（docker-compose down）"
else
    echo "✅ 交易未启用（观察模式）"
    echo "   - 系统会给出决策建议"
    echo "   - 但不会实际执行交易"
    echo "   - 确认系统正常后，修改 TRADING_ENABLED=true"
fi
echo ""
echo "📖 查看实现报告："
echo "   cat docs/v2.0实现报告.md"
echo ""
echo "Happy testing! 🧪"
echo ""

