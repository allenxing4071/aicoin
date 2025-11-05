#!/bin/bash

# 记录需要更新的页面及其配置
declare -A pages=(
  ["frontend/app/admin/exchanges/page.tsx"]="🔄|交易所管理|管理和切换不同的交易所|blue"
  ["frontend/app/admin/intelligence/page.tsx"]="🕵️‍♀️|Qwen情报系统管理|配置和监控市场情报收集系统、云平台管理|orange"
  ["frontend/app/admin/trading/page.tsx"]="📊|交易系统管理|策略配置、交易监控、风险控制、绩效分析|pink"
  ["frontend/app/admin/memory/page.tsx"]="🤖|AI记忆系统|查看DeepSeek交易员和Qwen情报员的多层存储状态|purple"
  ["frontend/app/admin/ai-decisions/page.tsx"]="🎯|AI决策记录|查看AI交易决策的历史记录和分析|purple"
  ["frontend/app/admin/model-performance/page.tsx"]="📈|模型性能监控|监控AI模型的性能指标和准确率|cyan"
  ["frontend/app/admin/trades/page.tsx"]="💰|交易记录|查看所有交易的详细记录|pink"
  ["frontend/app/admin/orders/page.tsx"]="📋|订单记录|查看所有订单的详细信息|pink"
  ["frontend/app/admin/accounts/page.tsx"]="💼|账户快照|查看账户余额和净值的历史快照|green"
  ["frontend/app/admin/market-data/page.tsx"]="📊|K线数据管理|查看和管理市场K线数据|green"
  ["frontend/app/admin/risk-events/page.tsx"]="⚠️|风控事件监控|监控和管理风险控制事件|orange"
  ["frontend/app/admin/permissions/page.tsx"]="🔐|权限管理|管理用户角色和权限配置|purple"
  ["frontend/app/admin/users/page.tsx"]="👥|用户管理|管理系统用户和账户|blue"
)

echo "📋 页面配置:"
for page in "${!pages[@]}"; do
  IFS='|' read -r icon title desc color <<< "${pages[$page]}"
  echo "  $page"
  echo "    图标: $icon  标题: $title  颜色: $color"
done

echo ""
echo "✅ 配置已准备,准备统一更新所有页面头部"
