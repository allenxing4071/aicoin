#!/bin/bash

# 辩论系统部署脚本
# 用途：一键部署和验证辩论系统

set -e

echo "🚀 开始部署辩论系统 v3.4.0..."

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 检查 Docker 服务
echo -e "\n${YELLOW}[1/6] 检查 Docker 服务...${NC}"
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Docker 服务未运行，请先启动 Docker${NC}"
    exit 1
fi
echo -e "${GREEN}✅ Docker 服务正常${NC}"

# 检查数据库服务
echo -e "\n${YELLOW}[2/6] 检查数据库服务...${NC}"
if ! docker-compose ps | grep -q "postgres.*Up"; then
    echo -e "${YELLOW}⚠️  数据库服务未运行，正在启动...${NC}"
    docker-compose up -d postgres
    echo "等待数据库启动（10秒）..."
    sleep 10
fi
echo -e "${GREEN}✅ 数据库服务正常${NC}"

# 执行数据库迁移
echo -e "\n${YELLOW}[3/6] 执行数据库迁移...${NC}"
docker-compose exec -T backend alembic upgrade head
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 数据库迁移成功${NC}"
else
    echo -e "${RED}❌ 数据库迁移失败${NC}"
    exit 1
fi

# 初始化辩论配置
echo -e "\n${YELLOW}[4/6] 初始化辩论配置...${NC}"
docker-compose exec -T backend python scripts/init_debate_config.py
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 辩论配置初始化成功${NC}"
else
    echo -e "${YELLOW}⚠️  辩论配置可能已存在，跳过${NC}"
fi

# 重启后端服务
echo -e "\n${YELLOW}[5/6] 重启后端服务...${NC}"
docker-compose restart backend
echo "等待后端服务启动（5秒）..."
sleep 5
echo -e "${GREEN}✅ 后端服务已重启${NC}"

# 重启前端服务
echo -e "\n${YELLOW}[6/6] 重启前端服务...${NC}"
docker-compose restart frontend
echo "等待前端服务启动（5秒）..."
sleep 5
echo -e "${GREEN}✅ 前端服务已重启${NC}"

# 验证部署
echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}🎉 辩论系统部署完成！${NC}"
echo -e "${GREEN}========================================${NC}"

echo -e "\n📋 验证步骤："
echo -e "1. 访问前端: ${YELLOW}http://localhost:3000/admin/debate${NC}"
echo -e "2. 查看配置: ${YELLOW}http://localhost:3000/admin/debate/config${NC}"
echo -e "3. 查看统计: ${YELLOW}http://localhost:3000/admin/debate/statistics${NC}"
echo -e "4. 查看记忆: ${YELLOW}http://localhost:3000/admin/debate/memory${NC}"

echo -e "\n📊 API 端点："
echo -e "- 辩论历史: ${YELLOW}http://localhost:8000/api/v1/debate/history${NC}"
echo -e "- 辩论配置: ${YELLOW}http://localhost:8000/api/v1/debate/config${NC}"
echo -e "- 辩论统计: ${YELLOW}http://localhost:8000/api/v1/debate/statistics${NC}"

echo -e "\n📖 文档："
echo -e "- 技术文档: ${YELLOW}docs/03-技术架构/09-辩论系统.md${NC}"
echo -e "- 版本日志: ${YELLOW}docs/10-版本更新/v3.4.0-辩论系统.md${NC}"

echo -e "\n${GREEN}✨ 部署成功！${NC}"

