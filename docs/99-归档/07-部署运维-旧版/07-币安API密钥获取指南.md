# 币安API密钥获取指南

## 📋 目录
- [前置要求](#前置要求)
- [获取API密钥步骤](#获取api密钥步骤)
- [配置权限](#配置权限)
- [安全设置](#安全设置)
- [配置到系统](#配置到系统)
- [测试连接](#测试连接)

---

## 前置要求

1. ✅ 已注册币安账户
2. ✅ 已完成KYC身份验证
3. ✅ 已开启双重验证(2FA)

---

## 获取API密钥步骤

### 1. 登录币安账户

访问: https://www.binance.com/

### 2. 进入API管理页面

**方式一: 通过账户菜单**
1. 点击右上角头像
2. 选择 **"API Management"** (API管理)

**方式二: 直接访问**
- 现货API: https://www.binance.com/zh-CN/my/settings/api-management
- 合约API: https://www.binance.com/zh-CN/futures/account/api-management

### 3. 创建API密钥

#### 步骤详解:

1. **点击"创建API"按钮**
   - 选择 **"系统生成"** (推荐)
   - 或 **"自主生成"** (高级用户)

2. **设置API标签**
   ```
   标签名称: AIcoin Trading Bot
   ```

3. **完成安全验证**
   - 输入邮箱验证码
   - 输入手机验证码
   - 输入Google Authenticator验证码(如已开启)

4. **获取密钥**
   ```
   API Key: 类似 "vmPUZE6mv9SD5VNHk4HlWFsOr6aKE2zvsw0MuIgwCIPy6utIco14y7Ju91duEh8A"
   Secret Key: 类似 "NhqPtmdSJYdKjVHjA7PZj4Mge3R5YNiP1e3UZjInClVN65XAbvqqM6A7H5fATj0j"
   ```

   ⚠️ **重要**: Secret Key只显示一次,请立即保存!

---

## 配置权限

### 推荐权限配置

根据您的使用场景选择:

#### 场景1: 只读模式(查看账户/市场数据)
```
✅ Enable Reading (启用读取)
❌ Enable Spot & Margin Trading (禁用现货交易)
❌ Enable Futures (禁用合约)
❌ Enable Withdrawals (禁用提现)
```

#### 场景2: 现货交易模式
```
✅ Enable Reading (启用读取)
✅ Enable Spot & Margin Trading (启用现货交易)
❌ Enable Futures (禁用合约)
❌ Enable Withdrawals (禁用提现)
```

#### 场景3: 合约交易模式(推荐用于AI交易)
```
✅ Enable Reading (启用读取)
❌ Enable Spot & Margin Trading (禁用现货交易)
✅ Enable Futures (启用合约)
❌ Enable Withdrawals (禁用提现)
```

⚠️ **安全建议**: 
- **永远不要**启用 "Enable Withdrawals" (提现权限)
- 只启用必需的权限

---

## 安全设置

### 1. IP白名单(强烈推荐)

**设置步骤:**
1. 在API管理页面找到 **"IP访问限制"**
2. 选择 **"限制访问受信任的IP"**
3. 添加您的服务器IP地址

**获取服务器IP:**
```bash
# 本地开发
curl ifconfig.me

# 远程服务器
ssh user@your-server
curl ifconfig.me
```

**示例配置:**
```
允许的IP:
- 123.45.67.89 (生产服务器)
- 98.76.54.32 (备用服务器)
```

### 2. 其他安全设置

- ✅ 设置API有效期(可选)
- ✅ 定期轮换密钥(建议每3个月)
- ✅ 监控API使用情况
- ✅ 启用异常活动通知

---

## 配置到系统

### 方法1: 环境变量配置(推荐)

#### 1. 编辑 `.env` 文件

```bash
cd /Users/xinghailong/Documents/soft/AIcoin
nano .env
```

#### 2. 添加币安配置

```bash
# ==========================================
# 币安交易所配置
# ==========================================

# 币安API密钥
BINANCE_API_KEY=your_binance_api_key_here
BINANCE_API_SECRET=your_binance_secret_key_here

# 币安网络配置
BINANCE_TESTNET=false  # true=测试网, false=主网
BINANCE_BASE_URL=https://api.binance.com  # 主网API地址

# 币安合约配置(如果使用合约)
BINANCE_FUTURES_BASE_URL=https://fapi.binance.com
```

#### 3. 保存并重启服务

```bash
# 重启后端
docker restart aicoin-backend

# 或重启整个系统
docker-compose restart
```

### 方法2: 通过管理后台配置

1. 访问: `http://localhost:3002/admin/exchanges`
2. 点击 **"添加交易所"**
3. 选择 **"Binance"**
4. 填写API密钥
5. 点击 **"测试连接"**
6. 保存配置

---

## 测试连接

### 方法1: 使用测试脚本

创建测试文件 `test_binance_connection.py`:

```python
import os
from binance.client import Client

# 从环境变量读取
api_key = os.getenv('BINANCE_API_KEY')
api_secret = os.getenv('BINANCE_API_SECRET')

# 创建客户端
client = Client(api_key, api_secret)

try:
    # 测试连接
    account = client.get_account()
    print("✅ 币安API连接成功!")
    print(f"账户类型: {account['accountType']}")
    print(f"是否可交易: {account['canTrade']}")
    
    # 获取余额
    balances = [b for b in account['balances'] if float(b['free']) > 0]
    print(f"\n💰 账户余额:")
    for balance in balances:
        print(f"  {balance['asset']}: {balance['free']}")
        
except Exception as e:
    print(f"❌ 连接失败: {e}")
```

运行测试:
```bash
python test_binance_connection.py
```

### 方法2: 使用curl测试

```bash
# 设置变量
API_KEY="your_api_key"
API_SECRET="your_api_secret"
TIMESTAMP=$(date +%s000)

# 生成签名
QUERY_STRING="timestamp=${TIMESTAMP}"
SIGNATURE=$(echo -n "${QUERY_STRING}" | openssl dgst -sha256 -hmac "${API_SECRET}" | cut -d' ' -f2)

# 测试请求
curl -H "X-MBX-APIKEY: ${API_KEY}" \
  "https://api.binance.com/api/v3/account?${QUERY_STRING}&signature=${SIGNATURE}"
```

---

## 常见问题

### Q1: API密钥无效
**解决方案:**
- 检查是否复制完整(包括所有字符)
- 确认API密钥状态为"已启用"
- 检查IP白名单设置

### Q2: 权限不足错误
**解决方案:**
- 检查API权限配置
- 确认已启用对应的交易权限
- 重新生成API密钥并配置正确权限

### Q3: 连接超时
**解决方案:**
- 检查网络连接
- 确认服务器可以访问币安API
- 检查防火墙设置

### Q4: 签名错误
**解决方案:**
- 检查系统时间是否同步
- 确认Secret Key正确
- 检查请求参数顺序

---

## 安全最佳实践

### ✅ 推荐做法

1. **使用专用API密钥**
   - 为每个应用创建独立的API密钥
   - 便于管理和撤销

2. **最小权限原则**
   - 只启用必需的权限
   - 禁用提现权限

3. **IP白名单**
   - 限制只有特定IP可以使用
   - 定期审查白名单

4. **定期轮换**
   - 每3个月更换一次密钥
   - 发现异常立即更换

5. **安全存储**
   - 使用环境变量,不要硬编码
   - 不要提交到Git仓库
   - 使用密钥管理服务

### ❌ 避免做法

1. ❌ 启用提现权限
2. ❌ 不设置IP白名单
3. ❌ 将密钥硬编码在代码中
4. ❌ 将密钥提交到Git
5. ❌ 使用同一密钥在多个地方
6. ❌ 长期不更换密钥

---

## 相关链接

- 币安API文档: https://binance-docs.github.io/apidocs/
- 币安API管理: https://www.binance.com/zh-CN/my/settings/api-management
- 币安安全中心: https://www.binance.com/zh-CN/my/security

---

## 下一步

配置完成后,您可以:

1. ✅ 测试API连接
2. ✅ 配置交易参数
3. ✅ 启动AI交易系统
4. ✅ 监控交易活动

参考文档:
- [交易所配置指南](./04-交易所配置指南.md)
- [主网操作指南](./03-主网操作指南.md)

