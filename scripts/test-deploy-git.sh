#!/bin/bash

################################################################################
# AIcoin 项目 - Git 部署测试脚本
# 用途：测试 Git 部署脚本是否配置正确（不实际部署）
################################################################################

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "════════════════════════════════════════════════════════════════"
echo "  🧪 Git 部署环境测试"
echo "════════════════════════════════════════════════════════════════"
echo ""

# 配置
SERVER_USER="root"
SERVER_HOST="47.250.132.166"
SERVER_PATH="/root/AIcoin"
SSH_KEY="ssh-configs/cloud-servers/AIcoin.pem"

PASSED=0
FAILED=0

# 测试函数
test_check() {
    local name=$1
    local command=$2
    
    echo -n "检查 $name... "
    if eval "$command" > /dev/null 2>&1; then
        echo -e "${GREEN}✓ 通过${NC}"
        ((PASSED++))
        return 0
    else
        echo -e "${RED}✗ 失败${NC}"
        ((FAILED++))
        return 1
    fi
}

# 1. 检查本地环境
echo -e "${BLUE}━━━ 本地环境检查 ━━━${NC}"
test_check "Git 安装" "command -v git"
test_check "SSH 密钥存在" "[ -f '$SSH_KEY' ]"
test_check "SSH 密钥权限" "[ \$(stat -f '%A' '$SSH_KEY' 2>/dev/null || stat -c '%a' '$SSH_KEY' 2>/dev/null) = '600' ] || chmod 600 '$SSH_KEY'"
echo ""

# 2. 检查服务器连接
echo -e "${BLUE}━━━ 服务器连接检查 ━━━${NC}"
test_check "SSH 连接" "ssh -i '$SSH_KEY' -o StrictHostKeyChecking=no -o ConnectTimeout=5 '${SERVER_USER}@${SERVER_HOST}' 'echo ok'"
echo ""

# 3. 检查服务器环境
echo -e "${BLUE}━━━ 服务器环境检查 ━━━${NC}"

if ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "${SERVER_USER}@${SERVER_HOST}" 'command -v git' > /dev/null 2>&1; then
    echo -e "检查 Git 安装... ${GREEN}✓ 通过${NC}"
    ((PASSED++))
else
    echo -e "检查 Git 安装... ${RED}✗ 失败${NC}"
    echo "  提示: 运行 'yum install -y git' 或 'apt-get install -y git'"
    ((FAILED++))
fi

if ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "${SERVER_USER}@${SERVER_HOST}" 'command -v docker' > /dev/null 2>&1; then
    echo -e "检查 Docker 安装... ${GREEN}✓ 通过${NC}"
    ((PASSED++))
else
    echo -e "检查 Docker 安装... ${RED}✗ 失败${NC}"
    ((FAILED++))
fi

if ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "${SERVER_USER}@${SERVER_HOST}" 'docker compose version' > /dev/null 2>&1; then
    echo -e "检查 Docker Compose... ${GREEN}✓ 通过${NC}"
    ((PASSED++))
else
    echo -e "检查 Docker Compose... ${RED}✗ 失败${NC}"
    ((FAILED++))
fi

echo ""

# 4. 检查 Git 仓库状态
echo -e "${BLUE}━━━ Git 仓库检查 ━━━${NC}"

if ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "${SERVER_USER}@${SERVER_HOST}" "[ -d '$SERVER_PATH/.git' ]" 2>/dev/null; then
    echo -e "项目目录存在... ${GREEN}✓ 通过${NC}"
    
    # 获取当前版本信息
    CURRENT_BRANCH=$(ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "${SERVER_USER}@${SERVER_HOST}" "cd $SERVER_PATH && git branch --show-current" 2>/dev/null)
    CURRENT_COMMIT=$(ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "${SERVER_USER}@${SERVER_HOST}" "cd $SERVER_PATH && git rev-parse --short HEAD" 2>/dev/null)
    
    echo "  分支: $CURRENT_BRANCH"
    echo "  提交: $CURRENT_COMMIT"
    ((PASSED++))
else
    echo -e "项目目录存在... ${YELLOW}⚠ 未初始化${NC}"
    echo "  提示: 首次部署时会自动克隆仓库"
    ((PASSED++))
fi

echo ""

# 5. 测试 Git 访问
echo -e "${BLUE}━━━ Git 仓库访问测试 ━━━${NC}"

GIT_REPO="https://github.com/allenxing4071/aicoin.git"
echo -n "测试仓库访问... "

if ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no "${SERVER_USER}@${SERVER_HOST}" "git ls-remote $GIT_REPO HEAD" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 通过${NC}"
    echo "  仓库: $GIT_REPO"
    ((PASSED++))
else
    echo -e "${RED}✗ 失败${NC}"
    echo "  提示: 如果是私有仓库，需要配置访问凭据"
    echo "  方法 1: SSH Key (推荐)"
    echo "    ssh-keygen -t ed25519 -C 'deploy@aicoin.com'"
    echo "    # 将公钥添加到 GitHub Deploy Keys"
    echo ""
    echo "  方法 2: Personal Access Token"
    echo "    git config --global credential.helper store"
    ((FAILED++))
fi

echo ""

# 总结
echo "════════════════════════════════════════════════════════════════"
echo -e "  测试完成: ${GREEN}通过 $PASSED${NC} / ${RED}失败 $FAILED${NC}"
echo "════════════════════════════════════════════════════════════════"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ 所有检查通过！可以开始部署${NC}"
    echo ""
    echo "执行部署命令："
    echo "  ./scripts/deploy-git.sh          # 标准部署"
    echo "  ./scripts/deploy-git-quick.sh    # 快速部署"
    echo ""
    exit 0
else
    echo -e "${YELLOW}⚠️  部分检查未通过，请修复后再部署${NC}"
    echo ""
    echo "常见问题排查："
    echo "  1. SSH 连接失败 → 检查密钥权限: chmod 600 $SSH_KEY"
    echo "  2. Git 未安装 → ssh 登录服务器安装: yum install -y git"
    echo "  3. Docker 未安装 → 参考 Docker 官方文档安装"
    echo "  4. Git 访问失败 → 配置仓库访问凭据（SSH Key 或 Token）"
    echo ""
    exit 1
fi

