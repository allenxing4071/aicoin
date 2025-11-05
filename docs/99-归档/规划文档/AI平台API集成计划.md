# 🌐 AI平台API集成计划

**创建时间**: 2025-11-05  
**状态**: 待实施  

---

## 🎯 核心原则

根据用户需求，构建"AI顾问委员会"，需要集成以下类型的AI平台：

1. **低成本/免费平台** - 用于高频基础监控
2. **强联网搜索平台** - 用于实时市场情报
3. **强推理平台** - 用于深度分析

---

## 📊 平台分类和集成计划

### 🆓 第一层：免费/低成本平台（高频监控）

| 平台 | API地址 | 能力 | 免费额度 | 优先级 | 状态 |
|------|---------|------|----------|--------|------|
| **Groq** | https://api.groq.com/openai/v1 | 超快推理速度 | 免费14,400 req/day | ⭐⭐⭐ | ❌ 待集成 |
| **Ollama本地** | http://localhost:11434 | 完全免费 | 无限制（本地） | ⭐⭐ | ❌ 待集成 |
| **HuggingFace** | https://api-inference.huggingface.co | 开源模型 | 有限免费 | ⭐ | ❌ 待集成 |

**建议选择**: **Groq** - 速度快、免费额度大、API兼容OpenAI

---

### 🔍 第二层：联网搜索平台（实时情报）

| 平台 | API地址 | 联网能力 | 成本 | 优先级 | 状态 |
|------|---------|----------|------|--------|------|
| **DeepSeek满血版** | https://api.deepseek.com | ✅ 支持联网搜索 | $0.14/$0.28 per 1M | ⭐⭐⭐⭐⭐ | ❌ 待集成 |
| **Perplexity** | https://api.perplexity.ai | ✅ 专注搜索 | $0.20/$1.00 per 1M | ⭐⭐⭐⭐ | ❌ 待集成 |
| **Qwen联网版** | https://dashscope.aliyuncs.com | ✅ 支持联网 | ¥0.50/1M tokens | ⭐⭐⭐ | ⚠️ 部分集成 |
| **OpenAI GPT-4 Turbo** | https://api.openai.com/v1 | ✅ Browsing功能 | $10/$30 per 1M | ⭐⭐ | ❌ 待集成 |

**建议优先**: **DeepSeek满血版** + **Perplexity**

---

### 🧠 第三层：深度推理平台（综合分析）

| 平台 | API地址 | 推理能力 | 成本 | 优先级 | 状态 |
|------|---------|----------|------|--------|------|
| **Claude Sonnet 4** | https://api.anthropic.com | ⭐⭐⭐⭐⭐ | $3/$15 per 1M | ⭐⭐⭐⭐⭐ | ❌ 待集成 |
| **GPT-4o** | https://api.openai.com/v1 | ⭐⭐⭐⭐ | $2.50/$10 per 1M | ⭐⭐⭐⭐ | ❌ 待集成 |
| **Qwen-Max** | https://dashscope.aliyuncs.com | ⭐⭐⭐ | ¥20/1M tokens | ⭐⭐⭐ | ⚠️ 部分集成 |
| **Gemini Pro** | https://generativelanguage.googleapis.com | ⭐⭐⭐ | $0.35/$1.05 per 1M | ⭐⭐ | ❌ 待集成 |

**建议优先**: **Claude Sonnet 4** - 目前最强推理能力

---

## 🔧 当前集成状态

### ✅ 已集成
- **Qwen基础API** - 阿里云DashScope
  - ⚠️ 但没有启用联网搜索功能
  - ⚠️ 只是普通的对话接口

### ❌ 未集成（严重缺失！）
- **DeepSeek满血版（联网搜索）** ❌
- **Perplexity（专业搜索）** ❌
- **Claude Sonnet 4（顶级推理）** ❌
- **GPT-4o** ❌
- **Groq（免费高速）** ❌

---

## 📝 详细集成方案

### 1️⃣ DeepSeek满血版（最高优先级）

**为什么选它**：
- ✅ 支持联网搜索（`search_web` 功能）
- ✅ 价格便宜（$0.14/$0.28 per 1M tokens）
- ✅ 中文友好
- ✅ API兼容OpenAI

**官方文档**：https://platform.deepseek.com/docs

**API示例**：
```python
import openai

client = openai.OpenAI(
    api_key="sk-xxxxx",
    base_url="https://api.deepseek.com"
)

# 启用联网搜索
response = client.chat.completions.create(
    model="deepseek-chat",  # 满血版模型
    messages=[
        {"role": "user", "content": "搜索BTC最新新闻"}
    ],
    tools=[{
        "type": "function",
        "function": {
            "name": "search_web",
            "description": "搜索网络获取实时信息",
            "parameters": {}
        }
    }],
    tool_choice="auto"  # 自动决定是否联网
)
```

**关键参数**：
- `model`: `deepseek-chat` (满血版)
- `tools`: 包含 `search_web` 函数
- `tool_choice`: `auto` 或 `required`

---

### 2️⃣ Perplexity（专业搜索）

**为什么选它**：
- ✅ 专门为搜索优化
- ✅ 返回来源链接
- ✅ 支持时间范围筛选
- ✅ 搜索质量高

**官方文档**：https://docs.perplexity.ai/

**API示例**：
```python
import openai

client = openai.OpenAI(
    api_key="pplx-xxxxx",
    base_url="https://api.perplexity.ai"
)

response = client.chat.completions.create(
    model="sonar-pro",  # 专业搜索模型
    messages=[
        {
            "role": "system",
            "content": "你是专业的加密货币情报员"
        },
        {
            "role": "user",
            "content": "搜索过去24小时BTC的重大新闻"
        }
    ]
)
```

**推荐模型**：
- `sonar-pro`: 最强搜索能力
- `sonar`: 标准搜索（更便宜）

---

### 3️⃣ Claude Sonnet 4（深度推理）

**为什么选它**：
- ✅ 当前最强推理能力
- ✅ 上下文窗口200K
- ✅ 逻辑严谨
- ✅ 适合复杂分析

**官方文档**：https://docs.anthropic.com/

**API示例**：
```python
import anthropic

client = anthropic.Anthropic(
    api_key="sk-ant-xxxxx"
)

response = client.messages.create(
    model="claude-sonnet-4-20250514",
    max_tokens=4096,
    system="你是顶级加密货币分析师",
    messages=[
        {
            "role": "user",
            "content": "综合分析以下市场情报..."
        }
    ]
)
```

**注意**：
- API格式与OpenAI不同
- 需要单独的SDK：`anthropic`
- 成本较高，用于关键决策

---

### 4️⃣ Groq（免费高速平台）

**为什么选它**：
- ✅ 完全免费（14,400 req/day）
- ✅ 速度超快（专用硬件LPU）
- ✅ API兼容OpenAI
- ✅ 适合高频监控

**官方文档**：https://console.groq.com/docs

**API示例**：
```python
import openai

client = openai.OpenAI(
    api_key="gsk_xxxxx",
    base_url="https://api.groq.com/openai/v1"
)

response = client.chat.completions.create(
    model="mixtral-8x7b-32768",  # 或 llama3-70b
    messages=[
        {"role": "user", "content": "快速筛选高影响力新闻"}
    ],
    temperature=0.3
)
```

**推荐模型**：
- `mixtral-8x7b-32768`: 平衡性能和速度
- `llama-3.1-70b-versatile`: 更强但稍慢

---

## 🎨 改进后的架构

```
┌─────────────────────────────────────────────────────────┐
│           Qwen情报员"AI顾问委员会"                         │
└─────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────┐
│  L1: 高频基础监控层（免费/低成本）                          │
├─────────────────────────────────────────────────────────┤
│  • Groq (免费高速)          - 快速筛选                     │
│  • 本地规则引擎             - 关键词过滤                   │
│  • Ollama本地              - 离线分析                      │
├─────────────────────────────────────────────────────────┤
│  输出: 高价值信息筛选                                      │
│  成本: $0                                                 │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  L2: 实时联网搜索层（按需付费）                            │
├─────────────────────────────────────────────────────────┤
│  • DeepSeek满血版 (联网)   - 主力搜索，中文优秀            │
│  • Perplexity             - 备用，返回来源                │
│  • Qwen联网版             - 备用，国内稳定                │
├─────────────────────────────────────────────────────────┤
│  输出: 实时新闻、官方公告、市场动态                          │
│  成本: $0.001-0.005 / 次                                 │
└─────────────────────────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────┐
│  L3: 深度推理分析层（高质量）                              │
├─────────────────────────────────────────────────────────┤
│  • Claude Sonnet 4        - 主力，顶级推理                │
│  • GPT-4o                - 备用，视觉理解                 │
│  • Qwen-Max              - 备用，中文深度                 │
├─────────────────────────────────────────────────────────┤
│  输出: 综合研判报告、风险评估、机会识别                      │
│  成本: $0.01-0.05 / 次                                   │
└─────────────────────────────────────────────────────────┘
                           ↓
              【输出给DeepSeek交易员】
```

---

## 🚀 实施步骤

### Phase 1: 核心联网搜索能力（最高优先级）

**目标**: 让情报员真正能联网获取实时信息

**任务**:
1. ✅ 注册DeepSeek满血版API密钥
2. ✅ 集成`search_web`功能到`QwenSearchAdapter`
3. ✅ 测试联网搜索能力
4. ✅ 集成Perplexity作为备用

**预期效果**:
- 能搜索"BTC最新新闻"并获得真实结果
- 能指定时间范围（如"过去24小时"）
- 能返回信息来源链接

---

### Phase 2: 免费高速监控（降低成本）

**目标**: 利用免费平台处理高频任务

**任务**:
1. ✅ 集成Groq API
2. ✅ 替换当前的`FreePlatformAdapter`
3. ✅ 设置请求限流（14,400/day）
4. ✅ 添加降级机制（Groq失败→本地规则）

**预期效果**:
- 80%的基础筛选由免费Groq处理
- 每日成本降低90%

---

### Phase 3: 顶级推理能力（提升质量）

**目标**: 让深度分析更专业

**任务**:
1. ✅ 集成Claude Sonnet 4 API
2. ✅ 替换当前的Qwen深度分析
3. ✅ 优化Prompt工程
4. ✅ 添加成本控制（按情况选择模型）

**预期效果**:
- 分析报告质量显著提升
- 逻辑推理更严谨
- 风险识别更准确

---

## 💰 成本估算

### 当前成本（几乎为0，因为没真正调用API）
- Qwen基础调用: ~$0

### 改进后成本（实际可用）

**每日100次情报收集场景**:

| 层级 | 平台 | 调用次数/日 | 单次成本 | 日成本 | 月成本 |
|------|------|------------|---------|--------|--------|
| L1 监控 | Groq | 100 | $0 | $0 | $0 |
| L2 搜索 | DeepSeek | 30 | $0.002 | $0.06 | $1.8 |
| L2 搜索 | Perplexity | 10 | $0.005 | $0.05 | $1.5 |
| L3 分析 | Claude S4 | 20 | $0.03 | $0.60 | $18 |
| L3 分析 | Qwen-Max | 80 | $0.01 | $0.80 | $24 |
| **总计** | - | 240 | - | **$1.51** | **$45.3** |

**备注**:
- 80%由免费Groq处理（监控层）
- 只有30%触发联网搜索（有重大事件时）
- 深度分析仅在关键时刻使用Claude

---

## 📋 配置文件更新

需要在`.env`中添加以下API密钥：

```bash
# ===== AI平台API密钥 =====

# L1: 免费监控层
GROQ_API_KEY=gsk_xxxxxxxxxxxxx

# L2: 联网搜索层
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxxxx         # DeepSeek满血版
PERPLEXITY_API_KEY=pplx-xxxxxxxxxxxxxxx    # Perplexity搜索

# L3: 深度推理层
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxx    # Claude Sonnet 4
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxx   # GPT-4o
QWEN_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx       # Qwen-Max（已有）

# ===== 平台开关 =====
ENABLE_GROQ=true
ENABLE_DEEPSEEK_SEARCH=true
ENABLE_PERPLEXITY=true
ENABLE_CLAUDE=true
ENABLE_GPT4=false  # 可选

# ===== 成本控制 =====
MAX_DAILY_COST_USD=10.0                    # 每日最大成本
PREFER_FREE_PLATFORMS=true                 # 优先使用免费平台
```

---

## ⚠️ 重要提醒

### 当前严重问题
1. **没有真正的联网搜索** - Qwen API只是对话，不是搜索
2. **没有多平台选择** - 只有一个平台，没有委员会
3. **成本没有优化** - 没有利用免费平台
4. **推理能力有限** - 没有使用顶级模型

### 需要立即行动
1. ✅ **集成DeepSeek满血版** - 获得真正的联网搜索能力
2. ✅ **集成Groq** - 利用免费额度降低成本
3. ✅ **集成Claude Sonnet 4** - 提升深度分析质量
4. ✅ **测试验证** - 确保每个平台都能正常工作

---

## 📚 参考文档

- **DeepSeek**: https://platform.deepseek.com/docs
- **Perplexity**: https://docs.perplexity.ai/
- **Claude**: https://docs.anthropic.com/
- **Groq**: https://console.groq.com/docs
- **Qwen**: https://help.aliyun.com/zh/dashscope/

---

**结论**: 当前系统只是搭建了架构框架，**实际上并没有真正的多平台AI协作能力**。需要立即集成上述平台的真实API才能实现"AI顾问委员会"的愿景。

**下一步**: 请确认是否要我立即开始集成这些平台？我会按Phase 1 → Phase 2 → Phase 3的顺序逐步实施。

