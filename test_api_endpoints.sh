#!/bin/bash

echo "=========================================="
echo "🧪 AIcoin v2.0 API端点测试"
echo "=========================================="
echo ""

BASE_URL="http://localhost:8000"

# 测试1: 健康检查
echo "1️⃣  健康检查 (GET /health)"
echo "-------------------------------------------"
curl -s "$BASE_URL/health" | python3 -m json.tool
echo ""
echo ""

# 测试2: 系统状态
echo "2️⃣  系统状态 (GET /api/v1/status)"
echo "-------------------------------------------"
curl -s "$BASE_URL/api/v1/status" | python3 -m json.tool
echo ""
echo ""

# 测试3: AI状态
echo "3️⃣  AI状态 (GET /api/v1/ai/status)"
echo "-------------------------------------------"
curl -s "$BASE_URL/api/v1/ai/status" | python3 -m json.tool 2>/dev/null || echo "{\"error\": \"端点可能需要实现\"}"
echo ""
echo ""

# 测试4: 账户余额
echo "4️⃣  账户余额 (GET /api/v1/account/balance)"
echo "-------------------------------------------"
curl -s "$BASE_URL/api/v1/account/balance" | python3 -m json.tool 2>/dev/null || echo "{\"error\": \"需要Hyperliquid连接\"}"
echo ""
echo ""

# 测试5: 持仓信息
echo "5️⃣  持仓信息 (GET /api/v1/account/positions)"
echo "-------------------------------------------"
curl -s "$BASE_URL/api/v1/account/positions" | python3 -m json.tool 2>/dev/null || echo "{\"error\": \"需要Hyperliquid连接\"}"
echo ""
echo ""

# 测试6: 市场数据
echo "6️⃣  市场数据 (GET /api/v1/market/price/BTC-PERP)"
echo "-------------------------------------------"
curl -s "$BASE_URL/api/v1/market/price/BTC-PERP" | python3 -m json.tool 2>/dev/null || echo "{\"error\": \"端点可能需要实现\"}"
echo ""
echo ""

# 测试7: 性能指标
echo "7️⃣  性能指标 (GET /api/v1/performance/summary)"
echo "-------------------------------------------"
curl -s "$BASE_URL/api/v1/performance/summary" | python3 -m json.tool 2>/dev/null || echo "{\"error\": \"端点可能需要实现\"}"
echo ""
echo ""

echo "=========================================="
echo "✅ API测试完成"
echo "=========================================="
echo ""
echo "📊 测试总结:"
echo "   - 已测试7个API端点"
echo "   - 可以通过 http://localhost:8000/docs 查看完整API文档"
echo ""

