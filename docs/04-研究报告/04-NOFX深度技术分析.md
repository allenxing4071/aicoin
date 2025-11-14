# NOFX 深度技术分析

**文档编号**: AICOIN-RESEARCH-004  
**文档版本**: v1.0.0  
**创建日期**: 2025-11-14  
**研究人员**: 技术团队  
**密级**: 内部公开

---

## 📋 执行摘要

NOFX 是一个基于 Go + React 的多AI模型交易竞赛系统，由 tinkle-community 开发并开源。本文档对其技术架构、核心模块、设计模式进行深度剖析，为 AIcoin 项目提供技术参考。

**核心特点**：
1. **轻量级架构**：Go单进程 + SQLite，资源占用低
2. **统一交易接口**：支持Binance、Hyperliquid、Aster三大交易所
3. **多模型竞赛**：DeepSeek vs Qwen 实时对比
4. **完整的Web界面**：React SPA，Binance风格UI
5. **Prompt模板系统**：可热加载的提示词管理

---

## 1. 系统架构深度剖析

### 1.1 整体架构图

```
┌─────────────────────────────────────────────────────────┐
│                    main.go (入口)                        │
│  - 初始化数据库 (SQLite)                                 │
│  - 同步config.json到数据库                               │
│  - 加载内测码                                            │
│  - 创建TraderManager                                     │
│  - 启动API Server (Gin)                                  │
│  - 启动WebSocket市场数据监控                             │
└────────────────────┬────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
┌───────▼──────────┐    ┌─────────▼─────────┐
│ TraderManager    │    │  API Server (Gin) │
│ - 管理多个Trader │    │  - RESTful API    │
│ - 并发控制       │    │  - JWT认证        │
│ - 竞赛数据缓存   │    │  - CORS支持       │
└───────┬──────────┘    └─────────┬─────────┘
        │                         │
        │ goroutine               │ HTTP
        │                         │
┌───────▼──────────────────────────▼─────────┐
│          AutoTrader (每个交易员独立)        │
│  ┌─────────────────────────────────────┐   │
│  │ 1. 获取账户状态                      │   │
│  │ 2. 获取持仓信息                      │   │
│  │ 3. 获取市场数据 (market.Get)         │   │
│  │ 4. 分析历史表现 (logger)             │   │
│  │ 5. 构建Prompt (decision.engine)      │   │
│  │ 6. 调用AI API (mcp.AIClient)         │   │
│  │ 7. 解析决策 (JSON)                   │   │
│  │ 8. 验证风控                          │   │
│  │ 9. 执行交易 (Trader接口)             │   │
│  │ 10. 记录日志 (logger)                │   │
│  └─────────────────────────────────────┘   │
└────────────────────────────────────────────┘
```

### 1.2 核心设计理念

#### 1.2.1 单进程多goroutine

```go
// main.go - 启动多个交易员
for _, traderCfg := range traders {
    go autoTrader.Run()  // 每个交易员独立goroutine
}
```

**优势**：
- ✅ 轻量级并发（goroutine开销小）
- ✅ 共享内存（无需IPC）
- ✅ 简单部署（单二进制文件）

**劣势**：
- ⚠️ 单机限制（无法横向扩展）
- ⚠️ 故障影响全局（一个crash影响所有）

#### 1.2.2 SQLite单文件数据库

```go
// config/database.go
db, err := sql.Open("sqlite3", dbPath)
```

**表结构**：
```sql
-- 核心表
users               -- 用户账户
ai_models           -- AI模型配置
exchanges           -- 交易所凭证
traders             -- 交易员实例
equity_history      -- 权益历史
system_config       -- 系统配置
beta_codes          -- 内测码
token_blacklist     -- JWT黑名单
```

**优势**：
- ✅ 零配置（无需独立数据库服务）
- ✅ 易备份（单文件拷贝）
- ✅ 跨平台（嵌入式数据库）

**劣势**：
- ⚠️ 并发写入限制
- ⚠️ 不适合大规模部署

---

## 2. 核心模块深度分析

### 2.1 AutoTrader - 自动交易核心

#### 2.1.1 结构设计

```go
// trader/auto_trader.go
type AutoTrader struct {
    id                    string           // 唯一标识
    name                  string           // 显示名称
    aiModel               string           // AI模型
    exchange              string           // 交易所
    trader                Trader           // 交易接口
    mcpClient             mcp.AIClient     // AI客户端
    decisionLogger        logger.IDecisionLogger
    initialBalance        float64
    customPrompt          string           // 自定义Prompt
    systemPromptTemplate  string           // 模板名称
    positionFirstSeenTime map[string]int64 // 持仓跟踪
    peakPnLCache          map[string]float64 // 峰值盈亏
    // ... 更多字段
}
```

#### 2.1.2 决策循环（核心流程）

```go
// trader/auto_trader.go - Run()方法
func (at *AutoTrader) Run() {
    ticker := time.NewTicker(at.config.ScanInterval) // 默认3-5分钟
    
    for {
        select {
        case <-ticker.C:
            // 1. 获取账户状态
            balance, err := at.trader.GetBalance()
            
            // 2. 获取持仓
            positions, err := at.trader.GetPositions()
            
            // 3. 构建决策上下文
            ctx := &decision.Context{
                Account:        accountInfo,
                Positions:      positionInfos,
                CandidateCoins: candidateCoins,
                // ... 更多上下文
            }
            
            // 4. 获取AI决策
            fullDecision, err := decision.GetFullDecisionWithCustomPrompt(
                ctx, 
                at.mcpClient, 
                at.customPrompt,
                at.overrideBasePrompt,
                at.systemPromptTemplate,
            )
            
            // 5. 执行决策
            for _, dec := range fullDecision.Decisions {
                at.executeDecision(dec)
            }
            
            // 6. 记录日志
            at.decisionLogger.LogDecision(record)
            
        case <-at.stopMonitorCh:
            return
        }
    }
}
```

**关键点**：
- 每个交易员独立运行在goroutine中
- 3-5分钟决策周期（可配置）
- 完整的错误处理和日志记录
- 支持优雅停止

#### 2.1.3 风控验证

```go
// trader/auto_trader.go
func (at *AutoTrader) validateRisk(decision *decision.Decision) error {
    // 1. 检查仓位限制
    if positionSize > maxPosition {
        return fmt.Errorf("仓位超限")
    }
    
    // 2. 检查保证金使用率
    if marginUsed > 0.9 {
        return fmt.Errorf("保证金不足")
    }
    
    // 3. 检查风险收益比
    if riskRewardRatio < 1.0/2.0 {
        return fmt.Errorf("风险收益比不足")
    }
    
    // 4. 检查防重复持仓
    if hasPosition(symbol, side) {
        return fmt.Errorf("已有同向持仓")
    }
    
    return nil
}
```

### 2.2 Trader接口 - 统一交易抽象

#### 2.2.1 接口设计

```go
// trader/interface.go
type Trader interface {
    GetBalance() (map[string]interface{}, error)
    GetPositions() ([]map[string]interface{}, error)
    OpenLong(symbol string, quantity float64, leverage int) (map[string]interface{}, error)
    OpenShort(symbol string, quantity float64, leverage int) (map[string]interface{}, error)
    CloseLong(symbol string, quantity float64) (map[string]interface{}, error)
    CloseShort(symbol string, quantity float64) (map[string]interface{}, error)
    SetStopLoss(symbol string, positionSide string, quantity, stopPrice float64) error
    SetTakeProfit(symbol string, positionSide string, quantity, takeProfitPrice float64) error
    CancelStopLossOrders(symbol string) error
    CancelTakeProfitOrders(symbol string) error
    FormatQuantity(symbol string, quantity float64) (string, error)
}
```

**设计优势**：
- ✅ 统一的接口抽象
- ✅ 多交易所无缝切换
- ✅ 易于扩展新交易所

#### 2.2.2 实现示例 - Binance

```go
// trader/binance_futures.go
type FuturesTrader struct {
    client *futures.Client
    userID string
}

func (t *FuturesTrader) OpenLong(symbol string, quantity float64, leverage int) (map[string]interface{}, error) {
    // 1. 设置杠杆
    t.SetLeverage(symbol, leverage)
    
    // 2. 格式化数量
    quantityStr, _ := t.FormatQuantity(symbol, quantity)
    
    // 3. 下市价单
    order, err := t.client.NewCreateOrderService().
        Symbol(symbol).
        Side(futures.SideTypeBuy).
        Type(futures.OrderTypeMarket).
        Quantity(quantityStr).
        Do(context.Background())
    
    return map[string]interface{}{
        "orderId": order.OrderID,
        "price":   order.AvgPrice,
    }, nil
}
```

#### 2.2.3 实现示例 - Hyperliquid

```go
// trader/hyperliquid_trader.go
type HyperliquidTrader struct {
    privateKey string
    walletAddr string
    isTestnet  bool
    client     *http.Client
}

func (t *HyperliquidTrader) OpenLong(symbol string, quantity float64, leverage int) (map[string]interface{}, error) {
    // 1. 构建订单参数
    order := map[string]interface{}{
        "coin":     symbol,
        "is_buy":   true,
        "sz":       quantity,
        "limit_px": 0, // 市价单
        "reduce_only": false,
    }
    
    // 2. 签名订单
    signature := t.signOrder(order)
    
    // 3. 提交订单
    resp, err := t.submitOrder(order, signature)
    
    return resp, nil
}
```

**关键点**：
- 每个交易所独立实现Trader接口
- 自动处理精度问题
- 统一的错误处理

### 2.3 Decision Engine - AI决策引擎

#### 2.3.1 决策流程

```go
// decision/engine.go
func GetFullDecisionWithCustomPrompt(
    ctx *Context,
    mcpClient mcp.AIClient,
    customPrompt string,
    overrideBase bool,
    templateName string,
) (*FullDecision, error) {
    // 1. 获取市场数据
    fetchMarketDataForContext(ctx)
    
    // 2. 构建System Prompt
    systemPrompt := buildSystemPromptWithCustom(
        ctx.Account.TotalEquity,
        ctx.BTCETHLeverage,
        ctx.AltcoinLeverage,
        customPrompt,
        overrideBase,
        templateName,
    )
    
    // 3. 构建User Prompt
    userPrompt := buildUserPrompt(ctx)
    
    // 4. 调用AI API
    aiResponse, err := mcpClient.CallWithMessages(systemPrompt, userPrompt)
    
    // 5. 解析AI响应
    decision, err := parseFullDecisionResponse(aiResponse, ...)
    
    return decision, nil
}
```

#### 2.3.2 Prompt构建策略

```go
// decision/engine.go
func buildSystemPromptWithCustom(...) string {
    var systemPrompt string
    
    // 1. 加载模板
    if templateName != "" {
        template, _ := GetPromptTemplate(templateName)
        systemPrompt = template.Content
    } else {
        systemPrompt = defaultSystemPrompt
    }
    
    // 2. 注入动态参数
    systemPrompt = strings.ReplaceAll(systemPrompt, "{total_equity}", fmt.Sprintf("%.2f", totalEquity))
    systemPrompt = strings.ReplaceAll(systemPrompt, "{btc_eth_leverage}", fmt.Sprintf("%d", btcEthLeverage))
    
    // 3. 添加自定义Prompt
    if customPrompt != "" {
        if overrideBase {
            systemPrompt = customPrompt
        } else {
            systemPrompt += "\n\n" + customPrompt
        }
    }
    
    return systemPrompt
}
```

#### 2.3.3 User Prompt构建

```go
// decision/engine.go
func buildUserPrompt(ctx *Context) string {
    var sb strings.Builder
    
    // 1. 当前时间和运行状态
    sb.WriteString(fmt.Sprintf("Current Time: %s\n", ctx.CurrentTime))
    sb.WriteString(fmt.Sprintf("Runtime: %d minutes\n", ctx.RuntimeMinutes))
    
    // 2. 账户状态
    sb.WriteString(fmt.Sprintf("Account Equity: $%.2f\n", ctx.Account.TotalEquity))
    sb.WriteString(fmt.Sprintf("Available Balance: $%.2f\n", ctx.Account.AvailableBalance))
    
    // 3. 持仓信息
    if len(ctx.Positions) > 0 {
        sb.WriteString("\nCurrent Positions:\n")
        for _, pos := range ctx.Positions {
            sb.WriteString(fmt.Sprintf("- %s %s: %.4f @ $%.2f (PnL: %.2f%%)\n",
                pos.Symbol, pos.Side, pos.Quantity, pos.EntryPrice, pos.UnrealizedPnLPct))
        }
    }
    
    // 4. 候选币种及市场数据
    sb.WriteString("\nCandidate Coins:\n")
    for _, coin := range ctx.CandidateCoins {
        marketData := ctx.MarketDataMap[coin.Symbol]
        sb.WriteString(fmt.Sprintf("- %s: Price $%.4f, 1h: %.2f%%, 4h: %.2f%%\n",
            coin.Symbol, marketData.CurrentPrice, marketData.PriceChange1h, marketData.PriceChange4h))
        sb.WriteString(fmt.Sprintf("  EMA20: %.4f, MACD: %.4f, RSI7: %.2f\n",
            marketData.CurrentEMA20, marketData.CurrentMACD, marketData.CurrentRSI7))
    }
    
    // 5. 历史表现分析
    if ctx.Performance != nil {
        sb.WriteString("\nPerformance Analysis:\n")
        sb.WriteString(fmt.Sprintf("%+v\n", ctx.Performance))
    }
    
    return sb.String()
}
```

#### 2.3.4 AI响应解析

```go
// decision/engine.go
func parseFullDecisionResponse(aiResponse string, ...) (*FullDecision, error) {
    // 1. 提取思维链（CoT）
    cotTrace := extractReasoningTag(aiResponse)
    
    // 2. 提取决策JSON
    decisionJSON := extractDecisionTag(aiResponse)
    
    // 3. 解析JSON为决策列表
    var decisions []Decision
    if err := json.Unmarshal([]byte(decisionJSON), &decisions); err != nil {
        return nil, fmt.Errorf("解析决策JSON失败: %w", err)
    }
    
    // 4. 验证决策
    for _, dec := range decisions {
        if err := validateDecision(&dec, ...); err != nil {
            return nil, err
        }
    }
    
    return &FullDecision{
        CoTTrace:  cotTrace,
        Decisions: decisions,
        Timestamp: time.Now(),
    }, nil
}
```

**关键点**：
- 使用XML标签分离思维链和决策
- 支持多种JSON格式（容错性强）
- 完整的验证逻辑

### 2.4 Market Data - 市场数据服务

#### 2.4.1 数据结构

```go
// market/types.go
type Data struct {
    Symbol            string
    CurrentPrice      float64
    PriceChange1h     float64
    PriceChange4h     float64
    CurrentEMA20      float64
    CurrentMACD       float64
    CurrentRSI7       float64
    OpenInterest      *OIData
    FundingRate       float64
    IntradaySeries    *IntradayData    // 日内序列
    LongerTermContext *LongerTermData  // 长期数据
}

type IntradayData struct {
    MidPrices []float64  // 3分钟价格序列
    EMA20s    []float64  // EMA20序列
    MACDs     []float64  // MACD序列
    RSI7s     []float64  // RSI7序列
    RSI14s    []float64  // RSI14序列
    Volumes   []float64  // 成交量序列
}
```

#### 2.4.2 WebSocket实时数据

```go
// market/websocket_client.go
type WSMonitor struct {
    symbols     []string
    interval    string
    klineCache  map[string][]Kline
    mu          sync.RWMutex
}

func (m *WSMonitor) Start(customCoins []string) {
    // 1. 订阅所有币种的K线数据
    for _, symbol := range m.symbols {
        go m.subscribeKline(symbol, "3m")
        go m.subscribeKline(symbol, "4h")
    }
    
    // 2. 处理WebSocket消息
    for {
        select {
        case msg := <-m.msgChan:
            m.updateKlineCache(msg)
        }
    }
}
```

**特点**：
- ✅ WebSocket实时推送（低延迟）
- ✅ 本地缓存（减少API调用）
- ✅ 多时间周期支持

#### 2.4.3 技术指标计算

```go
// market/data.go
func calculateEMA(klines []Kline, period int) float64 {
    // 1. 计算SMA作为初始EMA
    sum := 0.0
    for i := 0; i < period; i++ {
        sum += klines[i].Close
    }
    ema := sum / float64(period)
    
    // 2. 计算EMA
    multiplier := 2.0 / float64(period+1)
    for i := period; i < len(klines); i++ {
        ema = (klines[i].Close-ema)*multiplier + ema
    }
    
    return ema
}

func calculateMACD(klines []Kline) float64 {
    ema12 := calculateEMA(klines, 12)
    ema26 := calculateEMA(klines, 26)
    return ema12 - ema26
}

func calculateRSI(klines []Kline, period int) float64 {
    // RSI计算逻辑
    // ...
}
```

### 2.5 Logger - 决策日志系统

#### 2.5.1 日志结构

```go
// logger/decision_logger.go
type DecisionRecord struct {
    Timestamp           time.Time
    CycleNumber         int
    SystemPrompt        string
    InputPrompt         string
    CoTTrace            string            // AI思维链
    DecisionJSON        string
    AccountState        AccountSnapshot
    Positions           []PositionSnapshot
    CandidateCoins      []string
    Decisions           []DecisionAction
    ExecutionLog        []string
    Success             bool
    ErrorMessage        string
    AIRequestDurationMs int64
}
```

#### 2.5.2 性能分析

```go
// logger/decision_logger.go
type PerformanceAnalysis struct {
    TotalTrades       int
    WinRate           float64
    AvgProfit         float64
    AvgLoss           float64
    ProfitLossRatio   float64
    BestAsset         string
    WorstAsset        string
    ConsecutiveLosses int
    SharpeRatio       float64  // 夏普比率
}

func (l *DecisionLogger) AnalyzePerformance(lookbackCycles int) (*PerformanceAnalysis, error) {
    // 1. 获取最近N个周期的记录
    records, _ := l.GetLatestRecords(lookbackCycles)
    
    // 2. 统计交易数据
    var totalTrades, winTrades int
    var totalProfit, totalLoss float64
    
    for _, record := range records {
        for _, action := range record.Decisions {
            if action.Action == "close_long" || action.Action == "close_short" {
                totalTrades++
                pnl := calculatePnL(action)
                if pnl > 0 {
                    winTrades++
                    totalProfit += pnl
                } else {
                    totalLoss += math.Abs(pnl)
                }
            }
        }
    }
    
    // 3. 计算指标
    winRate := float64(winTrades) / float64(totalTrades)
    avgProfit := totalProfit / float64(winTrades)
    avgLoss := totalLoss / float64(totalTrades-winTrades)
    profitLossRatio := avgProfit / avgLoss
    
    // 4. 计算夏普比率
    sharpeRatio := calculateSharpeRatio(records)
    
    return &PerformanceAnalysis{
        TotalTrades:     totalTrades,
        WinRate:         winRate,
        AvgProfit:       avgProfit,
        AvgLoss:         avgLoss,
        ProfitLossRatio: profitLossRatio,
        SharpeRatio:     sharpeRatio,
    }, nil
}
```

**特点**：
- ✅ 完整的决策记录（包含Prompt和CoT）
- ✅ 自动性能分析
- ✅ 夏普比率计算
- ✅ 最佳/最差资产识别

### 2.6 Prompt Manager - 提示词管理

#### 2.6.1 模板系统

```go
// decision/prompt_manager.go
type PromptTemplate struct {
    Name    string
    Content string
}

type PromptManager struct {
    templates map[string]*PromptTemplate
    mu        sync.RWMutex
}

func (pm *PromptManager) LoadTemplates(dir string) error {
    // 扫描prompts/目录下的所有.txt文件
    files, _ := filepath.Glob(filepath.Join(dir, "*.txt"))
    
    for _, file := range files {
        content, _ := os.ReadFile(file)
        templateName := strings.TrimSuffix(filepath.Base(file), ".txt")
        
        pm.templates[templateName] = &PromptTemplate{
            Name:    templateName,
            Content: string(content),
        }
    }
    
    return nil
}
```

#### 2.6.2 默认Prompt分析

```
prompts/default.txt 核心要点：

1. 核心目标：最大化夏普比率
   - 高质量交易（高胜率、大盈亏比）
   - 稳定收益、控制回撤
   - 耐心持仓、让利润奔跑

2. 交易频率认知：
   - 优秀交易员：每天2-4笔 = 每小时0.1-0.2笔
   - 过度交易：每小时>2笔 = 严重问题
   - 最佳节奏：开仓后持有至少30-60分钟

3. 开仓标准（严格）：
   - 综合信心度 ≥ 75 才开仓
   - 多维度交叉验证（价格+量+OI+指标+序列形态）
   - 避免低质量信号（单一维度、相互矛盾、横盘震荡）

4. 夏普比率自我进化：
   - 夏普 < -0.5：停止交易，连续观望至少6个周期
   - 夏普 -0.5 ~ 0：严格控制，只做信心度>80的交易
   - 夏普 0 ~ 0.7：维持当前策略
   - 夏普 > 0.7：可适度扩大仓位
```

**设计亮点**：
- ✅ 明确的量化标准（夏普比率）
- ✅ 交易频率控制（防止过度交易）
- ✅ 自适应策略（基于表现调整）
- ✅ 完整的风险意识

---

## 3. API设计分析

### 3.1 RESTful API架构

```go
// api/server.go
func (s *Server) setupRoutes() {
    api := s.router.Group("/api")
    
    // 公开接口（无需认证）
    api.GET("/health", s.handleHealth)
    api.GET("/supported-models", s.handleGetSupportedModels)
    api.GET("/supported-exchanges", s.handleGetSupportedExchanges)
    api.GET("/traders", s.handlePublicTraderList)
    api.GET("/competition", s.handlePublicCompetition)
    
    // 认证接口
    api.POST("/register", s.handleRegister)
    api.POST("/login", s.handleLogin)
    
    // 需要认证的接口
    protected := api.Group("/", s.authMiddleware())
    {
        protected.GET("/my-traders", s.handleTraderList)
        protected.POST("/traders", s.handleCreateTrader)
        protected.POST("/traders/:id/start", s.handleStartTrader)
        protected.POST("/traders/:id/stop", s.handleStopTrader)
        protected.GET("/models", s.handleGetModelConfigs)
        protected.PUT("/models", s.handleUpdateModelConfigs)
        protected.GET("/exchanges", s.handleGetExchangeConfigs)
        protected.PUT("/exchanges", s.handleUpdateExchangeConfigs)
    }
}
```

### 3.2 JWT认证机制

```go
// auth/auth.go
func GenerateJWT(userID string) (string, error) {
    claims := jwt.MapClaims{
        "user_id": userID,
        "exp":     time.Now().Add(24 * time.Hour).Unix(),
    }
    
    token := jwt.NewWithClaims(jwt.SigningMethodHS256, claims)
    return token.SignedString([]byte(jwtSecret))
}

func (s *Server) authMiddleware() gin.HandlerFunc {
    return func(c *gin.Context) {
        // 1. 提取Token
        authHeader := c.GetHeader("Authorization")
        tokenString := strings.TrimPrefix(authHeader, "Bearer ")
        
        // 2. 验证Token
        token, err := jwt.Parse(tokenString, func(token *jwt.Token) (interface{}, error) {
            return []byte(jwtSecret), nil
        })
        
        // 3. 检查黑名单
        if s.database.IsTokenBlacklisted(tokenString) {
            c.JSON(401, gin.H{"error": "Token已失效"})
            c.Abort()
            return
        }
        
        // 4. 设置用户ID到上下文
        claims := token.Claims.(jwt.MapClaims)
        c.Set("user_id", claims["user_id"])
        c.Next()
    }
}
```

### 3.3 竞赛数据API

```go
// api/server.go
func (s *Server) handlePublicCompetition(c *gin.Context) {
    // 1. 获取所有交易员状态
    traders := s.traderManager.GetAllTraders()
    
    // 2. 计算排行榜
    var leaderboard []map[string]interface{}
    for _, trader := range traders {
        equity := trader.GetCurrentEquity()
        roi := (equity - trader.InitialBalance) / trader.InitialBalance * 100
        
        leaderboard = append(leaderboard, map[string]interface{}{
            "id":       trader.ID,
            "name":     trader.Name,
            "ai_model": trader.AIModel,
            "exchange": trader.Exchange,
            "equity":   equity,
            "roi":      roi,
            "trades":   trader.TotalTrades,
            "win_rate": trader.WinRate,
        })
    }
    
    // 3. 按ROI排序
    sort.Slice(leaderboard, func(i, j int) bool {
        return leaderboard[i]["roi"].(float64) > leaderboard[j]["roi"].(float64)
    })
    
    c.JSON(200, gin.H{
        "leaderboard": leaderboard,
        "timestamp":   time.Now(),
    })
}
```

---

## 4. 前端架构分析

### 4.1 技术栈

```typescript
// package.json
{
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "react-router-dom": "^6.23.0",
    "recharts": "^2.15.0",      // 图表
    "swr": "^2.2.5",            // 数据获取
    "zustand": "^5.0.2",        // 状态管理
    "tailwindcss": "^3.4.1",    // CSS框架
    "lucide-react": "^0.344.0"  // 图标
  }
}
```

### 4.2 核心组件

#### 4.2.1 竞赛页面

```typescript
// web/src/components/CompetitionPage.tsx
export function CompetitionPage() {
  // 1. 数据获取（SWR自动轮询）
  const { data: traders } = useSWR('/api/traders', fetcher, {
    refreshInterval: 5000  // 5秒刷新
  })
  
  // 2. 排行榜渲染
  return (
    <div className="competition-container">
      <h1>AI Trading Competition</h1>
      
      {/* 排行榜 */}
      <div className="leaderboard">
        {traders.map((trader, index) => (
          <TraderCard
            key={trader.id}
            rank={index + 1}
            trader={trader}
          />
        ))}
      </div>
      
      {/* 对比图表 */}
      <ComparisonChart traders={traders} />
    </div>
  )
}
```

#### 4.2.2 权益曲线图

```typescript
// web/src/components/EquityChart.tsx
export function EquityChart({ traderId }: { traderId: string }) {
  const { data } = useSWR(`/api/equity-history?trader_id=${traderId}`, fetcher)
  
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <XAxis dataKey="timestamp" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="equity" stroke="#8884d8" />
      </LineChart>
    </ResponsiveContainer>
  )
}
```

#### 4.2.3 对比图表

```typescript
// web/src/components/ComparisonChart.tsx
export function ComparisonChart({ traders }: { traders: Trader[] }) {
  return (
    <ResponsiveContainer width="100%" height={400}>
      <LineChart>
        <XAxis dataKey="timestamp" />
        <YAxis />
        <Tooltip />
        {traders.map((trader, index) => (
          <Line
            key={trader.id}
            type="monotone"
            dataKey={`roi_${trader.id}`}
            stroke={COLORS[index]}
            name={trader.name}
          />
        ))}
      </LineChart>
    </ResponsiveContainer>
  )
}
```

### 4.3 状态管理（Zustand）

```typescript
// web/src/stores/useAuthStore.ts
import create from 'zustand'

interface AuthState {
  user: User | null
  token: string | null
  login: (username: string, password: string) => Promise<void>
  logout: () => void
}

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  token: localStorage.getItem('token'),
  
  login: async (username, password) => {
    const response = await fetch('/api/login', {
      method: 'POST',
      body: JSON.stringify({ username, password })
    })
    const data = await response.json()
    
    set({ user: data.user, token: data.token })
    localStorage.setItem('token', data.token)
  },
  
  logout: () => {
    set({ user: null, token: null })
    localStorage.removeItem('token')
  }
}))
```

---

## 5. 核心优势总结

### 5.1 技术优势

1. **轻量级架构**：
   - Go单进程 + SQLite
   - 资源占用低（~50-100MB/交易员）
   - 部署简单（单二进制文件）

2. **统一交易接口**：
   - 清晰的接口抽象
   - 多交易所无缝切换
   - 易于扩展

3. **完整的决策系统**：
   - Prompt模板管理
   - 思维链记录
   - 性能分析

4. **实时竞赛系统**：
   - 多模型对比
   - 实时排行榜
   - 权益曲线

### 5.2 设计亮点

1. **Prompt工程**：
   - 模板化管理
   - 热加载支持
   - 夏普比率导向

2. **风控设计**：
   - 仓位限制
   - 保证金管理
   - 风险收益比
   - 防重复持仓

3. **日志系统**：
   - 完整的决策记录
   - 自动性能分析
   - JSON格式存储

4. **Web界面**：
   - Binance风格UI
   - 实时数据更新
   - 响应式设计

---

## 6. 可改进点分析

### 6.1 架构层面

1. **单机限制**：
   - 问题：无法横向扩展
   - 建议：引入分布式架构（Kubernetes）

2. **SQLite并发**：
   - 问题：写入并发有限
   - 建议：大规模场景使用PostgreSQL

3. **错误恢复**：
   - 问题：单进程crash影响全局
   - 建议：引入进程监控和自动重启

### 6.2 功能层面

1. **测试覆盖**：
   - 问题：测试覆盖率不足
   - 建议：增加单元测试和集成测试

2. **监控告警**：
   - 问题：缺少系统级监控
   - 建议：集成Prometheus + Grafana

3. **回测系统**：
   - 问题：无历史数据回测
   - 建议：增加回测模块

### 6.3 安全层面

1. **API密钥管理**：
   - 问题：数据库明文存储（虽有加密服务）
   - 建议：使用Vault等密钥管理服务

2. **访问控制**：
   - 问题：权限控制相对简单
   - 建议：引入RBAC

---

## 7. 对AIcoin的启示

### 7.1 可直接借鉴

1. **统一交易接口**：
   ```python
   # 参考NOFX的Trader接口设计
   class TraderInterface(ABC):
       @abstractmethod
       async def open_long(self, symbol, quantity, leverage): pass
       
       @abstractmethod
       async def open_short(self, symbol, quantity, leverage): pass
       
       @abstractmethod
       async def close_position(self, symbol, side): pass
   ```

2. **Prompt模板系统**：
   ```python
   # 实现类似的模板管理
   class PromptManager:
       def __init__(self, templates_dir="prompts"):
           self.templates = {}
           self.load_templates(templates_dir)
       
       def load_templates(self, dir):
           for file in glob.glob(f"{dir}/*.txt"):
               name = os.path.basename(file).replace(".txt", "")
               self.templates[name] = open(file).read()
   ```

3. **性能分析系统**：
   ```python
   # 借鉴夏普比率计算
   class PerformanceAnalyzer:
       def calculate_sharpe_ratio(self, returns):
           return np.mean(returns) / np.std(returns)
   ```

### 7.2 需要适配

1. **多模型竞赛**：
   - NOFX：多个独立交易员
   - AIcoin：集成到辩论系统

2. **决策流程**：
   - NOFX：单AI决策
   - AIcoin：多AI辩论 → 最终决策

3. **记忆系统**：
   - NOFX：文件日志
   - AIcoin：三层记忆（Redis + PostgreSQL + Qdrant）

### 7.3 差异化保持

1. **辩论系统**：AIcoin的核心优势，NOFX没有
2. **权限管理**：AIcoin的企业级RBAC，NOFX相对简单
3. **记忆检索**：AIcoin的向量检索，NOFX没有

---

## 8. 实施建议

### 8.1 短期（1-2周）

1. **统一交易接口**：
   - 重构AIcoin的交易服务
   - 参考NOFX的接口设计
   - 支持多交易所统一调用

2. **Prompt模板系统**：
   - 实现模板管理器
   - 支持热加载
   - 集成到决策引擎

### 8.2 中期（1-2月）

1. **多模型对比**：
   - 在辩论系统中集成多模型观点
   - 实现性能对比功能
   - 添加排行榜

2. **性能分析**：
   - 引入夏普比率计算
   - 实现自动性能分析
   - 优化决策反馈

### 8.3 长期（3-6月）

1. **混合架构**：
   - Go服务处理高频交易
   - Python服务处理复杂逻辑
   - 统一API网关

2. **完整竞赛系统**：
   - 实现类似NOFX的竞赛功能
   - 集成到AIcoin的辩论系统
   - 多模型自进化

---

## 9. 参考资料

1. **NOFX项目**：
   - GitHub: https://github.com/tinkle-community/nofx
   - 本地路径: `/Users/xinghailong/Documents/soft/nofx/`

2. **核心文件**：
   - 主程序: `main.go`
   - 交易核心: `trader/auto_trader.go`
   - 决策引擎: `decision/engine.go`
   - 交易接口: `trader/interface.go`
   - API服务: `api/server.go`

3. **文档**：
   - 架构文档: `docs/architecture/README.zh-CN.md`
   - 部署指南: `docs/getting-started/README.zh-CN.md`

---

**文档结束**

---

## 附录：核心代码片段

### A. 决策循环核心逻辑

```go
// trader/auto_trader.go - 简化版
func (at *AutoTrader) Run() {
    ticker := time.NewTicker(at.config.ScanInterval)
    
    for {
        select {
        case <-ticker.C:
            // 1. 获取账户和持仓
            balance, _ := at.trader.GetBalance()
            positions, _ := at.trader.GetPositions()
            
            // 2. 构建上下文
            ctx := &decision.Context{
                Account:   accountInfo,
                Positions: positionInfos,
                // ...
            }
            
            // 3. AI决策
            fullDecision, _ := decision.GetFullDecision(ctx, at.mcpClient)
            
            // 4. 执行决策
            for _, dec := range fullDecision.Decisions {
                at.executeDecision(dec)
            }
            
            // 5. 记录日志
            at.decisionLogger.LogDecision(record)
        }
    }
}
```

### B. 统一交易接口

```go
// trader/interface.go
type Trader interface {
    GetBalance() (map[string]interface{}, error)
    GetPositions() ([]map[string]interface{}, error)
    OpenLong(symbol string, quantity float64, leverage int) (map[string]interface{}, error)
    OpenShort(symbol string, quantity float64, leverage int) (map[string]interface{}, error)
    CloseLong(symbol string, quantity float64) (map[string]interface{}, error)
    CloseShort(symbol string, quantity float64) (map[string]interface{}, error)
}
```

### C. Prompt模板加载

```go
// decision/prompt_manager.go
func (pm *PromptManager) LoadTemplates(dir string) error {
    files, _ := filepath.Glob(filepath.Join(dir, "*.txt"))
    
    for _, file := range files {
        content, _ := os.ReadFile(file)
        templateName := strings.TrimSuffix(filepath.Base(file), ".txt")
        
        pm.templates[templateName] = &PromptTemplate{
            Name:    templateName,
            Content: string(content),
        }
    }
    
    return nil
}
```

