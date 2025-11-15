# Prompt模板系统

## 概述

借鉴NOFX的成熟框架，实现了轻量级、高效的Prompt模板管理系统。

### 核心特性

1. **文件化管理**：Prompt存储为`.txt`文件，易于编辑和版本控制
2. **热重载**：支持文件修改后自动重载，无需重启服务
3. **多策略支持**：可创建多个策略模板（default, conservative, aggressive等）
4. **优雅降级**：模板加载失败时自动回退到硬编码版本
5. **API管理**：提供完整的RESTful API进行模板管理
6. **零依赖**：不依赖Jinja2等复杂框架，使用Python原生字符串格式化

## 目录结构

```
prompts/
├── decision/              # 决策引擎Prompt
│   └── default.txt       # 默认决策策略
├── debate/               # 辩论系统Prompt
│   ├── bull_analyst.txt  # 多头分析师
│   ├── bear_analyst.txt  # 空头分析师
│   └── research_manager.txt  # 研究经理
└── intelligence/         # 情报系统Prompt（预留）
```

## 使用方法

### 1. 修改Prompt模板

直接编辑对应的`.txt`文件即可：

```bash
# 编辑决策引擎的默认策略
vim backend/prompts/decision/default.txt

# 编辑多头分析师的Prompt
vim backend/prompts/debate/bull_analyst.txt
```

### 2. 热重载模板

**方式1：自动重载（推荐）**
- 系统会自动监控文件变化并重载（需要安装watchdog）

**方式2：API手动重载**
```bash
# 重载所有模板
curl -X POST http://localhost:8000/api/v1/prompts/reload

# 重载指定类别
curl -X POST http://localhost:8000/api/v1/prompts/reload?category=decision
```

### 3. API管理

**列出所有模板**
```bash
GET /api/v1/prompts/{category}
```

**获取模板内容**
```bash
GET /api/v1/prompts/{category}/{name}
```

**更新模板**
```bash
PUT /api/v1/prompts/{category}/{name}
Content-Type: application/json

{
  "content": "新的Prompt内容..."
}
```

## 配置选项

在`.env`文件中可配置：

```env
# Prompt模板目录
PROMPTS_DIR=prompts

# 默认策略
DEFAULT_DECISION_STRATEGY=default
DEFAULT_DEBATE_STRATEGY=default

# 是否启用热重载
ENABLE_PROMPT_HOT_RELOAD=true
```

## 技术实现

### 核心组件

1. **PromptManager** (`app/services/decision/prompt_manager.py`)
   - 模板加载与缓存
   - 线程安全的模板管理
   - 优雅降级机制

2. **PromptWatcher** (`app/services/decision/prompt_watcher.py`)
   - 文件监控（基于watchdog）
   - 防抖机制
   - 自动热重载

3. **Prompt API** (`app/api/v1/prompts.py`)
   - RESTful API接口
   - 权限控制（仅管理员）
   - CRUD操作

### 集成点

- **DecisionEngineV2**：决策引擎使用`build_decision_prompt_v3`方法
- **DebateSystem**：辩论系统的BullAnalyst、BearAnalyst、ResearchManager都已集成
- **优雅降级**：所有组件都保留了硬编码版本作为fallback

## 与NOFX的对比

| 特性 | NOFX (Go) | AIcoin (Python) |
|------|-----------|-----------------|
| 文件格式 | `.txt` | `.txt` |
| 热重载 | ✅ | ✅ (watchdog) |
| 优雅降级 | ✅ | ✅ |
| API管理 | ✅ | ✅ |
| 模板引擎 | 原生字符串 | 原生字符串 |
| 多策略 | ✅ | ✅ |
| 线程安全 | ✅ (sync.RWMutex) | ✅ (threading.RLock) |

## 最佳实践

1. **版本控制**：将`prompts/`目录纳入Git管理
2. **备份策略**：修改前先备份原文件
3. **渐进式修改**：小步迭代，每次修改后测试
4. **A/B测试**：创建多个策略模板进行对比
5. **文档化**：在Prompt中添加注释说明设计意图

## 故障排查

### 问题1：模板加载失败

**症状**：日志显示"加载Prompt模板失败"

**解决**：
1. 检查文件路径是否正确
2. 检查文件权限
3. 查看日志中的详细错误信息
4. 系统会自动降级到硬编码版本

### 问题2：热重载不工作

**症状**：修改文件后没有自动重载

**解决**：
1. 确认已安装watchdog：`pip install watchdog`
2. 检查`ENABLE_PROMPT_HOT_RELOAD`配置
3. 手动调用API重载：`POST /api/v1/prompts/reload`

### 问题3：权限不足

**症状**：API返回403错误

**解决**：
- Prompt管理API仅限管理员访问
- 确认使用管理员账户登录

## 未来扩展

- [ ] Web UI管理界面（Monaco Editor）
- [ ] 版本历史与回滚
- [ ] A/B测试框架
- [ ] 性能分析与优化建议
- [ ] 多语言支持
- [ ] 模板市场（参考NOFX规划）

## 参考资料

- NOFX Prompt Manager: `/Users/xinghailong/Documents/soft/nofx/decision/prompt_manager.go`
- NOFX默认Prompt: `/Users/xinghailong/Documents/soft/nofx/prompts/default.txt`
- 实现计划: `/Users/xinghailong/Documents/soft/AIcoin/docs/04-研究报告/05-Prompt模板系统设计.md`

