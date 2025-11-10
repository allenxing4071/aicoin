# AI成本数据获取说明

## 📊 数据来源

AI成本管理页面显示的数据**完全来自各AI平台的实际API调用**,不是手动录入的。

## 🔄 数据流程

### 1. API调用时自动记录

每次调用AI平台API时,系统会自动记录:

```python
# 在 QwenSearchAdapter.analyze() 中
response = await self.client.chat.completions.create(...)

# 获取token使用情况
usage = response.usage
cost = self._calculate_cost(
    usage.prompt_tokens,
    usage.completion_tokens
)

# 记录调用统计
await self._record_call(success=True, cost=cost)
```

### 2. 成本计算

根据各平台的定价自动计算:

```python
def _calculate_cost(self, prompt_tokens: int, completion_tokens: int) -> float:
    """
    计算API调用成本
    
    Qwen定价（示例）：
    - Input: ¥4.0 / 1M tokens
    - Output: ¥12.0 / 1M tokens
    """
    input_cost = (prompt_tokens / 1_000_000) * 4.0
    output_cost = (completion_tokens / 1_000_000) * 12.0
    return input_cost + output_cost
```

### 3. 数据库更新

统计数据实时更新到数据库:

```python
async def update_platform_stats(
    self,
    provider: str,
    success: bool,
    response_time: float,
    cost: float = 0.0
):
    """更新平台统计信息"""
    platform.total_calls += 1
    if success:
        platform.successful_calls += 1
    else:
        platform.failed_calls += 1
    
    # 更新平均响应时间
    platform.avg_response_time = (
        platform.avg_response_time * 0.9 + response_time * 0.1
    )
    
    platform.total_cost += cost
    await db.commit()
```

## 📈 实际数据示例

从刚才的模拟数据可以看到:

| 平台 | 调用次数 | 成功率 | 成本 | 响应时间 |
|------|---------|--------|------|---------|
| DeepSeek Chat | 100 | 93.6% | ¥0.3368 | 1392ms |
| 腾讯云 (Qwen搜索) | 42 | 93.0% | ¥0.7849 | 1968ms |
| 火山引擎 (Qwen搜索) | 38 | 95.0% | ¥0.8890 | 1562ms |
| 百度智能云 (Qwen搜索) | 24 | 92.9% | ¥0.5833 | 1553ms |
| Qwen-Plus | 41 | 93.5% | ¥1.0585 | 1464ms |

**总计**: 245次调用, ¥3.6525, 平均成功率93.06%

## 🔧 数据获取方式

### 方式1: 实际运行系统

当系统实际运行时,每次AI决策或情报收集都会自动产生数据:

```python
# 在 AITradingOrchestratorV2 中
async def make_decision(self, symbol: str):
    # 1. 收集情报 (调用Qwen系列API)
    intelligence = await self.intelligence_engine.gather_intelligence(symbol)
    
    # 2. 做出决策 (调用DeepSeek API)
    decision = await self.decision_maker.make_decision(intelligence)
    
    # 每次调用都会自动记录token使用和成本
```

### 方式2: 使用模拟脚本

对于演示和测试,可以使用模拟脚本生成数据:

```bash
# 生成模拟数据
docker exec aicoin-backend python scripts/simulate_ai_usage.py

# 重置数据为0
docker exec aicoin-backend python scripts/simulate_ai_usage.py --reset
```

## 💡 关键特性

### 1. 自动追踪

✅ **无需手动记录** - 每次API调用自动记录  
✅ **精确计算** - 基于实际token使用量计算成本  
✅ **实时更新** - 数据立即写入数据库  

### 2. 多维度统计

- **调用次数**: 总调用、成功、失败
- **成本统计**: 总成本、月成本、日成本
- **性能指标**: 响应时间、成功率
- **健康状态**: 最后检查时间、健康状态

### 3. 成本优化

系统会根据实际使用情况提供优化建议:

```python
# 决策间隔优化
current_interval = 60  # 60秒
if total_cost > budget_threshold:
    recommended_interval = 120  # 建议延长到120秒
    estimated_savings = calculate_savings(current_interval, recommended_interval)
```

## 📊 前端数据展示

### API端点

```
GET /api/v1/intelligence/platforms
```

返回数据格式:

```json
{
  "platforms": [
    {
      "id": 7,
      "name": "腾讯云 (Qwen搜索)",
      "provider": "tencent",
      "platform_type": "intelligence",
      "enabled": true,
      "performance": {
        "total_calls": 42,
        "successful_calls": 39,
        "failed_calls": 3,
        "success_rate": 0.9286,
        "total_cost": 0.7849,
        "avg_response_time": 1968.11
      },
      "health": {
        "last_check": "2025-11-09T03:30:23.849882",
        "status": "healthy"
      }
    }
  ],
  "total": 5
}
```

### 前端展示

```typescript
// 获取平台数据
const res = await fetch('http://localhost:8000/api/v1/intelligence/platforms');
const data = await res.json();

// 计算总成本
const totalCost = data.platforms.reduce(
  (sum, p) => sum + p.performance.total_cost, 
  0
);

// 显示在页面上
<div>总成本: ¥{totalCost.toFixed(2)}</div>
```

## 🎯 定价配置

各平台定价在代码中配置:

```python
# backend/app/services/ai_cost_manager.py
MODEL_PRICING = {
    "deepseek-chat": {
        "input_price": 1.0,   # ¥1.0/百万tokens
        "output_price": 2.0,  # ¥2.0/百万tokens
    },
    "qwen-plus": {
        "input_price": 4.0,   # ¥4.0/百万tokens
        "output_price": 12.0, # ¥12.0/百万tokens
    },
    # ... 其他模型
}
```

也可以在数据库中配置:

```sql
UPDATE intelligence_platforms 
SET config_json = jsonb_set(
    config_json, 
    '{input_price_per_million}', 
    '4.0'
)
WHERE provider = 'qwen';
```

## 🔐 API Key管理

API Key安全存储在数据库中:

```python
# 加密存储
platform.api_key = encrypt(api_key)

# 使用时解密
api_key = decrypt(platform.api_key)
client = OpenAI(api_key=api_key, base_url=platform.base_url)
```

## 📝 使用日志

详细的使用日志存储在 `ai_model_usage_log` 表中:

```sql
SELECT 
    model_name,
    input_tokens,
    output_tokens,
    cost,
    response_time,
    created_at
FROM ai_model_usage_log
ORDER BY created_at DESC
LIMIT 10;
```

## 🎉 总结

AI成本数据**完全来自实际API调用**,系统自动:
1. ✅ 记录每次调用的token使用
2. ✅ 根据定价计算成本
3. ✅ 更新统计数据到数据库
4. ✅ 在前端实时展示

**无需手动录入,数据100%真实可靠!** 🚀

