#!/bin/bash

################################################################################
# AIcoin 项目 - 部署状态检查脚本
# 用途：快速检查服务器部署状态
################################################################################

SERVER_USER="root"
SERVER_HOST="47.250.132.166"
SSH_KEY="/Users/xinghailong/Documents/soft/AIcoin/ssh-configs/cloud-servers/AIcoin.pem"

# 颜色输出
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}  📊 AIcoin 部署状态检查${NC}"
echo -e "${BLUE}════════════════════════════════════════════════════════════════${NC}"
echo ""

echo -e "${YELLOW}🔍 检查 Docker 构建进程...${NC}"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no \
    "${SERVER_USER}@${SERVER_HOST}" \
    "ps aux | grep 'docker compose build' | grep -v grep || echo '没有构建进程'"
echo ""

echo -e "${YELLOW}🐳 检查 Docker 容器状态...${NC}"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no \
    "${SERVER_USER}@${SERVER_HOST}" \
    "cd /root/AIcoin && docker compose ps"
echo ""

echo -e "${YELLOW}📝 检查最新日志 (后端)...${NC}"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no \
    "${SERVER_USER}@${SERVER_HOST}" \
    "cd /root/AIcoin && docker compose logs --tail=10 backend 2>/dev/null || echo '后端容器未启动'"
echo ""

echo -e "${YELLOW}📝 检查最新日志 (前端)...${NC}"
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no \
    "${SERVER_USER}@${SERVER_HOST}" \
    "cd /root/AIcoin && docker compose logs --tail=10 frontend 2>/dev/null || echo '前端容器未启动'"
echo ""

echo -e "${GREEN}✅ 检查完成！${NC}"

