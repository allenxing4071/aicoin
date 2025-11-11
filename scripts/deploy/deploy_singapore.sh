#!/bin/bash

###############################################################################
# AIcoin 新加坡服务器彻底部署脚本
# 服务器: 47.250.132.166 (新加坡 - jifenpay.cc)
# 功能: 完全清理、重新构建、彻底部署
###############################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
MAGENTA='\033[0;35m'
NC='\033[0m'

# 新加坡服务器配置
REMOTE_HOST="47.250.132.166"
REMOTE_USER="root"
REMOTE_DIR="/root/AIcoin"
SSH_KEY="$HOME/Documents/soft/AIcoin/ssh-configs/cloud-servers/AIcoin.pem"
LOCAL_DIR="$(cd "$(dirname "$0")/../.." && pwd)"

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[✓]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[⚠]${NC} $1"; }
log_error() { echo -e "${RED}[✗]${NC} $1"; }
log_step() { echo -e "${CYAN}[STEP]${NC} $1"; }

echo ""
echo "=========================================================="
echo "  🚀 AIcoin 彻底部署到新加坡服务器"
echo "=========================================================="
echo "  服务器: 新加坡 (Singapore)"
echo "  IP地址: ${REMOTE_HOST}"
echo "  域名: jifenpay.cc"
echo "  部署类型: 完全重建（包含Docker完全重建）"
echo "=========================================================="
echo ""

# 1. 检查SSH连接
log_step "步骤 1/8: 检查SSH连接和密钥"
if [ ! -f "$SSH_KEY" ]; then
    log_error "SSH密钥不存在: $SSH_KEY"
    exit 1
fi

# 确保密钥权限正确
chmod 600 "$SSH_KEY" 2>/dev/null

log_info "测试SSH连接到新加坡服务器..."
if ! ssh -i "$SSH_KEY" -o ConnectTimeout=15 -o StrictHostKeyChecking=no ${REMOTE_USER}@${REMOTE_HOST} "echo 'SSH OK'" > /dev/null 2>&1; then
    log_error "无法连接到新加坡服务器 ${REMOTE_HOST}"
    log_error "请检查："
    echo "  1. 网络连接是否正常"
    echo "  2. SSH密钥是否正确"
    echo "  3. 服务器IP是否正确"
    exit 1
fi
log_success "SSH连接正常"

# 2. 检查远程服务器环境
log_step "步骤 2/8: 检查远程服务器环境"
ssh -i "$SSH_KEY" ${REMOTE_USER}@${REMOTE_HOST} << 'ENDSSH'
    echo "检查服务器信息..."
    echo "  主机名: $(hostname)"
    echo "  系统: $(cat /etc/os-release | grep PRETTY_NAME | cut -d '"' -f2)"
    echo "  内核: $(uname -r)"
    echo ""
    
    echo "检查Docker..."
    if command -v docker &> /dev/null; then
        echo "  ✓ Docker 版本: $(docker --version)"
    else
        echo "  ✗ Docker 未安装"
        exit 1
    fi
    
    if command -v docker-compose &> /dev/null; then
        echo "  ✓ Docker Compose 已安装"
    else
        echo "  ⚠ Docker Compose 未安装，尝试安装..."
        # 安装 docker-compose
        curl -SL https://github.com/docker/compose/releases/latest/download/docker-compose-linux-x86_64 -o /usr/local/bin/docker-compose
        chmod +x /usr/local/bin/docker-compose
        ln -sf /usr/local/bin/docker-compose /usr/bin/docker-compose
        echo "  ✓ Docker Compose 安装完成"
    fi
    
    echo ""
    echo "  磁盘空间: $(df -h / | tail -1 | awk '{print $4}') 可用"
    echo "  内存: $(free -h | grep Mem | awk '{print $7}') 可用"
ENDSSH

log_success "服务器环境检查完成"

# 3. 备份远程数据
log_step "步骤 3/8: 备份远程环境配置"
ssh -i "$SSH_KEY" ${REMOTE_USER}@${REMOTE_HOST} << 'ENDSSH'
    cd /root
    
    # 创建备份目录
    BACKUP_DIR="AIcoin_backups/backup_$(date +%Y%m%d_%H%M%S)"
    mkdir -p "$BACKUP_DIR"
    
    # 备份.env文件（如果存在）
    if [ -f AIcoin/.env ]; then
        cp AIcoin/.env "$BACKUP_DIR/.env"
        echo "✓ 已备份 .env 文件"
    fi
    
    # 备份docker-compose配置
    if [ -f AIcoin/deploy/docker-compose.prod.yml ]; then
        cp AIcoin/deploy/docker-compose.prod.yml "$BACKUP_DIR/"
        echo "✓ 已备份 docker-compose 配置"
    fi
    
    echo "✓ 备份完成: $BACKUP_DIR"
ENDSSH

log_success "备份完成"

# 4. 同步代码
log_step "步骤 4/8: 同步代码到新加坡服务器"
log_info "开始rsync同步（这可能需要1-2分钟）..."

rsync -avz --progress \
    -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=no" \
    --delete \
    --exclude 'node_modules' \
    --exclude '__pycache__' \
    --exclude '*.pyc' \
    --exclude '.git' \
    --exclude 'logs' \
    --exclude '*.log' \
    --exclude 'backend.pid' \
    --exclude 'frontend.pid' \
    --exclude 'celerybeat-schedule' \
    --exclude '.env' \
    --exclude 'frontend/.next' \
    --exclude 'frontend/tsconfig.tsbuildinfo' \
    --exclude 'frontend/node_modules' \
    --exclude 'backups' \
    --exclude 'AIcoin_backups' \
    "${LOCAL_DIR}/" \
    "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/" 2>&1 | grep -E "sending|total size|speedup" | tail -5

log_success "代码同步完成"

# 5. 停止所有服务
log_step "步骤 5/8: 停止现有服务"
ssh -i "$SSH_KEY" ${REMOTE_USER}@${REMOTE_HOST} << 'ENDSSH'
    cd /root/AIcoin
    
    echo "停止Docker Compose服务..."
    docker-compose -f deploy/docker-compose.prod.yml down 2>&1 | tail -5 || true
    
    echo ""
    echo "检查并停止所有AIcoin相关容器..."
    CONTAINERS=$(docker ps -a -q --filter "name=aicoin" 2>/dev/null)
    if [ ! -z "$CONTAINERS" ]; then
        docker stop $CONTAINERS 2>/dev/null || true
        docker rm $CONTAINERS 2>/dev/null || true
        echo "✓ 已清理残留容器"
    fi
    
    echo "✓ 所有服务已停止"
ENDSSH

log_success "服务停止完成"

# 6. 彻底清理
log_step "步骤 6/8: 彻底清理缓存和旧数据"
ssh -i "$SSH_KEY" ${REMOTE_USER}@${REMOTE_HOST} << 'ENDSSH'
    cd /root/AIcoin
    
    echo "清理Python缓存..."
    find backend -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find backend -type f -name "*.pyc" -delete 2>/dev/null || true
    echo "✓ Python缓存已清理"
    
    echo ""
    echo "清理Node.js构建缓存..."
    rm -rf frontend/.next 2>/dev/null || true
    rm -f frontend/tsconfig.tsbuildinfo 2>/dev/null || true
    echo "✓ Node.js缓存已清理"
    
    echo ""
    echo "清理日志文件..."
    rm -f logs/*.log 2>/dev/null || true
    rm -f *.log 2>/dev/null || true
    echo "✓ 日志已清理"
    
    echo ""
    echo "清理Docker系统..."
    docker system prune -af --volumes 2>&1 | tail -3
    echo "✓ Docker清理完成"
ENDSSH

log_success "清理完成"

# 7. 重新构建Docker镜像
log_step "步骤 7/8: 重新构建Docker镜像（需要3-8分钟）"
log_info "这将完全重建所有镜像，请耐心等待..."

ssh -i "$SSH_KEY" ${REMOTE_USER}@${REMOTE_HOST} << 'ENDSSH'
    cd /root/AIcoin
    
    echo ""
    echo "=========================================="
    echo "  开始构建Docker镜像"
    echo "=========================================="
    echo ""
    
    # 使用docker-compose重新构建
    docker-compose -f deploy/docker-compose.prod.yml build --no-cache --pull 2>&1 | \
        grep -E "Step|Successfully|Building|FINISHED|ERROR" | tail -20
    
    echo ""
    echo "✓ 镜像构建完成"
ENDSSH

log_success "Docker镜像构建完成"

# 8. 启动服务
log_step "步骤 8/8: 启动所有服务"
ssh -i "$SSH_KEY" ${REMOTE_USER}@${REMOTE_HOST} << 'ENDSSH'
    cd /root/AIcoin
    
    echo "启动Docker Compose服务..."
    docker-compose -f deploy/docker-compose.prod.yml up -d 2>&1 | tail -5
    
    echo ""
    echo "等待服务启动（30秒）..."
    for i in {1..30}; do
        echo -n "."
        sleep 1
    done
    echo ""
    
    echo ""
    echo "=========================================="
    echo "  服务状态"
    echo "=========================================="
    docker-compose -f deploy/docker-compose.prod.yml ps
    
    echo ""
    echo "=========================================="
    echo "  Backend 日志（最后20行）"
    echo "=========================================="
    docker-compose -f deploy/docker-compose.prod.yml logs --tail=20 backend 2>&1 | tail -20
    
    echo ""
    echo "=========================================="
    echo "  Frontend 日志（最后10行）"
    echo "=========================================="
    docker-compose -f deploy/docker-compose.prod.yml logs --tail=10 frontend 2>&1 | tail -10
    
    echo ""
    echo "✓ 服务启动完成"
ENDSSH

log_success "服务启动完成"

# 9. 健康检查
echo ""
log_step "执行健康检查..."
sleep 8

echo ""
log_info "检查前端服务 (https://jifenpay.cc)..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://jifenpay.cc 2>/dev/null || echo "000")
if [[ "$HTTP_CODE" =~ ^(200|301|302)$ ]]; then
    log_success "✓ 前端服务正常 (HTTP $HTTP_CODE)"
else
    log_warning "⚠ 前端服务响应码: $HTTP_CODE（可能还在启动中）"
fi

log_info "检查后端API (https://jifenpay.cc/api/v1/status)..."
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://jifenpay.cc/api/v1/status 2>/dev/null || echo "000")
if [[ "$HTTP_CODE" == "200" ]]; then
    log_success "✓ 后端API正常 (HTTP $HTTP_CODE)"
else
    log_warning "⚠ 后端API响应码: $HTTP_CODE（可能还在启动中）"
fi

log_info "检查成本趋势API..."
COST_API=$(curl -s https://jifenpay.cc/api/v1/ai-platforms/cost-trend-daily?days=7 2>/dev/null)
if echo "$COST_API" | grep -q "success"; then
    log_success "✓ 成本趋势API正常（新功能已部署）"
else
    log_warning "⚠ 成本趋势API还在初始化"
fi

# 10. 显示部署总结
echo ""
echo "=========================================================="
echo "  🎉 部署完成！"
echo "=========================================================="
echo ""
echo "  📍 服务器信息"
echo "  --------------------------------------------------------"
echo "  地区: 新加坡 (Singapore)"
echo "  IP: ${REMOTE_HOST}"
echo "  域名: jifenpay.cc"
echo ""
echo "  📊 访问地址"
echo "  --------------------------------------------------------"
echo "  🌐 网站首页: https://jifenpay.cc"
echo "  🔧 管理后台: https://jifenpay.cc/admin/login"
echo "  💰 成本管理: https://jifenpay.cc/admin/ai-cost"
echo "  📚 API文档: https://jifenpay.cc/api/docs"
echo "  📈 API状态: https://jifenpay.cc/api/v1/status"
echo ""
echo "  🔐 管理员账户"
echo "  --------------------------------------------------------"
echo "  用户名: admin"
echo "  密码: admin123"
echo ""
echo "  ✨ 本次更新内容"
echo "  --------------------------------------------------------"
echo "  ✓ 成本趋势图表功能（最近7天真实数据）"
echo "  ✓ 成本汇总API优化"
echo "  ✓ 修复AIModelUsageLog字段映射问题"
echo "  ✓ 前端CostTrendChart组件"
echo "  ✓ 完全重建Docker镜像"
echo "  ✓ 清理所有缓存"
echo ""
echo "  🔍 远程服务器操作"
echo "  --------------------------------------------------------"
echo "  连接服务器:"
echo "    ssh -i $SSH_KEY ${REMOTE_USER}@${REMOTE_HOST}"
echo ""
echo "  查看日志:"
echo "    cd /root/AIcoin"
echo "    docker-compose -f deploy/docker-compose.prod.yml logs -f"
echo ""
echo "  重启服务:"
echo "    docker-compose -f deploy/docker-compose.prod.yml restart"
echo ""
echo "=========================================================="
echo ""

log_success "🎉 部署流程全部完成！"
echo ""

