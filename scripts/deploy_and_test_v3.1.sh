#!/bin/bash
# AIcoin v3.1 部署和自检脚本
# 用途: 在服务器上部署最新代码并进行完整功能测试

set -e  # 遇到错误立即退出

echo "🚀 =========================================="
echo "🚀 AIcoin v3.1 部署和自检开始"
echo "🚀 =========================================="

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 拉取最新代码
echo -e "\n${YELLOW}📥 步骤1: 拉取最新代码${NC}"
git pull origin main
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 代码拉取成功${NC}"
else
    echo -e "${RED}❌ 代码拉取失败${NC}"
    exit 1
fi

# 2. 备份数据库
echo -e "\n${YELLOW}💾 步骤2: 备份数据库${NC}"
BACKUP_DIR="backups"
mkdir -p $BACKUP_DIR
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/aicoin_backup_${TIMESTAMP}.sql"

# 从环境变量或配置文件读取数据库信息
if [ -f ".env" ]; then
    # 使用 set -a 安全加载环境变量（避免命令执行）
    set -a
    source <(grep -v '^#' .env | grep -v '^$' | sed 's/\r$//')
    set +a
fi

# 使用pg_dump备份（如果是PostgreSQL）
if command -v pg_dump &> /dev/null; then
    echo "正在备份PostgreSQL数据库..."
    pg_dump -h ${DB_HOST:-localhost} -U ${DB_USER:-postgres} -d ${DB_NAME:-aicoin} > $BACKUP_FILE
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 数据库备份成功: $BACKUP_FILE${NC}"
    else
        echo -e "${YELLOW}⚠️  数据库备份失败，继续部署${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  pg_dump未找到，跳过数据库备份${NC}"
fi

# 3. 更新后端依赖
echo -e "\n${YELLOW}📦 步骤3: 更新后端依赖${NC}"
cd backend

# 检测可用的pip命令
if command -v pip3 &> /dev/null; then
    PIP_CMD="pip3"
elif command -v pip &> /dev/null; then
    PIP_CMD="pip"
else
    echo -e "${RED}❌ pip未找到，请先安装Python${NC}"
    exit 1
fi

# 临时禁用错误退出，允许部分依赖安装失败
set +e
$PIP_CMD install -r requirements.txt --upgrade
PIP_EXIT_CODE=$?
set -e

if [ $PIP_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ 后端依赖更新成功${NC}"
else
    echo -e "${YELLOW}⚠️  部分依赖更新失败，继续部署（可能已安装）${NC}"
    # 不退出，因为可能只是部分包需要系统依赖
fi

# 4. 运行数据库迁移
echo -e "\n${YELLOW}🗄️  步骤4: 运行数据库迁移${NC}"
if [ -f "alembic.ini" ]; then
    alembic upgrade head
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ 数据库迁移成功${NC}"
    else
        echo -e "${RED}❌ 数据库迁移失败${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  alembic.ini未找到，跳过迁移${NC}"
fi

# 5. 运行自检脚本
echo -e "\n${YELLOW}🧪 步骤5: 运行自检脚本${NC}"

# 检测可用的python命令
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}❌ Python未找到${NC}"
    exit 1
fi

PYTHONPATH=$(pwd) $PYTHON_CMD scripts/self_check.py
SELF_CHECK_EXIT_CODE=$?

if [ $SELF_CHECK_EXIT_CODE -eq 0 ]; then
    echo -e "${GREEN}✅ 自检通过${NC}"
else
    echo -e "${YELLOW}⚠️  自检部分失败（退出码: $SELF_CHECK_EXIT_CODE），查看上面的详细信息${NC}"
    echo -e "${YELLOW}是否继续部署？(y/n)${NC}"
    read -r CONTINUE
    if [ "$CONTINUE" != "y" ] && [ "$CONTINUE" != "Y" ]; then
        echo -e "${RED}❌ 部署中止${NC}"
        exit 1
    fi
fi

# 6. 更新前端
echo -e "\n${YELLOW}🎨 步骤6: 更新前端${NC}"
cd ../frontend
npm install
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 前端依赖安装成功${NC}"
else
    echo -e "${RED}❌ 前端依赖安装失败${NC}"
    exit 1
fi

npm run build
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ 前端构建成功${NC}"
else
    echo -e "${RED}❌ 前端构建失败${NC}"
    exit 1
fi

# 7. 重启服务
echo -e "\n${YELLOW}🔄 步骤7: 重启服务${NC}"
cd ..

# 检查是否使用pm2
if command -v pm2 &> /dev/null; then
    echo "使用PM2重启服务..."
    pm2 restart aicoin-backend || pm2 start backend/app/main.py --name aicoin-backend
    pm2 restart aicoin-frontend || pm2 start "npm run start" --name aicoin-frontend --cwd frontend
    echo -e "${GREEN}✅ 服务重启成功${NC}"
else
    echo -e "${YELLOW}⚠️  PM2未找到，请手动重启服务${NC}"
fi

# 8. 健康检查
echo -e "\n${YELLOW}🏥 步骤8: 健康检查${NC}"
sleep 5  # 等待服务启动

# 检查后端
echo "检查后端服务..."
BACKEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/intelligence/storage/system/health || echo "000")
if [ "$BACKEND_HEALTH" = "200" ]; then
    echo -e "${GREEN}✅ 后端服务正常 (HTTP 200)${NC}"
else
    echo -e "${YELLOW}⚠️  后端服务响应异常 (HTTP $BACKEND_HEALTH)${NC}"
fi

# 检查前端
echo "检查前端服务..."
FRONTEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 || echo "000")
if [ "$FRONTEND_HEALTH" = "200" ]; then
    echo -e "${GREEN}✅ 前端服务正常 (HTTP 200)${NC}"
else
    echo -e "${YELLOW}⚠️  前端服务响应异常 (HTTP $FRONTEND_HEALTH)${NC}"
fi

# 9. 测试关键API
echo -e "\n${YELLOW}🧪 步骤9: 测试关键API${NC}"

# 测试情报系统监控
echo "测试情报系统监控API..."
METRICS_RESPONSE=$(curl -s http://localhost:8000/api/v1/intelligence/storage/system/metrics)
if echo "$METRICS_RESPONSE" | grep -q "success"; then
    echo -e "${GREEN}✅ 情报系统监控API正常${NC}"
else
    echo -e "${YELLOW}⚠️  情报系统监控API响应异常${NC}"
fi

# 10. 显示服务状态
echo -e "\n${YELLOW}📊 步骤10: 服务状态${NC}"
if command -v pm2 &> /dev/null; then
    pm2 list
    pm2 logs --lines 20 --nostream
fi

# 完成
echo -e "\n${GREEN}=========================================="
echo -e "🎉 AIcoin v3.1 部署完成！"
echo -e "==========================================${NC}"

echo -e "\n${YELLOW}📝 部署摘要:${NC}"
echo "  - 代码版本: $(git rev-parse --short HEAD)"
echo "  - 部署时间: $(date)"
echo "  - 备份文件: $BACKUP_FILE"
echo "  - 后端状态: HTTP $BACKEND_HEALTH"
echo "  - 前端状态: HTTP $FRONTEND_HEALTH"

echo -e "\n${YELLOW}🔗 访问地址:${NC}"
echo "  - 前端: http://localhost:3000"
echo "  - 后端API: http://localhost:8000/docs"
echo "  - 情报监控: http://localhost:3000/admin/intelligence/monitoring"

echo -e "\n${YELLOW}📚 下一步:${NC}"
echo "  1. 访问前端页面验证UI功能"
echo "  2. 检查情报系统监控页面"
echo "  3. 手动触发一次情报收集: curl -X POST http://localhost:8000/api/v1/intelligence/refresh"
echo "  4. 查看日志: pm2 logs aicoin-backend"

exit 0

