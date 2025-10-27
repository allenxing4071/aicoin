# 真实数据与实盘交易实施计划

## 📋 项目目标

将 AIcoin 系统从模拟数据升级为**真实数据**和**实盘交易**，完全复刻 [nof1.ai](https://nof1.ai/) 的功能，但只使用 **DeepSeek** 和 **Qwen** 两个AI模型。

---

## 🎯 核心功能模块

### 1. 前端UI完善 (P0 - 立即执行)

#### 1.1 README.TXT 标签页
```
功能: 显示项目介绍、竞赛规则、技术说明
参考: nof1.ai 的 README.TXT 标签页
内容:
- 项目简介
- AI模型介绍 (DeepSeek, Qwen)
- 交易规则
- 风险提示
```

#### 1.2 终端状态栏
```
位置: 页面底部
样式: [████████████] STATUS: CONNECTED
功能: 显示系统连接状态
状态:
- CONNECTING TO SERVER
- CONNECTED
- DISCONNECTED
- ERROR
```

---

### 2. 真实行情数据集成 (P0 - 立即执行)

#### 2.1 Hyperliquid WebSocket 行情订阅
```python
# backend/app/services/hyperliquid_market_data.py

功能:
- 订阅 BTC, ETH, SOL, BNB, DOGE, XRP 实时价格
- 订阅 K线数据 (1m, 5m, 15m, 1h, 4h, 1d)
- 订阅订单簿数据
- 订阅最新成交数据

数据更新频率:
- 价格: 实时推送
- K线: 每分钟更新
- 订单簿: 实时推送
```

#### 2.2 价格数据缓存
```python
# 使用 Redis 缓存实时价格
redis_key_pattern:
- price:{symbol} -> 最新价格
- kline:{symbol}:{interval} -> K线数据
- orderbook:{symbol} -> 订单簿
```

---

### 3. 真实交易执行 (P0 - 核心功能)

#### 3.1 Hyperliquid 交易API集成
```python
# backend/app/services/hyperliquid_trading.py

功能:
1. 账户管理
   - 查询账户余额
   - 查询持仓信息
   - 查询保证金使用率

2. 订单管理
   - 下单 (市价单、限价单)
   - 撤单
   - 查询订单状态
   - 查询历史订单

3. 风险控制
   - 最大持仓限制
   - 最大杠杆限制
   - 单笔交易金额限制
   - 每日交易次数限制
```

#### 3.2 交易执行流程
```
AI决策 → 风险检查 → 订单生成 → 交易执行 → 结果记录 → 通知推送
```

---

### 4. AI决策引擎 (P0 - 核心功能)

#### 4.1 DeepSeek 决策引擎
```python
# backend/app/ai/deepseek_agent.py

输入数据:
- 实时价格
- K线数据 (多周期)
- 持仓信息
- 账户余额
- 市场情绪指标

输出决策:
- 操作类型: LONG / SHORT / CLOSE / HOLD
- 币种: BTC / ETH / SOL / BNB / DOGE / XRP
- 杠杆倍数: 1-20X
- 仓位大小: 账户余额的 %
- 信心度: 0-100%
- 决策理由: 文本说明
```

#### 4.2 Qwen 决策引擎
```python
# backend/app/ai/qwen_agent.py

功能: 同 DeepSeek
特点: 使用不同的 Prompt 策略
```

#### 4.3 AI Prompt 设计
```
系统角色:
你是一个专业的加密货币交易员，负责分析市场数据并做出交易决策。

输入格式:
- 当前时间: {timestamp}
- 账户余额: ${balance}
- 当前持仓: {positions}
- 市场数据: {market_data}

输出格式 (JSON):
{
  "action": "LONG|SHORT|CLOSE|HOLD",
  "symbol": "BTC|ETH|SOL|BNB|DOGE|XRP",
  "leverage": 1-20,
  "position_size_percent": 0-100,
  "confidence": 0-100,
  "reasoning": "决策理由"
}

风险控制规则:
1. 单笔交易不超过账户余额的 20%
2. 最大杠杆 20X
3. 同时持仓不超过 3 个币种
4. 信心度低于 60% 不执行交易
```

---

### 5. WebSocket 实时推送 (P1 - 重要功能)

#### 5.1 前端 WebSocket 连接
```typescript
// frontend/app/hooks/useWebSocket.ts

订阅频道:
- price_update: 价格更新
- trade_executed: 交易执行
- position_update: 持仓变化
- ai_decision: AI决策推送
- account_update: 账户余额更新
```

#### 5.2 后端 WebSocket 服务
```python
# backend/app/websocket/manager.py

功能:
- 管理客户端连接
- 广播实时数据
- 心跳检测
- 断线重连
```

---

### 6. 数据持久化 (P1 - 重要功能)

#### 6.1 数据库表设计

**trades 表 (交易记录)**
```sql
CREATE TABLE trades (
  id SERIAL PRIMARY KEY,
  model VARCHAR(50) NOT NULL,  -- 'deepseek' or 'qwen'
  symbol VARCHAR(20) NOT NULL,
  side VARCHAR(10) NOT NULL,   -- 'LONG' or 'SHORT'
  entry_price DECIMAL(20, 8),
  exit_price DECIMAL(20, 8),
  leverage INTEGER,
  position_size DECIMAL(20, 8),
  pnl DECIMAL(20, 8),
  pnl_percent DECIMAL(10, 4),
  confidence INTEGER,
  reasoning TEXT,
  entry_time TIMESTAMP,
  exit_time TIMESTAMP,
  status VARCHAR(20),  -- 'OPEN', 'CLOSED', 'LIQUIDATED'
  created_at TIMESTAMP DEFAULT NOW()
);
```

**positions 表 (持仓)**
```sql
CREATE TABLE positions (
  id SERIAL PRIMARY KEY,
  model VARCHAR(50) NOT NULL,
  symbol VARCHAR(20) NOT NULL,
  side VARCHAR(10) NOT NULL,
  entry_price DECIMAL(20, 8),
  current_price DECIMAL(20, 8),
  leverage INTEGER,
  position_size DECIMAL(20, 8),
  notional_value DECIMAL(20, 8),
  unrealized_pnl DECIMAL(20, 8),
  liquidation_price DECIMAL(20, 8),
  opened_at TIMESTAMP,
  updated_at TIMESTAMP DEFAULT NOW(),
  UNIQUE(model, symbol)
);
```

**ai_decisions 表 (AI决策记录)**
```sql
CREATE TABLE ai_decisions (
  id SERIAL PRIMARY KEY,
  model VARCHAR(50) NOT NULL,
  action VARCHAR(20) NOT NULL,
  symbol VARCHAR(20) NOT NULL,
  leverage INTEGER,
  position_size_percent DECIMAL(10, 4),
  confidence INTEGER,
  reasoning TEXT,
  market_data JSONB,
  executed BOOLEAN DEFAULT FALSE,
  created_at TIMESTAMP DEFAULT NOW()
);
```

**account_snapshots 表 (账户快照)**
```sql
CREATE TABLE account_snapshots (
  id SERIAL PRIMARY KEY,
  model VARCHAR(50) NOT NULL,
  balance DECIMAL(20, 8),
  equity DECIMAL(20, 8),
  unrealized_pnl DECIMAL(20, 8),
  margin_used DECIMAL(20, 8),
  margin_ratio DECIMAL(10, 4),
  created_at TIMESTAMP DEFAULT NOW()
);
```

---

### 7. 风险管理系统 (P0 - 核心功能)

#### 7.1 风险控制参数
```python
# backend/app/config/risk_config.py

RISK_LIMITS = {
    "max_position_size_percent": 20,  # 单笔交易最大仓位 20%
    "max_leverage": 20,                # 最大杠杆 20X
    "max_open_positions": 3,           # 最大同时持仓数
    "min_confidence": 60,              # 最低信心度 60%
    "max_daily_trades": 50,            # 每日最大交易次数
    "max_daily_loss_percent": 10,     # 每日最大亏损 10%
    "stop_loss_percent": 5,            # 止损比例 5%
    "take_profit_percent": 10,         # 止盈比例 10%
}
```

#### 7.2 风险检查流程
```python
def check_risk(decision: AIDecision, account: Account) -> bool:
    """
    风险检查
    """
    # 1. 检查仓位大小
    if decision.position_size_percent > RISK_LIMITS["max_position_size_percent"]:
        return False
    
    # 2. 检查杠杆倍数
    if decision.leverage > RISK_LIMITS["max_leverage"]:
        return False
    
    # 3. 检查持仓数量
    if len(account.positions) >= RISK_LIMITS["max_open_positions"]:
        return False
    
    # 4. 检查信心度
    if decision.confidence < RISK_LIMITS["min_confidence"]:
        return False
    
    # 5. 检查每日交易次数
    if account.daily_trades >= RISK_LIMITS["max_daily_trades"]:
        return False
    
    # 6. 检查每日亏损
    if account.daily_loss_percent >= RISK_LIMITS["max_daily_loss_percent"]:
        return False
    
    return True
```

---

### 8. 监控与告警 (P2 - 优化功能)

#### 8.1 系统监控
```
监控指标:
- API调用成功率
- WebSocket连接状态
- 数据库查询性能
- Redis缓存命中率
- AI决策延迟
- 交易执行延迟
```

#### 8.2 告警机制
```
告警条件:
- 账户余额低于阈值
- 单笔交易亏损超过阈值
- 每日亏损超过阈值
- API调用失败
- WebSocket断开连接
- 数据库连接失败
```

---

## 🔧 技术实现细节

### 1. Hyperliquid API 集成

#### 1.1 安装依赖
```bash
pip install hyperliquid-python-sdk
```

#### 1.2 API 配置
```python
# backend/app/config/hyperliquid_config.py

HYPERLIQUID_CONFIG = {
    "mainnet": {
        "api_url": "https://api.hyperliquid.xyz",
        "ws_url": "wss://api.hyperliquid.xyz/ws",
    },
    "testnet": {
        "api_url": "https://api.hyperliquid-testnet.xyz",
        "ws_url": "wss://api.hyperliquid-testnet.xyz/ws",
    }
}

# 使用环境变量配置
HYPERLIQUID_ENV = os.getenv("HYPERLIQUID_ENV", "testnet")
HYPERLIQUID_PRIVATE_KEY = os.getenv("HYPERLIQUID_PRIVATE_KEY")
```

#### 1.3 账户初始化
```python
from hyperliquid.exchange import Exchange
from hyperliquid.info import Info

# 初始化
exchange = Exchange(
    private_key=HYPERLIQUID_PRIVATE_KEY,
    testnet=(HYPERLIQUID_ENV == "testnet")
)

info = Info(testnet=(HYPERLIQUID_ENV == "testnet"))
```

---

### 2. AI 决策引擎实现

#### 2.1 DeepSeek API 调用
```python
import requests

def call_deepseek_api(prompt: str) -> dict:
    """
    调用 DeepSeek API
    """
    url = "https://api.deepseek.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }
    
    payload = {
        "model": "deepseek-chat",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "response_format": {"type": "json_object"}
    }
    
    response = requests.post(url, headers=headers, json=payload)
    return response.json()
```

#### 2.2 Qwen API 调用
```python
import dashscope

def call_qwen_api(prompt: str) -> dict:
    """
    调用 Qwen API
    """
    dashscope.api_key = QWEN_API_KEY
    
    response = dashscope.Generation.call(
        model="qwen-max",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        result_format="message",
        response_format={"type": "json_object"}
    )
    
    return response.output.choices[0].message.content
```

---

### 3. 定时任务调度

#### 3.1 使用 APScheduler
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

# 每分钟执行一次 AI 决策
@scheduler.scheduled_job('interval', minutes=1)
async def ai_decision_job():
    """
    AI 决策任务
    """
    # DeepSeek 决策
    deepseek_decision = await deepseek_agent.make_decision()
    if deepseek_decision:
        await execute_trade(deepseek_decision, model="deepseek")
    
    # Qwen 决策
    qwen_decision = await qwen_agent.make_decision()
    if qwen_decision:
        await execute_trade(qwen_decision, model="qwen")

# 每5分钟更新一次账户快照
@scheduler.scheduled_job('interval', minutes=5)
async def account_snapshot_job():
    """
    账户快照任务
    """
    await save_account_snapshot("deepseek")
    await save_account_snapshot("qwen")

# 启动调度器
scheduler.start()
```

---

## 📊 数据流程图

```
┌─────────────────────────────────────────────────────────────────┐
│                        数据采集层                                │
├─────────────────────────────────────────────────────────────────┤
│  Hyperliquid WebSocket → 实时价格、K线、订单簿、成交数据        │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                        数据缓存层                                │
├─────────────────────────────────────────────────────────────────┤
│  Redis → 缓存实时价格、K线数据、订单簿                          │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                        AI决策层                                  │
├─────────────────────────────────────────────────────────────────┤
│  DeepSeek Agent ←→ 市场数据 + 账户信息 → 交易决策               │
│  Qwen Agent     ←→ 市场数据 + 账户信息 → 交易决策               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                        风险控制层                                │
├─────────────────────────────────────────────────────────────────┤
│  风险检查 → 仓位限制、杠杆限制、信心度检查、每日限额            │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                        交易执行层                                │
├─────────────────────────────────────────────────────────────────┤
│  Hyperliquid API → 下单、撤单、查询订单、查询持仓               │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                        数据持久化层                              │
├─────────────────────────────────────────────────────────────────┤
│  PostgreSQL → 交易记录、持仓、AI决策、账户快照                  │
└────────────────────────┬────────────────────────────────────────┘
                         │
                         ↓
┌─────────────────────────────────────────────────────────────────┐
│                        实时推送层                                │
├─────────────────────────────────────────────────────────────────┤
│  WebSocket → 推送价格、交易、持仓、AI决策到前端                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🚀 实施步骤

### Phase 1: UI完善 (今天 - 2小时)
```
1. ✅ 添加 README.TXT 标签页
2. ✅ 添加终端状态栏
3. ✅ 测试UI功能
```

### Phase 2: 真实行情数据 (今天 - 4小时)
```
1. ⚠️ 集成 Hyperliquid WebSocket
2. ⚠️ 实现价格数据缓存
3. ⚠️ 更新前端显示真实价格
4. ⚠️ 更新K线图显示真实数据
```

### Phase 3: AI决策引擎 (明天 - 6小时)
```
1. ⚠️ 实现 DeepSeek 决策引擎
2. ⚠️ 实现 Qwen 决策引擎
3. ⚠️ 设计 AI Prompt
4. ⚠️ 测试 AI 决策输出
```

### Phase 4: 交易执行 (明天 - 4小时)
```
1. ⚠️ 集成 Hyperliquid 交易 API
2. ⚠️ 实现订单管理
3. ⚠️ 实现风险控制
4. ⚠️ 测试交易执行 (测试网)
```

### Phase 5: 数据持久化 (后天 - 3小时)
```
1. ⚠️ 创建数据库表
2. ⚠️ 实现交易记录存储
3. ⚠️ 实现持仓管理
4. ⚠️ 实现账户快照
```

### Phase 6: WebSocket推送 (后天 - 3小时)
```
1. ⚠️ 实现后端 WebSocket 服务
2. ⚠️ 实现前端 WebSocket 连接
3. ⚠️ 测试实时数据推送
```

### Phase 7: 测试与优化 (第4天 - 全天)
```
1. ⚠️ 在测试网进行完整测试
2. ⚠️ 性能优化
3. ⚠️ 安全加固
4. ⚠️ 文档完善
```

### Phase 8: 实盘部署 (第5天)
```
1. ⚠️ 配置实盘环境
2. ⚠️ 小额资金测试
3. ⚠️ 监控系统运行
4. ⚠️ 逐步增加资金
```

---

## ⚠️ 风险提示

### 1. 技术风险
```
- API 调用失败
- WebSocket 断开连接
- 数据库连接失败
- AI 决策错误
- 交易执行延迟
```

### 2. 市场风险
```
- 价格剧烈波动
- 流动性不足
- 滑点过大
- 爆仓风险
```

### 3. 资金风险
```
- 建议初始资金: $1,000 - $5,000
- 每个模型: $500 - $2,500
- 先在测试网充分测试
- 实盘从小额开始
```

---

## 📝 配置清单

### 1. 环境变量
```bash
# Hyperliquid
HYPERLIQUID_ENV=testnet  # testnet or mainnet
HYPERLIQUID_PRIVATE_KEY=your_private_key

# AI APIs
DEEPSEEK_API_KEY=your_deepseek_key
QWEN_API_KEY=your_qwen_key

# Database
DATABASE_URL=postgresql://admin:password@postgres:5432/aicoin

# Redis
REDIS_URL=redis://redis:6379
```

### 2. API 密钥申请
```
1. Hyperliquid: https://hyperliquid.xyz/
2. DeepSeek: https://platform.deepseek.com/
3. Qwen: https://dashscope.aliyun.com/
```

---

## 📚 参考资料

- **nof1.ai**: https://nof1.ai/
- **Hyperliquid Docs**: https://hyperliquid.gitbook.io/
- **DeepSeek API**: https://platform.deepseek.com/docs
- **Qwen API**: https://help.aliyun.com/zh/dashscope/

---

**文档版本**: v1.0  
**创建时间**: 2025-10-24 23:55:00  
**作者**: AI Assistant (Product Manager Mode)

