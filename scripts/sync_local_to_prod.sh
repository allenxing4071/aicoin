#!/bin/bash
# 同步本地数据到生产服务器
# 用途: 将本地开发环境的数据库同步到吉隆坡生产服务器

set -e

PROJECT_DIR="/Users/xinghailong/Documents/soft/AIcoin"
SSH_KEY="$PROJECT_DIR/ssh-configs/cloud-servers/AIcoin.pem"
SERVER="root@47.250.132.166"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

echo "=== AIcoin 数据同步到生产服务器 ==="
echo "开始时间: $(date)"
echo ""

# 1. 导出本地数据库
echo "步骤 1/3: 导出本地数据库..."
cd "$PROJECT_DIR"

if ! docker compose ps | grep -q "postgres.*Up"; then
    echo "❌ 本地数据库未运行，请先启动: docker compose up -d"
    exit 1
fi

docker compose exec -T postgres pg_dump -U aicoin aicoin --clean --if-exists > "/tmp/aicoin_local_${TIMESTAMP}.sql"
BACKUP_FILE="/tmp/aicoin_local_${TIMESTAMP}.sql"
BACKUP_SIZE=$(ls -lh "$BACKUP_FILE" | awk '{print $5}')
BACKUP_LINES=$(wc -l < "$BACKUP_FILE")
echo "✅ 导出完成: $BACKUP_SIZE, $BACKUP_LINES 行"

# 2. 上传到服务器
echo ""
echo "步骤 2/3: 上传到服务器..."
scp -i "$SSH_KEY" \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "$BACKUP_FILE" \
    "$SERVER:/tmp/aicoin_import.sql"
echo "✅ 上传完成"

# 3. 在服务器上导入
echo ""
echo "步骤 3/3: 在服务器上导入数据..."
ssh -i "$SSH_KEY" \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "$SERVER" << 'ENDSSH'
    
    # 检查容器是否运行
    if ! docker ps | grep -q "aicoin-postgres-prod"; then
        echo "❌ 生产数据库未运行"
        exit 1
    fi
    
    # 导入数据
    echo "正在导入数据..."
    cat /tmp/aicoin_import.sql | docker exec -i aicoin-postgres-prod psql -U aicoin aicoin
    
    # 清理临时文件
    rm -f /tmp/aicoin_import.sql
    
    echo "✅ 数据导入完成"
ENDSSH

# 4. 清理本地临时文件
rm -f "$BACKUP_FILE"

echo ""
echo "=== 同步完成 ==="
echo "结束时间: $(date)"

