#!/bin/bash
# 快速设置脚本 - 直接在服务器上创建管理员账户和基础数据
# 不再尝试导入本地数据，直接创建新数据

SSH_KEY="/Users/xinghailong/Documents/soft/AIcoin/ssh-configs/cloud-servers/gcp/gcp-aicoin-key"
SERVER="xinghailong@34.173.52.255"

echo "=== 快速设置 GCP 服务器 ==="
echo ""

ssh -i "$SSH_KEY" -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null "$SERVER" << 'ENDSSH'
cd /home/xinghailong/AIcoin

echo "1. 创建管理员账户..."
docker compose exec -T postgres psql -U aicoin_user -d aicoin_db << 'EOSQL'
-- 清空并重建管理员
TRUNCATE TABLE admin_users CASCADE;
INSERT INTO admin_users (username, hashed_password, email, role, is_active, created_at, updated_at)
VALUES ('admin', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY5GyYqgdViKe86', 'admin@aicoin.com', 'admin', true, NOW(), NOW());
SELECT '✅ 管理员创建成功' as status, username, email FROM admin_users;
EOSQL

echo ""
echo "2. 初始化交易所配置..."
docker compose exec -T postgres psql -U aicoin_user -d aicoin_db << 'EOSQL'
-- 清空并重建交易所配置
TRUNCATE TABLE exchange_configs CASCADE;
INSERT INTO exchange_configs (name, display_name, is_active, api_type, supported_markets, created_at, updated_at)
VALUES 
('hyperliquid', 'Hyperliquid', true, 'rest', '["spot", "futures"]', NOW(), NOW()),
('binance', 'Binance', true, 'rest', '["spot", "futures"]', NOW(), NOW());
SELECT '✅ 交易所配置完成' as status, name, display_name FROM exchange_configs;
EOSQL

echo ""
echo "3. 测试登录..."
curl -s -X POST "https://jifenpay.cc/api/v1/admin/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' | grep -q "access_token" && echo "✅ 登录测试成功" || echo "❌ 登录测试失败"

echo ""
echo "4. 测试 Hyperliquid 切换..."
curl -s -X POST "https://jifenpay.cc/api/v1/exchanges/switch?exchange_name=hyperliquid&market_type=spot" | grep -q "success" && echo "✅ Hyperliquid 切换成功" || echo "⚠️  Hyperliquid 切换需要配置 API"

echo ""
echo "✅ 快速设置完成！"
echo ""
echo "现在可以访问: https://jifenpay.cc/admin/login"
echo "用户名: admin"
echo "密码: admin123"
ENDSSH

echo ""
echo "🎉 设置完成！请访问 https://jifenpay.cc/admin/login 测试登录"

