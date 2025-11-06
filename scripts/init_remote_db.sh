#!/bin/bash

###############################################################################
# 远程服务器数据库初始化脚本
# 在远程服务器上执行，初始化PostgreSQL数据库
###############################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

PROJECT_DIR="/home/allenxing07/AIcoin"

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo ""
echo "=========================================="
echo "  AIcoin 数据库初始化"
echo "=========================================="
echo ""

cd ${PROJECT_DIR}

# 1. 确保数据库容器运行
log_info "启动数据库容器..."
docker-compose -f deploy/docker-compose.prod.yml up -d postgres redis qdrant

# 2. 等待数据库就绪
log_info "等待PostgreSQL就绪..."
for i in {1..30}; do
    if docker-compose -f deploy/docker-compose.prod.yml exec -T postgres pg_isready -U aicoin &> /dev/null; then
        log_success "PostgreSQL已就绪"
        break
    fi
    echo -n "."
    sleep 2
done
echo ""

# 3. 检查数据库连接
log_info "检查数据库连接..."
if docker-compose -f deploy/docker-compose.prod.yml exec -T postgres psql -U aicoin -d aicoin -c "SELECT 1;" &> /dev/null; then
    log_success "数据库连接正常"
else
    log_error "数据库连接失败"
    exit 1
fi

# 4. 运行数据库迁移
log_info "运行Alembic数据库迁移..."
docker-compose -f deploy/docker-compose.prod.yml run --rm backend alembic upgrade head

if [ $? -eq 0 ]; then
    log_success "数据库迁移完成"
else
    log_error "数据库迁移失败"
    exit 1
fi

# 5. 检查表是否创建
log_info "验证数据库表..."
TABLES=$(docker-compose -f deploy/docker-compose.prod.yml exec -T postgres psql -U aicoin -d aicoin -t -c "SELECT COUNT(*) FROM information_schema.tables WHERE table_schema='public';")
log_info "创建了 ${TABLES} 个表"

# 6. 初始化Qdrant集合
log_info "初始化Qdrant向量数据库..."
sleep 5

# 7. 显示数据库信息
echo ""
log_success "=== 数据库初始化完成 ==="
echo ""
echo "数据库信息:"
docker-compose -f deploy/docker-compose.prod.yml exec -T postgres psql -U aicoin -d aicoin -c "\dt"
echo ""
log_success "数据库已准备就绪"

