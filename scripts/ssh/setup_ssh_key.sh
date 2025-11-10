#!/bin/bash

###############################################################################
# SSH密钥认证设置脚本
# 为远程服务器配置SSH密钥，实现免密登录
###############################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

REMOTE_HOST="192.168.31.185"
REMOTE_USER="allenxing07"
REMOTE_PASSWORD="xhl196312"
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

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

echo ""
echo "=========================================="
echo "  SSH密钥认证设置"
echo "  目标: ${REMOTE_USER}@${REMOTE_HOST}"
echo "=========================================="
echo ""

# 1. 检查是否已有密钥
if [ -f "${SSH_KEY_PATH}" ]; then
    log_warning "密钥文件已存在: ${SSH_KEY_PATH}"
    read -p "是否覆盖现有密钥? (y/N): " overwrite
    if [[ ! $overwrite =~ ^[Yy]$ ]]; then
        log_info "使用现有密钥"
    else
        rm -f "${SSH_KEY_PATH}" "${SSH_KEY_PATH}.pub"
        log_info "已删除旧密钥"
    fi
fi

# 2. 生成SSH密钥对
if [ ! -f "${SSH_KEY_PATH}" ]; then
    log_info "生成SSH密钥对..."
    
    # 创建.ssh目录
    mkdir -p "$HOME/.ssh"
    chmod 700 "$HOME/.ssh"
    
    # 生成密钥（不设置密码短语，方便自动化）
    ssh-keygen -t ed25519 -f "${SSH_KEY_PATH}" -N "" -C "aicoin-deploy-key"
    
    if [ $? -eq 0 ]; then
        log_success "密钥生成成功"
        log_info "私钥: ${SSH_KEY_PATH}"
        log_info "公钥: ${SSH_KEY_PATH}.pub"
    else
        log_error "密钥生成失败"
        exit 1
    fi
else
    log_info "使用现有密钥: ${SSH_KEY_PATH}"
fi

# 3. 设置密钥权限
chmod 600 "${SSH_KEY_PATH}"
chmod 644 "${SSH_KEY_PATH}.pub"
log_success "密钥权限设置完成"

# 4. 显示公钥
echo ""
log_info "公钥内容:"
cat "${SSH_KEY_PATH}.pub"
echo ""

# 5. 复制公钥到远程服务器
log_info "将公钥复制到远程服务器..."
log_warning "需要输入密码: ${REMOTE_PASSWORD}"
echo ""

# 检查是否安装了sshpass
if command -v sshpass &> /dev/null; then
    # 使用sshpass自动输入密码
    sshpass -p "${REMOTE_PASSWORD}" ssh-copy-id -i "${SSH_KEY_PATH}.pub" -o StrictHostKeyChecking=no "${REMOTE_USER}@${REMOTE_HOST}"
else
    # 手动输入密码
    log_warning "未安装sshpass，需要手动输入密码"
    log_info "如需自动化，可安装sshpass: brew install sshpass (macOS) 或 apt-get install sshpass (Linux)"
    ssh-copy-id -i "${SSH_KEY_PATH}.pub" -o StrictHostKeyChecking=no "${REMOTE_USER}@${REMOTE_HOST}"
fi

if [ $? -eq 0 ]; then
    log_success "公钥已复制到远程服务器"
else
    log_error "公钥复制失败"
    echo ""
    log_info "您可以手动复制公钥到服务器:"
    echo "1. 复制公钥内容:"
    echo "   cat ${SSH_KEY_PATH}.pub"
    echo ""
    echo "2. SSH到服务器:"
    echo "   ssh ${REMOTE_USER}@${REMOTE_HOST}"
    echo ""
    echo "3. 将公钥添加到 ~/.ssh/authorized_keys:"
    echo "   mkdir -p ~/.ssh"
    echo "   echo '公钥内容' >> ~/.ssh/authorized_keys"
    echo "   chmod 700 ~/.ssh"
    echo "   chmod 600 ~/.ssh/authorized_keys"
    exit 1
fi

# 6. 测试SSH连接
echo ""
log_info "测试SSH密钥认证..."
if ssh -i "${SSH_KEY_PATH}" -o BatchMode=yes -o ConnectTimeout=5 "${REMOTE_USER}@${REMOTE_HOST}" exit 2>/dev/null; then
    log_success "SSH密钥认证测试成功！"
else
    log_error "SSH密钥认证测试失败"
    exit 1
fi

# 7. 配置SSH config文件
SSH_CONFIG="$HOME/.ssh/config"
log_info "配置SSH config文件..."

# 检查是否已有配置
if grep -q "Host aicoin-server" "${SSH_CONFIG}" 2>/dev/null; then
    log_warning "SSH config中已存在 aicoin-server 配置"
else
    cat >> "${SSH_CONFIG}" << EOF

# AIcoin 部署服务器
Host aicoin-server
    HostName ${REMOTE_HOST}
    User ${REMOTE_USER}
    IdentityFile ${SSH_KEY_PATH}
    StrictHostKeyChecking no
    UserKnownHostsFile /dev/null
    ServerAliveInterval 60
    ServerAliveCountMax 3

EOF
    log_success "SSH config配置完成"
fi

# 8. 导出PEM格式（可选）
PEM_KEY_PATH="${SSH_KEY_PATH}.pem"
log_info "生成PEM格式私钥..."
ssh-keygen -p -m PEM -f "${SSH_KEY_PATH}" -N "" -P "" 2>/dev/null || cp "${SSH_KEY_PATH}" "${PEM_KEY_PATH}"
chmod 600 "${PEM_KEY_PATH}"
log_success "PEM格式私钥: ${PEM_KEY_PATH}"

# 9. 显示使用说明
echo ""
log_success "=========================================="
log_success "  SSH密钥认证设置完成！"
log_success "=========================================="
echo ""
echo -e "${GREEN}现在可以免密登录了！${NC}"
echo ""
echo "方式1 - 使用别名登录:"
echo "  ssh aicoin-server"
echo ""
echo "方式2 - 使用密钥文件:"
echo "  ssh -i ${SSH_KEY_PATH} ${REMOTE_USER}@${REMOTE_HOST}"
echo ""
echo "方式3 - 使用PEM格式:"
echo "  ssh -i ${PEM_KEY_PATH} ${REMOTE_USER}@${REMOTE_HOST}"
echo ""
echo -e "${BLUE}密钥文件位置:${NC}"
echo "  私钥(OpenSSH): ${SSH_KEY_PATH}"
echo "  私钥(PEM):     ${PEM_KEY_PATH}"
echo "  公钥:          ${SSH_KEY_PATH}.pub"
echo ""
echo -e "${YELLOW}测试连接:${NC}"
echo "  ssh aicoin-server 'echo \"连接成功！\"'"
echo ""
echo -e "${YELLOW}部署脚本会自动使用密钥认证${NC}"
echo ""

