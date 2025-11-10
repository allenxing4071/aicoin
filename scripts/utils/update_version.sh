#!/bin/bash

# 版本号更新脚本
# 用法: ./update_version.sh <new_version>
# 示例: ./update_version.sh 3.3.0

set -e

if [ -z "$1" ]; then
    echo "❌ 错误: 请提供新版本号"
    echo "用法: ./update_version.sh <new_version>"
    echo "示例: ./update_version.sh 3.3.0"
    exit 1
fi

NEW_VERSION=$1

# 验证版本号格式 (x.y.z)
if ! [[ $NEW_VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "❌ 错误: 版本号格式不正确"
    echo "正确格式: x.y.z (例如: 3.2.0)"
    exit 1
fi

echo "🔄 开始更新版本号到 v$NEW_VERSION..."
echo ""

# 1. 更新 VERSION 文件
echo "📝 更新 VERSION 文件..."
echo "$NEW_VERSION" > VERSION
echo "  ✅ VERSION"

# 2. 更新后端配置文件
echo ""
echo "📝 更新后端配置..."
sed -i '' "s/APP_VERSION: str = \"[0-9.]*\"/APP_VERSION: str = \"$NEW_VERSION\"/" backend/app/core/config.py
echo "  ✅ backend/app/core/config.py"

# 3. 更新前端 package.json
echo ""
echo "📝 更新前端 package.json..."
if [ -f "frontend/package.json" ]; then
    sed -i '' "s/\"version\": \"[0-9.]*\"/\"version\": \"$NEW_VERSION\"/" frontend/package.json
    echo "  ✅ frontend/package.json"
fi

# 4. 更新 README.md 中的版本号
echo ""
echo "📝 更新 README.md..."
if [ -f "README.md" ]; then
    # 更新版本徽章
    sed -i '' "s/version-[0-9.]*/version-$NEW_VERSION/" README.md
    echo "  ✅ README.md"
fi

# 5. 创建版本标签
echo ""
echo "🏷️  创建 Git 标签..."
CURRENT_BRANCH=$(git branch --show-current)
echo "  当前分支: $CURRENT_BRANCH"

read -p "是否创建 Git 标签 v$NEW_VERSION? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    git tag -a "v$NEW_VERSION" -m "Release version $NEW_VERSION"
    echo "  ✅ 已创建标签 v$NEW_VERSION"
    
    read -p "是否推送标签到远程? (y/n) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        git push origin "v$NEW_VERSION"
        echo "  ✅ 已推送标签到远程"
    fi
fi

echo ""
echo "🎉 版本号更新完成！"
echo ""
echo "📊 更新摘要："
echo "  - 新版本: v$NEW_VERSION"
echo "  - VERSION 文件: ✅"
echo "  - 后端配置: ✅"
echo "  - 前端配置: ✅"
echo "  - README: ✅"
echo ""
echo "⚠️  下一步："
echo "  1. 检查更改: git diff"
echo "  2. 提交更改: git add . && git commit -m 'chore: bump version to $NEW_VERSION'"
echo "  3. 重新构建: docker compose build"
echo "  4. 重启服务: docker compose up -d"
echo ""

