#!/bin/bash

# 彻底重启Next.js开发服务器
# 清除所有缓存

echo "🧹 清除Next.js缓存..."
rm -rf .next

echo "🧹 清除node_modules缓存..."
rm -rf node_modules/.cache

echo "✅ 缓存清除完成！"
echo "🚀 请手动运行: npm run dev"
echo ""
echo "⚠️  然后在浏览器中使用 Cmd+Shift+R (Mac) 或 Ctrl+Shift+R (Windows) 硬刷新"

