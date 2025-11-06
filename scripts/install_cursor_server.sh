#!/bin/bash

###############################################################################
# 在服务器上安装Cursor CLI和开发环境
# 服务器: 192.168.31.185
###############################################################################

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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
echo "  Cursor Server 安装脚本"
echo "=========================================="
echo ""

# 1. 更新系统
log_info "更新系统包..."
sudo apt-get update

# 2. 安装必要的依赖
log_info "安装依赖包..."
sudo apt-get install -y \
    wget \
    curl \
    git \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release

log_success "依赖包安装完成"

# 3. 安装Node.js (Cursor需要)
log_info "安装Node.js..."
if ! command -v node &> /dev/null; then
    curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
    sudo apt-get install -y nodejs
    log_success "Node.js安装完成: $(node --version)"
else
    log_success "Node.js已安装: $(node --version)"
fi

# 4. 安装code-server (开源的VS Code Server)
log_info "安装code-server..."
if ! command -v code-server &> /dev/null; then
    curl -fsSL https://code-server.dev/install.sh | sh
    log_success "code-server安装完成"
else
    log_success "code-server已安装"
fi

# 5. 配置code-server
log_info "配置code-server..."
mkdir -p ~/.config/code-server

cat > ~/.config/code-server/config.yaml << EOF
bind-addr: 0.0.0.0:8080
auth: password
password: aicoin2025
cert: false
EOF

log_success "code-server配置完成"
log_info "访问地址: http://192.168.31.185:8080"
log_info "密码: aicoin2025"

# 6. 安装Cursor CLI (如果可用)
log_info "尝试安装Cursor CLI..."
if [ -f /usr/local/bin/cursor ]; then
    log_success "Cursor CLI已安装"
else
    log_warning "Cursor CLI暂不支持直接服务器安装"
    log_info "建议使用code-server作为替代"
fi

# 7. 创建systemd服务
log_info "创建code-server systemd服务..."
sudo tee /etc/systemd/system/code-server.service > /dev/null << EOF
[Unit]
Description=code-server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME
ExecStart=/usr/bin/code-server --config ~/.config/code-server/config.yaml
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable code-server
sudo systemctl start code-server

log_success "code-server服务已启动"

# 8. 检查服务状态
log_info "检查服务状态..."
sleep 3
if systemctl is-active --quiet code-server; then
    log_success "code-server运行正常"
else
    log_error "code-server启动失败"
    sudo systemctl status code-server
fi

# 9. 配置防火墙
log_info "配置防火墙..."
if command -v ufw &> /dev/null; then
    sudo ufw allow 8080/tcp
    log_success "防火墙规则已添加"
fi

# 10. 安装常用扩展
log_info "安装常用VS Code扩展..."
code-server --install-extension ms-python.python
code-server --install-extension dbaeumer.vscode-eslint
code-server --install-extension esbenp.prettier-vscode
code-server --install-extension ms-vscode.vscode-typescript-next

log_success "扩展安装完成"

echo ""
log_success "=========================================="
log_success "  安装完成！"
log_success "=========================================="
echo ""
echo "📝 访问信息:"
echo "  URL:      http://192.168.31.185:8080"
echo "  密码:     aicoin2025"
echo ""
echo "🔧 常用命令:"
echo "  启动服务: sudo systemctl start code-server"
echo "  停止服务: sudo systemctl stop code-server"
echo "  重启服务: sudo systemctl restart code-server"
echo "  查看状态: sudo systemctl status code-server"
echo "  查看日志: sudo journalctl -u code-server -f"
echo ""
echo "💡 提示:"
echo "  1. 在浏览器中访问 http://192.168.31.185:8080"
echo "  2. 输入密码: aicoin2025"
echo "  3. 开始编码！"
echo ""

