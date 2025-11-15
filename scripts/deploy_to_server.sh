#!/bin/bash

# AIcoin v3.1 服务器部署脚本
# 在服务器上执行Git拉取和Docker部署

set -e  # 遇到错误立即退出

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 =========================================="
echo -e "🚀 AIcoin v3.1 服务器部署"
echo -e "🚀 ==========================================${NC}"

# 检查是否在服务器上
if [ ! -f "/etc/os-release" ]; then
    echo -e "${YELLOW}⚠️  警告: 似乎不在Linux服务器上${NC}"
fi

# 项目目录（根据实际情况修改）
PROJECT_DIR="${PROJECT_DIR:-/root/AIcoin}"

echo -e "\n${YELLOW}📍 项目目录: $PROJECT_DIR${NC}"

# 步骤1: 进入项目目录
echo -e "\n${YELLOW}📂 步骤1: 进入项目目录${NC}"
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}❌ 错误: 项目目录不存在: $PROJECT_DIR${NC}"
    echo -e "${YELLOW}💡 请先克隆项目: git clone <repository-url> $PROJECT_DIR${NC}"
    exit 1
fi
cd "$PROJECT_DIR"
echo -e "${GREEN}✅ 已进入项目目录${NC}"

# 步骤2: 备份当前状态
echo -e "\n${YELLOW}💾 步骤2: 备份当前状态${NC}"
BACKUP_DIR="backups/deploy_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
if [ -f ".env" ]; then
    cp .env "$BACKUP_DIR/.env.backup"
    echo -e "${GREEN}✅ .env文件已备份${NC}"
fi
echo -e "${GREEN}✅ 备份完成: $BACKUP_DIR${NC}"

# 步骤3: 拉取最新代码
echo -e "\n${YELLOW}📥 步骤3: 拉取最新代码${NC}"
git fetch origin
CURRENT_BRANCH=$(git branch --show-current)
echo -e "${BLUE}当前分支: $CURRENT_BRANCH${NC}"

# 显示即将拉取的更新
echo -e "${BLUE}即将拉取的更新:${NC}"
git log HEAD..origin/$CURRENT_BRANCH --oneline | head -10

# 拉取代码
git pull origin $CURRENT_BRANCH
echo -e "${GREEN}✅ 代码已更新${NC}"

# 步骤4: 检查环境变量
echo -e "\n${YELLOW}🔐 步骤4: 检查环境变量${NC}"
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ 错误: .env文件不存在${NC}"
    echo -e "${YELLOW}💡 请从env.example复制并配置.env文件${NC}"
    exit 1
fi
echo -e "${GREEN}✅ .env文件存在${NC}"

# 步骤5: 停止现有服务
echo -e "\n${YELLOW}🛑 步骤5: 停止现有服务${NC}"
cd deploy
if docker-compose ps | grep -q "Up"; then
    echo -e "${BLUE}正在停止服务...${NC}"
    docker-compose down
    echo -e "${GREEN}✅ 服务已停止${NC}"
else
    echo -e "${BLUE}没有运行中的服务${NC}"
fi

# 步骤6: 清理旧镜像（可选）
echo -e "\n${YELLOW}🧹 步骤6: 清理旧镜像${NC}"
read -p "是否清理旧镜像？(y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker images | grep aicoin | awk '{print $3}' | xargs -r docker rmi -f 2>/dev/null || true
    docker system prune -f
    echo -e "${GREEN}✅ 旧镜像已清理${NC}"
else
    echo -e "${BLUE}跳过清理${NC}"
fi

# 步骤7: 构建新镜像
echo -e "\n${YELLOW}🔨 步骤7: 构建Docker镜像${NC}"
echo -e "${BLUE}这可能需要几分钟时间...${NC}"

# 使用国内镜像源加速（如果需要）
if [ -f "/etc/docker/daemon.json" ]; then
    echo -e "${BLUE}Docker配置:${NC}"
    cat /etc/docker/daemon.json | grep -A 3 "registry-mirrors" || echo "未配置镜像源"
fi

docker-compose build --no-cache
echo -e "${GREEN}✅ 镜像构建完成${NC}"

# 步骤8: 启动服务
echo -e "\n${YELLOW}🚀 步骤8: 启动服务${NC}"
docker-compose up -d
echo -e "${GREEN}✅ 服务已启动${NC}"

# 步骤9: 等待服务就绪
echo -e "\n${YELLOW}⏳ 步骤9: 等待服务就绪${NC}"
echo -e "${BLUE}等待数据库启动...${NC}"
sleep 15

# 步骤10: 运行数据库迁移
echo -e "\n${YELLOW}🗄️  步骤10: 运行数据库迁移${NC}"
docker-compose exec -T backend alembic upgrade head || {
    echo -e "${YELLOW}⚠️  数据库迁移失败（可能是首次运行）${NC}"
}

# 步骤11: 检查服务状态
echo -e "\n${YELLOW}📊 步骤11: 检查服务状态${NC}"
docker-compose ps

# 步骤12: 健康检查
echo -e "\n${YELLOW}🏥 步骤12: 服务健康检查${NC}"
sleep 5

# 检查后端API
if curl -s -f http://localhost:8000/docs > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 后端API正常 (http://localhost:8000/docs)${NC}"
else
    echo -e "${RED}❌ 后端API无法访问${NC}"
    echo -e "${YELLOW}查看后端日志:${NC}"
    docker-compose logs --tail=20 backend
fi

# 检查前端
if curl -s -f http://localhost:3002 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ 前端正常 (http://localhost:3002)${NC}"
else
    echo -e "${RED}❌ 前端无法访问${NC}"
fi

# 检查Nginx
if curl -s -f http://localhost:80 > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Nginx正常 (http://jifenpay.cc)${NC}"
else
    echo -e "${YELLOW}⚠️  Nginx未配置或未启动${NC}"
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

# 步骤13: 运行自检
echo -e "\n${YELLOW}🧪 步骤13: 运行系统自检${NC}"
docker-compose exec -T backend python scripts/self_check.py || {
    echo -e "${YELLOW}⚠️  自检失败，请查看日志${NC}"
}

# 步骤14: 显示日志
echo -e "\n${YELLOW}📋 步骤14: 最近的服务日志${NC}"
echo -e "${BLUE}后端日志:${NC}"
docker-compose logs --tail=10 backend

echo -e "\n${GREEN}🎉 =========================================="
echo -e "🎉 部署完成！"
echo -e "🎉 ==========================================${NC}"
echo ""
echo -e "${BLUE}📍 服务访问地址:${NC}"
echo "   - 主站: http://jifenpay.cc"
echo "   - 后端API: http://jifenpay.cc/api"
echo "   - API文档: http://jifenpay.cc/docs"
echo "   - 管理后台: http://jifenpay.cc/admin"
echo ""
echo -e "${BLUE}📋 常用命令:${NC}"
echo "   - 查看日志: docker-compose logs -f [service]"
echo "   - 重启服务: docker-compose restart [service]"
echo "   - 停止服务: docker-compose down"
echo "   - 进入容器: docker-compose exec [service] bash"
echo "   - 运行自检: docker-compose exec backend python scripts/self_check.py"
echo ""
echo -e "${BLUE}🔍 监控命令:${NC}"
echo "   - 实时日志: docker-compose logs -f"
echo "   - 服务状态: docker-compose ps"
echo "   - 资源使用: docker stats"
echo ""

