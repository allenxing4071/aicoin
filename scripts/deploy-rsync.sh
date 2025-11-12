#!/bin/bash

################################################################################
# AIcoin 项目 - rsync 快速部署脚本
# 用途：将本地代码快速同步到服务器并重新构建
# 适用场景：开发阶段快速迭代
################################################################################

set -e  # 遇到错误立即退出

# ============================================================================
# 配置区域
# ============================================================================
SERVER_USER="root"
SERVER_HOST="47.250.132.166"
SERVER_PATH="/root/AIcoin"
SSH_KEY="/Users/xinghailong/Documents/soft/AIcoin/ssh-configs/cloud-servers/AIcoin.pem"
LOCAL_PROJECT_PATH="/Users/xinghailong/Documents/soft/AIcoin"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# ============================================================================
# 辅助函数
# ============================================================================
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

# ============================================================================
# 主流程
# ============================================================================

echo "════════════════════════════════════════════════════════════════"
echo "  🚀 AIcoin 项目 - rsync 快速部署"
echo "════════════════════════════════════════════════════════════════"
echo ""

# 1️⃣ 检查本地环境
log_info "检查本地环境..."
if [ ! -f "$SSH_KEY" ]; then
    log_error "SSH 密钥不存在: $SSH_KEY"
    exit 1
fi

if [ ! -d "$LOCAL_PROJECT_PATH" ]; then
    log_error "项目目录不存在: $LOCAL_PROJECT_PATH"
    exit 1
fi

log_success "本地环境检查通过"
echo ""

# 2️⃣ 测试服务器连接
log_info "测试服务器连接..."
if ! ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no -o ConnectTimeout=5 \
    "${SERVER_USER}@${SERVER_HOST}" "echo '连接成功'" > /dev/null 2>&1; then
    log_error "无法连接到服务器"
    exit 1
fi
log_success "服务器连接正常"
echo ""

# 3️⃣ 同步代码（排除不必要的文件）
log_info "开始同步代码到服务器..."
rsync -avz --delete \
    --exclude='node_modules/' \
    --exclude='.next/' \
    --exclude='__pycache__/' \
    --exclude='*.pyc' \
    --exclude='.git/' \
    --exclude='.env.local' \
    --exclude='logs/' \
    --exclude='backups/' \
    --exclude='*.log' \
    --exclude='.DS_Store' \
    -e "ssh -i $SSH_KEY -o StrictHostKeyChecking=no" \
    "${LOCAL_PROJECT_PATH}/" \
    "${SERVER_USER}@${SERVER_HOST}:${SERVER_PATH}/"

if [ $? -eq 0 ]; then
    log_success "代码同步完成"
else
    log_error "代码同步失败"
    exit 1
fi
echo ""

# 4️⃣ 在服务器上重新构建镜像
log_info "在服务器上重新构建 Docker 镜像..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no \
    "${SERVER_USER}@${SERVER_HOST}" << 'ENDSSH'
set -e
cd /root/AIcoin

echo "🔨 停止现有容器..."
docker compose down

echo "🏗️ 构建前端镜像 (no-cache)..."
docker compose build frontend --no-cache

echo "🏗️ 构建后端镜像 (no-cache)..."
docker compose build backend --no-cache

echo "🚀 启动所有服务..."
docker compose up -d

echo "⏳ 等待服务启动 (15秒)..."
sleep 15

echo "📊 检查容器状态..."
docker compose ps

echo "✅ 部署完成！"
ENDSSH

if [ $? -eq 0 ]; then
    log_success "Docker 镜像构建完成"
else
    log_error "Docker 镜像构建失败"
    exit 1
fi
echo ""

# 5️⃣ 验证部署
log_info "验证部署状态..."
ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no \
    "${SERVER_USER}@${SERVER_HOST}" \
    "cd ${SERVER_PATH} && docker compose ps --format json" | python3 -m json.tool

echo ""
log_success "🎉 部署完成！请访问 https://jifenpay.cc 验证"
echo ""
echo "════════════════════════════════════════════════════════════════"

