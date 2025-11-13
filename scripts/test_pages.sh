#!/bin/bash

echo "=========================================="
echo "🌐 测试关键页面访问"
echo "=========================================="
echo ""

# 定义测试的页面
declare -A pages=(
    ["主页"]="http://localhost:3000"
    ["AI日记"]="http://localhost:3000/admin/trading"
    ["情报平台配置"]="http://localhost:3000/admin/ai-platforms/intelligence"
    ["决策间隔优化"]="http://localhost:3000/admin/ai-cost/optimization"
    ["交易所管理"]="http://localhost:3000/admin/exchanges"
)

# 测试每个页面
for page_name in "${!pages[@]}"; do
    url="${pages[$page_name]}"
    status=$(curl -s -o /dev/null -w "%{http_code}" "$url" --max-time 5)
    
    if [ "$status" = "200" ]; then
        echo "✅ $page_name: 可访问 ($url)"
    elif [ "$status" = "000" ]; then
        echo "⚠️  $page_name: 超时或连接失败"
    else
        echo "❌ $page_name: HTTP $status"
    fi
done

echo ""
echo "=========================================="
echo "🎯 访问主页面:"
echo "   http://localhost:3000"
echo ""
echo "🎯 访问AI日记页面 (查看Qwen工作状态):"
echo "   http://localhost:3000/admin/trading"
echo "=========================================="
