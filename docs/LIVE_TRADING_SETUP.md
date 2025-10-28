# 🔴 实盘交易配置指南

## ⚠️ 重要警告

**实盘交易涉及真实资金，请务必谨慎操作！**

- ❌ 不要在不理解的情况下启用实盘
- ❌ 不要将私钥提交到Git或分享给他人
- ❌ 不要在未测试的情况下投入大额资金
- ✅ 建议先在测试网充分测试
- ✅ 建议设置合理的风险限额
- ✅ 建议人工监督AI决策

---

## 📋 当前系统状态

### ✅ 已实现的真实数据
- **市场价格**: Hyperliquid API 真实数据
- **K线数据**: Hyperliquid API 真实历史数据
- **行情更新**: 每5秒实时更新

### ❌ 当前模拟的数据
- **账户余额**: 模拟的 $21,571.52
- **持仓信息**: 模拟的持仓数据
- **交易记录**: 模拟的交易历史
- **AI交易**: 不执行真实交易

---

## 🔑 需要准备的信息

### 1. Hyperliquid 钱包私钥 (必需)
- **用途**: 签名交易、查询真实账户
- **格式**: `0x` 开头的64位十六进制字符串
- **示例**: `0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef`
- **获取方式**: 
  - 从MetaMask等钱包导出
  - 使用Hyperliquid官网创建
  - 使用命令行工具生成

### 2. Hyperliquid 钱包地址 (必需)
- **用途**: 账户识别、查询余额和持仓
- **格式**: 以太坊地址格式
- **示例**: `0xABCDEF1234567890ABCDEF1234567890ABCDEF12`

### 3. DeepSeek API Key (可选 - AI交易)
- **用途**: AI自动交易决策
- **获取**: https://platform.deepseek.com
- **格式**: `sk-xxxxxx`
- **价格**: 约 $0.14/1M tokens (input), $0.28/1M tokens (output)

### 4. Qwen API Key (可选 - AI交易)
- **用途**: AI自动交易决策
- **获取**: https://dashscope.aliyuncs.com
- **格式**: `sk-xxxxxx`
- **已有**: `sk-cfe26fffcd564dab9e6fea61481551d1`

---

## ⚙️ 配置步骤

### 第一步: 创建 .env 文件

```bash
cd /Users/xinghailong/Documents/soft/AIcoin
cp env.example .env
```

### 第二步: 编辑 .env 文件

使用文本编辑器打开 `.env` 文件，填入以下信息：

```bash
# ==================== Hyperliquid 配置 ====================
# 你的 Hyperliquid 钱包地址
HYPERLIQUID_WALLET_ADDRESS=0xYourWalletAddressHere

# 你的 Hyperliquid 钱包私钥 (⚠️ 务必保密!)
HYPERLIQUID_PRIVATE_KEY=0xYourPrivateKeyHere

# 是否使用测试网 (建议先用测试网测试)
# true = 测试网 (不使用真实资金)
# false = 主网 (使用真实资金)
HYPERLIQUID_TESTNET=true

# ==================== AI 配置 (可选) ====================
# DeepSeek API Key (用于AI决策)
DEEPSEEK_API_KEY=your_deepseek_api_key_here

# Qwen API Key (用于AI决策)
QWEN_API_KEY=sk-cfe26fffcd564dab9e6fea61481551d1

# ==================== 交易控制 ====================
# 是否启用真实交易执行
# false = 只显示AI决策，不执行交易
# true = AI决策会执行真实交易
TRADING_ENABLED=false

# ==================== 数据库配置 ====================
DB_PASSWORD=changeme123

# ==================== 安全密钥 ====================
SECRET_KEY=your-secret-key-change-in-production
```

### 第三步: 重启服务

```bash
# 停止所有服务
docker-compose down

# 重新启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f backend
```

---

## 🧪 测试流程

### 阶段1: 测试网测试 (推荐)

1. **配置测试网**
   ```bash
   HYPERLIQUID_TESTNET=true
   TRADING_ENABLED=false
   ```

2. **验证账户连接**
   ```bash
   curl http://localhost:8000/api/v1/hyperliquid/account
   ```
   应该返回你的真实账户信息

3. **检查持仓**
   ```bash
   curl http://localhost:8000/api/v1/hyperliquid/positions
   ```

4. **手动测试下单** (通过API文档)
   - 访问 http://localhost:8000/docs
   - 测试 `/api/v1/hyperliquid/orders` 端点

### 阶段2: 只读模式 (主网)

1. **切换到主网，但不启用交易**
   ```bash
   HYPERLIQUID_TESTNET=false
   TRADING_ENABLED=false
   ```

2. **验证真实账户数据**
   - 查看真实余额
   - 查看真实持仓
   - 观察AI决策但不执行

### 阶段3: 启用实盘交易 (⚠️ 谨慎)

1. **小额测试**
   ```bash
   HYPERLIQUID_TESTNET=false
   TRADING_ENABLED=true
   ```

2. **修改风险参数** (后面详细说明)

3. **监控运行**
   - 实时查看日志
   - 监控交易执行
   - 随时准备停止

---

## 🛡️ 风险管理配置

### 修改风险参数

编辑 `backend/app/services/hyperliquid_trading.py`:

```python
class HyperliquidTradingService:
    def __init__(self, redis_client: RedisClient, testnet: bool = True):
        # ... 其他代码 ...
        
        # ============ 风险控制参数 ============
        self.max_daily_trades = 100        # 每日最大交易次数
        self.max_risk_per_trade = 100.0    # 单笔最大风险金额 ($)
        self.max_position_size = 1000.0    # 最大持仓金额 ($)
        self.stop_loss_percentage = 0.02   # 止损比例 (2%)
        self.take_profit_percentage = 0.05 # 止盈比例 (5%)
```

### 建议参数配置

**保守配置** (小额测试):
```python
self.max_daily_trades = 10
self.max_risk_per_trade = 50.0
self.max_position_size = 200.0
self.stop_loss_percentage = 0.01  # 1%
```

**中等配置** (小规模运营):
```python
self.max_daily_trades = 50
self.max_risk_per_trade = 200.0
self.max_position_size = 1000.0
self.stop_loss_percentage = 0.02  # 2%
```

**激进配置** (⚠️ 高风险):
```python
self.max_daily_trades = 100
self.max_risk_per_trade = 500.0
self.max_position_size = 5000.0
self.stop_loss_percentage = 0.03  # 3%
```

---

## 📝 获取Hyperliquid钱包

### 方法1: 使用现有钱包 (MetaMask)

1. 打开 MetaMask
2. 点击账户详情
3. 点击 "Export Private Key"
4. 输入密码确认
5. 复制私钥和地址

### 方法2: 创建新钱包 (Hyperliquid官网)

1. 访问 https://app.hyperliquid.xyz
2. 点击 "Connect Wallet"
3. 选择 "Create New Wallet"
4. 保存助记词和私钥
5. 转入资金

### 方法3: 使用Python生成

```python
from eth_account import Account

# 创建新账户
account = Account.create()

print(f"地址: {account.address}")
print(f"私钥: {account.key.hex()}")

# ⚠️ 请妥善保存这些信息！
```

---

## 💰 资金建议

### 测试阶段
- **测试网**: 免费，无需真实资金
- **主网小额**: $100-$500 (熟悉系统)

### 正式运营
- **小规模**: $1,000-$5,000
- **中等规模**: $5,000-$20,000
- **大规模**: $20,000+

### 资金分配建议
- 70% 用于交易
- 20% 作为保证金缓冲
- 10% 应急备用金

---

## 🚨 紧急停止

### 如何立即停止所有交易

1. **停止AI自动交易**
   ```bash
   curl -X POST http://localhost:8000/api/v1/hyperliquid/ai/stop
   ```

2. **关闭系统**
   ```bash
   docker-compose down
   ```

3. **修改配置**
   ```bash
   # 编辑 .env
   TRADING_ENABLED=false
   ```

4. **取消所有订单** (通过Hyperliquid官网)
   - 访问 https://app.hyperliquid.xyz
   - 手动取消所有订单
   - 平仓所有持仓

---

## 📊 监控和日志

### 实时监控

1. **查看后端日志**
   ```bash
   docker logs -f aicoin-backend
   ```

2. **查看AI状态**
   ```bash
   curl http://localhost:8000/api/v1/hyperliquid/ai/status
   ```

3. **查看账户状态**
   ```bash
   curl http://localhost:8000/api/v1/hyperliquid/account
   ```

4. **查看持仓**
   ```bash
   curl http://localhost:8000/api/v1/hyperliquid/positions
   ```

### 关键指标监控

- ✅ 账户余额变化
- ✅ 持仓数量和盈亏
- ✅ 交易成功率
- ✅ AI决策准确度
- ✅ 风险指标

---

## ⚡ 快速启动实盘 (Checklist)

- [ ] 1. 准备好Hyperliquid钱包私钥和地址
- [ ] 2. 钱包有足够资金 (建议$100以上测试)
- [ ] 3. 创建 .env 文件并填入信息
- [ ] 4. 先在测试网测试 (`HYPERLIQUID_TESTNET=true`)
- [ ] 5. 验证账户连接成功
- [ ] 6. 手动测试下单功能
- [ ] 7. 切换到主网但不启用交易 (`TRADING_ENABLED=false`)
- [ ] 8. 观察AI决策是否合理
- [ ] 9. 调整风险参数
- [ ] 10. 启用小额实盘 (`TRADING_ENABLED=true`)
- [ ] 11. 密切监控运行状况
- [ ] 12. 随时准备紧急停止

---

## 🔒 安全最佳实践

### 私钥安全
- ✅ 使用硬件钱包存储主要资金
- ✅ 只在交易钱包中保留必要资金
- ✅ 定期备份私钥到安全位置
- ✅ 使用强密码保护服务器
- ❌ 不要将私钥提交到Git
- ❌ 不要在公共网络输入私钥
- ❌ 不要截图或拍照私钥

### 系统安全
- ✅ 使用防火墙限制服务器访问
- ✅ 定期更新系统和依赖
- ✅ 监控异常登录和访问
- ✅ 启用2FA认证
- ❌ 不要在公共云上运行实盘
- ❌ 不要使用弱密码

### 交易安全
- ✅ 设置合理的止损
- ✅ 不要投入超过承受能力的资金
- ✅ 分散风险，不要全仓一个币种
- ✅ 定期检查AI决策质量
- ❌ 不要追高杀跌
- ❌ 不要情绪化交易

---

## 📞 技术支持

### 常见问题

**Q: 私钥格式错误？**
A: 确保私钥以 `0x` 开头，且是64位十六进制字符串

**Q: 账户连接失败？**
A: 检查钱包地址和私钥是否正确，网络是否可访问Hyperliquid

**Q: AI不执行交易？**
A: 检查 `TRADING_ENABLED` 是否为 `true`

**Q: 如何测试不用真实资金？**
A: 设置 `HYPERLIQUID_TESTNET=true` 使用测试网

### 获取帮助

如果遇到问题，可以：
1. 查看后端日志: `docker logs aicoin-backend`
2. 查看API文档: http://localhost:8000/docs
3. 检查配置文件: `.env`

---

## ⚠️ 免责声明

**本系统仅供学习和研究使用。使用本系统进行实盘交易所产生的任何盈利或亏损，均由使用者自行承担。**

- 加密货币交易存在高风险
- AI决策可能出现错误
- 市场波动可能导致重大损失
- 请务必做好风险管理
- 建议咨询专业人士

---

## 📚 相关文档

- [Hyperliquid官方文档](https://hyperliquid.gitbook.io/)
- [API文档](http://localhost:8000/docs)
- [风险管理策略](./05-风控策略研究.md)
- [AI交易策略研究](./02-AI交易策略研究.md)

---

**最后更新**: 2025-10-27  
**版本**: 1.0.0

