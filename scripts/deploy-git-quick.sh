#!/bin/bash

################################################################################
# AIcoin 项目 - Git 快速部署脚本
# 用途：快速拉取最新代码并重启服务（不重新构建镜像）
# 适用场景：配置文件修改、数据库迁移脚本等不需要重新构建的场景
################################################################################

set -e

# ============================================================================
# 配置区域
# ============================================================================
SERVER_USER="root"
SERVER_HOST="47.250.132.166"
SERVER_PATH="/root/AIcoin"
SSH_KEY="/Users/xinghailong/Documents/soft/AIcoin/ssh-configs/cloud-servers/AIcoin.pem"
GIT_BRANCH="${1:-main}"

# 颜色输出
GREEN='\033[0;32m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# ============================================================================
# 主流程
# ============================================================================

echo "════════════════════════════════════════════════════════════════"
echo "  ⚡ AIcoin - Git 快速部署 (不重新构建)"
echo "════════════════════════════════════════════════════════════════"
echo ""

ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no \
    "${SERVER_USER}@${SERVER_HOST}" bash << ENDSSH
set -e
cd $SERVER_PATH

echo -e "${BLUE}📡 拉取最新代码...${NC}"
git fetch origin
git reset --hard origin/$GIT_BRANCH
git pull origin $GIT_BRANCH

echo ""
echo -e "${CYAN}📝 最新提交:${NC}"
git log -1 --oneline --decorate

echo ""
echo -e "${BLUE}🔄 重启服务...${NC}"
docker compose restart

echo ""
echo -e "${BLUE}⏳ 等待服务启动（10 秒）...${NC}"
sleep 10

echo ""
echo -e "${GREEN}✅ 快速部署完成${NC}"
docker compose ps

ENDSSH

echo ""
echo -e "${GREEN}🎉 部署完成！访问 https://jifenpay.cc 验证${NC}"
echo ""

