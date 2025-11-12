# 🪙 AIcoin - AI驱动的加密货币智能交易系统

> **多AI平台驱动的智能量化交易系统** | v3.3.0 | MIT License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14-black.svg)](https://nextjs.org/)
[![Status](https://img.shields.io/badge/Status-Active-success.svg)]()

---

## 📋 项目简介

AIcoin 是一个基于多AI平台（DeepSeek、Qwen、Doubao）的智能加密货币交易系统，集成了情报分析、决策支持、成本管理等功能模块，提供完整的量化交易解决方案。

### ✨ 核心特性

- 🤖 **多AI平台集成** - DeepSeek决策 + Qwen情报 + Doubao分析
- 📊 **智能情报系统** - 实时市场情报 + AI综合分析
- 💰 **AI成本管理** - 预算控制 + 使用统计 + 成本优化
- 🎯 **权限等级系统** - L0-L5动态权限管理
- 🔐 **企业级RBAC** - 角色权限管理 + 动态权限配置 + 审计日志
- 📈 **性能监控** - 调用统计 + 成功率分析 + 响应时间监控
- 🎨 **现代化UI** - 统一设计系统 + 响应式布局

---

## 🚀 快速开始

### 📦 使用 Docker（推荐）

```bash
# 1. 克隆项目
git clone https://github.com/allenxing4071/aicoin.git
cd aicoin

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入必要的API密钥

# 3. 启动服务
docker compose up -d

# 4. 访问系统
# 前端: http://localhost:3000
# 后端API: http://localhost:8000
# API文档: http://localhost:8000/docs
```

详细部署指南: [docs/00-快速开始/DOCKER_QUICK_START.md](./docs/00-快速开始/DOCKER_QUICK_START.md)

---

## 🏗️ 技术架构

### 后端技术栈
- **Python 3.11** + **FastAPI** - 高性能异步API框架
- **PostgreSQL 15** - 主数据库
- **Redis 7** - 缓存和会话管理
- **Alembic** - 数据库迁移管理
- **Docker** - 容器化部署

### 前端技术栈
- **Next.js 14** + **React 18** - 服务端渲染框架
- **TypeScript** - 类型安全
- **TailwindCSS** - 原子化CSS框架
- **Axios** - HTTP客户端

### AI平台
- **DeepSeek** - 交易决策引擎
- **Qwen (通义千问)** - 情报分析
- **Doubao (豆包)** - 辅助分析

### 交易所
- **Hyperliquid** - 去中心化永续合约交易所
- **Binance** - 币安交易所（支持）

---

## 📁 项目结构

```
AIcoin/
├── backend/                    # 后端服务
│   ├── app/
│   │   ├── api/               # API路由
│   │   ├── core/              # 核心配置
│   │   ├── models/            # 数据模型
│   │   ├── services/          # 业务逻辑
│   │   └── main.py            # 应用入口
│   ├── alembic/               # 数据库迁移
│   ├── Dockerfile
│   └── requirements.txt
│
├── frontend/                   # 前端应用
│   ├── app/
│   │   ├── admin/             # 管理后台
│   │   ├── components/        # 公共组件
│   │   └── page.tsx           # 主页
│   ├── Dockerfile
│   └── package.json
│
├── docs/                       # 📚 项目文档
│   ├── 00-快速开始/           # 快速开始指南
│   ├── 03-技术架构/           # 技术架构文档
│   ├── 06-快速参考/           # 快速参考手册
│   ├── 07-部署运维/           # 部署运维指南
│   ├── 08-前端系统/           # 前端系统文档
│   └── 10-版本更新/           # 版本更新日志
│
├── scripts/                    # 工具脚本
│   ├── deployment/            # 部署脚本
│   ├── maintenance/           # 维护脚本
│   └── utils/                 # 工具脚本
│
├── .env.example               # 环境变量模板
├── docker-compose.yml         # Docker编排配置
├── VERSION                    # 版本号文件
└── README.md                  # 本文件
```

---

## 🎯 核心功能模块

### 1. 管理后台 (`/admin`)

#### 📊 AI平台管理
- **情报模型配置** - Qwen情报平台配置和管理
- **决策模型配置** - DeepSeek决策引擎配置
- **分析模型配置** - Doubao分析平台配置

#### 📈 性能监控
- **调用统计** - 实时监控各平台调用量和趋势
- **成功率分析** - 失败原因分析和稳定性评估
- **响应时间分析** - P50/P95/P99延迟监控

#### 🔍 情报分析
- **实时情报** - 最新市场情报流和AI综合分析
- **历史报告** - 情报历史记录和数据导出

#### 💰 AI成本管理
- **成本概览** - 总体成本统计和趋势分析
- **预算设置** - 预算配置和预警管理

#### 🔧 系统管理
- **RBAC权限管理** - 企业级角色权限系统，支持动态配置和审计
  - 权限配置 - 页面/API/按钮级别细粒度权限
  - 角色管理 - 自定义角色 + 角色继承
  - 审计日志 - 完整的权限变更记录
- **用户管理** - 用户账号管理和权限分配
- **数据备份** - 自动备份 + 数据清理 + 备份管理
- **日志管理** - 多级日志 + 文件管理 + 实时监控
- **数据库管理** - 数据库状态和表统计
- **记忆系统** - 三层记忆系统状态监控

### 2. 交易监控

- **实时价格** - 6个主流币种价格跑马灯
- **账户信息** - 实时账户余额和盈亏
- **持仓管理** - 当前持仓列表和未实现盈亏
- **交易历史** - 已完成交易记录

---

## 📚 文档导航

### 🚀 快速开始
- [Docker快速启动](./docs/00-快速开始/DOCKER_QUICK_START.md)
- [完整快速开始指南](./docs/00-快速开始/QUICKSTART.md)

### 🏗️ 技术架构
- [系统架构设计](./docs/03-技术架构/00-系统架构设计.md)
- [权限等级管理系统](./docs/03-技术架构/05-权限等级管理系统.md)
- [Qwen情报系统](./docs/03-技术架构/06-Qwen情报系统.md)
- [AI平台性能监控系统](./docs/03-技术架构/07-AI平台性能监控系统.md)

### 📖 快速参考
- [v3.1快速上手指南](./docs/06-快速参考/05-v3.1快速上手指南.md)
- [AI多平台使用指南](./docs/06-快速参考/06-AI多平台使用指南.md)
- [权限管理速查](./docs/06-快速参考/02-权限管理速查.md)

### 🔧 部署运维
- [部署指南](./docs/07-部署运维/01-部署指南.md)
- [版本管理指南](./docs/07-部署运维/07-版本管理指南.md)
- [敏感信息管理规范](./docs/07-部署运维/00-敏感信息管理规范.md)
- [AI平台API密钥配置](./docs/07-部署运维/05-AI平台API密钥配置.md)

### 🎨 前端系统
- [功能模块说明](./docs/08-前端系统/01-功能模块说明.md)
- [组件文档](./docs/08-前端系统/02-组件文档.md)
- [API集成](./docs/08-前端系统/04-API集成.md)

### 📝 版本更新
- [更新日志](./docs/10-版本更新/CHANGELOG.md)
- [v3.1版本说明](./docs/10-版本更新/v3.1_版本说明.md)

---

## 🔐 环境配置

### 必需的环境变量

创建 `.env` 文件（参考 `.env.example`）：

```bash
# 数据库配置
DATABASE_URL=postgresql://user:password@localhost:5432/aicoin

# Redis配置
REDIS_URL=redis://localhost:6379/0

# AI平台API密钥
DEEPSEEK_API_KEY=your_deepseek_api_key
QWEN_API_KEY=your_qwen_api_key
DOUBAO_API_KEY=your_doubao_api_key

# 交易所API密钥
HYPERLIQUID_PRIVATE_KEY=your_hyperliquid_private_key
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret

# 应用配置
SECRET_KEY=your_secret_key
ENVIRONMENT=development
```

详细配置说明: [docs/07-部署运维/00-敏感信息管理规范.md](./docs/07-部署运维/00-敏感信息管理规范.md)

---

## 🛠️ 开发指南

### 本地开发

#### 后端开发

```bash
cd backend

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 运行数据库迁移
alembic upgrade head

# 启动开发服务器
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端开发

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev

# 构建生产版本
npm run build
```

### 代码规范

- **Python**: Black + Flake8 + isort
- **TypeScript**: ESLint + Prettier
- **提交规范**: Conventional Commits

---

## 📊 版本历史

### v3.3.0 (2025-11-12) - 当前版本

**✨ 新增功能**
- 🔐 **企业级RBAC权限系统** - 完整的角色权限管理
  - 细粒度权限控制（页面/API/按钮级别）
  - 动态权限配置和角色管理
  - 角色继承和权限审计日志
- 📋 **数据备份系统** - 自动化备份和数据清理
- 📊 **日志管理系统** - 多级日志和实时监控
- 🔄 **前端RBAC集成** - 基于权限的动态菜单和组件渲染

**🎨 系统优化**
- 简化用户管理界面，集成RBAC
- 优化权限检查逻辑，提升性能
- 统一权限校验中间件

**📚 文档更新**
- RBAC系统使用指南
- 权限配置最佳实践
- API安全规范

### v3.2.0 (2025-11-10)

**✨ 新增功能**
- 成熟的版本管理系统
- 前端动态版本获取
- 敏感信息管理规范

**🎨 样式优化**
- 统一设计系统
- 可复用组件库
- 93%代码重复减少

**⚡ 性能优化**
- Docker镜像优化
- 数据库索引优化
- Next.js编译优化

**📚 文档完善**
- 版本管理指南
- 版本发布流程
- 安全管理规范

### v3.1.0 (2025-11-08)

**✨ 新增功能**
- AI多平台集成（DeepSeek + Qwen + Doubao）
- AI成本管理系统
- AI平台性能监控
- 情报分析系统

### v3.0.0 (2025-11-06)

**✨ 新增功能**
- Qwen情报系统集成
- AI日记系统
- 权限等级管理

更多版本历史: [docs/10-版本更新/CHANGELOG.md](./docs/10-版本更新/CHANGELOG.md)

---

## 🤝 参与贡献

欢迎贡献代码、报告问题或提出建议！

### 贡献流程

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'feat: add some amazing feature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

### 开发规范

- 遵循项目代码风格
- 添加必要的测试
- 更新相关文档
- 使用语义化的提交信息

---

## 📜 许可证

本项目采用 [MIT License](./LICENSE) 开源协议。

### ⚠️ 免责声明

**本软件仅供学习和研究使用。**

- ⚠️ 加密货币交易存在重大风险
- ⚠️ 请勿使用超出承受能力的资金
- ⚠️ 过去的表现不代表未来的结果
- ⚠️ 作者不对任何经济损失负责

**使用本软件即表示您理解并接受上述风险。**

---

## 📞 联系方式

- **GitHub**: [https://github.com/allenxing4071/aicoin](https://github.com/allenxing4071/aicoin)
- **Issues**: [提交问题](https://github.com/allenxing4071/aicoin/issues)
- **Discussions**: [参与讨论](https://github.com/allenxing4071/aicoin/discussions)

---

## ⭐ Star History

如果这个项目对你有帮助，请给一个 Star ⭐

---

**创建时间**: 2025-10-22  
**最后更新**: 2025-11-12  
**当前版本**: v3.3.0  
**系统状态**: ✅ 活跃开发中

---

*🚀 基于多AI平台的智能量化交易系统*
