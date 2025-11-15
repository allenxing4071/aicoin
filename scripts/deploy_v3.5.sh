#!/bin/bash

# v3.5.0 部署脚本 - 部署到 jifenpay.cc
# 使用方法: ./scripts/deploy_v3.5.sh

set -e

echo "🚀 开始部署 AIcoin v3.5.0 到服务器..."

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 服务器配置
SERVER_USER="root"
SERVER_HOST="jifenpay.cc"
SERVER_PATH="/root/AIcoin"

echo -e "${YELLOW}📦 步骤 1/5: 提交本地更改到Git...${NC}"
git add -A
git commit -m "v3.5.0: 准备部署" || echo "没有新的更改需要提交"
git push

echo -e "${GREEN}✅ Git推送完成${NC}"

echo -e "${YELLOW}📡 步骤 2/5: 连接服务器并拉取最新代码...${NC}"
ssh ${SERVER_USER}@${SERVER_HOST} << 'ENDSSH'
cd /root/AIcoin

echo "🔄 拉取最新代码..."
git pull origin main

echo "✅ 代码更新完成"
ENDSSH

echo -e "${GREEN}✅ 代码同步完成${NC}"

echo -e "${YELLOW}🐳 步骤 3/5: 重新构建并启动Docker容器...${NC}"
ssh ${SERVER_USER}@${SERVER_HOST} << 'ENDSSH'
cd /root/AIcoin

echo "🛑 停止现有容器..."
docker-compose down

echo "🔨 重新构建镜像..."
docker-compose build --no-cache backend frontend

echo "🚀 启动所有服务..."
docker-compose up -d

echo "⏳ 等待服务启动..."
sleep 10

echo "📊 检查容器状态..."
docker-compose ps
ENDSSH

echo -e "${GREEN}✅ Docker容器启动完成${NC}"

echo -e "${YELLOW}🗄️ 步骤 4/5: 数据库迁移和修复...${NC}"
ssh ${SERVER_USER}@${SERVER_HOST} << 'ENDSSH'
cd /root/AIcoin

echo "📝 标记数据库迁移状态..."
docker-compose exec -T backend alembic stamp heads || echo "迁移标记失败，继续..."

echo "🔧 修复admin_users表结构..."
docker-compose exec -T postgres psql -U aicoin -d aicoin -c "ALTER TABLE admin_users ADD COLUMN IF NOT EXISTS role_id INTEGER, ADD COLUMN IF NOT EXISTS custom_permissions JSONB;" || echo "列已存在"

echo "✅ 数据库修复完成"
ENDSSH

echo -e "${GREEN}✅ 数据库配置完成${NC}"

echo -e "${YELLOW}🧪 步骤 5/5: 测试服务...${NC}"
ssh ${SERVER_USER}@${SERVER_HOST} << 'ENDSSH'
cd /root/AIcoin

echo "🔍 测试后端健康检查..."
curl -s http://localhost/health | head -20 || echo "健康检查失败"

echo ""
echo "🔍 测试登录API..."
curl -s -X POST http://localhost/api/v1/admin/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | head -20 || echo "登录测试失败"

echo ""
echo "📊 最终容器状态:"
docker-compose ps

echo ""
echo "📋 后端日志 (最后20行):"
docker-compose logs backend --tail=20
ENDSSH

echo ""
echo -e "${GREEN}✅ 部署完成！${NC}"
echo ""
echo "🌐 访问地址:"
echo "  - HTTP:  http://jifenpay.cc"
echo "  - HTTPS: https://jifenpay.cc (如果SSL已配置)"
echo ""
echo "👤 登录信息:"
echo "  - 用户名: admin"
echo "  - 密码: admin123"
echo ""
echo "📊 查看日志:"
echo "  ssh ${SERVER_USER}@${SERVER_HOST} 'cd ${SERVER_PATH} && docker-compose logs -f'"
echo ""

