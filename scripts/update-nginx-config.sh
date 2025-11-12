#!/bin/bash

# Nginx 配置更新脚本
# 用于修复 /docs 和 /redoc 路由无法访问的问题

set -e

echo "==================================="
echo "Nginx 配置更新脚本"
echo "==================================="
echo ""

# 检查是否有 sudo 权限
if [ "$EUID" -ne 0 ]; then 
    echo "请使用 sudo 运行此脚本"
    echo "用法: sudo bash update-nginx-config.sh"
    exit 1
fi

# 检查 Nginx 容器是否运行
if ! docker ps | grep -q nginx; then
    echo "错误: Nginx 容器未运行"
    exit 1
fi

# 备份当前配置
BACKUP_DIR="/var/backups/nginx-$(date +%Y%m%d-%H%M%S)"
echo "1. 备份当前 Nginx 配置到: $BACKUP_DIR"
docker exec nginx mkdir -p /tmp/nginx-backup
docker exec nginx cp /etc/nginx/nginx.conf /tmp/nginx-backup/ || true
docker cp nginx:/tmp/nginx-backup "$BACKUP_DIR"
echo "   ✓ 备份完成"
echo ""

# 测试新配置文件语法
echo "2. 测试新 Nginx 配置文件语法"
if ! docker run --rm -v "$(pwd)/deploy/nginx/nginx.conf:/etc/nginx/nginx.conf:ro" nginx nginx -t; then
    echo "   ✗ Nginx 配置文件语法错误，请检查配置文件"
    exit 1
fi
echo "   ✓ 配置文件语法正确"
echo ""

# 复制新配置到容器
echo "3. 更新 Nginx 配置文件"
docker cp deploy/nginx/nginx.conf nginx:/etc/nginx/nginx.conf
echo "   ✓ 配置文件已更新"
echo ""

# 测试配置是否正确
echo "4. 在容器内测试配置"
if ! docker exec nginx nginx -t; then
    echo "   ✗ 配置测试失败，恢复备份"
    docker cp "$BACKUP_DIR/nginx.conf" nginx:/etc/nginx/nginx.conf
    docker exec nginx nginx -s reload
    exit 1
fi
echo "   ✓ 配置测试通过"
echo ""

# 重新加载 Nginx
echo "5. 重新加载 Nginx"
docker exec nginx nginx -s reload
echo "   ✓ Nginx 已重新加载"
echo ""

# 等待一秒确保服务完全启动
sleep 2

# 验证更改
echo "6. 验证配置更改"
echo "   测试 /docs 路由..."
if curl -f -s -o /dev/null https://jifenpay.cc/docs; then
    echo "   ✓ /docs 可访问"
else
    echo "   ✗ /docs 无法访问（可能需要检查后端服务）"
fi

echo "   测试 /redoc 路由..."
if curl -f -s -o /dev/null https://jifenpay.cc/redoc; then
    echo "   ✓ /redoc 可访问"
else
    echo "   ✗ /redoc 无法访问（可能需要检查后端服务）"
fi

echo "   测试 /openapi.json 路由..."
if curl -f -s -o /dev/null https://jifenpay.cc/openapi.json; then
    echo "   ✓ /openapi.json 可访问"
else
    echo "   ✗ /openapi.json 无法访问（可能需要检查后端服务）"
fi
echo ""

echo "==================================="
echo "Nginx 配置更新完成！"
echo "==================================="
echo ""
echo "如果遇到问题，可以从备份恢复："
echo "  docker cp $BACKUP_DIR/nginx.conf nginx:/etc/nginx/nginx.conf"
echo "  docker exec nginx nginx -s reload"
echo ""

