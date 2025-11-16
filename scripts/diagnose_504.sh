#!/bin/bash
# 504 Gateway Timeout 诊断脚本
# 用于快速定位后端服务问题

echo "========================================="
echo "🔍 AIcoin 系统状态诊断"
echo "========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 检查 Docker 服务状态
echo "1️⃣  检查 Docker 服务状态..."
echo "-----------------------------------"
docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}" | grep "aicoin"
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 未找到 AIcoin 容器！${NC}"
    echo "   请运行: cd /path/to/AIcoin && docker-compose up -d"
    exit 1
else
    echo -e "${GREEN}✅ Docker 容器运行中${NC}"
fi
echo ""

# 2. 检查后端服务健康状态
echo "2️⃣  检查后端 API 健康状态..."
echo "-----------------------------------"
BACKEND_HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/status --max-time 5)
if [ "$BACKEND_HEALTH" = "200" ]; then
    echo -e "${GREEN}✅ 后端 API 响应正常 (HTTP $BACKEND_HEALTH)${NC}"
else
    echo -e "${RED}❌ 后端 API 无响应或异常 (HTTP $BACKEND_HEALTH)${NC}"
    echo "   正在检查后端日志..."
    docker logs aicoin-backend --tail 50
fi
echo ""

# 3. 检查数据库连接
echo "3️⃣  检查数据库连接..."
echo "-----------------------------------"
docker exec aicoin-postgres pg_isready -U aicoin > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ PostgreSQL 数据库正常${NC}"
    # 检查数据库大小和连接数
    docker exec aicoin-postgres psql -U aicoin -d aicoin -c "SELECT pg_database_size('aicoin')/1024/1024 AS size_mb;" 2>/dev/null | grep -E "[0-9]+" | head -1
    echo "   活跃连接数:"
    docker exec aicoin-postgres psql -U aicoin -d aicoin -c "SELECT count(*) FROM pg_stat_activity WHERE state = 'active';" 2>/dev/null | grep -E "[0-9]+" | head -1
else
    echo -e "${RED}❌ PostgreSQL 数据库异常${NC}"
fi
echo ""

# 4. 检查 Redis 连接
echo "4️⃣  检查 Redis 缓存..."
echo "-----------------------------------"
docker exec aicoin-redis redis-cli ping > /dev/null 2>&1
if [ $? -eq 0 ]; then
    echo -e "${GREEN}✅ Redis 缓存正常${NC}"
else
    echo -e "${RED}❌ Redis 缓存异常${NC}"
fi
echo ""

# 5. 检查服务器资源
echo "5️⃣  检查服务器资源使用..."
echo "-----------------------------------"
echo "内存使用:"
free -h | grep Mem
echo ""
echo "CPU 负载:"
uptime
echo ""
echo "磁盘使用:"
df -h | grep -E "/$|/var/lib/docker"
echo ""

# 6. 检查后端日志错误
echo "6️⃣  检查后端最近错误日志..."
echo "-----------------------------------"
ERROR_COUNT=$(docker logs aicoin-backend --since 5m 2>&1 | grep -i "error\|exception\|traceback" | wc -l)
if [ $ERROR_COUNT -gt 0 ]; then
    echo -e "${RED}⚠️  发现 $ERROR_COUNT 条错误日志${NC}"
    echo "   最近的错误:"
    docker logs aicoin-backend --since 5m 2>&1 | grep -i "error\|exception" | tail -10
else
    echo -e "${GREEN}✅ 最近5分钟无错误日志${NC}"
fi
echo ""

# 7. 测试超时的 API 端点
echo "7️⃣  测试问题 API 端点..."
echo "-----------------------------------"
echo "测试 /api/v1/intelligence/platforms (5秒超时)..."
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}|%{time_total}" http://localhost:8000/api/v1/intelligence/platforms --max-time 5)
HTTP_CODE=$(echo $RESPONSE | cut -d'|' -f1)
TIME=$(echo $RESPONSE | cut -d'|' -f2)
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ 响应成功 - HTTP $HTTP_CODE - 耗时: ${TIME}s${NC}"
elif [ "$HTTP_CODE" = "000" ]; then
    echo -e "${RED}❌ 请求超时 (>5秒)${NC}"
else
    echo -e "${YELLOW}⚠️  HTTP $HTTP_CODE - 耗时: ${TIME}s${NC}"
fi
echo ""

# 8. Nginx 错误日志
echo "8️⃣  检查 Nginx 错误日志..."
echo "-----------------------------------"
if [ -f "./deploy/logs/error.log" ]; then
    NGINX_ERRORS=$(tail -50 ./deploy/logs/error.log | grep -i "timeout\|502\|503\|504" | wc -l)
    if [ $NGINX_ERRORS -gt 0 ]; then
        echo -e "${YELLOW}⚠️  发现 $NGINX_ERRORS 条超时/网关错误${NC}"
        tail -10 ./deploy/logs/error.log
    else
        echo -e "${GREEN}✅ Nginx 日志正常${NC}"
    fi
else
    echo -e "${YELLOW}⚠️  未找到 Nginx 日志文件${NC}"
fi
echo ""

# 9. 建议操作
echo "========================================="
echo "📋 诊断总结与建议"
echo "========================================="
echo ""

if [ "$BACKEND_HEALTH" != "200" ]; then
    echo -e "${RED}🔥 后端服务异常，建议操作：${NC}"
    echo "   1. 查看完整日志: docker logs aicoin-backend -f"
    echo "   2. 重启后端服务: docker-compose restart backend"
    echo "   3. 检查环境变量: docker exec aicoin-backend env | grep -E 'DATABASE|REDIS'"
    echo ""
fi

if [ $ERROR_COUNT -gt 5 ]; then
    echo -e "${YELLOW}⚠️  错误日志较多，建议：${NC}"
    echo "   1. 检查数据库连接配置"
    echo "   2. 检查 API 密钥是否有效"
    echo "   3. 查看具体错误: docker logs aicoin-backend --since 10m | grep ERROR"
    echo ""
fi

echo -e "${GREEN}✅ 诊断完成！${NC}"
echo ""
echo "如需查看实时日志:"
echo "  docker logs aicoin-backend -f --tail 100"
echo ""

