#!/bin/bash

# ============================================
# AIcoin 数据恢复脚本
# 用于在清空Docker后快速恢复默认配置
# ============================================

set -e

echo "🔄 开始恢复AIcoin默认数据..."

# 检查Docker容器是否运行
if ! docker ps | grep -q aicoin-postgres; then
    echo "❌ PostgreSQL容器未运行，请先启动Docker服务"
    exit 1
fi

# 等待PostgreSQL就绪
echo "⏳ 等待PostgreSQL就绪..."
sleep 3

# 执行恢复脚本
echo "📝 执行数据恢复..."
docker exec -i aicoin-postgres psql -U aicoin -d aicoin < "$(dirname "$0")/restore_default_data.sql"

echo ""
echo "✅ 数据恢复完成！"
echo ""
echo "📊 已恢复:"
echo "  - 权限等级配置 (L0-L5)"
echo "  - 交易所配置 (Hyperliquid)"
echo "  - 智能平台配置:"
echo "    • Qwen-Plus (阿里云) - 已启用"
echo "    • 百度智能云 (Qwen搜索) - 未启用"
echo "    • 腾讯云 (Qwen搜索) - 未启用"
echo "    • 火山引擎 (Qwen搜索) - 未启用"
echo ""
echo "🔑 同步API密钥..."
if [ -f "$(dirname "$0")/sync_api_keys.sh" ]; then
    bash "$(dirname "$0")/sync_api_keys.sh"
else
    echo "⚠️  未找到sync_api_keys.sh，跳过API密钥同步"
    echo "🔄 重启后端服务..."
    docker restart aicoin-backend
    sleep 8
fi

echo ""
echo "✅ 系统已完全恢复！"
echo "🌐 前端: http://localhost:3000"
echo "🔧 后端: http://localhost:8000"

