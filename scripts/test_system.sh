#!/bin/bash

echo "=========================================="
echo "🧪 AIcoin 系统测试"
echo "=========================================="
echo ""

# 测试 1: 后端健康检查
echo "1️⃣ 测试后端健康状态..."
curl -s http://localhost:8000/health | python3 -m json.tool | grep -E "status|is_running|decision_interval"
echo ""

# 测试 2: 今日日记
echo "2️⃣ 测试 AI 日记 API..."
curl -s "http://localhost:8000/api/v1/ai-journal/daily-journal?target_date=$(date +%Y-%m-%d)" | python3 -c "import sys, json; data = json.load(sys.stdin); print(f'✅ 日记加载成功'); print(f'📊 Qwen 报告数: {data[\"data_summary\"][\"qwen_reports_count\"]}'); print(f'📰 新闻数: {data[\"data_summary\"][\"news_count\"]}'); print(f'🐋 巨鲸活动: {data[\"data_summary\"][\"whale_signals_count\"]}'); print(f'🤖 DeepSeek 决策: {data[\"data_summary\"][\"decisions_count\"]}')"
echo ""

# 测试 3: 情报平台状态
echo "3️⃣ 测试情报平台..."
curl -s http://localhost:8000/api/v1/intelligence/platforms | python3 -c "import sys, json; data = json.load(sys.stdin); print(f'✅ 平台数量: {data[\"total\"]}'); [print(f'  - {p[\"name\"]}: {\"启用\" if p[\"enabled\"] else \"禁用\"}') for p in data['platforms'][:3]]"
echo ""

# 测试 4: 前端页面
echo "4️⃣ 测试前端页面..."
if curl -s -o /dev/null -w "%{http_code}" http://localhost:3000 | grep -q "200"; then
    echo "✅ 前端页面可访问 (http://localhost:3000)"
else
    echo "❌ 前端页面不可访问"
fi
echo ""

# 测试 5: 交易所配置
echo "5️⃣ 测试交易所配置..."
curl -s http://localhost:8000/api/v1/exchanges | python3 -c "import sys, json; data = json.load(sys.stdin); print(f'✅ 交易所数量: {len(data)}'); [print(f'  - {ex[\"name\"]}: {\"已选\" if ex.get(\"is_selected\") else \"未选\"}') for ex in data[:3]]" 2>/dev/null || echo "⚠️ 交易所 API 可能还未完全加载"
echo ""

echo "=========================================="
echo "📊 测试完成"
echo "=========================================="
