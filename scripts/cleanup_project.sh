#!/bin/bash
# AIcoin 项目清理脚本
# 执行日期: 2025-11-07
# 作用: 清理临时文件、备份文件和未使用的文件

set -e

PROJECT_ROOT="/Users/xinghailong/Documents/soft/AIcoin"
cd "$PROJECT_ROOT"

echo "🧹 开始清理 AIcoin 项目..."
echo "======================================"

# 1. 清理 .bak 备份文件
echo ""
echo "📦 1. 清理备份文件 (.bak)"
echo "--------------------------------------"
BAK_COUNT=$(find . -name "*.bak" -type f | wc -l | tr -d ' ')
echo "发现 $BAK_COUNT 个 .bak 文件"

if [ "$BAK_COUNT" -gt 0 ]; then
    echo "备份文件列表:"
    find . -name "*.bak" -type f | head -10
    echo ""
    read -p "是否删除这些备份文件? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        find . -name "*.bak" -type f -delete
        echo "✅ 已删除 $BAK_COUNT 个备份文件"
    else
        echo "⏭️  跳过备份文件清理"
    fi
fi

# 2. 清理 Python 缓存
echo ""
echo "🐍 2. 清理 Python 缓存文件"
echo "--------------------------------------"
PYC_COUNT=$(find backend -name "*.pyc" -type f 2>/dev/null | wc -l | tr -d ' ')
PYCACHE_COUNT=$(find backend -name "__pycache__" -type d 2>/dev/null | wc -l | tr -d ' ')
echo "发现 $PYC_COUNT 个 .pyc 文件"
echo "发现 $PYCACHE_COUNT 个 __pycache__ 目录"

if [ "$PYC_COUNT" -gt 0 ] || [ "$PYCACHE_COUNT" -gt 0 ]; then
    find backend -name "*.pyc" -type f -delete 2>/dev/null || true
    find backend -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    echo "✅ 已清理 Python 缓存"
fi

# 3. 清理 Node.js 缓存
echo ""
echo "📦 3. 检查 Node.js 缓存"
echo "--------------------------------------"
if [ -d "frontend/.next" ]; then
    echo "发现 .next 构建缓存"
    read -p "是否清理 Next.js 构建缓存? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -rf frontend/.next
        echo "✅ 已清理 Next.js 缓存"
    else
        echo "⏭️  保留 Next.js 缓存"
    fi
fi

# 4. 清理临时日志文件
echo ""
echo "📝 4. 清理临时日志文件"
echo "--------------------------------------"
if [ -f "/tmp/aicoin_backend.log" ]; then
    LOG_SIZE=$(du -h /tmp/aicoin_backend.log | cut -f1)
    echo "发现后端日志文件: $LOG_SIZE"
    read -p "是否清理临时日志? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        rm -f /tmp/aicoin_backend.log
        echo "✅ 已清理临时日志"
    else
        echo "⏭️  保留临时日志"
    fi
fi

# 5. 检查未使用的脚本
echo ""
echo "📜 5. 检查临时脚本"
echo "--------------------------------------"
if [ -d "backend/scripts" ]; then
    echo "backend/scripts 目录内容:"
    ls -lh backend/scripts/ | tail -n +2
fi

echo ""
echo "======================================"
echo "✅ 清理完成！"
echo ""
echo "📊 清理统计:"
echo "  - 备份文件: $BAK_COUNT 个"
echo "  - Python缓存: $PYC_COUNT 个 .pyc + $PYCACHE_COUNT 个目录"
echo ""
echo "💡 建议:"
echo "  1. 定期运行此脚本保持项目整洁"
echo "  2. 提交代码前先清理临时文件"
echo "  3. 大型重构后清理旧的备份文件"
echo ""

