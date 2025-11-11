#!/bin/bash

echo "🔧 配置服务器使用代理"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

# 您的开发机 IP
PROXY_HOST="192.168.31.133"
PROXY_PORT="8888"
PROXY_URL="http://${PROXY_HOST}:${PROXY_PORT}"

echo "📍 代理地址: ${PROXY_URL}"
echo ""

# SSH 到服务器并配置
ssh -i ssh-configs/local-servers/dev-server-key.pem allenxing07@192.168.31.185 << EOF
cd ~/AIcoin

echo "=== 1. 备份 .env 文件 ==="
cp .env .env.backup.proxy.\$(date +%Y%m%d_%H%M%S)

echo ""
echo "=== 2. 添加代理配置到 .env ==="
# 删除旧的代理配置（如果有）
sed -i '/^HTTP_PROXY=/d' .env
sed -i '/^HTTPS_PROXY=/d' .env
sed -i '/^NO_PROXY=/d' .env

# 添加新的代理配置
echo "" >> .env
echo "# 代理配置（通过开发机访问外网）" >> .env
echo "HTTP_PROXY=${PROXY_URL}" >> .env
echo "HTTPS_PROXY=${PROXY_URL}" >> .env
echo "NO_PROXY=localhost,127.0.0.1,postgres,redis,qdrant" >> .env

echo ""
echo "=== 3. 确认配置 ==="
grep -E "(HTTP_PROXY|HTTPS_PROXY|NO_PROXY)" .env

echo ""
echo "=== 4. 更新 docker-compose.yml ==="
# 检查是否已有代理配置
if grep -q "HTTP_PROXY" docker-compose.yml; then
  echo "docker-compose.yml 已包含代理配置"
else
  echo "添加代理配置到 docker-compose.yml..."
  # 在 backend 的 environment 部分添加代理配置
  sed -i '/backend:/,/environment:/ {
    /environment:/a\      - HTTP_PROXY=${PROXY_URL}
    /environment:/a\      - HTTPS_PROXY=${PROXY_URL}
    /environment:/a\      - NO_PROXY=localhost,127.0.0.1,postgres,redis,qdrant
  }' docker-compose.yml
fi

echo ""
echo "=== 5. 重启后端服务 ==="
docker-compose restart backend

echo ""
echo "等待 15 秒让后端完全启动..."
sleep 15

echo ""
echo "=== 6. 测试代理连接 ==="
echo "测试 Binance API..."
docker-compose exec -T backend curl -s -m 5 https://api.binance.com/api/v3/ping || echo "⚠️ 连接失败（可能是代理未启动）"

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ 配置完成！"
echo ""
echo "📝 下一步:"
echo "   1. 在您的开发机上运行: ./start_proxy.sh"
echo "   2. 在浏览器中测试交易所切换功能"
echo ""
EOF

echo ""
echo "✅ 服务器配置完成！"
echo ""
echo "🚀 现在请在您的开发机上启动代理服务器:"
echo "   ./start_proxy.sh"
echo ""

