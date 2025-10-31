#!/bin/bash

echo "=========================================="
echo "📊 AIcoin v2.0 实时监控系统"
echo "=========================================="
echo ""
echo "开始监控... (按 Ctrl+C 停止)"
echo ""

while true; do
    clear
    echo "======================================================================================================="
    echo "🤖 AIcoin v2.0 实时监控 - $(date '+%Y-%m-%d %H:%M:%S')"
    echo "======================================================================================================="
    echo ""
    
    # 系统健康状态
    echo "🏥 系统健康状态"
    echo "-------------------------------------------------------------------------------------------------------"
    HEALTH=$(curl -s http://localhost:8000/health)
    echo "$HEALTH" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    print(f\"  状态: {data.get('status', 'unknown')}\" + (' ✅' if data.get('status') == 'healthy' else ' ❌'))
    print(f\"  版本: {data.get('version', 'unknown')}\")
    
    services = data.get('services', {})
    print(\"  服务状态:\")
    for service, status in services.items():
        print(f\"    - {service}: {'✅ 运行中' if status else '❌ 停止'}\")
    
    if 'orchestrator_status' in data:
        orch = data['orchestrator_status']
        print(\"\\n  Orchestrator 状态:\")
        print(f\"    - 运行状态: {'✅ 运行中' if orch.get('is_running') else '❌ 停止'}\")
        print(f\"    - 权限等级: {orch.get('permission_level')}\")
        print(f\"    - 运行时长: {orch.get('runtime_hours', 0):.2f}小时\")
        print(f\"    - 总决策数: {orch.get('total_decisions', 0)}\")
        print(f\"    - 通过决策: {orch.get('approved_decisions', 0)}\")
        print(f\"    - 通过率: {orch.get('approval_rate', 0):.1f}%\")
        print(f\"    - 决策间隔: {orch.get('decision_interval', 0)}秒\")
except:
    print('  ❌ 无法解析健康状态')
"
    
    echo ""
    echo "📈 系统状态详情"
    echo "-------------------------------------------------------------------------------------------------------"
    STATUS=$(curl -s http://localhost:8000/api/v1/status)
    echo "$STATUS" | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    
    perm = data.get('permission_summary', {})
    print(\"  权限信息:\")
    print(f\"    - 等级: {perm.get('level')} ({perm.get('name')})\")
    print(f\"    - 最大仓位: {perm.get('max_position_pct')}\")
    print(f\"    - 最大杠杆: {perm.get('max_leverage')}\")
    print(f\"    - 置信度阈值: {perm.get('confidence_threshold')}\")
    print(f\"    - 日交易限制: {perm.get('max_daily_trades')}次\")
except:
    print('  ❌ 无法解析系统状态')
"
    
    echo ""
    echo "📝 最近日志 (最新10条)"
    echo "-------------------------------------------------------------------------------------------------------"
    docker-compose -f docker-compose.testnet.yml --env-file .env.testnet logs --tail=10 backend 2>&1 | \
        grep -E "(INFO|WARNING|ERROR|✅|❌|⚠️|🤖|📊|🔄)" | \
        sed 's/aicoin-backend-testnet-v2  | //' | \
        tail -10
    
    echo ""
    echo "======================================================================================================="
    echo "刷新间隔: 10秒 | 按 Ctrl+C 停止监控"
    echo "======================================================================================================="
    
    sleep 10
done

