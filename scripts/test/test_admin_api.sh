#!/bin/bash

# 管理后台 API 测试脚本
# 用于快速验证所有管理后台 API 接口是否正常工作

echo "=========================================="
echo "AIcoin 管理后台 API 测试"
echo "=========================================="
echo ""

BASE_URL="http://localhost:8000/api/v1/admin"

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 测试函数
test_endpoint() {
    local name=$1
    local endpoint=$2
    
    echo -n "测试 $name ... "
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$BASE_URL$endpoint")
    
    if [ "$response" = "200" ]; then
        echo -e "${GREEN}✓ 成功${NC} (HTTP $response)"
    else
        echo -e "${RED}✗ 失败${NC} (HTTP $response)"
    fi
}

# 检查后端是否运行
echo "检查后端服务状态..."
if curl -s "http://localhost:8000/health" > /dev/null 2>&1; then
    echo -e "${GREEN}✓ 后端服务正在运行${NC}"
    echo ""
else
    echo -e "${RED}✗ 后端服务未运行${NC}"
    echo "请先启动后端服务:"
    echo "  cd backend && uvicorn app.main:app --reload"
    exit 1
fi

# 测试所有管理后台 API
echo "开始测试管理后台 API..."
echo ""

test_endpoint "列出数据表" "/tables"
test_endpoint "系统统计" "/stats"
test_endpoint "交易记录" "/trades?page=1&page_size=10"
test_endpoint "订单记录" "/orders?page=1&page_size=10"
test_endpoint "账户快照" "/accounts?page=1&page_size=10"
test_endpoint "AI决策日志" "/ai-decisions?page=1&page_size=10"
test_endpoint "K线数据" "/market-data?page=1&page_size=10"
test_endpoint "风控事件" "/risk-events?page=1&page_size=10"

echo ""
echo "=========================================="
echo "测试完成!"
echo "=========================================="
echo ""
echo "访问以下地址查看详细信息:"
echo "  - API 文档: http://localhost:8000/docs"
echo "  - 管理后台: http://localhost:3000/admin"
echo ""

