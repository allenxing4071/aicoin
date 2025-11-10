# AI成本管理系统说明

## 📋 概述

AIcoin系统现已集成完整的AI成本管理功能，可以实时监控各个AI模型的使用情况、费用统计和预算控制。

---

## 🎯 主要功能

### 1. 模型定价管理
- 支持多个AI模型的定价配置
- 区分输入/输出token价格
- 支持免费模型标记

### 2. 使用统计
- 实时记录每次AI调用
- 统计总调用次数、token使用量
- 计算实际花费

### 3. 预算控制
- 设置月度预算限制
- 自动告警（达到80%阈值）
- 超预算提醒

### 4. 成本优化建议
- 分析使用模式
- 提供优化建议
- 决策间隔成本对比

---

## 💰 已配置的AI模型定价

### DeepSeek系列（决策模型）

| 模型 | 输入价格 | 输出价格 | 用途 |
|------|---------|---------|------|
| **DeepSeek Chat** | ¥1.0/百万tokens | ¥2.0/百万tokens | AI交易决策 |
| **DeepSeek Reasoner** | ¥4.0/百万tokens | ¥16.0/百万tokens | 深度推理 |

### Qwen系列（情报模型）

| 模型 | 输入价格 | 输出价格 | 用途 |
|------|---------|---------|------|
| **Qwen-Plus** | ¥4.0/百万tokens | ¥12.0/百万tokens | 情报分析 |
| **Qwen-Turbo** | ¥2.0/百万tokens | ¥6.0/百万tokens | 快速响应 |
| **Qwen-Max** | ¥40.0/百万tokens | ¥120.0/百万tokens | 最强性能 |

### OpenAI系列（分析模型）

| 模型 | 输入价格 | 输出价格 | 用途 |
|------|---------|---------|------|
| **GPT-4o** | ¥15.0/百万tokens | ¥60.0/百万tokens | 多模态分析 |
| **GPT-4o Mini** | ¥1.05/百万tokens | ¥4.2/百万tokens | 性价比高 |

### Claude系列（分析模型）

| 模型 | 输入价格 | 输出价格 | 用途 |
|------|---------|---------|------|
| **Claude 3.5 Sonnet** | ¥21.0/百万tokens | ¥105.0/百万tokens | 强大推理 |

### 免费模型

| 模型 | 价格 | 用途 |
|------|------|------|
| **Groq Llama** | 免费 | 快速监控 |

---

## 📊 决策间隔成本分析

基于单次决策成本 ¥1.047，不同决策间隔的成本对比：

| 模式 | 间隔 | 日决策次数 | 日成本 | 月成本 | 节省 |
|------|------|-----------|--------|--------|------|
| **激进模式** | 1分钟 | 1,440 | ¥1,500 | ¥45,000 | - |
| **标准模式** | 5分钟 | 288 | ¥300 | ¥9,000 | 80% |
| **平衡模式（当前）** | 10分钟 | 144 | ¥150 | ¥4,500 | 90% ⭐ |
| **保守模式** | 15分钟 | 96 | ¥100 | ¥3,000 | 93% |
| **智能触发** | 事件驱动 | 30 | ¥31 | ¥940 | 98% |

**当前配置**: 10分钟间隔，月成本约 ¥4,500，相比1分钟间隔节省90%

---

## 🔧 API接口

### 1. 获取模型定价和统计

```bash
GET /api/v1/ai-cost/models
```

**响应示例**:
```json
{
  "success": true,
  "data": [
    {
      "model_name": "deepseek-chat",
      "display_name": "DeepSeek Chat",
      "provider": "deepseek",
      "type": "decision",
      "is_free": false,
      "enabled": true,
      "total_calls": 150,
      "total_cost": 45.50,
      "current_month_cost": 12.30,
      "monthly_budget": 1000.0,
      "remaining_budget": 987.70,
      "usage_percentage": 1.2,
      "input_price": 1.0,
      "output_price": 2.0
    }
  ],
  "count": 9
}
```

### 2. 获取成本总览

```bash
GET /api/v1/ai-cost/summary
```

**响应示例**:
```json
{
  "success": true,
  "data": {
    "total_cost": 1250.50,
    "month_cost": 450.30,
    "today_cost": 15.20,
    "total_calls": 5000,
    "model_count": 9
  }
}
```

### 3. 获取使用历史

```bash
GET /api/v1/ai-cost/usage-history?days=7&limit=100
```

### 4. 更新模型预算

```bash
PUT /api/v1/ai-cost/models/{model_name}/budget?budget=1000
```

### 5. 获取优化建议

```bash
GET /api/v1/ai-cost/optimization-suggestions
```

### 6. 获取决策间隔分析

```bash
GET /api/v1/ai-cost/decision-interval-analysis
```

---

## 💡 成本优化建议

### 方案A: 调整决策间隔（推荐）

**当前**: 10分钟间隔，月成本 ¥4,500

**优化选项**:
1. **15分钟间隔** → 月成本 ¥3,000（节省33%）
   - 适合: 长期持仓策略
   - 影响: 可能错过部分短期机会

2. **5分钟间隔** → 月成本 ¥9,000（增加100%）
   - 适合: 中频交易
   - 影响: 更多交易机会，但成本翻倍

**修改方法**:
```bash
# 编辑.env文件
DECISION_INTERVAL=900  # 15分钟

# 重启后端
docker restart aicoin-backend
```

### 方案B: 智能触发（高级）

只在关键时刻触发AI决策：
- 价格波动 > 2%
- 成交量异常
- 持仓盈亏 > 5%
- 重要新闻事件

**预期效果**: 月成本 ¥1,000-2,000（节省95%+）

**需要**: 开发智能触发逻辑

### 方案C: 使用更便宜的模型

| 当前模型 | 替代方案 | 成本节省 |
|---------|---------|---------|
| Qwen-Plus | Qwen-Turbo | 50% |
| GPT-4o | GPT-4o Mini | 75% |
| Claude 3.5 | Qwen-Max | 50% |

### 方案D: 优化Prompt

- 减少发送的市场数据量
- 使用更精简的指令
- 缓存常用分析结果

**预期效果**: 减少50-70% tokens使用

---

## 📈 监控和告警

### 自动告警触发条件

1. **预算告警**（Warning）
   - 当月成本达到预算的80%
   - 自动记录到 `ai_budget_alerts` 表

2. **超预算告警**（Critical）
   - 当月成本超过预算
   - 建议立即调整使用策略

### 查看告警

```sql
-- 查看未解决的告警
SELECT * FROM ai_budget_alerts 
WHERE is_resolved = false 
ORDER BY created_at DESC;
```

---

## 🗄️ 数据库表结构

### ai_model_pricing（模型定价配置）

```sql
CREATE TABLE ai_model_pricing (
    id SERIAL PRIMARY KEY,
    model_name VARCHAR(100) UNIQUE NOT NULL,
    provider VARCHAR(50) NOT NULL,
    display_name VARCHAR(100) NOT NULL,
    model_type VARCHAR(50) NOT NULL,
    input_price_per_million FLOAT NOT NULL DEFAULT 0.0,
    output_price_per_million FLOAT NOT NULL DEFAULT 0.0,
    total_calls INTEGER DEFAULT 0,
    total_input_tokens INTEGER DEFAULT 0,
    total_output_tokens INTEGER DEFAULT 0,
    total_cost FLOAT DEFAULT 0.0,
    monthly_budget FLOAT DEFAULT 0.0,
    current_month_cost FLOAT DEFAULT 0.0,
    alert_threshold FLOAT DEFAULT 0.8,
    enabled BOOLEAN DEFAULT true,
    is_free BOOLEAN DEFAULT false,
    description TEXT,
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    last_used_at TIMESTAMP WITH TIME ZONE
);
```

### ai_model_usage_log（使用日志）

记录每次AI调用的详细信息，用于成本分析和审计。

### ai_budget_alerts（预算告警）

记录预算告警历史，支持告警管理和追踪。

---

## 🔄 每月维护

### 月初重置成本

系统会自动在每月1号重置 `current_month_cost`，也可以手动触发：

```bash
POST /api/v1/ai-cost/reset-monthly-costs
```

### 预算调整

根据上月实际使用情况，调整各模型的月度预算：

```bash
PUT /api/v1/ai-cost/models/deepseek-chat/budget?budget=2000
PUT /api/v1/ai-cost/models/qwen-plus/budget?budget=1500
```

---

## 📝 使用示例

### 1. 查看当前成本

```bash
curl http://localhost:8000/api/v1/ai-cost/summary | jq '.'
```

### 2. 查看各模型使用情况

```bash
curl http://localhost:8000/api/v1/ai-cost/models | jq '.data[] | {name: .display_name, cost: .current_month_cost, budget: .monthly_budget}'
```

### 3. 获取优化建议

```bash
curl http://localhost:8000/api/v1/ai-cost/optimization-suggestions | jq '.data'
```

### 4. 分析决策间隔成本

```bash
curl http://localhost:8000/api/v1/ai-cost/decision-interval-analysis | jq '.data.intervals'
```

---

## ⚠️ 注意事项

1. **定价更新**: 模型定价可能会变化，需要定期更新数据库中的价格
2. **预算设置**: 建议为每个模型设置合理的月度预算
3. **成本监控**: 定期查看成本报告，及时调整使用策略
4. **日志保留**: 使用日志默认保留90天，可根据需要调整

---

## 🚀 未来规划

1. **前端可视化**
   - 成本趋势图表
   - 模型使用对比
   - 预算使用进度条

2. **智能推荐**
   - 基于历史数据推荐最优模型
   - 自动调整决策间隔
   - 成本异常检测

3. **批量操作**
   - 批量设置预算
   - 批量启用/禁用模型
   - 导出成本报告

4. **集成告警**
   - 邮件/短信告警
   - Webhook通知
   - 钉钉/企业微信集成

---

## 📚 相关文档

- [成本优化方案](./cost_optimization_plan.md)
- [AI平台API密钥配置](./07-部署运维/05-AI平台API密钥配置.md)
- [云平台配置快速参考](./07-部署运维/09-云平台配置快速参考表.md)

---

**最后更新**: 2025-11-08  
**版本**: v1.0

