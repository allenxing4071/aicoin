# 🔧 Scripts目录说明

> **最后更新**: 2025-11-09  
> **版本**: v3.2

---

## 📁 目录结构

```
scripts/
├── deploy/              # 部署类脚本
├── monitor/             # 监控类脚本
├── test/                # 测试类脚本
├── utils/               # 工具类脚本
├── ssh/                 # SSH/远程类脚本
├── start.sh             # 启动脚本
├── start_all.sh         # 启动所有服务
├── start_testnet.sh     # 启动测试网
├── stop_all.sh          # 停止所有服务
└── stop_system_emergency.sh  # 紧急停止
```

---

## 🚀 部署类脚本 (deploy/)

### deploy_prod.sh
**用途**: 生产环境部署  
**使用**: `./scripts/deploy/deploy_prod.sh`

### deploy_to_remote.sh
**用途**: 部署到远程服务器  
**使用**: `./scripts/deploy/deploy_to_remote.sh`

### remote_quick_deploy.sh
**用途**: 快速远程部署  
**使用**: `./scripts/deploy/remote_quick_deploy.sh`

### build_docker.sh
**用途**: 构建Docker镜像  
**使用**: `./scripts/deploy/build_docker.sh`

---

## 📊 监控类脚本 (monitor/)

### monitor_system.sh
**用途**: 系统监控  
**使用**: `./scripts/monitor/monitor_system.sh`

### monitor_trading.sh
**用途**: 交易监控  
**使用**: `./scripts/monitor/monitor_trading.sh`

### alert_config.sh
**用途**: 告警配置  
**使用**: `./scripts/monitor/alert_config.sh`

---

## 🧪 测试类脚本 (test/)

### test_admin_api.sh
**用途**: 测试管理API  
**使用**: `./scripts/test/test_admin_api.sh`

### test_api_endpoints.sh
**用途**: 测试API端点  
**使用**: `./scripts/test/test_api_endpoints.sh`

### test_ai_decision.py
**用途**: 测试AI决策  
**使用**: `python ./scripts/test/test_ai_decision.py`

---

## 🛠️ 工具类脚本 (utils/)

### cleanup_project.sh
**用途**: 清理项目文件  
**使用**: `./scripts/utils/cleanup_project.sh`

### restore_data.sh
**用途**: 恢复数据  
**使用**: `./scripts/utils/restore_data.sh`

### sync_api_keys.sh
**用途**: 同步API密钥  
**使用**: `./scripts/utils/sync_api_keys.sh`

### fix_v3_issues.sh
**用途**: 修复v3问题  
**使用**: `./scripts/utils/fix_v3_issues.sh`

### cleanup.sh
**用途**: 清理临时文件  
**使用**: `./scripts/utils/cleanup.sh`

### replace_headers.sh
**用途**: 替换文件头  
**使用**: `./scripts/utils/replace_headers.sh`

### update_page_headers.sh
**用途**: 更新页面头部  
**使用**: `./scripts/utils/update_page_headers.sh`

### database_optimization.sql
**用途**: 数据库优化检查  
**使用**: 
```bash
docker compose exec -T db psql -U aicoin -d aicoin < scripts/utils/database_optimization.sql
```

---

## 🔐 SSH/远程类脚本 (ssh/)

### setup_ssh_key.sh
**用途**: 设置SSH密钥  
**使用**: `./scripts/ssh/setup_ssh_key.sh`

### setup_ssh_key_manual.sh
**用途**: 手动设置SSH密钥  
**使用**: `./scripts/ssh/setup_ssh_key_manual.sh`

### check_remote_env.sh
**用途**: 检查远程环境  
**使用**: `./scripts/ssh/check_remote_env.sh`

### init_remote_db.sh
**用途**: 初始化远程数据库  
**使用**: `./scripts/ssh/init_remote_db.sh`

### install_cursor_desktop.sh
**用途**: 安装Cursor桌面版  
**使用**: `./scripts/ssh/install_cursor_desktop.sh`

### install_cursor_server.sh
**用途**: 安装Cursor服务器版  
**使用**: `./scripts/ssh/install_cursor_server.sh`

---

## ▶️ 启动/停止脚本

### start.sh
**用途**: 启动开发环境  
**使用**: `./scripts/start.sh`

### start_all.sh
**用途**: 启动所有服务  
**使用**: `./scripts/start_all.sh`

### start_testnet.sh
**用途**: 启动测试网环境  
**使用**: `./scripts/start_testnet.sh`

### stop_all.sh
**用途**: 停止所有服务  
**使用**: `./scripts/stop_all.sh`

### stop_system_emergency.sh
**用途**: 紧急停止系统  
**使用**: `./scripts/stop_system_emergency.sh`

---

## 📝 使用建议

### 开发环境
```bash
# 启动开发环境
./scripts/start.sh

# 测试API
./scripts/test/test_api_endpoints.sh

# 停止服务
./scripts/stop_all.sh
```

### 生产部署
```bash
# 构建镜像
./scripts/deploy/build_docker.sh

# 部署到生产
./scripts/deploy/deploy_prod.sh

# 监控系统
./scripts/monitor/monitor_system.sh
```

### 数据库维护
```bash
# 检查数据库
docker compose exec -T db psql -U aicoin -d aicoin < scripts/utils/database_optimization.sql

# 备份数据
./scripts/utils/restore_data.sh backup

# 恢复数据
./scripts/utils/restore_data.sh restore
```

---

## ⚠️ 注意事项

1. **权限**: 所有脚本需要执行权限 (`chmod +x script.sh`)
2. **环境**: 确保在项目根目录执行
3. **配置**: 检查环境变量和配置文件
4. **备份**: 生产操作前先备份数据

---

**维护者**: AIcoin Team  
**最后更新**: 2025-11-09
