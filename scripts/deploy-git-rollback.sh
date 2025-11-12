#!/bin/bash

################################################################################
# AIcoin 项目 - Git 回滚脚本
# 用途：回滚到指定的 Git 提交或标签
# 使用方法：
#   ./deploy-git-rollback.sh <commit-hash>    # 回滚到指定提交
#   ./deploy-git-rollback.sh HEAD~1           # 回滚到上一个提交
#   ./deploy-git-rollback.sh v3.2.0           # 回滚到指定标签
################################################################################

set -e

# ============================================================================
# 配置区域
# ============================================================================
SERVER_USER="root"
SERVER_HOST="47.250.132.166"
SERVER_PATH="/root/AIcoin"
SSH_KEY="/Users/xinghailong/Documents/soft/AIcoin/ssh-configs/cloud-servers/AIcoin.pem"

# 回滚目标（从命令行参数获取）
ROLLBACK_TARGET="${1}"

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# ============================================================================
# 参数检查
# ============================================================================

if [ -z "$ROLLBACK_TARGET" ]; then
    echo -e "${RED}错误：请指定回滚目标${NC}"
    echo ""
    echo "用法："
    echo "  $0 <commit-hash>    # 回滚到指定提交"
    echo "  $0 HEAD~1           # 回滚到上一个提交"
    echo "  $0 v3.2.0           # 回滚到指定标签"
    echo ""
    echo "查看可用版本："
    echo "  git log --oneline -10"
    echo "  git tag"
    exit 1
fi

# ============================================================================
# 主流程
# ============================================================================

echo "════════════════════════════════════════════════════════════════"
echo "  ⏮️  AIcoin 项目 - 版本回滚"
echo "════════════════════════════════════════════════════════════════"
echo ""
echo -e "${YELLOW}⚠️  警告：即将回滚到版本 $ROLLBACK_TARGET${NC}"
echo ""

# 确认操作
read -p "确认执行回滚？(输入 yes 继续): " CONFIRM
if [ "$CONFIRM" != "yes" ]; then
    echo -e "${RED}❌ 已取消回滚操作${NC}"
    exit 0
fi

echo ""
echo -e "${BLUE}开始回滚...${NC}"
echo ""

ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no \
    "${SERVER_USER}@${SERVER_HOST}" bash << ENDSSH
set -e
cd $SERVER_PATH

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 当前版本信息"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "分支: \$(git branch --show-current)"
echo "提交: \$(git rev-parse HEAD)"
echo "消息: \$(git log -1 --format=%s)"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🔨 停止服务..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker compose down

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "⏮️  回滚代码到: $ROLLBACK_TARGET"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
git fetch origin
git checkout $ROLLBACK_TARGET
git reset --hard $ROLLBACK_TARGET

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 回滚后版本信息"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "分支: \$(git branch --show-current)"
echo "提交: \$(git rev-parse HEAD)"
echo "消息: \$(git log -1 --format=%s)"
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🏗️  重新构建镜像..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker compose build --no-cache

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🚀 启动服务..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker compose up -d

echo ""
echo "⏳ 等待服务启动（15 秒）..."
sleep 15

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📊 容器状态"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
docker compose ps

ENDSSH

echo ""
echo -e "${GREEN}✅ 回滚完成！${NC}"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  🌐 访问地址: https://jifenpay.cc"
echo "  📝 请验证功能是否正常"
echo ""
echo "  如需恢复到最新版本，请运行："
echo "  ./deploy-git.sh main"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

