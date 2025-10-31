#!/bin/bash

echo "=========================================="
echo "🔔 AIcoin v2.0 告警监控设置"
echo "=========================================="
echo ""

# 告警阈值配置
MAX_DRAWDOWN=10.0
MAX_DAILY_LOSS=5.0
MIN_MARGIN_RATIO=20.0
MAX_CONSECUTIVE_LOSSES=3

LOG_FILE="logs/alerts.log"
mkdir -p logs

echo "📋 告警配置:"
echo "   - 最大回撤阈值: ${MAX_DRAWDOWN}%"
echo "   - 最大日亏损阈值: ${MAX_DAILY_LOSS}%"
echo "   - 最低保证金率: ${MIN_MARGIN_RATIO}%"
echo "   - 最大连续亏损: ${MAX_CONSECUTIVE_LOSSES}次"
echo "   - 告警日志: ${LOG_FILE}"
echo ""

# 检查函数
check_system() {
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    # 获取系统状态
    local health=$(curl -s http://localhost:8000/health)
    
    # 检查AI Orchestrator
    if echo "$health" | grep -q '"ai_orchestrator": false'; then
        echo "[$timestamp] ⚠️  警告: AI Orchestrator未运行" | tee -a "$LOG_FILE"
        return 1
    fi
    
    # 检查权限降级
    local current_level=$(echo "$health" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('orchestrator_status', {}).get('permission_level', 'unknown'))")
    if [ "$current_level" = "L0" ]; then
        echo "[$timestamp] 🚨 严重: 权限降级到L0保护模式！" | tee -a "$LOG_FILE"
        # 发送通知（可以集成钉钉、企业微信等）
        return 1
    fi
    
    # 检查决策通过率
    local approval_rate=$(echo "$health" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('orchestrator_status', {}).get('approval_rate', 0))")
    local total_decisions=$(echo "$health" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('orchestrator_status', {}).get('total_decisions', 0))")
    
    if [ "$total_decisions" -gt 10 ] && [ "$(echo "$approval_rate < 10" | bc -l)" -eq 1 ]; then
        echo "[$timestamp] ⚠️  警告: 决策通过率过低 (${approval_rate}%)" | tee -a "$LOG_FILE"
    fi
    
    echo "[$timestamp] ✅ 系统健康检查通过" >> "$LOG_FILE"
    return 0
}

# 后台监控循环
if [ "$1" = "daemon" ]; then
    echo "🚀 启动后台告警监控..."
    echo "   - 检查间隔: 60秒"
    echo "   - 日志文件: $LOG_FILE"
    echo ""
    
    while true; do
        check_system
        sleep 60
    done
else
    # 单次检查
    echo "🔍 执行一次健康检查..."
    echo ""
    check_system
    echo ""
    echo "💡 提示: 运行 './alert_config.sh daemon' 启动后台监控"
    echo ""
fi

