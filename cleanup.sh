#!/bin/bash
# AIcoin 项目清理脚本

echo "🧹 AIcoin 项目瘦身开始..."
echo ""

# 记录开始大小
START_SIZE=$(du -sh . | awk '{print $1}')
echo "📊 清理前大小: $START_SIZE"
echo ""

# 1. Python缓存
echo "1️⃣  清理Python缓存..."
find backend/ -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find backend/ -type f -name "*.pyc" -delete 2>/dev/null
echo "   ✅ Python缓存已清理"

# 2. 前端构建缓存
echo "2️⃣  清理前端构建缓存..."
rm -rf frontend/.next 2>/dev/null
rm -rf frontend/.turbo 2>/dev/null
rm -rf frontend/out 2>/dev/null
echo "   ✅ 前端缓存已清理"

# 3. 系统文件
echo "3️⃣  清理系统临时文件..."
find . -name ".DS_Store" -delete 2>/dev/null
echo "   ✅ 系统文件已清理"

# 4. 日志文件
echo "4️⃣  清理日志文件..."
find logs/ -name "*.log" -delete 2>/dev/null
echo "   ✅ 日志文件已清理"

# 5. 临时文档
echo "5️⃣  清理临时文档..."
rm -f docs/文档整理完成报告.md 2>/dev/null
rm -f 项目瘦身优化方案.md 2>/dev/null
echo "   ✅ 临时文档已清理"

echo ""
echo "🎉 清理完成!"
echo ""

# 记录结束大小
END_SIZE=$(du -sh . | awk '{print $1}')
echo "📊 清理后大小: $END_SIZE"
echo ""
echo "💡 提示: 运行 'git gc --aggressive' 可进一步优化Git仓库"
