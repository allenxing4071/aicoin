# 📚 AIcoin 文档中心

> **v4.1 完整文档** | 简洁 | 实用 | 易读

---

## 🚀 快速开始

### 5 分钟快速部署
- **[快速开始指南](quickstart.md)** - 最快的方式体验 AIcoin

### 完整入门
- **[快速开始](00-快速开始/01-快速开始指南.md)** - Docker/本地/测试网部署

---

## 📖 核心文档

### 01-用户指南
- **[用户指南](01-用户指南/user-guide.md)** - 完整使用手册
  - 系统概述
  - 核心概念
  - 权限等级系统 (L0-L5)
  - 交易规则
  - 风险管理
  - 常用术语

### 02-部署运维
- **[快速部署](02-部署运维/quick-deploy.md)** - Docker/本地/远程/测试网/主网
- **[配置指南](02-部署运维/configuration.md)** - 环境变量/AI平台/交易所/权限
- **[运维操作](02-部署运维/operations.md)** - 监控/备份/日志/版本管理
- **[故障排查](02-部署运维/troubleshooting.md)** - 常见问题诊断与解决

### 03-开发文档
- **[系统架构](03-开发文档/architecture.md)** - 完整技术架构
  - 整体架构
  - 核心模块 (AI决策/权限/风控/记忆/情报/辩论)
  - 数据架构 (PostgreSQL/Redis/Qdrant)
  - 部署架构
  - 扩展性设计

---

## 🗂️ 文档目录结构

```
docs/
├── quickstart.md                    # 5分钟快速开始
├── 00-快速开始/
│   └── 01-快速开始指南.md           # 完整快速开始
├── 01-用户指南/
│   └── user-guide.md                # 用户指南
├── 02-部署运维/
│   ├── quick-deploy.md              # 快速部署
│   ├── configuration.md             # 配置指南
│   ├── operations.md                # 运维操作
│   └── troubleshooting.md           # 故障排查
├── 03-开发文档/
│   ├── architecture.md              # 系统架构
│   ├── research/                    # 研究报告
│   ├── experiments/                 # 实验记录
│   ├── frontend/                    # 前端文档
│   ├── api/                         # API文档
│   └── intelligence/                # 情报系统
├── 04-版本历史/
│   └── history/                     # 版本历史
└── 99-归档/                         # 旧版文档归档
```

---

## 🎯 按角色查找

### 👤 新手用户
1. [快速开始](quickstart.md) - 5分钟部署
2. [用户指南](01-用户指南/user-guide.md) - 核心概念
3. [故障排查](02-部署运维/troubleshooting.md) - 常见问题

### 💼 产品经理
1. [用户指南](01-用户指南/user-guide.md) - 功能说明
2. [系统架构](03-开发文档/architecture.md) - 技术架构
3. [研究报告](03-开发文档/research/) - 策略研究

### 👨‍💻 开发人员
1. [系统架构](03-开发文档/architecture.md) - 技术架构
2. [API文档](03-开发文档/api/) - API接口
3. [前端文档](03-开发文档/frontend/) - 前端开发

### 🔧 运维人员
1. [快速部署](02-部署运维/quick-deploy.md) - 部署指南
2. [配置指南](02-部署运维/configuration.md) - 配置说明
3. [运维操作](02-部署运维/operations.md) - 日常运维
4. [故障排查](02-部署运维/troubleshooting.md) - 问题诊断

---

## 📊 文档统计

| 类别 | 文档数 | 说明 |
|------|--------|------|
| **核心文档** | 8 | 快速开始、用户指南、部署运维、架构 |
| **开发文档** | 20+ | 研究报告、实验记录、API、前端 |
| **版本历史** | 10 | 核心版本发布记录 |
| **归档文档** | 100+ | 旧版文档 (仅供参考) |

---

## 🔍 快速搜索

### 按主题搜索

#### 部署相关
- Docker 部署 → [快速部署](02-部署运维/quick-deploy.md#2-docker-部署-推荐)
- 远程服务器 → [快速部署](02-部署运维/quick-deploy.md#4-远程服务器部署)
- 测试网/主网 → [快速部署](02-部署运维/quick-deploy.md#5-测试网-vs-主网)
- Git 自动化 → [快速部署](02-部署运维/quick-deploy.md#6-git-自动化部署)

#### 配置相关
- 环境变量 → [配置指南](02-部署运维/configuration.md#1-环境变量配置)
- DeepSeek → [配置指南](02-部署运维/configuration.md#21-deepseek-主要决策)
- Hyperliquid → [配置指南](02-部署运维/configuration.md#31-hyperliquid-配置)
- 权限配置 → [配置指南](02-部署运维/configuration.md#4-权限等级配置)

#### 运维相关
- 日常监控 → [运维操作](02-部署运维/operations.md#1-日常监控)
- 数据备份 → [运维操作](02-部署运维/operations.md#2-数据备份与恢复)
- 日志管理 → [运维操作](02-部署运维/operations.md#3-日志管理)
- 版本管理 → [运维操作](02-部署运维/operations.md#4-版本管理)

#### 问题诊断
- 部署问题 → [故障排查](02-部署运维/troubleshooting.md#1-部署问题)
- 服务问题 → [故障排查](02-部署运维/troubleshooting.md#2-服务问题)
- 数据库问题 → [故障排查](02-部署运维/troubleshooting.md#3-数据库问题)
- 交易问题 → [故障排查](02-部署运维/troubleshooting.md#4-交易问题)

#### 架构相关
- 整体架构 → [系统架构](03-开发文档/architecture.md#1-整体架构)
- AI决策引擎 → [系统架构](03-开发文档/architecture.md#21-ai-决策引擎)
- 权限系统 → [系统架构](03-开发文档/architecture.md#22-权限管理系统)
- 记忆系统 → [系统架构](03-开发文档/architecture.md#24-记忆学习系统)

---

## 📝 贡献指南

### 文档更新原则
1. **简洁优先**: 避免冗余，保持精简
2. **实用导向**: 以解决问题为目标
3. **结构清晰**: 使用清晰的目录和标题
4. **示例丰富**: 提供实际可用的代码示例

### 文档命名规范
- 使用中文文件名
- 使用连字符分隔
- 避免特殊字符

### 提交文档
```bash
# 1. 修改文档
nano docs/guides/user-guide.md

# 2. 提交变更
git add docs/
git commit -m "docs: 更新用户指南"
git push origin main
```

---

## 🔄 版本记录

### 最新版本: v4.1 (2025-11-15)
- ✅ 文档深度简化完成
- ✅ 合并 50+ 文档 → 8 个核心文档
- ✅ 新增快速开始指南
- ✅ 重组文档目录结构
- ✅ 优化文档可读性

### 历史版本
- **v4.0** (2025-11-13): Prompt 模板系统
- **v3.5** (2025-11-12): HTTPS 部署支持
- **v3.4** (2025-11-11): 辩论系统发布
- **v3.3** (2025-11-10): RBAC 权限系统
- **v3.0** (2025-11-06): 情报系统集成

查看完整版本历史: [changelog/history/](changelog/history/)

---

## 🆘 获取帮助

### 文档问题
- 查看 [故障排查](deployment/troubleshooting.md)
- 搜索 [GitHub Issues](https://github.com/allenxing4071/aicoin/issues)

### 技术支持
- 提交 Issue: https://github.com/allenxing4071/aicoin/issues/new
- API 文档: http://localhost:8000/docs

---

## 📌 重要提示

1. **从快速开始指南开始**: [quickstart.md](quickstart.md)
2. **测试网先行**: 生产环境前务必在测试网验证
3. **理解风险**: 加密货币交易有风险，请谨慎操作
4. **保护密钥**: 妥善保管 API Key 和私钥

---

**文档维护**: AIcoin Team  
**最后更新**: 2025-11-15  
**文档版本**: v2.0  
**项目版本**: v4.1

---

**祝你使用愉快！** 🎉

如有问题，请查看 [故障排查](deployment/troubleshooting.md) 或提交 [GitHub Issue](https://github.com/allenxing4071/aicoin/issues)。
