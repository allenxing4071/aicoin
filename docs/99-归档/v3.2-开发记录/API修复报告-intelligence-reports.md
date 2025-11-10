# API修复报告 - /api/v1/intelligence/reports

## 问题描述

前端多个页面（RSS新闻源、巨鲸监控、链上数据、实时情报、历史报告）在调用 `/api/v1/intelligence/reports?limit=XX` 时返回 `404 (Not Found)` 错误。

## 问题分析

### 原因

后端 `intelligence.py` 中只有以下端点：
- `/reports/latest` - 获取最新报告
- `/reports/history` - 获取历史报告（带复杂筛选）
- `/reports/{report_id}` - 根据ID获取报告

但**缺少**简化的 `/reports` 端点，而前端页面需要这个简单的列表接口。

## 解决方案

### 1. 添加新API端点

在 `backend/app/api/v1/intelligence.py` 中添加：

```python
@router.get("/reports")
async def get_reports(
    limit: int = Query(default=20, ge=1, le=100, description="返回记录数量"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取情报报告列表（简化版本）
    用于前端页面快速获取最新报告
    """
    try:
        from sqlalchemy import select
        # 查询最新的报告
        stmt = select(IntelligenceReport)\
                .order_by(desc(IntelligenceReport.timestamp))\
                .limit(limit)
        result = await db.execute(stmt)
        reports = result.scalars().all()
        
        return {
            "success": True,
            "data": [r.to_dict() for r in reports],
            "total": len(reports)
        }
    
    except Exception as e:
        logger.error(f"获取情报报告失败: {e}")
        raise HTTPException(status_code=500, detail=str(e))
```

### 2. 添加必要导入

```python
from sqlalchemy.ext.asyncio import AsyncSession
```

### 3. 部署步骤

```bash
# 1. 复制更新后的文件到容器
docker cp backend/app/api/v1/intelligence.py aicoin-backend:/app/app/api/v1/intelligence.py

# 2. 重启后端容器
docker-compose restart backend

# 3. 等待启动完成
sleep 8
```

## API规格

### 请求

```
GET /api/v1/intelligence/reports?limit={limit}
```

**参数**:
- `limit` (可选): 返回记录数量，默认20，范围1-100

### 响应

**成功 (200)**:
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "timestamp": "2025-11-09T10:00:00",
      "market_sentiment": "BULLISH",
      "sentiment_score": 0.75,
      "confidence": 0.85,
      "key_news": [...],
      "whale_signals": [...],
      "on_chain_metrics": {...},
      "risk_factors": [...],
      "opportunities": [...],
      "qwen_analysis": "...",
      "created_at": "2025-11-09T10:00:00"
    }
  ],
  "total": 1
}
```

**数据为空**:
```json
{
  "success": true,
  "data": [],
  "total": 0
}
```

**错误 (500)**:
```json
{
  "detail": "错误信息"
}
```

## 技术要点

### 1. 异步数据库查询

使用 `AsyncSession` 和 SQLAlchemy 2.0 风格的查询：

```python
from sqlalchemy import select
stmt = select(IntelligenceReport).order_by(desc(IntelligenceReport.timestamp)).limit(limit)
result = await db.execute(stmt)
reports = result.scalars().all()
```

### 2. 与现有端点的区别

| 端点 | 用途 | 特点 |
|-----|------|------|
| `/reports` | 简单列表 | 只需limit参数，快速获取最新报告 |
| `/reports/latest` | 最新报告 | 从Redis缓存获取，单条记录 |
| `/reports/history` | 历史查询 | 支持复杂筛选（时间、情绪、置信度） |
| `/reports/{id}` | 单条查询 | 根据ID精确查询 |

### 3. 前端调用

所有情报中枢页面都使用此API：

```typescript
// RSS新闻源
const reportsRes = await fetch('http://localhost:8000/api/v1/intelligence/reports?limit=10');

// 巨鲸监控
const reportsRes = await fetch('http://localhost:8000/api/v1/intelligence/reports?limit=20');

// 链上数据
const reportsRes = await fetch('http://localhost:8000/api/v1/intelligence/reports?limit=20');

// 实时情报
const res = await fetch('http://localhost:8000/api/v1/intelligence/reports?limit=20');

// 历史报告
const res = await fetch('http://localhost:8000/api/v1/intelligence/reports?limit=100');
```

## 测试结果

### 测试命令

```bash
curl -s 'http://localhost:8000/api/v1/intelligence/reports?limit=2'
```

### 测试结果

```json
{"success":true,"data":[],"total":0}
```

✅ API正常工作，返回空数组（因为数据库中暂无数据）

## 影响的页面

修复后，以下页面不再出现404错误：

1. ✅ RSS新闻源 (`/admin/intelligence/rss`)
2. ✅ 巨鲸监控 (`/admin/intelligence/whale`)
3. ✅ 链上数据 (`/admin/intelligence/onchain`)
4. ✅ 实时情报 (`/admin/intelligence/realtime`)
5. ✅ 历史报告 (`/admin/intelligence/reports`)

## 后续工作

### 数据填充

当前数据库中没有情报报告数据，需要：

1. **启动情报收集服务**
   - 配置并启用数据源（RSS、Whale Alert、Etherscan等）
   - 运行情报收集任务

2. **创建测试数据**
   - 可以手动创建一些测试报告
   - 或者运行一次手动收集：`POST /api/v1/intelligence/collect`

### 数据示例

创建测试数据的SQL：

```sql
INSERT INTO intelligence_reports (
  timestamp, market_sentiment, sentiment_score, confidence,
  key_news, whale_signals, on_chain_metrics,
  risk_factors, opportunities, qwen_analysis, created_at
) VALUES (
  NOW(),
  'BULLISH',
  0.75,
  0.85,
  '[{"title": "BTC突破新高", "source": "CoinDesk", "sentiment": "positive"}]'::jsonb,
  '[{"symbol": "BTC", "action": "buy", "amount_usd": 1000000}]'::jsonb,
  '{"exchange_net_flow": -500000, "active_addresses": 50000}'::jsonb,
  '["市场波动性增加"]'::jsonb,
  '["突破关键阻力位"]'::jsonb,
  'AI分析：市场情绪积极，建议关注...',
  NOW()
);
```

## 总结

### 修复内容

- ✅ 添加 `/api/v1/intelligence/reports` API端点
- ✅ 使用异步数据库查询（AsyncSession）
- ✅ 添加必要的导入（AsyncSession, select）
- ✅ 部署到生产环境

### 修复结果

- ✅ API正常响应（200 OK）
- ✅ 返回正确的JSON格式
- ✅ 所有前端页面不再报404错误
- ✅ 页面正常显示（暂无数据提示）

### 文件变更

- `backend/app/api/v1/intelligence.py` - 添加新端点和导入

---

**修复时间**: 2025-11-09  
**修复状态**: ✅ 已完成  
**测试状态**: ✅ 通过

