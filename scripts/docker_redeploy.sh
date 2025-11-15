#!/bin/bash

# AIcoin v3.1 Docker完全重新部署脚本
# 清理所有容器和镜像（保留数据卷），重新构建并启动

set -e  # 遇到错误立即退出

echo "🚀 =========================================="
echo "🚀 AIcoin v3.1 Docker完全重新部署"
echo "🚀 =========================================="

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${YELLOW}📍 当前目录: $PROJECT_ROOT${NC}"

# 步骤1: 检查.env文件
echo -e "\n${YELLOW}📋 步骤1: 检查环境变量${NC}"
if [ ! -f .env ]; then
    echo -e "${RED}❌ 错误: .env文件不存在${NC}"
    echo "请从env.example复制并配置.env文件"
    exit 1
fi
echo -e "${GREEN}✅ .env文件存在${NC}"

# 步骤2: 停止并删除所有容器
echo -e "\n${YELLOW}🛑 步骤2: 停止并删除现有容器${NC}"
docker-compose down || true
echo -e "${GREEN}✅ 容器已停止并删除${NC}"

# 步骤3: 清理Docker镜像（保留数据卷）
echo -e "\n${YELLOW}🧹 步骤3: 清理Docker镜像${NC}"
echo "删除AIcoin相关镜像..."
docker images | grep aicoin | awk '{print $3}' | xargs -r docker rmi -f || true
echo -e "${GREEN}✅ 镜像已清理${NC}"

# 步骤4: 清理悬空镜像和构建缓存
echo -e "\n${YELLOW}🧹 步骤4: 清理Docker构建缓存${NC}"
docker system prune -f
echo -e "${GREEN}✅ 构建缓存已清理${NC}"

# 步骤5: 拉取最新代码
echo -e "\n${YELLOW}📥 步骤5: 拉取最新代码${NC}"
git pull origin main
echo -e "${GREEN}✅ 代码已更新${NC}"

# 步骤6: 重新构建镜像
echo -e "\n${YELLOW}🔨 步骤6: 重新构建Docker镜像${NC}"
echo "这可能需要几分钟时间..."
docker-compose build --no-cache
echo -e "${GREEN}✅ 镜像构建完成${NC}"

# 步骤7: 启动服务
echo -e "\n${YELLOW}🚀 步骤7: 启动所有服务${NC}"
docker-compose up -d
echo -e "${GREEN}✅ 服务已启动${NC}"

# 步骤8: 等待服务就绪
echo -e "\n${YELLOW}⏳ 步骤8: 等待服务就绪${NC}"
echo "等待数据库启动..."
sleep 10

# 检查服务状态
echo -e "\n${YELLOW}📊 步骤9: 检查服务状态${NC}"
docker-compose ps

# 步骤10: 运行数据库迁移
echo -e "\n${YELLOW}🗄️  步骤10: 运行数据库迁移${NC}"
docker-compose exec -T backend alembic upgrade head || {
    echo -e "${YELLOW}⚠️  数据库迁移失败（可能是首次运行）${NC}"
}

# 步骤11: 查看后端日志（最后20行）
echo -e "\n${YELLOW}📋 步骤11: 后端服务日志${NC}"
docker-compose logs --tail=20 backend

# 步骤12: 健康检查
echo -e "\n${YELLOW}🏥 步骤12: 服务健康检查${NC}"
sleep 5

# 检查后端API
if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 后端API正常 (http://localhost:8000/docs)${NC}"
else
    echo -e "${RED}❌ 后端API无法访问${NC}"
fi

# 检查前端
if curl -s http://localhost:3000 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 前端正常 (http://localhost:3000)${NC}"
else
    echo -e "${RED}❌ 前端无法访问${NC}"
fi

# 检查Redis
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Redis正常${NC}"
else
    echo -e "${RED}❌ Redis无法访问${NC}"
fi

# 检查PostgreSQL
if docker-compose exec -T postgres pg_isready -U aicoin > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL正常${NC}"
else
    echo -e "${RED}❌ PostgreSQL无法访问${NC}"
fi

# 检查Qdrant
if curl -s http://localhost:6333 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Qdrant正常${NC}"
else
    echo -e "${RED}❌ Qdrant无法访问${NC}"
fi

echo -e "\n${GREEN}🎉 =========================================="
echo -e "🎉 Docker重新部署完成！"
echo -e "🎉 ==========================================${NC}"
echo ""
echo "📍 服务访问地址:"
echo "   - 后端API: http://localhost:8000"
echo "   - API文档: http://localhost:8000/docs"
echo "   - 前端界面: http://localhost:3000"
echo ""
echo "📋 常用命令:"
echo "   - 查看日志: docker-compose logs -f [service]"
echo "   - 重启服务: docker-compose restart [service]"
echo "   - 停止服务: docker-compose down"
echo "   - 进入容器: docker-compose exec [service] bash"
echo ""
echo "🔍 运行自检:"
echo "   docker-compose exec backend python scripts/self_check.py"
echo ""

