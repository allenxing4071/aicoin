#!/bin/bash

echo "=========================================="
echo "🚨 AIcoin 紧急停止脚本"
echo "=========================================="
echo ""
echo "原因：v1.0系统存在严重缺陷（-48.8%亏损）"
echo "方案：立即停止，等待v2.0新系统完成"
echo ""

# 1. 检查Docker容器状态
echo "📋 第1步：检查当前运行的容器..."
docker-compose ps

echo ""
read -p "确认要停止所有容器吗？(输入 YES 继续): " confirm

if [ "$confirm" != "YES" ]; then
    echo "❌ 操作已取消"
    exit 1
fi

echo ""
echo "🛑 第2步：停止所有Docker容器..."
docker-compose down

echo ""
echo "✅ 容器已停止"
echo ""

# 2. 检查是否还有残留进程
echo "🔍 第3步：检查是否有残留Python进程..."
ps aux | grep -E "uvicorn|celery|python.*app.main" | grep -v grep

echo ""
echo "=========================================="
echo "✅ 系统已成功停止！"
echo "=========================================="
echo ""
echo "⚠️  重要提醒："
echo ""
echo "1. 🏦 立即登录 Hyperliquid 平台"
echo "   网址: https://app.hyperliquid.xyz/"
echo "   - 检查当前持仓"
echo "   - 手动平仓所有持仓（如果有）"
echo "   - 记录当前账户余额"
echo ""
echo "2. 📊 记录当前状态："
echo "   - 初始资金: \$599.80"
echo "   - 当前余额: \$_____  (请填写)"
echo "   - 总亏损:   -_____%  (请计算)"
echo ""
echo "3. 🔒 系统已进入保护模式"
echo "   - 所有自动交易已停止"
echo "   - 数据仍然保存在数据库中"
echo "   - 可以随时查看历史记录"
echo ""
echo "4. 📅 下一步计划（3-5天）："
echo "   Day 1-2: 实现DecisionEngineV2"
echo "   Day 3:   单元测试"
echo "   Day 4:   测试网集成测试"
echo "   Day 5:   小资金试运行(\$100)"
echo ""
echo "=========================================="
echo "等待v2.0新系统完成后再启动交易！"
echo "=========================================="
echo ""

