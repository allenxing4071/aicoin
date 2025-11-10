#!/bin/bash

###############################################################################
# AIcoin 快速部署脚本（在远程服务器上执行）
# 此脚本将被上传到远程服务器并在服务器上直接执行
###############################################################################

set -e

# 颜色输出
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

# 检查Docker
check_docker() {
    log_info "检查Docker环境..."
    
    if ! command -v docker &> /dev/null; then
        log_error "Docker未安装，请先安装Docker"
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        log_error "Docker Compose未安装，请先安装Docker Compose"
        exit 1
    fi
    
    log_success "Docker环境正常"
}

# 停止旧服务
stop_old_services() {
    log_info "停止旧服务..."
    cd ${PROJECT_DIR}
    
    docker-compose -f deploy/docker-compose.prod.yml down 2>/dev/null || true
    
    log_success "旧服务已停止"
}

# 清理旧镜像
cleanup_old_images() {
    log_info "清理旧Docker镜像..."
    
    docker image prune -f
    
    log_success "清理完成"
}

# 构建镜像
build_images() {
    log_info "构建Docker镜像..."
    cd ${PROJECT_DIR}
    
    # 构建后端
    log_info "构建后端镜像..."
    cd backend
    docker build -t aicoin-backend:latest .
    
    # 构建前端
    log_info "构建前端镜像..."
    cd ../frontend
    docker build -t aicoin-frontend:latest .
    
    cd ..
    log_success "镜像构建完成"
}

# 初始化数据库
init_database() {
    log_info "初始化数据库..."
    cd ${PROJECT_DIR}
    
    # 先启动数据库服务
    docker-compose -f deploy/docker-compose.prod.yml up -d postgres redis qdrant
    
    # 等待数据库就绪
    log_info "等待数据库启动..."
    sleep 15
    
    # 运行数据库迁移
    log_info "运行数据库迁移..."
    docker-compose -f deploy/docker-compose.prod.yml run --rm backend alembic upgrade head
    
    log_success "数据库初始化完成"
}

# 启动所有服务
start_services() {
    log_info "启动所有服务..."
    cd ${PROJECT_DIR}
    
    docker-compose -f deploy/docker-compose.prod.yml up -d
    
    log_info "等待服务启动..."
    sleep 20
    
    log_success "服务启动完成"
}

# 检查服务状态
check_services() {
    log_info "检查服务状态..."
    cd ${PROJECT_DIR}
    
    echo ""
    echo "=== Docker容器状态 ==="
    docker-compose -f deploy/docker-compose.prod.yml ps
    
    echo ""
    echo "=== 后端健康检查 ==="
    if curl -f http://localhost:8000/health 2>/dev/null; then
        log_success "后端服务正常"
    else
        log_error "后端服务异常"
    fi
    
    echo ""
    echo "=== 前端检查 ==="
    if curl -f http://localhost:3000 2>/dev/null; then
        log_success "前端服务正常"
    else
        log_error "前端服务异常"
    fi
}

# 显示日志
show_logs() {
    log_info "显示最近日志..."
    cd ${PROJECT_DIR}
    
    docker-compose -f deploy/docker-compose.prod.yml logs --tail=50
}

# 主函数
main() {
    echo ""
    echo "=========================================="
    echo "  AIcoin 快速部署"
    echo "=========================================="
    echo ""
    
    check_docker
    stop_old_services
    cleanup_old_images
    build_images
    init_database
    start_services
    check_services
    
    echo ""
    log_success "=== 部署完成 ==="
    echo ""
    echo "访问地址:"
    echo "  前端: http://$(hostname -I | awk '{print $1}'):3000"
    echo "  后端: http://$(hostname -I | awk '{print $1}'):8000"
    echo "  文档: http://$(hostname -I | awk '{print $1}'):8000/docs"
    echo ""
    echo "常用命令:"
    echo "  查看日志: cd ${PROJECT_DIR} && docker-compose -f deploy/docker-compose.prod.yml logs -f"
    echo "  重启服务: cd ${PROJECT_DIR} && docker-compose -f deploy/docker-compose.prod.yml restart"
    echo "  停止服务: cd ${PROJECT_DIR} && docker-compose -f deploy/docker-compose.prod.yml down"
    echo ""
}

main "$@"

