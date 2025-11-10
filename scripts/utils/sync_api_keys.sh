#!/bin/bash

# ============================================
# 同步.env中的API密钥到数据库
# ============================================

set -e

echo "🔄 开始同步API密钥到数据库..."

# 检查.env文件是否存在
if [ ! -f ".env" ]; then
    echo "❌ .env文件不存在"
    exit 1
fi

# 加载环境变量
source .env

# 检查Docker容器是否运行
if ! docker ps | grep -q aicoin-postgres; then
    echo "❌ PostgreSQL容器未运行"
    exit 1
fi

echo "📝 同步API密钥..."

# 同步Qwen-Plus密钥
if [ ! -z "$QWEN_API_KEY" ]; then
    docker exec aicoin-postgres psql -U aicoin -d aicoin -c "
    UPDATE intelligence_platforms 
    SET api_key = '$QWEN_API_KEY', enabled = true, updated_at = NOW()
    WHERE provider = 'qwen' AND platform_type = 'qwen-plus';
    " > /dev/null
    echo "  ✅ Qwen-Plus (阿里云) - 已同步"
else
    echo "  ⚠️  Qwen-Plus - 未找到QWEN_API_KEY"
fi

# 同步腾讯云密钥
if [ ! -z "$TENCENT_QWEN_API_KEY" ]; then
    TENCENT_BASE_URL="${TENCENT_QWEN_BASE_URL:-https://api.hunyuan.cloud.tencent.com/v1}"
    docker exec aicoin-postgres psql -U aicoin -d aicoin -c "
    UPDATE intelligence_platforms 
    SET api_key = '$TENCENT_QWEN_API_KEY', 
        base_url = '$TENCENT_BASE_URL',
        enabled = true, 
        updated_at = NOW()
    WHERE provider = 'tencent';
    " > /dev/null
    echo "  ✅ 腾讯云 - 已同步"
else
    echo "  ⚠️  腾讯云 - 未找到TENCENT_QWEN_API_KEY"
fi

# 同步火山引擎密钥
if [ ! -z "$VOLCANO_QWEN_API_KEY" ]; then
    VOLCANO_BASE_URL="${VOLCANO_QWEN_BASE_URL:-https://ark.cn-beijing.volces.com/api/v3}"
    docker exec aicoin-postgres psql -U aicoin -d aicoin -c "
    UPDATE intelligence_platforms 
    SET api_key = '$VOLCANO_QWEN_API_KEY',
        base_url = '$VOLCANO_BASE_URL',
        enabled = true,
        updated_at = NOW()
    WHERE provider = 'volcano';
    " > /dev/null
    echo "  ✅ 火山引擎 - 已同步"
else
    echo "  ⚠️  火山引擎 - 未找到VOLCANO_QWEN_API_KEY"
fi

# 同步百度智能云密钥
if [ ! -z "$BAIDU_QWEN_API_KEY" ]; then
    BAIDU_BASE_URL="${BAIDU_QWEN_BASE_URL:-https://aip.baidubce.com/rpc/2.0/ai_custom/v1/wenxinworkshop}"
    docker exec aicoin-postgres psql -U aicoin -d aicoin -c "
    UPDATE intelligence_platforms 
    SET api_key = '$BAIDU_QWEN_API_KEY',
        base_url = '$BAIDU_BASE_URL',
        enabled = true,
        updated_at = NOW()
    WHERE provider = 'baidu';
    " > /dev/null
    echo "  ✅ 百度智能云 - 已同步"
else
    echo "  ⚠️  百度智能云 - 未找到BAIDU_QWEN_API_KEY"
fi

echo ""
echo "📊 当前配置状态:"
docker exec aicoin-postgres psql -U aicoin -d aicoin -c "
SELECT 
  name,
  provider,
  CASE 
    WHEN api_key IS NULL OR api_key = '' THEN '❌ 未配置'
    ELSE '✅ 已配置 (' || LENGTH(api_key) || ' 字符)'
  END as api_key_status,
  CASE WHEN enabled THEN '✅' ELSE '🔒' END as enabled
FROM intelligence_platforms 
ORDER BY provider;
"

echo ""
echo "🔄 重启后端服务..."
docker restart aicoin-backend > /dev/null

echo ""
echo "✅ API密钥同步完成！"

