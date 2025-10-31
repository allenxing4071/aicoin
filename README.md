# 🪙 AIcoin - AI加密货币自主交易系统

> **DeepSeek驱动的智能量化交易系统** | v2.1 | MIT License

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11-blue.svg)](https://www.python.org/)
[![Status](https://img.shields.io/badge/Status-Development-orange.svg)]()

---

## ⚠️ 重要警告

```diff
- ❌ 系统当前处于开发阶段，不可用于真实交易
- ❌ 初始测试导致48.8%亏损（$599.80 → $307.30）
+ ✅ 问题已识别，正在实施Phase 1改进
+ ✅ 预计1-2周后Phase 1完成可小资金测试
```

**风险提示**: 加密货币交易存在重大风险，请勿使用超出您承受能力的资金。

---

## 🚀 快速开始

### 📚 文档入口（推荐从这里开始）

```bash
# 1. 阅读完整文档
cd docs/
cat 00-文档导航.md          # 导航中心（5分钟）

# 2. 核心文档
cat 01-核心规则/AI交易规则文档.md  # 系统"宪法"（1-2小时）

# 3. 快速参考
cat 06-快速参考/核心要点速查卡.md  # 1页速查（打印版）
cat 06-快速参考/术语表.md          # 50+术语定义
```

### 🎯 核心特性

- 🤖 **AI自主决策** - 基于DeepSeek V3.1大语言模型
- 🎚️ **动态权限系统** - L0-L5等级，随表现自动调整
- 🛡️ **智能约束框架** - 硬约束+软约束，保护本金
- 🧠 **三层记忆系统** - Redis+Qdrant+PostgreSQL
- 📊 **专业量化指标** - 13+风险指标，机构级标准
- 🔄 **持续学习** - 从每次交易中学习和优化

---

## 📁 项目结构

```
AIcoin/
├── LICENSE                        # MIT许可证+免责声明
├── README.md                      # 本文件
│
├── docs/                          # 📚 完整文档（20+文件）
│   ├── 00-文档导航.md             # ⭐ 从这里开始
│   ├── 01-核心规则/               # 系统"宪法"
│   ├── 02-问题分析/               # -48.8%亏损分析
│   ├── 03-技术架构/               # 技术文档+8个架构图
│   ├── 04-研究报告/               # 5篇深度研究
│   ├── 05-实验记录/               # 测试记录模板
│   └── 06-快速参考/               # 速查卡+术语表
│
├── backend/                       # 后端服务
│   ├── app/
│   │   ├── api/                   # FastAPI路由
│   │   ├── services/              # 业务逻辑
│   │   ├── models/                # 数据模型
│   │   └── config/                # 配置文件
│   └── requirements.txt
│
├── frontend/                      # 前端界面
│   ├── src/
│   │   ├── components/            # React组件
│   │   ├── pages/                 # 页面
│   │   └── utils/                 # 工具函数
│   └── package.json
│
└── docker-compose.yml             # Docker部署配置
```

---

## 🏗️ 技术栈

### 后端
- **Python 3.11** + **FastAPI** - 高性能异步API
- **PostgreSQL 15** - 主数据库
- **Redis 7** - 短期记忆缓存
- **Qdrant** - 向量数据库（长期记忆）

### AI/ML
- **DeepSeek V3.1** - 大语言模型
- **Transformers** + **PyTorch** - 模型训练
- **PEFT (LoRA)** - 轻量级微调

### 前端
- **Next.js 14** + **React 18** - 现代化前端
- **TailwindCSS** - 样式框架
- **Lightweight Charts** - 图表展示

### 交易所
- **Hyperliquid** - 去中心化永续合约交易所

---

## 🎯 三阶段实施计划

### Phase 1: 基础修复（1-2周）⏳ 当前阶段
```
目标: 修复当前系统的关键问题
├── 重写Prompt（保守策略）
├── 实现硬性约束（回撤10%、单日亏损5%）
├── 添加止损/止盈自动执行
└── 实现L1-L3权限系统

验收标准:
✅ 7天测试，$100资金
✅ 无单日亏损>5%
✅ 胜率>40%
✅ 最大回撤<10%
```

### Phase 2: 记忆增强（2-4周）
```
目标: 添加记忆系统，AI能从历史学习
├── 部署Redis短期记忆
├── 部署Qdrant向量数据库
├── 实现记忆注入Prompt
└── 添加经验教训提取

验收标准:
✅ 14天测试，$200资金
✅ 胜率>55%
✅ 夏普比率>1.0
✅ 能明显看到"从历史中学习"
```

### Phase 3: 模型自建（1-2月）
```
目标: 部署专用模型，实现完全自主
├── 收集10,000+训练样本
├── 阿里云PAI平台LoRA微调
├── A/B测试（通用 vs 专用）
└── 性能评估和切换

验收标准:
✅ 自建模型胜率>60%
✅ 夏普比率>1.5
✅ 优于DeepSeek API基线
```

---

## 🔧 开发环境搭建

### 前置要求
- Python 3.11+
- Node.js 18+
- Docker & Docker Compose
- Git

### 快速启动

```bash
# 1. 克隆项目
git clone https://github.com/allenxing4071/aicoin.git
cd aicoin

# 2. 配置环境变量
cp .env.example .env
# 编辑.env，填入API密钥

# 3. 启动服务
docker-compose up -d

# 4. 访问
# Backend API: http://localhost:8000/docs
# Frontend: http://localhost:3000
```

### 开发命令

```bash
# 后端开发
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# 前端开发
cd frontend
npm install
npm run dev

# 运行测试
pytest                    # 后端测试
npm test                  # 前端测试
```

---

## 📊 性能目标

| Phase | 胜率 | 夏普比率 | 最大回撤 | 资金 |
|-------|------|---------|---------|------|
| Phase 1 | >40% | N/A | <10% | $100 |
| Phase 2 | >55% | >1.0 | <8% | $200 |
| Phase 3 | >60% | >1.5 | <5% | 逐步扩大 |

---

## 📚 文档

### 核心文档
- [📖 文档导航中心](./docs/00-文档导航.md) - 从这里开始
- [🎯 AI交易规则文档](./docs/01-核心规则/AI交易规则文档.md) - 系统"宪法"（20,000字）
- [🔍 系统问题总结](./docs/02-问题分析/系统问题总结.md) - -48.8%亏损分析

### 技术文档
- [🏗️ 系统架构设计](./docs/03-技术架构/00-系统架构设计.md) - 8个Mermaid架构图
- [⚙️ 智能约束框架](./docs/03-技术架构/01-智能约束框架.md) - 完整技术实现

### 快速参考
- [⚡ 核心要点速查卡](./docs/06-快速参考/核心要点速查卡.md) - 1页A4打印版
- [📚 术语表](./docs/06-快速参考/术语表.md) - 50+核心术语定义

### AI协作文档
- [项目上下文](./.claudecontext) - AI助手项目记忆
- [开发规范](./.clinerules) - 开发规范和约束

---

## 🤝 参与贡献

我们欢迎各种形式的贡献！

### 如何贡献
1. 🐛 **报告问题** - [创建Issue](https://github.com/allenxing4071/aicoin/issues)
2. 💡 **提出建议** - 通过Pull Request
3. 📝 **完善文档** - 遵循现有格式
4. 🧪 **测试验证** - 提交测试结果

### 开发规范
- 代码风格: Black + Flake8（Python）
- 提交规范: Conventional Commits
- 分支管理: Git Flow
- 测试覆盖: >80%

---

## 📜 许可证

本项目采用 [MIT License](./LICENSE)。

### ⚠️ 重要免责声明

**本软件当前处于开发阶段，不可用于生产环境。**

- ❌ 请勿在未经充分测试的情况下使用真实资金
- ❌ 加密货币交易存在重大亏损风险
- ❌ 过去的表现不代表未来的结果
- ⚠️ 初始测试结果: -48.8%亏损

**作者和贡献者对因使用本软件而产生的任何经济损失不承担责任。**

**使用风险自负。**

---

## 📞 联系方式

- **GitHub Issues**: [提交问题](https://github.com/allenxing4071/aicoin/issues)
- **项目仓库**: [GitHub](https://github.com/allenxing4071/aicoin)
- **文档中心**: [docs/](./docs/)

---

## 🎯 路线图

- [x] **v1.0** - 初始版本（存在严重问题）
- [x] **v2.0** - 文档重组，问题识别
- [x] **v2.1** - 技术架构文档+快速参考
- [ ] **v2.2** - Phase 1实施（当前）
- [ ] **v3.0** - Phase 2完成（记忆系统）
- [ ] **v4.0** - Phase 3完成（自建模型）

---

## ⭐ Star History

如果这个项目对你有帮助，请给一个Star⭐！

---

**创建时间**: 2025-10-22  
**最后更新**: 2025-10-31  
**当前版本**: v2.1  
**系统状态**: ⚠️ 开发中

---

*🚀 从-48.8%亏损到稳定盈利的AI交易系统改进之路*

