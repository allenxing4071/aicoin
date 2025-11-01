#!/bin/bash

echo "=========================================="
echo "🏗️  AIcoin v2.0 Docker镜像构建脚本"
echo "=========================================="
echo ""

# 选择环境
echo "请选择构建环境："
echo "1) 测试网 (testnet)"
echo "2) 生产环境 (production)"
echo ""
read -p "请输入选项 (1/2): " env_choice

case $env_choice in
    1)
        ENV="testnet"
        COMPOSE_FILE="docker-compose.testnet.yml"
        ;;
    2)
        ENV="production"
        COMPOSE_FILE="docker-compose.prod.yml"
        ;;
    *)
        echo "❌ 无效的选项"
        exit 1
        ;;
esac

echo ""
echo "📋 构建配置："
echo "   - 环境: $ENV"
echo "   - Compose文件: $COMPOSE_FILE"
echo ""

# 确认构建
read -p "确认开始构建？(yes/no): " confirm

if [ "$confirm" != "yes" ]; then
    echo "❌ 构建已取消"
    exit 0
fi

echo ""
echo "🏗️  开始构建Docker镜像..."
echo ""

# 构建后端
echo "📦 构建Backend镜像..."
docker build -t aicoin-backend:v2.0 ./backend

if [ $? -ne 0 ]; then
    echo "❌ Backend构建失败"
    exit 1
fi

echo "✅ Backend镜像构建成功"
echo ""

# 构建前端
echo "📦 构建Frontend镜像..."
docker build -t aicoin-frontend:v2.0 ./frontend

if [ $? -ne 0 ]; then
    echo "❌ Frontend构建失败"
    exit 1
fi

echo "✅ Frontend镜像构建成功"
echo ""

# 显示镜像信息
echo "=========================================="
echo "✅ Docker镜像构建完成！"
echo "=========================================="
echo ""
echo "📦 已构建的镜像："
docker images | grep aicoin
echo ""

echo "🚀 下一步："
if [ "$ENV" = "testnet" ]; then
    echo "   - 测试网部署: ./start_testnet.sh"
    echo "   - 或手动启动: docker-compose -f $COMPOSE_FILE up -d"
else
    echo "   - 生产环境部署: ./deploy_prod.sh"
    echo "   - 或手动启动: docker-compose -f $COMPOSE_FILE up -d"
fi
echo ""

echo "📋 查看日志："
echo "   docker-compose -f $COMPOSE_FILE logs -f"
echo ""

echo "🛑 停止服务："
echo "   docker-compose -f $COMPOSE_FILE down"
echo ""

