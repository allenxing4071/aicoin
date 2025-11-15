#!/bin/bash

# AIcoin Docker完全清理脚本
# ⚠️  警告: 此脚本会删除所有数据（包括数据库、Redis、Qdrant数据）

set -e

echo "⚠️  =========================================="
echo "⚠️  警告: 即将删除所有Docker容器、镜像和数据卷"
echo "⚠️  这将清除所有交易历史、配置和缓存数据"
echo "⚠️  =========================================="
echo ""
read -p "确认要继续吗？(输入 YES 继续): " confirm

if [ "$confirm" != "YES" ]; then
    echo "❌ 操作已取消"
    exit 0
fi

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "\n${YELLOW}🛑 步骤1: 停止所有容器${NC}"
docker-compose down -v
echo -e "${GREEN}✅ 容器已停止${NC}"

echo -e "\n${YELLOW}🗑️  步骤2: 删除所有AIcoin镜像${NC}"
docker images | grep aicoin | awk '{print $3}' | xargs -r docker rmi -f || true
echo -e "${GREEN}✅ 镜像已删除${NC}"

echo -e "\n${YELLOW}🗑️  步骤3: 删除所有数据卷${NC}"
docker volume rm aicoin_postgres_data aicoin_redis_data aicoin_qdrant_data 2>/dev/null || true
echo -e "${GREEN}✅ 数据卷已删除${NC}"

echo -e "\n${YELLOW}🗑️  步骤4: 删除网络${NC}"
docker network rm aicoin-network 2>/dev/null || true
echo -e "${GREEN}✅ 网络已删除${NC}"

echo -e "\n${YELLOW}🧹 步骤5: 清理Docker系统${NC}"
docker system prune -af --volumes
echo -e "${GREEN}✅ Docker系统已清理${NC}"

echo -e "\n${GREEN}🎉 =========================================="
echo -e "🎉 完全清理完成！"
echo -e "🎉 ==========================================${NC}"
echo ""
echo "下一步: 运行 ./scripts/docker_redeploy.sh 重新部署"
echo ""

