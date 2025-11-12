# AIcoin 更新日志

## v3.3.0 (2025-11-12) - 当前版本

### 🔐 核心功能：企业级RBAC权限系统

#### 1. RBAC权限管理
- ✅ **细粒度权限控制** - 页面/API/按钮三个级别
- ✅ **系统角色** - super_admin、admin、risk_manager、trader、analyst、viewer
- ✅ **动态权限配置** - 无需重启系统
- ✅ **角色继承** - 支持父子角色关系
- ✅ **审计日志** - 完整记录权限变更

#### 2. 数据模型
- 新增`permissions`表 - 35个系统权限
- 新增`roles`表 - 6个系统角色
- 新增`role_permissions`表 - 角色权限关联
- 新增`permission_audit_logs`表 - 权限审计日志
- 扩展`admin_users`表 - 添加role_id和custom_permissions字段

#### 3. 前端集成
- `/admin/rbac/roles` - 角色管理页面
- `/admin/rbac/permissions` - 权限管理页面
- `PermissionsProvider` - 权限上下文
- `usePermissions` - 权限Hook
- `PermissionGuard` - 权限守卫组件
- 动态菜单渲染 - 基于用户权限

#### 4. 后端API
- 权限管理API - 增删改查权限
- 角色管理API - 角色和权限分配
- 审计日志API - 查询权限变更记录
- 权限校验中间件 - @require_permissions装饰器

### 📋 系统管理增强

- **数据备份系统** - 自动备份、手动备份、备份管理
- **日志管理系统** - 多级日志、文件管理、实时监控
- **用户管理简化** - 集成RBAC，统一权限管理

### 🐛 Bug修复

1. **React useMemo依赖问题** - 修复登录后页面崩溃（Error #310）
2. **AI成本页面500错误** - 修复数据库表缺失问题
3. **Redoc页面访问** - 修复API文档页面无法访问

### 📚 文档更新

- `docs/03-技术架构/08-RBAC权限系统.md` - RBAC完整文档
- `docs/07-部署运维/08-数据备份与清理指南.md` - 备份系统文档
- `docs/07-部署运维/09-日志管理系统.md` - 日志系统文档
- `docs/10-版本更新/v3.3.0_RBAC系统发布.md` - 版本发布说明
- `README.md` - 更新至v3.3.0

---

## v3.2.0 (2025-11-10)

### ✨ 新增功能

#### 1. 版本管理系统
- 成熟的版本管理机制
- 前端动态版本获取
- 版本号统一管理

#### 2. 安全规范
- 敏感信息管理规范
- .gitignore优化
- 环境变量最佳实践

### 🎨 样式统一优化

#### 1. 设计系统
- 统一设计系统（unified-design-system.ts）
- 可复用卡片组件库
- 93%代码重复减少

#### 2. 性能优化
- Docker镜像优化（40%体积减少）
- 数据库索引优化
- Next.js编译优化

### 📚 文档完善

- `docs/07-部署运维/07-版本管理指南.md`
- `docs/07-部署运维/08-版本发布流程.md`
- `docs/07-部署运维/00-敏感信息管理规范.md`

---

## v3.1.0 (2025-11-08)

### 🤖 AI多平台集成

#### 1. AI平台管理
- **DeepSeek** - 交易决策引擎
- **Qwen (通义千问)** - 情报分析
- **Doubao (豆包)** - 辅助分析
- 三平台统一管理界面

#### 2. AI成本管理系统
- 成本概览 - 总成本统计和趋势
- 平台统计 - 各平台使用详情
- 预算设置 - 预算配置和预警
- 成本优化 - 智能优化建议

#### 3. AI平台性能监控
- 调用统计 - 实时监控调用量和趋势
- 成功率分析 - 失败原因和稳定性评估
- 响应时间分析 - P50/P95/P99延迟监控
- 平台对比 - 多维度性能对比

#### 4. 情报分析系统
- 实时情报 - 最新市场情报流
- AI综合分析 - 多平台情报分析
- 历史报告 - 情报历史记录

### 🎨 前端功能

#### 新增页面
- `/admin/ai-platforms` - AI平台管理
- `/admin/ai-platforms/stats` - 平台统计
- `/admin/ai-platforms/success-rate` - 成功率分析
- `/admin/ai-platforms/response-time` - 响应时间分析
- `/admin/ai-cost` - AI成本概览
- `/admin/ai-cost/budget` - 预算设置
- `/admin/ai-cost/optimization` - 成本优化
- `/admin/intelligence` - 情报系统

### 🔧 后端功能

#### 新增API
- AI平台统计API - `/api/v1/ai-platforms/stats`
- 成本管理API - `/api/v1/ai-platforms/cost/*`
- 预算管理API - `/api/v1/ai-platforms/budget/*`
- 情报分析API - `/api/v1/intelligence/*`

#### 数据库
- `ai_model_usage_log` - AI使用日志
- `ai_platform_budget` - 平台预算配置
- `intelligence_reports` - 情报报告

### 📚 文档

- `docs/03-技术架构/07-AI平台性能监控系统.md`
- `docs/06-快速参考/06-AI多平台使用指南.md`
- `docs/07-部署运维/05-AI平台API密钥配置.md`

---

## v3.0.0 (2025-11-06)

### 🎉 重大更新

#### 1. Qwen情报系统
- 双AI引擎架构（Qwen情报 + DeepSeek决策）
- 自动情报收集和分析
- 30分钟自动更新
- Redis + PostgreSQL双层存储

#### 2. AI日记系统
- 每日交易总结
- AI性能分析
- 经验教训记录

#### 3. 权限等级管理
- L0-L5动态权限系统
- 智能约束框架
- 权限自动升降级

---

## v2.1 (2025-11-04)

### 🎉 核心新功能

#### 1. 双AI引擎架构
- **Qwen情报官**: 负责市场情报收集和分析
- **DeepSeek交易官**: 负责交易决策和执行
- 职责清晰分离，专业化分工

#### 2. Qwen情报系统
- 自动收集新闻、巨鲸活动、链上数据
- AI分析市场情绪和风险机会
- 30分钟自动更新
- Redis + PostgreSQL双层存储

#### 3. 数据源管理系统
- 15个预置数据源（新闻/巨鲸/链上）
- API Key配置和连接测试
- 支持自定义数据源添加/删除
- 实时状态监控

#### 4. 长期记忆多Provider支持
- 支持Qwen Embedding（推荐，成本降低70%）
- 支持DeepSeek特征哈希（完全免费）
- 支持OpenAI Embedding（效果最好）
- 自动provider选择机制

#### 5. PostgreSQL持久化存储
- 情报数据永久存储
- 支持历史查询和趋势分析
- Alembic数据库迁移
- 完整的分析API

### 🎨 前端功能

#### 新增管理页面
- `/admin/intelligence` - 情报系统配置
- `/admin/permissions` - 权限管理
- `/admin/database` - 数据库管理

#### UI优化
- 统一现代化设计风格
- 渐变背景和流畅动画
- 响应式布局优化
- 交互体验提升

### 🔧 后端功能

#### 新增API端点
- `GET /api/v1/intelligence/reports/*` - 情报查询
- `GET /api/v1/intelligence/analytics/*` - 数据分析
- `GET/POST /api/v1/admin/intelligence/*` - 情报配置
- `GET/PUT /api/v1/admin/permissions/*` - 权限管理
- `GET /api/v1/admin/database/*` - 数据库管理
- `GET /api/v1/admin/memory/*` - 记忆管理

#### 服务增强
- QwenIntelligenceEngine - 情报引擎
- IntelligenceStorage - 情报存储
- DataSourceCollectors - 数据收集器
- Multi-Provider Embedding - 多provider支持

### 💾 数据库升级

#### 新增表
- `permission_configs` - 权限配置表
- `intelligence_reports` - 情报报告表

#### Alembic迁移
- `003_add_permission_configs.py` - 权限配置表
- `004_add_intelligence_reports.py` - 情报报告表

### 🐛 Bug修复

1. **Redis Client API兼容性**
   - 修复 `set()` 参数错误（`ex` → `expire`）
   - 添加 `lpush`、`lrange`、`ltrim` 方法

2. **Qdrant连接配置**
   - 修复Docker环境连接配置
   - 添加 `QDRANT_HOST` 环境变量

3. **情报报告属性名**
   - 统一使用模型定义的属性名
   - 修正API返回格式

4. **前端API路径**
   - 修正多处API路径错误
   - 统一使用完整路径

5. **Docker缓存问题**
   - 使用 `--no-cache` 强制重建
   - 确保最新代码生效

6. **环境变量传递**
   - 显式传递所有必要的环境变量
   - 验证配置正确性

### ⚡ 性能优化

1. **Redis缓存优化**
   - 7天自动过期
   - 查询响应 < 10ms

2. **数据库索引优化**
   - 添加4个高效索引
   - 查询速度提升10-100倍

3. **Embedding成本优化**
   - 使用Qwen降低成本70%
   - 月成本: $9 → $3

4. **前端性能优化**
   - 首屏加载提升30%
   - 内存占用降低20%

### 📚 文档更新

#### 新增文档
- `docs/03-技术架构/06-Qwen情报系统.md`
- `docs/06-快速参考/权限管理速查.md`
- `docs/07-部署运维/主网操作指南.md`
- `docs/08-前端系统/*` - 4篇前端文档
- `docs/09-API接口文档/README.md`
- `docs/10-版本更新/v2.1功能清单.md`

#### 更新文档
- `docs/README.md` - 版本更新到v2.1
- `docs/00-快速开始/*` - 更新快速开始指南

#### 文档整理
- 归档9个临时文档
- 删除21个过时报告
- 优化目录结构

### 📊 统计数据

- **开发周期**: 2天
- **文件变更**: 101个文件
- **代码新增**: 9,777行
- **代码删除**: 11,339行
- **新增功能**: 15个核心功能
- **新增API**: 20+个接口
- **新增页面**: 3个管理页面
- **文档更新**: 10+篇

### 🎯 技术亮点

1. **双AI引擎**: 情报收集与交易决策分离
2. **成本优化**: embedding成本降低70%
3. **双层存储**: Redis + PostgreSQL
4. **完整管理**: 可视化配置界面
5. **灵活扩展**: 支持自定义数据源

---

## v2.0 (2025-11-03)

### 核心功能
- AI编排器v2.0
- L0-L5动态权限系统
- 智能约束框架
- 三层记忆系统
- 主网生产环境部署

### 前端系统
- Next.js 14升级
- 全中文化界面
- 实时WebSocket通信
- 性能仪表盘

### 后端系统
- FastAPI异步架构
- PostgreSQL + Redis + Qdrant
- Hyperliquid主网集成
- 完整的监控和日志

---

## v1.0 (2025-10-01)

### 初始版本
- 基础交易功能
- 简单的AI决策
- 测试网环境
- 基础前端界面

---

**维护者**: AIcoin Team  
**最后更新**: 2025-11-04

