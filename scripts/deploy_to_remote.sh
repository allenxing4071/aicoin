#!/bin/bash

###############################################################################
# AIcoin 远程服务器部署脚本
# 目标服务器: 192.168.31.85
# 用户: allenxing07
###############################################################################

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置变量
REMOTE_HOST="192.168.31.185"
REMOTE_USER="allenxing07"
REMOTE_DIR="/home/allenxing07/AIcoin"
LOCAL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# 日志函数
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查SSH连接
check_ssh_connection() {
    log_info "检查SSH连接到 ${REMOTE_USER}@${REMOTE_HOST}..."
    if ssh -o ConnectTimeout=5 -o BatchMode=yes ${REMOTE_USER}@${REMOTE_HOST} exit 2>/dev/null; then
        log_success "SSH连接正常（使用密钥认证）"
        return 0
    else
        log_warning "SSH密钥认证失败，将使用密码认证"
        log_info "请准备输入密码: xhl196312"
        return 1
    fi
}

# 检查远程服务器环境
check_remote_environment() {
    log_info "检查远程服务器环境..."
    
    ssh ${REMOTE_USER}@${REMOTE_HOST} 'bash -s' << 'ENDSSH'
        echo "=== 系统信息 ==="
        uname -a
        echo ""
        
        echo "=== 检查Docker ==="
        if command -v docker &> /dev/null; then
            docker --version
            echo "✅ Docker已安装"
        else
            echo "❌ Docker未安装"
            exit 1
        fi
        
        echo ""
        echo "=== 检查Docker Compose ==="
        if command -v docker-compose &> /dev/null; then
            docker-compose --version
            echo "✅ Docker Compose已安装"
        else
            echo "❌ Docker Compose未安装"
            exit 1
        fi
        
        echo ""
        echo "=== 磁盘空间 ==="
        df -h /
        
        echo ""
        echo "=== 内存信息 ==="
        free -h
        
        echo ""
        echo "=== 检查端口占用 ==="
        echo "检查端口 8000, 3000, 5432, 6379, 6333..."
        for port in 8000 3000 5432 6379 6333; do
            if netstat -tuln 2>/dev/null | grep -q ":$port "; then
                echo "⚠️  端口 $port 已被占用"
            else
                echo "✅ 端口 $port 可用"
            fi
        done
ENDSSH
    
    if [ $? -eq 0 ]; then
        log_success "远程环境检查通过"
    else
        log_error "远程环境检查失败"
        exit 1
    fi
}

# 安装Docker和Docker Compose（如果需要）
install_docker() {
    log_info "在远程服务器上安装Docker..."
    
    ssh ${REMOTE_USER}@${REMOTE_HOST} 'bash -s' << 'ENDSSH'
        # 检查是否已安装
        if command -v docker &> /dev/null && command -v docker-compose &> /dev/null; then
            echo "Docker和Docker Compose已安装，跳过安装步骤"
            exit 0
        fi
        
        # 更新包管理器
        sudo apt-get update
        
        # 安装必要的依赖
        sudo apt-get install -y \
            apt-transport-https \
            ca-certificates \
            curl \
            gnupg \
            lsb-release
        
        # 添加Docker官方GPG密钥
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
        
        # 设置稳定版仓库
        echo \
          "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu \
          $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
        
        # 安装Docker Engine
        sudo apt-get update
        sudo apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin
        
        # 将当前用户添加到docker组
        sudo usermod -aG docker $USER
        
        # 安装Docker Compose
        sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
        
        echo "✅ Docker和Docker Compose安装完成"
ENDSSH
    
    log_success "Docker安装完成"
}

# 同步代码到远程服务器
sync_code() {
    log_info "同步代码到远程服务器..."
    
    # 创建远程目录
    ssh ${REMOTE_USER}@${REMOTE_HOST} "mkdir -p ${REMOTE_DIR}"
    
    # 使用rsync同步代码（排除不必要的文件）
    rsync -avz --progress \
        --exclude 'node_modules' \
        --exclude '__pycache__' \
        --exclude '*.pyc' \
        --exclude '.git' \
        --exclude 'logs' \
        --exclude '*.log' \
        --exclude 'backend.pid' \
        --exclude 'celerybeat-schedule' \
        --exclude '.env' \
        --exclude 'frontend/.next' \
        --exclude 'frontend/tsconfig.tsbuildinfo' \
        "${LOCAL_DIR}/" \
        "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/"
    
    log_success "代码同步完成"
}

# 创建环境配置文件
create_env_file() {
    log_info "创建环境配置文件..."
    
    ssh ${REMOTE_USER}@${REMOTE_HOST} "bash -s" << ENDSSH
        cd ${REMOTE_DIR}
        
        # 如果已存在.env文件，先备份
        if [ -f .env ]; then
            cp .env .env.backup.\$(date +%Y%m%d_%H%M%S)
            echo "已备份现有.env文件"
        fi
        
        # 创建新的.env文件
        cat > .env << 'EOF'
# Database
POSTGRES_USER=aicoin
POSTGRES_PASSWORD=aicoin_prod_2025
DATABASE_URL=postgresql://aicoin:aicoin_prod_2025@postgres:5432/aicoin

# Redis
REDIS_URL=redis://redis:6379

# Qdrant
QDRANT_HOST=qdrant
QDRANT_PORT=6333

# Security
SECRET_KEY=\$(openssl rand -hex 32)
JWT_SECRET_KEY=\$(openssl rand -hex 32)
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI API Keys (需要手动填写)
DEEPSEEK_API_KEY=sk-your-deepseek-api-key
QWEN_API_KEY=sk-your-qwen-api-key
GROK_API_KEY=xai-your-grok-api-key
CLAUDE_API_KEY=sk-ant-your-claude-api-key
OPENAI_API_KEY=sk-your-openai-api-key

# Hyperliquid (需要手动填写)
HYPERLIQUID_WALLET_ADDRESS=0x...
HYPERLIQUID_PRIVATE_KEY=0x...
HYPERLIQUID_VAULT_ADDRESS=
HYPERLIQUID_TESTNET=false
HYPERLIQUID_API_URL=https://api.hyperliquid.xyz

# Trading Config
TRADING_ENABLED=false
DECISION_INTERVAL=300
INITIAL_PERMISSION_LEVEL=L1
DEFAULT_SYMBOL=BTC-PERP

# Risk Management
MAX_POSITION_SIZE=10000
MAX_DAILY_LOSS=1000
MAX_DRAWDOWN=0.15
MAX_POSITION_PCT=0.20
MAX_DAILY_LOSS_PCT=0.05
MAX_DRAWDOWN_PCT=0.10

# Frontend
NEXT_PUBLIC_API_URL=http://192.168.31.85:8000

# App Config
APP_VERSION=3.1.0
EOF
        
        echo "✅ .env文件创建完成"
        echo ""
        echo "⚠️  重要提醒：请编辑 ${REMOTE_DIR}/.env 文件，填写以下必需配置："
        echo "   1. DEEPSEEK_API_KEY"
        echo "   2. HYPERLIQUID_WALLET_ADDRESS"
        echo "   3. HYPERLIQUID_PRIVATE_KEY"
        echo ""
        echo "编辑命令: nano ${REMOTE_DIR}/.env"
ENDSSH
    
    log_success "环境配置文件创建完成"
    log_warning "请SSH到远程服务器编辑.env文件，填写API密钥和钱包信息"
}

# 构建Docker镜像
build_docker_images() {
    log_info "在远程服务器上构建Docker镜像..."
    
    ssh ${REMOTE_USER}@${REMOTE_HOST} "bash -s" << ENDSSH
        cd ${REMOTE_DIR}
        
        echo "=== 构建后端镜像 ==="
        cd backend
        docker build -t aicoin-backend:latest .
        
        echo ""
        echo "=== 构建前端镜像 ==="
        cd ../frontend
        docker build -t aicoin-frontend:latest .
        
        cd ..
        echo "✅ Docker镜像构建完成"
ENDSSH
    
    log_success "Docker镜像构建完成"
}

# 启动服务
start_services() {
    log_info "启动Docker服务..."
    
    ssh ${REMOTE_USER}@${REMOTE_HOST} "bash -s" << ENDSSH
        cd ${REMOTE_DIR}
        
        # 停止旧服务（如果存在）
        docker-compose -f deploy/docker-compose.prod.yml down 2>/dev/null || true
        
        # 启动新服务
        docker-compose -f deploy/docker-compose.prod.yml up -d
        
        echo ""
        echo "=== 等待服务启动 ==="
        sleep 10
        
        echo ""
        echo "=== 检查服务状态 ==="
        docker-compose -f deploy/docker-compose.prod.yml ps
        
        echo ""
        echo "=== 检查后端健康 ==="
        sleep 5
        curl -f http://localhost:8000/health || echo "⚠️  后端健康检查失败"
        
        echo ""
        echo "✅ 服务启动完成"
ENDSSH
    
    log_success "服务启动完成"
}

# 显示访问信息
show_access_info() {
    log_success "=== 部署完成 ==="
    echo ""
    echo -e "${GREEN}访问地址:${NC}"
    echo "  前端界面: http://192.168.31.85:3000"
    echo "  后端API:  http://192.168.31.85:8000"
    echo "  API文档:  http://192.168.31.85:8000/docs"
    echo "  Qdrant:   http://192.168.31.85:6333/dashboard"
    echo ""
    echo -e "${YELLOW}后续操作:${NC}"
    echo "  1. SSH登录: ssh ${REMOTE_USER}@${REMOTE_HOST}"
    echo "  2. 编辑配置: nano ${REMOTE_DIR}/.env"
    echo "  3. 重启服务: cd ${REMOTE_DIR} && docker-compose -f deploy/docker-compose.prod.yml restart"
    echo "  4. 查看日志: cd ${REMOTE_DIR} && docker-compose -f deploy/docker-compose.prod.yml logs -f"
    echo ""
    echo -e "${RED}重要提醒:${NC}"
    echo "  - 请立即修改.env文件中的API密钥和钱包信息"
    echo "  - 交易功能默认关闭(TRADING_ENABLED=false)"
    echo "  - 启用交易前请充分测试"
    echo ""
}

# 主函数
main() {
    echo ""
    echo "=========================================="
    echo "  AIcoin 远程服务器部署工具"
    echo "  目标: ${REMOTE_USER}@${REMOTE_HOST}"
    echo "=========================================="
    echo ""
    
    # 检查本地是否在项目目录
    if [ ! -f "${LOCAL_DIR}/backend/requirements.txt" ]; then
        log_error "请在AIcoin项目根目录下运行此脚本"
        exit 1
    fi
    
    # 执行部署步骤
    check_ssh_connection
    check_remote_environment
    
    # 询问是否需要安装Docker
    read -p "是否需要安装/更新Docker? (y/N): " install_docker_choice
    if [[ $install_docker_choice =~ ^[Yy]$ ]]; then
        install_docker
    fi
    
    sync_code
    create_env_file
    
    # 提示用户编辑配置
    echo ""
    log_warning "请现在SSH到远程服务器编辑.env文件"
    log_info "命令: ssh ${REMOTE_USER}@${REMOTE_HOST}"
    log_info "然后: cd ${REMOTE_DIR} && nano .env"
    echo ""
    read -p "配置完成后，按Enter继续..." 
    
    build_docker_images
    start_services
    show_access_info
    
    log_success "部署流程完成！"
}

# 运行主函数
main "$@"

