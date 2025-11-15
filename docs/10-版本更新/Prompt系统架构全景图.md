# Prompt系统在AIcoin系统中的完整体现

## 🎯 系统架构全景图

```
┌─────────────────────────────────────────────────────────────────────┐
│                        AIcoin 智能交易系统                            │
│                     (Prompt系统深度集成)                              │
└─────────────────────────────────────────────────────────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
   ┌────▼────┐               ┌─────▼──────┐            ┌──────▼──────┐
   │ 前端UI  │               │  后端API   │            │  决策引擎   │
   │ (React) │               │ (FastAPI)  │            │ (AI Core)   │
   └────┬────┘               └─────┬──────┘            └──────┬──────┘
        │                           │                           │
        │                           │                           │
   ┌────▼─────────────────────┐    │    ┌─────────────────────▼──────┐
   │  Prompt管理页面          │    │    │  DecisionEngineV2          │
   │  /admin/prompts-v2/      │◄───┼───►│  (核心决策引擎)            │
   │                          │    │    │                            │
   │  • 列表页                │    │    │  • 集成PromptManagerDB    │
   │  • 编辑页                │    │    │  • 根据L0-L5加载Prompt    │
   │  • A/B测试页             │    │    │  • 智能推荐最佳Prompt     │
   │  • 风险指标页            │    │    │  • 记录到三层记忆         │
   └──────────────────────────┘    │    └────────────────────────────┘
                                    │
                             ┌──────▼──────┐
                             │  API路由    │
                             │  /prompts/  │
                             └──────┬──────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
   ┌────▼────────┐         ┌───────▼────────┐       ┌─────────▼────────┐
   │ PostgreSQL  │         │     Redis      │       │     Qdrant       │
   │ (持久化)    │         │   (缓存层)     │       │   (向量检索)     │
   │             │         │                │       │                  │
   │ • Prompt表  │         │ • 5分钟TTL     │       │ • 性能向量       │
   │ • 版本表    │         │ • 热重载       │       │ • 相似场景       │
   │ • 性能表    │         │ • Pub/Sub      │       │ • 智能推荐       │
   └─────────────┘         └────────────────┘       └──────────────────┘
```

---

## 📍 1. 后端集成点（Backend）

### 1.1 主应用入口 (`app/main.py`)

**位置**: `backend/app/main.py:16`

```python
from app.api.v1 import prompts  # Prompt模板管理
```

**API路由注册**: `backend/app/main.py:340-344`

```python
# v3.5: Prompt模板管理（借鉴NOFX）
app.include_router(
    prompts.router,
    prefix=f"{settings.API_V1_PREFIX}/prompts/v2",
    tags=["Prompt Template Management"]
)
```

**访问地址**: `http://localhost:8000/api/v1/prompts/v2/`

---

### 1.2 API路由层 (`app/api/v1/prompts.py`)

**文件**: `backend/app/api/v1/prompts.py` (323行)

**核心功能**:
```python
router = APIRouter()

# CRUD操作
@router.get("/")                    # 获取所有Prompt
@router.get("/{prompt_id}")         # 获取单个Prompt
@router.post("/")                   # 创建Prompt
@router.put("/{prompt_id}")         # 更新Prompt
@router.delete("/{prompt_id}")      # 删除Prompt

# 热重载
@router.post("/reload")             # 热重载所有Prompt

# 版本管理
@router.get("/{prompt_id}/versions")  # 获取版本历史
@router.post("/{prompt_id}/rollback") # 回滚到指定版本

# DeepSeek智能优化
@router.post("/{prompt_id}/optimize") # AI优化Prompt

# 性能分析
@router.get("/{prompt_id}/metrics")   # 获取风险指标
@router.get("/{prompt_id}/ab-tests")  # 获取A/B测试结果
```

**API文档**: `http://localhost:8000/docs#/Prompt%20Template%20Management`

---

### 1.3 核心决策引擎 (`DecisionEngineV2`)

**文件**: `backend/app/services/decision/decision_engine_v2.py`

**集成位置**: Line 20, 72-75, 399-410

```python
from app.services.decision.prompt_manager_db import PromptManagerDB

class DecisionEngineV2:
    def __init__(self, ...):
        # 初始化Prompt管理器（数据库版本）
        self.prompt_manager = PromptManagerDB(db_session)
        self._prompt_manager_initialized = False
        logger.info("✅ Prompt管理器（数据库版）初始化成功")
    
    async def make_decision(self, market_data, account_state):
        # === 第3步：构建Prompt ===
        logger.info("📝 构建决策Prompt...")
        
        # 确保Prompt管理器已加载
        await self._ensure_prompt_manager_loaded()
        
        # 获取对应权限等级的Prompt模板
        template = self.prompt_manager.get_template(
            category="decision",
            name="default",
            permission_level=self.current_permission_level  # L0-L5
        )
        
        if template:
            # 使用模板渲染
            prompt = template.render(
                market_data=market_data,
                account_state=account_state,
                constraints=constraints,
                memory=memory_context
            )
```

**关键流程**:
1. 根据用户当前权限等级（L0-L5）加载对应Prompt
2. 使用Jinja2模板引擎渲染动态数据
3. 调用DeepSeek API进行决策
4. 记录Prompt使用情况到三层记忆

---

### 1.4 Prompt管理器 (`PromptManagerDB`)

**文件**: `backend/app/services/decision/prompt_manager_db.py` (291行)

**核心类**:

```python
class PromptManagerDB:
    """
    Prompt模板管理器（数据库版 - 性能优化版）
    
    三级缓存策略：
    1. 内存缓存（60秒）
    2. Redis缓存（5分钟）
    3. PostgreSQL数据库
    """
    
    async def load_from_db(self, force_reload=False):
        """从数据库加载Prompt（带缓存）"""
        # 1. 检查内存缓存
        if not force_reload and self.templates:
            return
        
        # 2. 尝试从Redis加载
        if self.redis_client:
            cached = await self.redis_client.get(key)
            if cached:
                return
        
        # 3. 从PostgreSQL加载
        templates = await self.db.execute(query)
        
        # 4. 写入Redis缓存
        await self.redis_client.set(key, data, expire=300)
    
    def get_template(self, category, name, permission_level):
        """获取Prompt模板（支持L0-L5权限）"""
        # 优先级：
        # 1. 特定等级模板（如：decision/default/L3）
        # 2. 通用模板（如：decision/default）
        # 3. 内置默认模板
```

**使用的地方**:
- `DecisionEngineV2` - 决策引擎
- `DebateSystem` - 辩论系统
- `IntelligenceAgent` - 情报系统

---

### 1.5 辩论系统集成 (`DebateSystem`)

**文件**: `backend/app/services/decision/debate_system.py`

```python
from app.services.decision.prompt_manager_db import PromptManagerDB

class DebateCoordinator:
    def __init__(self, ...):
        self.prompt_manager = PromptManagerDB(db_session)
    
    async def run_debate(self, ...):
        # 获取辩论Prompt
        template = self.prompt_manager.get_template(
            category="debate",
            name="bull_bear",
            permission_level=permission_level
        )
```

---

### 1.6 三层记忆集成

#### 短期记忆（Redis）
**文件**: `backend/app/services/memory/prompt_memory_extension.py`

```python
class PromptMemoryExtension:
    """扩展短期记忆，追踪Prompt使用"""
    
    async def record_prompt_usage(self, prompt_id, decision_id):
        """记录Prompt使用情况"""
        await self.redis.hset(
            f"prompt:usage:{prompt_id}",
            decision_id,
            json.dumps({"timestamp": now, "result": result})
        )
```

#### 长期记忆（Qdrant）
**文件**: `backend/app/services/memory/prompt_performance_memory.py`

```python
class PromptPerformanceMemory:
    """Qdrant向量存储 - Prompt性能记忆"""
    
    async def recommend_best_prompt(self, market_data, permission_level):
        """智能推荐最佳Prompt（基于历史性能）"""
        # 1. 向量化当前市场状态
        embedding = await self.get_embedding(market_data)
        
        # 2. 在Qdrant中搜索相似场景
        similar_scenarios = await self.qdrant.search(
            collection="prompt_performance",
            vector=embedding,
            filter={"permission_level": permission_level}
        )
        
        # 3. 返回历史表现最好的Prompt
        return best_prompt
```

#### 知识库（PostgreSQL）
**文件**: `backend/app/services/memory/prompt_knowledge_aggregator.py`

```python
class PromptKnowledgeAggregator:
    """聚合Prompt性能数据到知识库"""
    
    async def aggregate_daily_performance(self):
        """每日聚合Prompt性能"""
        # 从Qdrant读取今日所有Prompt性能
        # 计算胜率、夏普比率、最大回撤
        # 写入PostgreSQL的prompt_performance表
```

---

### 1.7 性能优化组件

#### Redis缓存优化
**文件**: `backend/app/services/memory/prompt_performance_memory_optimized.py`

```python
class PromptPerformanceMemoryOptimized:
    """Qdrant智能缓存（Redis加速）"""
    
    async def get_similar_prompts(self, context, embedding):
        # 1. 尝试从Redis获取（基于市场状态）
        cache_key = self._build_cache_key(context)
        cached = await self.redis.get(cache_key)
        if cached:
            return json.loads(cached)  # 5-10ms
        
        # 2. Qdrant向量检索
        results = await self.qdrant.search(...)  # 150-300ms
        
        # 3. 写入Redis（10分钟TTL）
        await self.redis.set(cache_key, json.dumps(results), ex=600)
```

#### DeepSeek流式响应
**文件**: `backend/app/services/decision/decision_engine_optimized.py`

```python
class DecisionEnginePerformanceOptimizer:
    """决策引擎性能优化器"""
    
    async def call_llm_stream(self, prompt):
        """流式调用DeepSeek（降低25-40%延迟）"""
        response = await self.client.chat.completions.create(
            model="deepseek-chat",
            messages=[{"role": "user", "content": prompt}],
            stream=True  # 启用流式
        )
        
        full_content = ""
        async for chunk in response:
            content = chunk.choices[0].delta.content
            full_content += content
            # 边接收边处理
        
        return full_content
```

---

## 📍 2. 前端集成点（Frontend）

### 2.1 管理后台菜单

**文件**: `frontend/app/admin/layout.tsx`

**菜单项**（需要添加）:
```typescript
{
  key: 'prompts',
  icon: <FileTextOutlined />,
  label: <Link href="/admin/prompts-v2">Prompt管理</Link>,
  children: [
    {
      key: 'prompts-list',
      label: <Link href="/admin/prompts-v2">模板列表</Link>
    },
    {
      key: 'prompts-ab-tests',
      label: <Link href="/admin/prompts-v2/ab-tests">A/B测试</Link>
    }
  ]
}
```

---

### 2.2 Prompt管理页面

#### 旧版（文件系统）
**路径**: `/admin/prompts/`  
**文件**: `frontend/app/admin/prompts/page.tsx` (309行)

**功能**:
- 📁 文件系统管理
- 📝 在线编辑
- 🔄 热重载

**状态**: ⚠️ 已弃用（保留作为备份）

---

#### 新版（数据库版）
**路径**: `/admin/prompts-v2/`  
**文件**: `frontend/app/admin/prompts-v2/page.tsx` (172行)

**功能**:
```typescript
export default function PromptsV2Page() {
  // 1. 筛选功能
  const [selectedCategory, setSelectedCategory] = useState('all')
  const [selectedLevel, setSelectedLevel] = useState('all')
  
  // 2. 列表展示
  const fetchPrompts = async () => {
    const response = await fetch('/api/prompts/v2/')
    const data = await response.json()
    setPrompts(data)
  }
  
  // 3. 热重载
  const handleReload = async () => {
    await fetch('/api/prompts/v2/reload', { method: 'POST' })
  }
  
  return (
    <div>
      {/* 筛选器 */}
      <select value={selectedCategory}>
        <option value="decision">决策</option>
        <option value="debate">辩论</option>
        <option value="intelligence">情报</option>
      </select>
      
      <select value={selectedLevel}>
        <option value="L0">L0 - 极度保守</option>
        <option value="L1">L1 - 保守稳健</option>
        <option value="L2">L2 - 平衡型</option>
        <option value="L3">L3 - 积极进取</option>
        <option value="L4">L4 - 高风险</option>
        <option value="L5">L5 - 极限激进</option>
      </select>
      
      {/* Prompt列表 */}
      {prompts.map(prompt => (
        <Card key={prompt.id}>
          <h3>{prompt.name}</h3>
          <Badge>{prompt.permission_level}</Badge>
          <Button onClick={() => router.push(`/admin/prompts-v2/${prompt.id}/edit`)}>
            编辑
          </Button>
        </Card>
      ))}
    </div>
  )
}
```

---

### 2.3 Prompt编辑页面

**路径**: `/admin/prompts-v2/[id]/edit`  
**文件**: `frontend/app/admin/prompts-v2/[id]/edit/page.tsx` (148行)

**功能**:
```typescript
export default function PromptEditPage() {
  return (
    <div className="grid grid-cols-2 gap-4">
      {/* 左侧：当前版本 */}
      <div>
        <h3>当前版本 (v{currentVersion})</h3>
        <Textarea value={currentContent} readOnly />
      </div>
      
      {/* 右侧：编辑区 */}
      <div>
        <h3>编辑中</h3>
        <Textarea value={editedContent} onChange={...} />
        
        {/* DeepSeek智能优化按钮 */}
        <Button onClick={handleOptimize}>
          🤖 DeepSeek智能优化
        </Button>
        
        {/* 保存选项 */}
        <Button onClick={() => handleSave('new_version')}>
          保存为新版本
        </Button>
        <Button onClick={() => handleSave('replace')}>
          替换当前版本
        </Button>
      </div>
    </div>
  )
}
```

---

### 2.4 A/B测试页面

**路径**: `/admin/prompts-v2/ab-tests`  
**文件**: `frontend/app/admin/prompts-v2/ab-tests/page.tsx` (104行)

**功能**:
```typescript
export default function ABTestsPage() {
  return (
    <div>
      {/* 创建A/B测试 */}
      <Button onClick={handleCreateTest}>创建新测试</Button>
      
      {/* 测试列表 */}
      {tests.map(test => (
        <Card key={test.id}>
          <h3>{test.name}</h3>
          <p>Prompt A: {test.prompt_a_name} vs Prompt B: {test.prompt_b_name}</p>
          <p>流量分配: {test.traffic_split}%</p>
          <Badge>{test.status}</Badge>
          
          {/* 实时结果 */}
          {test.status === 'running' && (
            <div>
              <p>A组胜率: {test.a_win_rate}%</p>
              <p>B组胜率: {test.b_win_rate}%</p>
              <p>统计显著性: {test.p_value < 0.05 ? '✅ 显著' : '⚠️ 不显著'}</p>
            </div>
          )}
        </Card>
      ))}
    </div>
  )
}
```

---

### 2.5 风险指标页面

**路径**: `/admin/prompts-v2/[id]/metrics`  
**文件**: `frontend/app/admin/prompts-v2/[id]/metrics/page.tsx` (133行)

**功能**:
```typescript
export default function PromptMetricsPage() {
  return (
    <div>
      {/* 关键指标卡片 */}
      <div className="grid grid-cols-4 gap-4">
        <Card>
          <h4>胜率</h4>
          <p className="text-3xl">{metrics.win_rate}%</p>
        </Card>
        
        <Card>
          <h4>夏普比率</h4>
          <p className="text-3xl">{metrics.sharpe_ratio}</p>
        </Card>
        
        <Card>
          <h4>最大回撤</h4>
          <p className="text-3xl text-red-500">{metrics.max_drawdown}%</p>
        </Card>
        
        <Card>
          <h4>VaR (95%)</h4>
          <p className="text-3xl">{metrics.var_95}%</p>
        </Card>
      </div>
      
      {/* 性能曲线图 */}
      <Card>
        <h3>累计收益曲线</h3>
        <LineChart data={metrics.pnl_curve} />
      </Card>
      
      {/* 市场状态分析 */}
      <Card>
        <h3>不同市场状态下的表现</h3>
        <BarChart data={metrics.performance_by_regime} />
      </Card>
    </div>
  )
}
```

---

## 📍 3. 数据库集成点（Database）

### 3.1 PostgreSQL表结构

**文件**: `backend/app/models/prompt_template.py`

```sql
-- 1. Prompt模板表
CREATE TABLE prompt_templates (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    permission_level VARCHAR(10),  -- L0-L5
    content TEXT NOT NULL,
    version INTEGER DEFAULT 1,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- 2. Prompt版本历史表
CREATE TABLE prompt_template_versions (
    id SERIAL PRIMARY KEY,
    prompt_template_id INTEGER REFERENCES prompt_templates(id),
    version INTEGER NOT NULL,
    content TEXT NOT NULL,
    change_summary TEXT,
    created_by VARCHAR(100),
    created_at TIMESTAMP DEFAULT NOW()
);

-- 3. Prompt性能表
CREATE TABLE prompt_performance (
    id SERIAL PRIMARY KEY,
    prompt_template_id INTEGER REFERENCES prompt_templates(id),
    permission_level VARCHAR(10),
    total_uses INTEGER DEFAULT 0,
    win_count INTEGER DEFAULT 0,
    loss_count INTEGER DEFAULT 0,
    total_pnl DECIMAL(20, 8) DEFAULT 0,
    sharpe_ratio DECIMAL(10, 4),
    max_drawdown DECIMAL(10, 4),
    last_updated TIMESTAMP DEFAULT NOW()
);

-- 4. Prompt A/B测试表
CREATE TABLE prompt_ab_tests (
    id SERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    prompt_a_id INTEGER REFERENCES prompt_templates(id),
    prompt_b_id INTEGER REFERENCES prompt_templates(id),
    traffic_split INTEGER DEFAULT 50,  -- A组流量百分比
    status VARCHAR(20) DEFAULT 'pending',  -- pending/running/completed
    start_time TIMESTAMP,
    end_time TIMESTAMP,
    a_win_rate DECIMAL(10, 4),
    b_win_rate DECIMAL(10, 4),
    p_value DECIMAL(10, 6),  -- 统计显著性
    winner VARCHAR(10),  -- 'A' or 'B' or 'tie'
    created_at TIMESTAMP DEFAULT NOW()
);
```

**迁移文件**: `backend/alembic/versions/015_add_prompt_system.py`

---

### 3.2 Redis缓存结构

```redis
# 1. Prompt模板缓存（5分钟TTL）
prompt_templates:all = {
    "decision/default/L0": {...},
    "decision/default/L1": {...},
    "decision/default/L2": {...},
    "decision/default/L3": {...},
    "decision/default/L4": {...},
    "decision/default/L5": {...},
    "debate/bull_bear/L3": {...}
}

# 2. 相似Prompt缓存（10分钟TTL）
prompt_similar:{hash} = [
    {"prompt_id": 1, "similarity": 0.95, "win_rate": 0.68},
    {"prompt_id": 3, "similarity": 0.88, "win_rate": 0.72}
]

# 3. Top Prompt预计算（1小时TTL）
top_prompts:high_volatility = [...]
top_prompts:low_volatility = [...]
top_prompts:trending = [...]

# 4. Prompt使用追踪（短期记忆）
prompt:usage:{prompt_id} = {
    "decision_123": {"timestamp": "...", "result": "win"},
    "decision_124": {"timestamp": "...", "result": "loss"}
}

# 5. 热重载通知（Pub/Sub）
PUBLISH prompt_reload "decision/default/L3"
```

---

### 3.3 Qdrant向量存储

**Collection**: `prompt_performance_vectors`

```python
{
    "id": "prompt_1_v2_1699999999",
    "vector": [0.123, -0.456, ...],  # 1536维向量
    "payload": {
        "prompt_id": 1,
        "prompt_version": 2,
        "permission_level": "L3",
        "market_regime": "high_volatility",
        "volatility": 0.45,
        "win_rate": 0.68,
        "sharpe_ratio": 1.85,
        "pnl": 125.50,
        "timestamp": "2025-11-15T10:30:00Z"
    }
}
```

**查询示例**:
```python
# 查找相似市场状态下表现最好的Prompt
results = qdrant.search(
    collection_name="prompt_performance_vectors",
    query_vector=current_market_embedding,
    query_filter={
        "must": [
            {"key": "permission_level", "match": {"value": "L3"}},
            {"key": "sharpe_ratio", "range": {"gte": 1.5}}
        ]
    },
    limit=5
)
```

---

## 📍 4. 完整决策流程示例

### 场景：用户发起交易决策（L3权限）

```
1️⃣ 用户触发决策
   ↓
   DecisionEngineV2.make_decision()
   
2️⃣ 检查权限等级
   ↓
   PermissionManager.get_current_level() → "L3"
   
3️⃣ 加载Prompt（三级缓存）
   ↓
   PromptManagerDB.get_template("decision", "default", "L3")
   ├─ 检查内存缓存（60秒）
   ├─ 检查Redis缓存（5分钟）→ 命中！返回 (1-5ms)
   └─ [未命中则查PostgreSQL (50-100ms)]
   
4️⃣ 智能推荐（可选）
   ↓
   PromptPerformanceMemory.recommend_best_prompt()
   ├─ 向量化当前市场状态
   ├─ 在Qdrant中搜索相似场景
   └─ 返回历史表现最好的Prompt
   
5️⃣ 渲染Prompt
   ↓
   template.render(
       market_data={...},
       account_state={...},
       constraints={...}
   )
   使用Jinja2模板引擎 (2-5ms)
   
6️⃣ 调用DeepSeek API
   ↓
   DecisionEngineOptimizer.call_llm_stream(prompt)
   流式响应 (1500-3000ms)
   
7️⃣ 记录到三层记忆
   ↓
   ├─ 短期记忆（Redis）：记录Prompt使用
   ├─ 长期记忆（Qdrant）：存储性能向量
   └─ 知识库（PostgreSQL）：聚合统计数据
   
8️⃣ 返回决策结果
   ↓
   {
       "action": "LONG",
       "size": 0.5,
       "confidence": 0.85,
       "prompt_id": 3,
       "prompt_version": 2
   }
```

**总耗时**: ~2264ms（优化后）vs ~3822ms（优化前）

---

## 📍 5. 核心文件清单

### 后端核心文件（13个）

| 文件路径 | 行数 | 功能 |
|---------|------|------|
| `app/main.py` | 571 | 主应用入口，注册Prompt路由 |
| `app/api/v1/prompts.py` | 323 | Prompt API路由（CRUD+热重载+优化） |
| `app/models/prompt_template.py` | 150 | 数据库模型定义 |
| `app/services/decision/prompt_manager_db.py` | 291 | Prompt管理器（三级缓存） |
| `app/services/decision/decision_engine_v2.py` | 410 | 决策引擎（集成Prompt） |
| `app/services/decision/decision_engine_optimized.py` | 300 | 性能优化器（流式+批量+监控） |
| `app/services/decision/prompt_redis_subscriber.py` | 120 | Redis Pub/Sub热重载 |
| `app/services/memory/prompt_memory_extension.py` | 80 | 短期记忆扩展 |
| `app/services/memory/prompt_performance_memory.py` | 200 | 长期记忆（Qdrant） |
| `app/services/memory/prompt_performance_memory_optimized.py` | 250 | Qdrant智能缓存 |
| `app/services/memory/prompt_knowledge_aggregator.py` | 150 | 知识库聚合 |
| `app/services/quantitative/risk_metrics.py` | 180 | 风险指标计算 |
| `app/services/quantitative/ab_test.py` | 200 | A/B测试框架 |

**总计**: ~3,225行核心代码

---

### 前端核心文件（5个）

| 文件路径 | 行数 | 功能 |
|---------|------|------|
| `app/admin/prompts-v2/page.tsx` | 172 | Prompt列表页 |
| `app/admin/prompts-v2/[id]/edit/page.tsx` | 148 | Prompt编辑页 |
| `app/admin/prompts-v2/ab-tests/page.tsx` | 104 | A/B测试页 |
| `app/admin/prompts-v2/[id]/metrics/page.tsx` | 133 | 风险指标页 |
| `app/admin/prompts/page.tsx` | 309 | 旧版页面（已弃用） |

**总计**: ~866行前端代码

---

### 数据库文件（2个）

| 文件路径 | 行数 | 功能 |
|---------|------|------|
| `alembic/versions/015_add_prompt_system.py` | 120 | 数据库迁移脚本 |
| `scripts/migrate_prompts_to_db.py` | 150 | 数据迁移工具 |

---

### 文档文件（5个）

| 文件路径 | 页数 | 功能 |
|---------|------|------|
| `docs/10-版本更新/v4.0_Prompt模板系统开发进度.md` | 8 | 开发进度文档 |
| `docs/10-版本更新/v4.0_Prompt系统部署指南.md` | 12 | 部署指南 |
| `docs/10-版本更新/v4.0_清理完成报告.md` | 6 | 代码清理报告 |
| `docs/10-版本更新/v4.0_集成完成报告.md` | 5 | 集成完成报告 |
| `docs/10-版本更新/v4.1_性能优化完成报告.md` | 15 | 性能优化报告 |

---

## 📍 6. 访问入口汇总

### API端点

```bash
# 基础URL
BASE_URL=http://localhost:8000/api/v1/prompts/v2

# 1. 获取所有Prompt
GET ${BASE_URL}/

# 2. 获取单个Prompt
GET ${BASE_URL}/{prompt_id}

# 3. 创建Prompt
POST ${BASE_URL}/

# 4. 更新Prompt
PUT ${BASE_URL}/{prompt_id}

# 5. 删除Prompt
DELETE ${BASE_URL}/{prompt_id}

# 6. 热重载
POST ${BASE_URL}/reload

# 7. 版本历史
GET ${BASE_URL}/{prompt_id}/versions

# 8. 回滚版本
POST ${BASE_URL}/{prompt_id}/rollback

# 9. DeepSeek优化
POST ${BASE_URL}/{prompt_id}/optimize

# 10. 风险指标
GET ${BASE_URL}/{prompt_id}/metrics

# 11. A/B测试
GET ${BASE_URL}/{prompt_id}/ab-tests
POST ${BASE_URL}/ab-tests
```

---

### 前端页面

```bash
# 基础URL
BASE_URL=http://localhost:3000/admin

# 1. Prompt列表页
${BASE_URL}/prompts-v2/

# 2. Prompt编辑页
${BASE_URL}/prompts-v2/{id}/edit

# 3. A/B测试页
${BASE_URL}/prompts-v2/ab-tests

# 4. 风险指标页
${BASE_URL}/prompts-v2/{id}/metrics

# 5. 旧版页面（已弃用）
${BASE_URL}/prompts/
```

---

### API文档

```bash
# Swagger UI
http://localhost:8000/docs

# ReDoc
http://localhost:8000/redoc

# OpenAPI JSON
http://localhost:8000/openapi.json
```

---

## 📍 7. 性能监控指标

### 实时监控

```python
from app.services.decision.decision_engine_optimized import performance_monitor

# 获取性能统计
stats = performance_monitor.get_stats()

{
    "db_query": {
        "count": 100,
        "avg": 0.055,  # 55ms
        "p50": 0.050,
        "p95": 0.095,
        "p99": 0.120
    },
    "qdrant_search": {
        "count": 50,
        "avg": 0.008,  # 8ms (Redis缓存)
        "p50": 0.005,
        "p95": 0.015,
        "p99": 0.025
    },
    "prompt_render": {
        "count": 100,
        "avg": 0.003,  # 3ms (Jinja2)
        "p50": 0.002,
        "p95": 0.005,
        "p99": 0.008
    },
    "llm_call": {
        "count": 100,
        "avg": 2.264,  # 2264ms (流式)
        "p50": 2.000,
        "p95": 3.020,
        "p99": 3.500
    }
}
```

---

## 🎯 总结

### Prompt系统在AIcoin中的体现

| 层级 | 体现方式 | 核心价值 |
|------|---------|---------|
| **决策层** | DecisionEngineV2集成 | 根据L0-L5动态加载策略 |
| **API层** | FastAPI路由 | 完整的CRUD+热重载+优化 |
| **存储层** | PostgreSQL+Redis+Qdrant | 三级缓存+向量检索 |
| **前端层** | React管理页面 | 可视化编辑+A/B测试+指标 |
| **记忆层** | 三层记忆集成 | 短期追踪+长期学习+知识沉淀 |
| **优化层** | 性能优化组件 | 40.8%性能提升+50%成本降低 |

### 核心优势

1. **智能化**: DeepSeek自动优化+Qdrant智能推荐
2. **科学化**: A/B测试+风险指标+过拟合检测
3. **工程化**: 三级缓存+热重载+版本管理
4. **可视化**: 完整的前端管理界面
5. **高性能**: 40.8%响应时间提升+50%成本降低

---

**🎉 Prompt系统已深度集成到AIcoin的每一个角落！**

