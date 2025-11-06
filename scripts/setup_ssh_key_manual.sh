#!/bin/bash

###############################################################################
# SSH密钥认证手动设置脚本
# 生成密钥并提供手动配置步骤
###############################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

REMOTE_HOST="192.168.31.185"
REMOTE_USER="allenxing07"
SSH_KEY_PATH="$HOME/.ssh/aicoin_deploy"

log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

echo ""
echo "=========================================="
echo "  SSH密钥手动配置指南"
echo "=========================================="
echo ""

# 1. 生成密钥
log_info "步骤1: 生成SSH密钥对"
echo ""

mkdir -p "$HOME/.ssh"
chmod 700 "$HOME/.ssh"

if [ -f "${SSH_KEY_PATH}" ]; then
    log_warning "密钥已存在: ${SSH_KEY_PATH}"
    log_info "跳过密钥生成步骤"
else
    log_info "执行命令:"
    echo "  ssh-keygen -t ed25519 -f ${SSH_KEY_PATH} -N \"\" -C \"aicoin-deploy\""
    echo ""
    
    ssh-keygen -t ed25519 -f "${SSH_KEY_PATH}" -N "" -C "aicoin-deploy"
    
    chmod 600 "${SSH_KEY_PATH}"
    chmod 644 "${SSH_KEY_PATH}.pub"
    
    log_success "密钥生成完成"
fi

# 2. 显示公钥
echo ""
log_info "步骤2: 复制公钥内容"
echo ""
log_warning "请复制下面的公钥内容（整行）:"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
cat "${SSH_KEY_PATH}.pub"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 3. 手动配置步骤
echo ""
log_info "步骤3: 在远程服务器上配置公钥"
echo ""
echo "请执行以下步骤:"
echo ""
echo "1️⃣  SSH登录到服务器:"
echo "    ssh ${REMOTE_USER}@${REMOTE_HOST}"
echo "    密码: xhl196312"
echo ""
echo "2️⃣  创建.ssh目录（如果不存在）:"
echo "    mkdir -p ~/.ssh"
echo "    chmod 700 ~/.ssh"
echo ""
echo "3️⃣  编辑authorized_keys文件:"
echo "    nano ~/.ssh/authorized_keys"
echo ""
echo "4️⃣  将上面复制的公钥内容粘贴到文件末尾（新的一行）"
echo ""
echo "5️⃣  保存文件（Ctrl+O, Enter, Ctrl+X）"
echo ""
echo "6️⃣  设置文件权限:"
echo "    chmod 600 ~/.ssh/authorized_keys"
echo ""
echo "7️⃣  退出SSH:"
echo "    exit"
echo ""

# 4. 配置SSH config
echo ""
log_info "步骤4: 配置本地SSH config"
echo ""

SSH_CONFIG="$HOME/.ssh/config"

if grep -q "Host aicoin-server" "${SSH_CONFIG}" 2>/dev/null; then
    log_warning "SSH config中已存在配置"
else
    log_info "将以下内容添加到 ${SSH_CONFIG}:"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    cat << EOF
# AIcoin 部署服务器
Host aicoin-server
    HostName ${REMOTE_HOST}
    User ${REMOTE_USER}
    IdentityFile ${SSH_KEY_PATH}
    StrictHostKeyChecking no
    ServerAliveInterval 60
EOF
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    
    read -p "是否自动添加到SSH config? (Y/n): " add_config
    if [[ ! $add_config =~ ^[Nn]$ ]]; then
        cat >> "${SSH_CONFIG}" << EOF

# AIcoin 部署服务器
Host aicoin-server
    HostName ${REMOTE_HOST}
    User ${REMOTE_USER}
    IdentityFile ${SSH_KEY_PATH}
    StrictHostKeyChecking no
    ServerAliveInterval 60

EOF
        log_success "已添加到SSH config"
    fi
fi

# 5. 生成PEM格式
echo ""
log_info "步骤5: 生成PEM格式密钥（可选）"
echo ""

PEM_KEY_PATH="${SSH_KEY_PATH}.pem"
cp "${SSH_KEY_PATH}" "${PEM_KEY_PATH}"
chmod 600 "${PEM_KEY_PATH}"
log_success "PEM格式密钥: ${PEM_KEY_PATH}"

# 6. 测试说明
echo ""
log_info "步骤6: 测试SSH连接"
echo ""
echo "完成上述步骤后，测试连接:"
echo ""
echo "  ssh aicoin-server"
echo ""
echo "或者:"
echo ""
echo "  ssh -i ${SSH_KEY_PATH} ${REMOTE_USER}@${REMOTE_HOST}"
echo ""

# 7. 总结
echo ""
log_success "=========================================="
log_success "  配置完成后的使用方式"
log_success "=========================================="
echo ""
echo "✅ 免密登录:"
echo "   ssh aicoin-server"
echo ""
echo "✅ 使用密钥文件:"
echo "   ssh -i ${SSH_KEY_PATH} ${REMOTE_USER}@${REMOTE_HOST}"
echo ""
echo "✅ 使用PEM格式:"
echo "   ssh -i ${PEM_KEY_PATH} ${REMOTE_USER}@${REMOTE_HOST}"
echo ""
echo "✅ 部署脚本会自动使用密钥"
echo ""
echo "📁 密钥文件位置:"
echo "   私钥: ${SSH_KEY_PATH}"
echo "   公钥: ${SSH_KEY_PATH}.pub"
echo "   PEM:  ${PEM_KEY_PATH}"
echo ""

