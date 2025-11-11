#!/bin/bash

echo "🌐 启动本地代理服务器"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📍 您的局域网 IP: 192.168.31.133"
echo "🔌 代理端口: 8888"
echo ""
echo "🔧 在服务器上配置代理:"
echo "   export HTTP_PROXY=http://192.168.31.133:8888"
echo "   export HTTPS_PROXY=http://192.168.31.133:8888"
echo ""
echo "或者在 docker-compose.yml 中添加:"
echo "   environment:"
echo "     - HTTP_PROXY=http://192.168.31.133:8888"
echo "     - HTTPS_PROXY=http://192.168.31.133:8888"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "按 Ctrl+C 停止代理服务器"
echo ""

# 启动代理服务器
python3 proxy_server.py

