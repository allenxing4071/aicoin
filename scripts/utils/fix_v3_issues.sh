#!/bin/bash
# AIcoin v3.0 问题快速修复脚本
# 日期: 2025-11-05

set -e  # 遇到错误立即退出

echo "🔧 AIcoin v3.0 问题修复脚本"
echo "================================"
echo ""

# 颜色定义
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="/Users/xinghailong/Documents/soft/AIcoin"
cd "$PROJECT_ROOT"

# 检查函数
check_docker() {
    if ! command -v docker &> /dev/null; then
        echo -e "${RED}❌ Docker未安装${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Docker已安装${NC}"
}

check_docker_compose() {
    if ! command -v docker-compose &> /dev/null; then
        echo -e "${RED}❌ Docker Compose未安装${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ Docker Compose已安装${NC}"
}

# 1. 执行数据库迁移
fix_database_migration() {
    echo ""
    echo -e "${YELLOW}📊 步骤1: 执行数据库迁移...${NC}"
    
    if docker ps --format '{{.Names}}' | grep -q "aicoin-backend"; then
        echo "执行Alembic迁移..."
        docker-compose -f deploy/docker-compose.yml exec -T backend alembic upgrade head
        echo -e "${GREEN}✅ 数据库迁移完成${NC}"
    else
        echo -e "${RED}❌ 后端容器未运行，跳过迁移${NC}"
    fi
}

# 2. 修复Celery Beat配置
fix_celery_beat() {
    echo ""
    echo -e "${YELLOW}⏰ 步骤2: 修复Celery Beat配置...${NC}"
    
    # 备份原文件
    if [ -f "deploy/docker-compose.yml" ]; then
        cp deploy/docker-compose.yml deploy/docker-compose.yml.backup
        echo "已备份: deploy/docker-compose.yml.backup"
    fi
    
    # 修改Celery Beat命令
    # 使用Python模块方式调用celery
    echo "修改Celery Beat启动命令..."
    
    cat > /tmp/celery_fix.txt << 'EOF'
找到celery-beat服务，将command修改为:
command: python -m celery -A app.tasks.intelligence_learning beat -l info

或者直接使用bash -c:
command: bash -c "cd /app && python -m celery -A app.tasks.intelligence_learning beat -l info"
EOF
    
    cat /tmp/celery_fix.txt
    echo ""
    echo -e "${YELLOW}请手动编辑 deploy/docker-compose.yml 修改celery-beat的command${NC}"
    echo "然后运行: docker-compose -f deploy/docker-compose.yml up -d celery-beat"
}

# 3. 重新构建前端
rebuild_frontend() {
    echo ""
    echo -e "${YELLOW}🎨 步骤3: 重新构建前端...${NC}"
    
    if [ -d "frontend" ]; then
        echo "进入前端目录..."
        cd frontend
        
        # 检查node_modules
        if [ ! -d "node_modules" ]; then
            echo "安装依赖..."
            npm install
        fi
        
        echo "构建前端..."
        npm run build
        
        cd ..
        
        echo "重启前端容器..."
        docker-compose -f deploy/docker-compose.yml restart frontend
        
        echo -e "${GREEN}✅ 前端重新构建完成${NC}"
    else
        echo -e "${RED}❌ frontend目录不存在${NC}"
    fi
}

# 4. 检查环境变量
check_env_config() {
    echo ""
    echo -e "${YELLOW}🔑 步骤4: 检查环境变量配置...${NC}"
    
    if [ -f ".env" ]; then
        echo "检查关键配置..."
        
        # 检查必要的配置项
        required_vars=(
            "QWEN_API_KEY"
            "DEEPSEEK_API_KEY"
            "POSTGRES_PASSWORD"
            "REDIS_PASSWORD"
        )
        
        for var in "${required_vars[@]}"; do
            if grep -q "^${var}=" .env; then
                echo -e "${GREEN}✅ ${var} 已配置${NC}"
            else
                echo -e "${YELLOW}⚠️  ${var} 未配置${NC}"
            fi
        done
        
        # 检查v3.0新增配置
        echo ""
        echo "检查v3.0新增配置..."
        v3_vars=(
            "ENABLE_FREE_PLATFORM"
            "ENABLE_QWEN_SEARCH"
            "ENABLE_QWEN_DEEP_ANALYSIS"
        )
        
        for var in "${v3_vars[@]}"; do
            if grep -q "^${var}=" .env; then
                echo -e "${GREEN}✅ ${var} 已配置${NC}"
            else
                echo -e "${YELLOW}⚠️  ${var} 未配置，将使用默认值${NC}"
            fi
        done
    else
        echo -e "${RED}❌ .env文件不存在${NC}"
        echo "请复制env.example创建.env文件"
    fi
}

# 5. 启动Celery Worker（测试）
start_celery_worker() {
    echo ""
    echo -e "${YELLOW}🔄 步骤5: 测试启动Celery Worker...${NC}"
    
    if docker ps --format '{{.Names}}' | grep -q "aicoin-backend"; then
        echo "在后台容器中测试Celery Worker..."
        docker-compose -f deploy/docker-compose.yml exec -d backend \
            python -m celery -A app.tasks.intelligence_learning worker -l info
        
        echo -e "${GREEN}✅ Celery Worker已在后台启动${NC}"
        echo "查看日志: docker-compose -f deploy/docker-compose.yml logs -f backend"
    else
        echo -e "${RED}❌ 后端容器未运行${NC}"
    fi
}

# 6. 验证服务状态
verify_services() {
    echo ""
    echo -e "${YELLOW}🔍 步骤6: 验证服务状态...${NC}"
    echo ""
    
    # 检查Docker容器
    echo "Docker容器状态:"
    docker ps --filter "name=aicoin" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    echo ""
    
    # 测试API
    echo "测试后端API..."
    if curl -s http://localhost:8000/ > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 后端API响应正常${NC}"
    else
        echo -e "${RED}❌ 后端API无响应${NC}"
    fi
    
    # 测试前端
    echo "测试前端..."
    if curl -s http://localhost:3002/ > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 前端响应正常${NC}"
    else
        echo -e "${RED}❌ 前端无响应${NC}"
    fi
    
    # 测试情报API
    echo "测试情报API..."
    if curl -s http://localhost:8000/api/v1/intelligence/latest > /dev/null 2>&1; then
        echo -e "${GREEN}✅ 情报API响应正常${NC}"
    else
        echo -e "${RED}❌ 情报API无响应${NC}"
    fi
}

# 7. 生成修复报告
generate_report() {
    echo ""
    echo -e "${YELLOW}📝 步骤7: 生成修复报告...${NC}"
    
    REPORT_FILE="修复报告_$(date +%Y%m%d_%H%M%S).txt"
    
    cat > "$REPORT_FILE" << EOF
AIcoin v3.0 修复报告
生成时间: $(date)
=====================================

Docker容器状态:
$(docker ps --filter "name=aicoin" --format "table {{.Names}}\t{{.Status}}")

服务测试结果:
- 后端API: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ 2>/dev/null || echo "无响应")
- 前端: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:3002/ 2>/dev/null || echo "无响应")
- 情报API: $(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/intelligence/latest 2>/dev/null || echo "无响应")

数据库迁移状态:
$(docker-compose -f deploy/docker-compose.yml exec -T backend alembic current 2>/dev/null || echo "无法获取")

环境变量检查:
$(grep -E "^(ENABLE_|QWEN_|DEEPSEEK_)" .env 2>/dev/null || echo "无法读取.env")

下一步建议:
1. 手动修改deploy/docker-compose.yml中的celery-beat配置
2. 重启Celery Beat: docker-compose -f deploy/docker-compose.yml up -d celery-beat
3. 访问新的管理页面: http://localhost:3002/admin/intelligence-platforms
4. 配置Qwen API Key以启用多平台协同

EOF
    
    echo -e "${GREEN}✅ 修复报告已生成: $REPORT_FILE${NC}"
}

# 主函数
main() {
    echo "开始修复流程..."
    echo ""
    
    # 前置检查
    check_docker
    check_docker_compose
    
    # 执行修复步骤
    fix_database_migration
    fix_celery_beat
    rebuild_frontend
    check_env_config
    start_celery_worker
    verify_services
    generate_report
    
    echo ""
    echo -e "${GREEN}================================${NC}"
    echo -e "${GREEN}🎉 修复流程完成！${NC}"
    echo -e "${GREEN}================================${NC}"
    echo ""
    echo "下一步操作:"
    echo "1. 查看修复报告了解详情"
    echo "2. 手动修复Celery Beat配置（见步骤2的说明）"
    echo "3. 访问管理界面测试新功能"
    echo ""
    echo "相关命令:"
    echo "  查看日志: docker-compose -f deploy/docker-compose.yml logs -f"
    echo "  重启服务: docker-compose -f deploy/docker-compose.yml restart"
    echo "  查看状态: docker-compose -f deploy/docker-compose.yml ps"
}

# 执行主函数
main "$@"

