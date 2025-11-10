#!/bin/bash

###############################################################################
# 在Ubuntu服务器上安装Cursor桌面版（需要图形界面）
# 如果服务器有桌面环境，可以使用此脚本
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
echo "  Cursor 桌面版安装脚本"
echo "=========================================="
echo ""

# 检查是否有图形界面
if [ -z "$DISPLAY" ] && [ -z "$WAYLAND_DISPLAY" ]; then
    log_warning "未检测到图形界面环境"
    log_info "如果服务器没有桌面环境，建议使用 install_cursor_server.sh 安装code-server"
    read -p "是否继续安装桌面版? (y/N): " continue_install
    if [[ ! $continue_install =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

# 1. 下载最新版Cursor
log_info "下载Cursor最新版..."
CURSOR_VERSION="latest"
DOWNLOAD_URL="https://downloader.cursor.sh/linux/appImage/x64"

cd /tmp
wget -O cursor.AppImage "$DOWNLOAD_URL"

if [ $? -ne 0 ]; then
    log_error "下载失败"
    exit 1
fi

log_success "下载完成"

# 2. 设置执行权限
log_info "设置执行权限..."
chmod +x cursor.AppImage

# 3. 安装到系统
log_info "安装Cursor..."
sudo mkdir -p /opt/cursor
sudo mv cursor.AppImage /opt/cursor/cursor.AppImage

# 4. 创建符号链接
sudo ln -sf /opt/cursor/cursor.AppImage /usr/local/bin/cursor

# 5. 创建桌面快捷方式
log_info "创建桌面快捷方式..."
cat > ~/.local/share/applications/cursor.desktop << EOF
[Desktop Entry]
Name=Cursor
Comment=The AI-first Code Editor
Exec=/opt/cursor/cursor.AppImage %F
Terminal=false
Type=Application
Icon=cursor
StartupWMClass=Cursor
Categories=Development;IDE;
MimeType=text/plain;inode/directory;
EOF

log_success "Cursor安装完成"

echo ""
log_success "=========================================="
log_success "  安装完成！"
log_success "=========================================="
echo ""
echo "🚀 启动Cursor:"
echo "  命令行: cursor"
echo "  或在应用菜单中找到 Cursor"
echo ""
echo "📁 安装位置: /opt/cursor/"
echo ""

