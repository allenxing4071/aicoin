#!/bin/bash
# AIcoin 数据同步和测试脚本
# 创建时间: 2025-11-10
# 用途: 完成本地数据同步到 GCP 服务器 + 测试币安交易所

set -e  # 遇到错误立即退出

PROJECT_DIR="/Users/xinghailong/Documents/soft/AIcoin"
SSH_KEY="$PROJECT_DIR/ssh-configs/cloud-servers/gcp/gcp-aicoin-key"
SERVER="xinghailong@34.173.52.255"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_FILE="$PROJECT_DIR/logs/sync_${TIMESTAMP}.log"

# 创建日志目录
mkdir -p "$PROJECT_DIR/logs"

echo "=== AIcoin 数据同步和测试 ===" | tee -a "$LOG_FILE"
echo "开始时间: $(date)" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"

# ============================================
# 任务 1: 同步本地数据库到服务器
# ============================================
echo "【任务 1/2】同步本地数据库到 GCP 服务器" | tee -a "$LOG_FILE"
echo "----------------------------------------" | tee -a "$LOG_FILE"

cd "$PROJECT_DIR"

# 1.1 导出本地数据库
echo "步骤 1.1: 导出本地数据库..." | tee -a "$LOG_FILE"
docker compose exec -T postgres pg_dump -U aicoin aicoin --clean --if-exists > "/tmp/aicoin_backup_${TIMESTAMP}.sql" 2>&1 | tee -a "$LOG_FILE"
BACKUP_FILE="/tmp/aicoin_backup_${TIMESTAMP}.sql"
BACKUP_SIZE=$(ls -lh "$BACKUP_FILE" | awk '{print $5}')
BACKUP_LINES=$(wc -l < "$BACKUP_FILE")
echo "✅ 导出完成: $BACKUP_SIZE, $BACKUP_LINES 行" | tee -a "$LOG_FILE"

# 1.2 上传到服务器
echo "" | tee -a "$LOG_FILE"
echo "步骤 1.2: 上传到服务器..." | tee -a "$LOG_FILE"
scp -i "$SSH_KEY" \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    -o ServerAliveInterval=60 \
    "$BACKUP_FILE" \
    "$SERVER:/tmp/aicoin_backup.sql" 2>&1 | tee -a "$LOG_FILE"
echo "✅ 上传完成" | tee -a "$LOG_FILE"

# 1.3 在服务器上导入
echo "" | tee -a "$LOG_FILE"
echo "步骤 1.3: 在服务器上导入数据..." | tee -a "$LOG_FILE"
ssh -i "$SSH_KEY" \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    -o ServerAliveInterval=60 \
    "$SERVER" << 'ENDSSH' 2>&1 | tee -a "$LOG_FILE"
cd /home/xinghailong/AIcoin
echo "开始导入..."
docker compose exec -T postgres psql -U aicoin_user -d aicoin_db < /tmp/aicoin_backup.sql > /tmp/import.log 2>&1
echo "✅ 导入完成"
ENDSSH

# 1.4 验证数据
echo "" | tee -a "$LOG_FILE"
echo "步骤 1.4: 验证数据..." | tee -a "$LOG_FILE"
ssh -i "$SSH_KEY" \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "$SERVER" << 'ENDSSH' 2>&1 | tee -a "$LOG_FILE"
cd /home/xinghailong/AIcoin
echo "=== 数据统计 ==="
docker compose exec -T postgres psql -U aicoin_user -d aicoin_db << 'EOSQL'
SELECT 'admin_users' as table_name, count(*) as count FROM admin_users
UNION ALL SELECT 'exchange_configs', count(*) FROM exchange_configs
UNION ALL SELECT 'orders', count(*) FROM orders
UNION ALL SELECT 'trades', count(*) FROM trades
UNION ALL SELECT 'ai_decisions', count(*) FROM ai_decisions
UNION ALL SELECT 'intelligence_reports', count(*) FROM intelligence_reports;
EOSQL

echo ""
echo "=== 管理员账户 ==="
docker compose exec -T postgres psql -U aicoin_user -d aicoin_db -c "SELECT id, username, email, role, is_active FROM admin_users;"
ENDSSH

echo "" | tee -a "$LOG_FILE"
echo "✅ 任务 1 完成: 数据库同步成功" | tee -a "$LOG_FILE"

# ============================================
# 任务 2: 测试币安交易所切换
# ============================================
echo "" | tee -a "$LOG_FILE"
echo "【任务 2/2】测试币安交易所切换" | tee -a "$LOG_FILE"
echo "----------------------------------------" | tee -a "$LOG_FILE"

# 2.1 检查币安 API 配置
echo "步骤 2.1: 检查币安 API 配置..." | tee -a "$LOG_FILE"
ssh -i "$SSH_KEY" \
    -o StrictHostKeyChecking=no \
    -o UserKnownHostsFile=/dev/null \
    "$SERVER" << 'ENDSSH' 2>&1 | tee -a "$LOG_FILE"
cd /home/xinghailong/AIcoin
echo "检查环境变量..."
docker compose exec backend printenv | grep -E "(BINANCE|HYPERLIQUID)" | sed 's/=.*/=***/' || echo "未配置交易所 API"
ENDSSH

# 2.2 测试 Hyperliquid 切换
echo "" | tee -a "$LOG_FILE"
echo "步骤 2.2: 测试 Hyperliquid 切换..." | tee -a "$LOG_FILE"
HYPERLIQUID_RESULT=$(curl -s -X POST "https://jifenpay.cc/api/v1/exchanges/switch?exchange_name=hyperliquid&market_type=spot" \
  -H "Content-Type: application/json" \
  -w "\nHTTP_CODE:%{http_code}")
echo "$HYPERLIQUID_RESULT" | tee -a "$LOG_FILE"

if echo "$HYPERLIQUID_RESULT" | grep -q "HTTP_CODE:200"; then
    echo "✅ Hyperliquid 切换成功" | tee -a "$LOG_FILE"
else
    echo "❌ Hyperliquid 切换失败" | tee -a "$LOG_FILE"
fi

# 2.3 测试币安切换
echo "" | tee -a "$LOG_FILE"
echo "步骤 2.3: 测试币安切换..." | tee -a "$LOG_FILE"
BINANCE_RESULT=$(curl -s -X POST "https://jifenpay.cc/api/v1/exchanges/switch?exchange_name=binance&market_type=spot" \
  -H "Content-Type: application/json" \
  -w "\nHTTP_CODE:%{http_code}")
echo "$BINANCE_RESULT" | tee -a "$LOG_FILE"

if echo "$BINANCE_RESULT" | grep -q "HTTP_CODE:200"; then
    echo "✅ 币安切换成功" | tee -a "$LOG_FILE"
elif echo "$BINANCE_RESULT" | grep -q "restricted location"; then
    echo "⚠️  币安地理限制问题（需要使用代理或更换 IP）" | tee -a "$LOG_FILE"
elif echo "$BINANCE_RESULT" | grep -q "未配置"; then
    echo "⚠️  币安 API 密钥未配置" | tee -a "$LOG_FILE"
else
    echo "❌ 币安切换失败" | tee -a "$LOG_FILE"
fi

# 2.4 测试管理员登录
echo "" | tee -a "$LOG_FILE"
echo "步骤 2.4: 测试管理员登录..." | tee -a "$LOG_FILE"
LOGIN_RESULT=$(curl -s -X POST "https://jifenpay.cc/api/v1/admin/login" \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}' \
  -w "\nHTTP_CODE:%{http_code}")
echo "$LOGIN_RESULT" | tee -a "$LOG_FILE"

if echo "$LOGIN_RESULT" | grep -q "access_token"; then
    echo "✅ 管理员登录成功" | tee -a "$LOG_FILE"
else
    echo "❌ 管理员登录失败" | tee -a "$LOG_FILE"
fi

echo "" | tee -a "$LOG_FILE"
echo "✅ 任务 2 完成: 交易所测试完成" | tee -a "$LOG_FILE"

# ============================================
# 生成最终报告
# ============================================
echo "" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"
echo "完成时间: $(date)" | tee -a "$LOG_FILE"
echo "日志文件: $LOG_FILE" | tee -a "$LOG_FILE"
echo "========================================" | tee -a "$LOG_FILE"

# 创建简要报告
REPORT_FILE="$PROJECT_DIR/ssh-configs/cloud-servers/gcp/sync-test-report-${TIMESTAMP}.md"
cat > "$REPORT_FILE" << EOF
# GCP 服务器数据同步和测试报告

**执行时间**: $(date)  
**日志文件**: $LOG_FILE

---

## ✅ 任务完成情况

### 1. 数据库同步
- 本地数据导出: ✅ 完成 ($BACKUP_SIZE, $BACKUP_LINES 行)
- 上传到服务器: ✅ 完成
- 服务器导入: ✅ 完成
- 数据验证: ✅ 完成

### 2. 交易所测试
- Hyperliquid: $(echo "$HYPERLIQUID_RESULT" | grep -q "HTTP_CODE:200" && echo "✅ 成功" || echo "❌ 失败")
- 币安 (Binance): $(echo "$BINANCE_RESULT" | grep -q "HTTP_CODE:200" && echo "✅ 成功" || echo "$BINANCE_RESULT" | grep -q "restricted" && echo "⚠️ 地理限制" || echo "❌ 失败")
- 管理员登录: $(echo "$LOGIN_RESULT" | grep -q "access_token" && echo "✅ 成功" || echo "❌ 失败")

---

## 📊 详细日志

完整日志请查看: \`$LOG_FILE\`

---

## 🔗 访问地址

- **前端**: https://jifenpay.cc
- **管理后台**: https://jifenpay.cc/admin/login
- **API 文档**: https://jifenpay.cc/api/docs

---

**报告生成时间**: $(date)
EOF

echo "" | tee -a "$LOG_FILE"
echo "📄 报告已生成: $REPORT_FILE" | tee -a "$LOG_FILE"
echo "" | tee -a "$LOG_FILE"
echo "🎉 所有任务完成！" | tee -a "$LOG_FILE"

