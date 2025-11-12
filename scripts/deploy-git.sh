#!/bin/bash

################################################################################
# AIcoin 项目 - Git 部署脚本（推荐生产环境使用）
# 用途：通过 Git 在服务器上拉取代码并自动构建 Docker 镜像
# 优势：版本可控、回滚方便、符合 GitOps 最佳实践
################################################################################

set -e  # 遇到错误立即退出

# ============================================================================
# 配置区域
# ============================================================================
SERVER_USER="root"
SERVER_HOST="47.250.132.166"
SERVER_PATH="/root/AIcoin"
SSH_KEY="/Users/xinghailong/Documents/soft/AIcoin/ssh-configs/cloud-servers/AIcoin.pem"

# Git 配置
GIT_REPO="https://github.com/allenxing4071/aicoin.git"
GIT_BRANCH="${1:-main}"  # 默认部署 main 分支，可通过参数指定

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
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

log_step() {
    echo -e "${CYAN}[$1]${NC} $2"
}

# ============================================================================
# 主流程
# ============================================================================

echo "════════════════════════════════════════════════════════════════"
echo "  🚀 AIcoin 项目 - Git 自动化部署"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo "  📦 仓库: $GIT_REPO"
echo "  🌿 分支: $GIT_BRANCH"
echo "  🖥️  服务器: $SERVER_HOST"
echo "  📁 路径: $SERVER_PATH"
echo ""
echo "════════════════════════════════════════════════════════════════"
echo ""

# 1️⃣ 检查本地环境
log_step "1/6" "检查本地环境..."
if [ ! -f "$SSH_KEY" ]; then
    log_error "SSH 密钥不存在: $SSH_KEY"
    exit 1
fi

# 修改 SSH 密钥权限（如果需要）
chmod 600 "$SSH_KEY" 2>/dev/null || true

log_success "本地环境检查通过"
echo ""

# 2️⃣ 测试服务器连接
log_step "2/6" "测试服务器连接..."
if ! ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no -o ConnectTimeout=10 \
    "${SERVER_USER}@${SERVER_HOST}" "echo '连接成功'" > /dev/null 2>&1; then
    log_error "无法连接到服务器 ${SERVER_HOST}"
    log_error "请检查："
    log_error "  1. 服务器 IP 是否正确"
    log_error "  2. SSH 密钥权限是否正确 (应为 600)"
    log_error "  3. 服务器防火墙是否开放 22 端口"
    exit 1
fi
log_success "服务器连接正常"
echo ""

# 3️⃣ 在服务器上初始化或更新 Git 仓库
log_step "3/6" "拉取最新代码 (分支: $GIT_BRANCH)..."

ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no \
    "${SERVER_USER}@${SERVER_HOST}" bash << ENDSSH
set -e

# 颜色定义（服务器端）
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo -e "\${BLUE}📡 服务器端操作开始...${NC}"
echo ""

# 检查 Git 是否安装
if ! command -v git &> /dev/null; then
    echo -e "\${RED}❌ Git 未安装，正在安装...${NC}"
    if command -v yum &> /dev/null; then
        yum install -y git
    elif command -v apt-get &> /dev/null; then
        apt-get update && apt-get install -y git
    else
        echo -e "\${RED}❌ 无法自动安装 Git，请手动安装${NC}"
        exit 1
    fi
fi

# 检查项目目录是否存在
if [ -d "$SERVER_PATH/.git" ]; then
    # 目录存在，执行 git pull
    echo -e "\${BLUE}📂 项目目录存在，更新代码...${NC}"
    cd "$SERVER_PATH"
    
    # 保存当前分支和提交信息
    OLD_COMMIT=\$(git rev-parse HEAD 2>/dev/null || echo "unknown")
    OLD_BRANCH=\$(git branch --show-current 2>/dev/null || echo "unknown")
    
    echo -e "\${YELLOW}当前版本:${NC}"
    echo "  分支: \$OLD_BRANCH"
    echo "  提交: \$OLD_COMMIT"
    echo ""
    
    # 清理可能的本地修改
    echo -e "\${BLUE}清理本地修改...${NC}"
    git fetch origin
    git reset --hard origin/$GIT_BRANCH
    git checkout $GIT_BRANCH
    git pull origin $GIT_BRANCH
    
else
    # 目录不存在，克隆仓库
    echo -e "\${BLUE}📥 首次部署，克隆仓库...${NC}"
    
    # 如果目录存在但不是 Git 仓库，先备份
    if [ -d "$SERVER_PATH" ]; then
        BACKUP_DIR="${SERVER_PATH}_backup_\$(date +%Y%m%d_%H%M%S)"
        echo -e "\${YELLOW}⚠️  目录存在但非 Git 仓库，备份到: \$BACKUP_DIR${NC}"
        mv "$SERVER_PATH" "\$BACKUP_DIR"
    fi
    
    git clone -b $GIT_BRANCH $GIT_REPO $SERVER_PATH
    cd "$SERVER_PATH"
fi

# 显示新版本信息
NEW_COMMIT=\$(git rev-parse HEAD)
NEW_BRANCH=\$(git branch --show-current)

echo ""
echo -e "\${GREEN}✅ 代码更新完成${NC}"
echo -e "\${GREEN}新版本:${NC}"
echo "  分支: \$NEW_BRANCH"
echo "  提交: \$NEW_COMMIT"

# 显示最近的提交日志
echo ""
echo -e "\${CYAN}📝 最近 3 次提交:${NC}"
git log -3 --oneline --decorate --color=always

echo ""
echo -e "\${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

ENDSSH

if [ $? -eq 0 ]; then
    log_success "代码拉取完成"
else
    log_error "代码拉取失败"
    exit 1
fi
echo ""

# 4️⃣ 检查并准备环境文件
log_step "4/6" "检查环境配置..."

ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no \
    "${SERVER_USER}@${SERVER_HOST}" bash << 'ENDSSH'
set -e

cd /root/AIcoin

# 检查必要的环境文件
if [ ! -f ".env" ]; then
    echo "⚠️  警告: .env 文件不存在"
    echo "提示: 请在服务器上手动创建 .env 文件"
    echo ""
fi

# 检查 Docker 和 Docker Compose
if ! command -v docker &> /dev/null; then
    echo "❌ Docker 未安装"
    exit 1
fi

if ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose 未安装或版本过低"
    exit 1
fi

echo "✅ 环境检查通过"
echo "   Docker: $(docker --version)"
echo "   Docker Compose: $(docker compose version)"

ENDSSH

log_success "环境配置检查完成"
echo ""

# 5️⃣ 构建并启动 Docker 容器
log_step "5/6" "构建 Docker 镜像并启动服务..."

ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no \
    "${SERVER_USER}@${SERVER_HOST}" bash << 'ENDSSH'
set -e
cd /root/AIcoin

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔨 步骤 1/4: 停止现有容器..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker compose down || true
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏗️  步骤 2/4: 构建前端镜像..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker compose build frontend --no-cache
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏗️  步骤 3/4: 构建后端镜像..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker compose build backend --no-cache
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 步骤 4/4: 启动所有服务..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker compose up -d
echo ""

echo "⏳ 等待服务启动（15 秒）..."
sleep 15
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 容器运行状态:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker compose ps
echo ""

# 检查容器健康状态
echo "🏥 健康检查:"
UNHEALTHY=$(docker compose ps --format json | grep -c '"State":"running"' || echo "0")
if [ "$UNHEALTHY" -gt 0 ]; then
    echo "✅ 所有服务运行正常"
else
    echo "⚠️  部分服务可能未正常启动，请检查日志"
fi

ENDSSH

if [ $? -eq 0 ]; then
    log_success "Docker 容器启动完成"
else
    log_error "Docker 容器启动失败"
    log_warning "请手动登录服务器检查日志: docker compose logs -f"
    exit 1
fi
echo ""

# 6️⃣ 验证部署
log_step "6/6" "验证部署状态..."

ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no \
    "${SERVER_USER}@${SERVER_HOST}" bash << 'ENDSSH'
cd /root/AIcoin

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 部署摘要"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Git 信息
echo "📦 版本信息:"
echo "   分支: $(git branch --show-current)"
echo "   提交: $(git rev-parse --short HEAD)"
echo "   时间: $(git log -1 --format=%cd --date=format:'%Y-%m-%d %H:%M:%S')"
echo "   作者: $(git log -1 --format=%an)"
echo "   消息: $(git log -1 --format=%s)"
echo ""

# 容器信息
echo "🐳 容器状态:"
docker compose ps --format "table {{.Service}}\t{{.Status}}\t{{.Ports}}" 2>/dev/null || docker compose ps
echo ""

# 镜像信息
echo "🖼️  镜像版本:"
docker images | grep -E "(aicoin|REPOSITORY)" | head -5
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

ENDSSH

echo ""
log_success "🎉 部署完成！"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  ✅ 部署成功"
echo "  🌐 访问地址: https://jifenpay.cc"
echo "  📊 管理后台: https://jifenpay.cc/admin"
echo ""
echo "  📝 常用命令:"
echo "     查看日志: ssh -i $SSH_KEY $SERVER_USER@$SERVER_HOST 'cd $SERVER_PATH && docker compose logs -f'"
echo "     重启服务: ssh -i $SSH_KEY $SERVER_USER@$SERVER_HOST 'cd $SERVER_PATH && docker compose restart'"
echo "     停止服务: ssh -i $SSH_KEY $SERVER_USER@$SERVER_HOST 'cd $SERVER_PATH && docker compose down'"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
