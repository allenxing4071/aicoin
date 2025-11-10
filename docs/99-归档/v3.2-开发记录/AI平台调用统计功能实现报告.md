# AI平台调用统计功能实现报告

## 📋 概述

**实施时间**：2025年11月9日  
**页面路径**：`/admin/ai-platforms/stats`  
**状态**：✅ 已完成

## 🎯 实现目标

将原本硬编码的AI平台调用统计页面改造为基于真实数据库日志的动态统计系统，支持按时间范围查询和峰值时段分析。

## 📊 功能特性

### 1. 按时间范围统计 ⏰

支持三种时间维度的统计：

| 时间范围 | 说明 | 数据来源 |
|---------|------|---------|
| **今日** | 当天00:00至今 | `ai_model_usage_log` 表 |
| **本周** | 最近7天 | `ai_model_usage_log` 表 |
| **本月** | 最近30天 | `ai_model_usage_log` 表 |

**实现方式**：
- 前端通过时间范围按钮切换
- 后端根据 `time_range` 参数动态计算起始时间
- 实时查询数据库获取统计数据

### 2. 平台维度统计 📈

为每个AI平台单独统计：

- **总调用次数** - 成功 + 失败调用总数
- **成功调用** - `success=true` 的调用数
- **失败调用** - `success=false` 的调用数
- **成功率** - 成功调用 / 总调用 × 100%
- **平均响应时间** - 所有成功调用的平均响应时间
- **总成本** - 该时间段内的累计成本
- **调用量占比** - 该平台调用量占总调用量的百分比

**平台识别逻辑**：
```python
provider_model_map = {
    "deepseek": ["deepseek"],
    "qwen": ["qwen"],
    "tencent": ["hunyuan"],
    "volcano": ["doubao"],
    "baidu": ["ernie", "wenxin"],
}
```

通过模糊匹配 `model_name` 字段来归类调用记录。

### 3. 整体统计汇总 📊

页面顶部显示4个关键指标卡片：

1. **总调用次数** - 蓝色边框
2. **成功调用** - 绿色边框
3. **失败调用** - 红色边框
4. **整体成功率** - 紫色边框

### 4. 峰值时段分析 🔥

**支持时间范围**：今日、本周（月度数据量大，暂不支持）

**功能特性**：
- **峰值时段高亮** - 自动识别调用量最高的小时
- **按小时统计** - 显示每小时的调用量、成功/失败数、成本
- **可视化进度条** - 直观展示各小时调用量占比
- **时间格式化** - 中文友好的时间显示

**峰值卡片显示**：
- 峰值时间点
- 调用次数
- 成功/失败数
- 该小时成本

## 🔧 技术实现

### 后端 API

#### 1. 平台统计接口

**路径**：`GET /api/v1/ai-platforms/stats`

**参数**：
- `time_range`: `today` | `week` | `month` | `all`

**返回数据结构**：
```json
{
  "success": true,
  "data": {
    "time_range": "today",
    "time_label": "今日",
    "start_time": "2025-11-09T00:00:00",
    "end_time": "2025-11-09T14:00:00",
    "summary": {
      "total_calls": 288,
      "successful_calls": 275,
      "failed_calls": 13,
      "success_rate": 95.49,
      "total_cost": 15.67
    },
    "platforms": [
      {
        "id": 1,
        "name": "DeepSeek决策引擎",
        "provider": "deepseek",
        "total_calls": 150,
        "successful_calls": 145,
        "failed_calls": 5,
        "success_rate": 96.67,
        "avg_response_time": 1.234,
        "total_cost": 8.50
      },
      // ... 其他平台
    ]
  }
}
```

#### 2. 小时统计接口

**路径**：`GET /api/v1/ai-platforms/hourly-stats`

**参数**：
- `time_range`: `today` | `week`

**返回数据结构**：
```json
{
  "success": true,
  "data": {
    "time_range": "today",
    "start_time": "2025-11-09T00:00:00",
    "end_time": "2025-11-09T14:00:00",
    "hourly_stats": [
      {
        "hour": "2025-11-09T08:00:00",
        "calls": 45,
        "successful": 43,
        "failed": 2,
        "cost": 2.34
      },
      // ... 其他小时
    ],
    "peak_hour": {
      "hour": "2025-11-09T10:00:00",
      "calls": 52,
      "successful": 50,
      "failed": 2,
      "cost": 2.89
    }
  }
}
```

### 前端实现

#### 文件路径
`frontend/app/admin/ai-platforms/stats/page.tsx`

#### 核心功能

1. **时间范围切换**
```typescript
const [timeRange, setTimeRange] = useState<'today' | 'week' | 'month'>('today');

useEffect(() => {
  fetchData();
  fetchHourlyData();
}, [timeRange]);
```

2. **数据获取**
```typescript
const fetchData = async () => {
  const res = await fetch(`http://localhost:8000/api/v1/ai-platforms/stats?time_range=${timeRange}`);
  const data = await res.json();
  if (data.success && data.data) {
    setPlatforms(data.data.platforms);
  }
};
```

3. **峰值时段可视化**
```typescript
const maxCalls = Math.max(...hourlyStats.map(s => s.calls));
const percentage = maxCalls > 0 ? (stat.calls / maxCalls) * 100 : 0;

<div className="w-full bg-gray-200 rounded-full h-2">
  <div
    className="h-2 bg-blue-500 rounded-full"
    style={{ width: `${percentage}%` }}
  />
</div>
```

## 📁 文件清单

### 新增文件

1. **后端API**
   - `backend/app/api/v1/endpoints/platform_stats.py` - 统计API实现

### 修改文件

1. **后端**
   - `backend/app/main.py` - 注册新的路由

2. **前端**
   - `frontend/app/admin/ai-platforms/stats/page.tsx` - 完整重构

## 🔄 数据流程

```
┌─────────────────┐
│  用户选择时间范围  │
└────────┬────────┘
         │
         ▼
┌─────────────────────────────┐
│  前端发送API请求              │
│  /api/v1/ai-platforms/stats  │
│  ?time_range=today           │
└────────┬────────────────────┘
         │
         ▼
┌─────────────────────────────────────┐
│  后端计算时间范围                      │
│  - today: 今天00:00至今               │
│  - week: 最近7天                      │
│  - month: 最近30天                    │
└────────┬────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  查询 ai_model_usage_log 表           │
│  - 按 provider 分组                   │
│  - 统计成功/失败次数                  │
│  - 计算平均响应时间                   │
│  - 汇总成本                           │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  返回统计数据                          │
│  - 各平台详细统计                      │
│  - 整体汇总数据                        │
└────────┬─────────────────────────────┘
         │
         ▼
┌──────────────────────────────────────┐
│  前端渲染UI                            │
│  - 顶部汇总卡片                        │
│  - 各平台统计列表                      │
│  - 峰值时段分析                        │
└──────────────────────────────────────┘
```

## 📊 数据来源

### 主要数据表

#### 1. `ai_model_usage_log` 表

记录每次AI调用的详细信息：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | Integer | 主键 |
| `model_name` | String | 模型名称（如 deepseek-chat） |
| `input_tokens` | Integer | 输入token数 |
| `output_tokens` | Integer | 输出token数 |
| `cost` | Float | 本次成本（元） |
| `response_time` | Float | 响应时间（秒） |
| `success` | Boolean | 是否成功 |
| `error_message` | Text | 错误信息 |
| `purpose` | String | 调用目的（decision/intelligence） |
| `created_at` | DateTime | 创建时间 |

#### 2. `intelligence_platforms` 表

存储平台配置信息：

| 字段 | 类型 | 说明 |
|------|------|------|
| `id` | Integer | 主键 |
| `name` | String | 平台名称 |
| `provider` | String | 提供商（deepseek/qwen/tencent等） |
| `enabled` | Boolean | 是否启用 |

## 🎨 UI设计

### 颜色方案

- **蓝色** - 总调用次数、调用量进度条
- **绿色** - 成功调用、成功率高（≥95%）
- **红色** - 失败调用
- **紫色** - 整体成功率
- **橙色** - 峰值时段高亮
- **黄色** - 成功率中等（80-95%）

### 成功率颜色分级

```typescript
const getSuccessRateColor = (rate: number) => {
  if (rate >= 95) return 'text-green-600';
  if (rate >= 80) return 'text-yellow-600';
  return 'text-red-600';
};
```

## 🚀 部署步骤

1. **复制后端文件到Docker容器**
```bash
docker cp backend/app/api/v1/endpoints/platform_stats.py aicoin-backend:/app/app/api/v1/endpoints/
docker cp backend/app/main.py aicoin-backend:/app/app/
```

2. **重启后端服务**
```bash
docker-compose restart backend
```

3. **重新构建前端**
```bash
docker-compose build frontend --no-cache
docker-compose up -d frontend
```

## ✅ 测试验证

### 测试场景

1. **时间范围切换**
   - ✅ 点击"今日"按钮，显示今天的统计
   - ✅ 点击"本周"按钮，显示最近7天的统计
   - ✅ 点击"本月"按钮，显示最近30天的统计

2. **平台统计**
   - ✅ 各平台调用次数正确显示
   - ✅ 成功率计算准确
   - ✅ 调用量占比进度条正确渲染

3. **峰值时段分析**
   - ✅ 今日/本周模式下显示小时统计
   - ✅ 峰值时段正确高亮
   - ✅ 月度模式下显示提示信息

4. **数据为空场景**
   - ✅ 无调用数据时显示友好提示
   - ✅ 无小时统计时显示占位符

## 📈 性能优化

### 数据库查询优化

1. **索引使用**
   - `created_at` 字段有索引，时间范围查询高效
   - `model_name` 字段有索引，模糊匹配性能良好

2. **查询优化**
   - 使用聚合函数 `COUNT()`, `SUM()`, `AVG()` 减少数据传输
   - 按平台分组查询，避免全表扫描

3. **前端优化**
   - 使用 `useEffect` 依赖 `timeRange`，避免不必要的重复请求
   - 小时统计仅在今日/本周模式下获取

## 🔮 未来扩展

### 计划功能

1. **图表可视化** 📊
   - 使用 Chart.js 或 Recharts 绘制趋势图
   - 支持调用量、成功率、成本的时间序列图

2. **导出功能** 📥
   - 导出CSV格式的统计报表
   - 支持自定义时间范围导出

3. **实时刷新** 🔄
   - WebSocket 实时推送最新调用数据
   - 自动刷新机制（可配置间隔）

4. **更多维度** 🎯
   - 按 `purpose` 分类统计（决策 vs 情报）
   - 按交易对（`symbol`）统计
   - 按错误类型统计失败原因

5. **告警功能** 🚨
   - 成功率低于阈值时告警
   - 调用量异常时告警
   - 成本超预算时告警

## 📝 注意事项

1. **数据一致性**
   - 统计数据基于 `ai_model_usage_log` 表
   - 需要确保每次AI调用都正确记录日志

2. **时区问题**
   - 后端使用 UTC 时间
   - 前端显示时自动转换为本地时区

3. **性能考虑**
   - 月度数据量大时，小时统计可能较慢
   - 建议月度模式下不显示小时统计

4. **模型名称匹配**
   - 依赖 `model_name` 字段的命名规范
   - 新增平台时需更新 `provider_model_map`

## 🎉 总结

本次实现将AI平台调用统计页面从硬编码改造为基于真实数据的动态统计系统，具备以下优势：

✅ **真实数据** - 基于实际调用日志，数据准确可靠  
✅ **灵活查询** - 支持多种时间范围，满足不同分析需求  
✅ **详细统计** - 平台级、小时级多维度统计  
✅ **直观展示** - 可视化进度条、峰值高亮、颜色分级  
✅ **性能优化** - 数据库索引、聚合查询、按需加载  

该功能为AI成本管理和性能优化提供了重要的数据支撑！

---

**文档版本**：v1.0  
**创建时间**：2025年11月9日  
**维护者**：AIcoin开发团队

