#!/bin/bash

cd frontend/app/admin

# 账户快照页面
if [ -f "accounts/page.tsx" ]; then
  sed -i '' 's|<h1 className="text-2xl font-bold text-gray-900 mb-6">账户快照</h1>|<PageHeader icon="💼" title="账户快照" description="查看账户余额和净值的历史快照" color="green" />|g' accounts/page.tsx
  sed -i '' 's|<div>$|<div className="space-y-6">|g' accounts/page.tsx
  echo "✅ accounts/page.tsx"
fi

# K线数据页面
if [ -f "market-data/page.tsx" ]; then
  sed -i '' 's|<h1 className="text-2xl font-bold text-gray-900 mb-6">K线数据</h1>|<PageHeader icon="📊" title="K线数据管理" description="查看和管理市场K线数据" color="green" />|g' market-data/page.tsx
  sed -i '' 's|return ($|return (|g' market-data/page.tsx
  echo "✅ market-data/page.tsx"
fi

echo ""
echo "✅ 批量替换完成"
