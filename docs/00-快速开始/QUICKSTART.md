# 🚀 AIcoin v2.0 快速启动指南

> **当前状态**: ✅ 测试网已启动并运行  
> **创建时间**: 2025-10-31  
> **适用版本**: v2.0-alpha

---

## 📊 当前系统状态

```bash
# 快速检查
curl -s http://localhost:8000/health | python3 -m json.tool

# 预期输出:
# - status: "healthy"
# - ai_orchestrator: true
# - permission_level: "L1"
# - decision_interval: 300秒 (5分钟)
```

---

## 🎯 核心命令速查

### 系统管理

```bash
# 启动系统（使用.env.testnet配置）
docker-compose -f deploy/docker-compose.testnet.yml --env-file .env.testnet up -d

# 停止系统
docker-compose -f deploy/docker-compose.testnet.yml --env-file .env.testnet down

# 重启backend
docker-compose -f deploy/docker-compose.testnet.yml --env-file .env.testnet restart backend

# 紧急停止（关闭所有并提醒手动平仓）
./scripts/stop_system_emergency.sh
```

### 日志查看

```bash
# 实时查看所有日志
docker-compose -f deploy/docker-compose.testnet.yml --env-file .env.testnet logs -f backend

# 只看决策日志
docker-compose -f deploy/docker-compose.testnet.yml --env-file .env.testnet logs backend | grep "决策"

# 只看权限变化
docker-compose -f deploy/docker-compose.testnet.yml --env-file .env.testnet logs backend | grep "权限"

# 只看错误
docker-compose -f deploy/docker-compose.testnet.yml --env-file .env.testnet logs backend | grep "ERROR"

# 只看emoji标记的关键信息
docker-compose -f deploy/docker-compose.testnet.yml --env-file .env.testnet logs backend | grep -E "(🔄|✅|❌|⚠️|🤖)"
```

### 监控工具

```bash
# 实时监控系统（推荐）
./scripts/monitor_system.sh

# 后台告警监控
./scripts/alert_config.sh daemon &

# 查看告警日志
tail -f logs/alerts.log

# API端点测试
./scripts/test_api_endpoints.sh
```

### API访问

```bash
# 健康检查
curl http://localhost:8000/health | python3 -m json.tool

# 系统状态
curl http://localhost:8000/api/v1/status | python3 -m json.tool

# 持仓信息
curl http://localhost:8000/api/v1/account/positions | python3 -m json.tool

# API文档（浏览器打开）
open http://localhost:8000/docs

# Qdrant Dashboard
open http://localhost:6333/dashboard
```

---

## ⚙️  配置管理

### 修改决策频率

```bash
# 编辑配置
vim .env.testnet

# 修改这一行
DECISION_INTERVAL=300  # 改为你想要的秒数（如180=3分钟）

# 重启生效
docker-compose -f deploy/docker-compose.testnet.yml --env-file .env.testnet restart backend
```

### 启用/禁用AI决策

```bash
# 编辑配置
vim .env.testnet

# 修改这一行
TRADING_ENABLED=true   # true=启用AI决策，false=禁用

# 完全重启生效
docker-compose -f deploy/docker-compose.testnet.yml --env-file .env.testnet down
docker-compose -f deploy/docker-compose.testnet.yml --env-file .env.testnet up -d
```

### 修改初始权限等级

```bash
# 编辑配置
vim .env.testnet

# 修改这一行
INITIAL_PERMISSION_LEVEL=L1  # L1-L5，L1最保守

# 重启生效
docker-compose -f deploy/docker-compose.testnet.yml --env-file .env.testnet restart backend
```

---

## 📈 理解AI决策过程

### 决策循环（每5分钟）

```
🔄 第N次决策循环
   ↓
📊 获取市场数据
   ↓
💼 获取账户状态
   ↓
🤖 调用DecisionEngineV2
   ├─ 🔑 权限检查（L0-L5）
   ├─ 🧠 加载记忆数据
   ├─ 📝 构建Prompt
   ├─ 🤖 调用AI模型
   ├─ 📊 解析AI响应
   ├─ 🔍 软约束验证（置信度、频率）
   ├─ 🛡️  硬约束验证（8项红线）
   ├─ 🔐 权限验证
   └─ 📝 记录决策
   ↓
✅ 决策通过 → 执行交易
❌ 决策拒绝 → 继续观察
```

### 决策结果类型

| 结果 | 说明 | 日志标记 |
|------|------|---------|
| ✅ APPROVED | 决策通过，执行交易 | `✅ 决策通过` |
| ❌ REJECTED | 决策拒绝（软约束） | `❌ 软约束拒绝` |
| 🚫 REJECTED | 决策拒绝（硬约束） | `🚫 硬约束拒绝` |
| 🔒 REJECTED | 决策拒绝（权限限制） | `🔒 权限限制拒绝` |
| 🚨 FORCED | 强制平仓（风控触发） | `🚨 触发强制平仓` |

---

## 🎯 权限等级说明

| 等级 | 名称 | 单仓位 | 杠杆 | 置信度 | 日频率 |
|------|------|--------|------|--------|--------|
| L0 | 保护模式 | 0% | 1x | 100% | 0 |
| **L1** | **新手级** | **10%** | **2x** | **80%** | **1次** |
| L2 | 成长级 | 12% | 2x | 75% | 2次 |
| L3 | 稳定级 | 15% | 3x | 70% | 4次 |
| L4 | 熟练级 | 20% | 4x | 65% | 6次 |
| L5 | 专家级 | 25% | 5x | 60% | 无限 |

**当前等级**: L1（最保守，适合测试）

---

## 🔍 故障排查

### 问题1: AI Orchestrator未启动

**症状**: `"ai_orchestrator": false`

**解决**:
```bash
# 检查TRADING_ENABLED
grep TRADING_ENABLED .env.testnet

# 确保是true
sed -i '' 's/TRADING_ENABLED=false/TRADING_ENABLED=true/' .env.testnet

# 完全重启
docker-compose -f docker-compose.testnet.yml --env-file .env.testnet down
docker-compose -f docker-compose.testnet.yml --env-file .env.testnet up -d
```

### 问题2: 决策一直被拒绝

**症状**: `❌ 软约束拒绝: 置信度不足`

**原因**: AI置信度 < 权限要求阈值

**解决**:
- 正常现象，说明风控在工作
- L1要求80%置信度，非常保守
- 可以降低等级或等待高置信度机会
- 查看完整决策理由：`grep "reasoning" logs/backend.log`

### 问题3: Redis错误

**症状**: `'RedisClient' object has no attribute 'zadd'`

**原因**: Redis客户端方法调用问题

**临时影响**: 记忆系统部分功能受影响，但核心决策正常

**解决**: 需要修复代码，但不影响测试

### 问题4: 容器无法启动

**症状**: 容器反复重启

**解决**:
```bash
# 查看错误日志
docker-compose -f deploy/docker-compose.testnet.yml --env-file .env.testnet logs backend | tail -50

# 重新构建镜像
docker-compose -f deploy/docker-compose.testnet.yml build --no-cache backend

# 重启所有
docker-compose -f deploy/docker-compose.testnet.yml --env-file .env.testnet down
docker-compose -f deploy/docker-compose.testnet.yml --env-file .env.testnet up -d
```

---

## 📚 相关文档

| 文档 | 用途 |
|------|------|
| `README.md` | 项目总览 |
| `docs/00-文档导航.md` | 文档导航 |
| `docs/01-核心规则/AI交易规则文档.md` | AI交易规则 |
| `docs/03-技术架构/README.md` | 技术架构说明 |
| `docs/07-部署运维/测试网部署指南.md` | 详细部署步骤 |
| `docs/08-前端系统/README.md` | 前端系统说明 |
| `docs/09-API接口文档/README.md` | API接口文档 |

---

## ⚠️  重要提醒

### 当前是测试网环境

- ✅ **安全**: 测试网代币无价值，可以放心测试
- ✅ **真实**: 连接真实的Hyperliquid测试网
- ⚠️  **限制**: 测试网性能可能不稳定
- ⚠️  **数据**: 测试网数据可能被重置

### 上主网前必须

- [ ] 测试网稳定运行至少7天
- [ ] AI决策逻辑合理，无明显错误
- [ ] 风控系统正常触发
- [ ] 权限升降级机制正常
- [ ] 理解所有配置参数的含义
- [ ] 准备好小资金试运行（$100起步）

---

## 💡 最佳实践

### 1. 持续监控（前24小时）

```bash
# 开一个终端实时监控
./scripts/monitor_system.sh

# 开另一个终端查看日志
docker-compose -f deploy/docker-compose.testnet.yml --env-file .env.testnet logs -f backend

# 定期检查健康状态
watch -n 60 'curl -s http://localhost:8000/health | python3 -m json.tool'
```

### 2. 定期检查告警

```bash
# 每小时检查一次告警日志
tail -20 logs/alerts.log

# 或启动后台监控
./scripts/alert_config.sh daemon &
```

### 3. 记录重要事件

```bash
# 创建测试日志
echo "$(date): 系统启动，开始观察" >> logs/test_journal.log
echo "$(date): AI做出首次决策" >> logs/test_journal.log
echo "$(date): 发现问题: XXX" >> logs/test_journal.log
```

### 4. 定期备份配置

```bash
# 备份当前配置
cp .env.testnet .env.testnet.backup.$(date +%Y%m%d)

# 备份重要日志
cp logs/alerts.log logs/alerts.log.backup.$(date +%Y%m%d)
```

---

## 🆘 紧急情况处理

### 如果系统失控

```bash
# 1. 立即停止Docker
./scripts/stop_system_emergency.sh

# 2. 手动登录Hyperliquid平仓
open https://app.hyperliquid-testnet.xyz/

# 3. 查看日志找原因
docker-compose -f deploy/docker-compose.testnet.yml --env-file .env.testnet logs backend > emergency_log.txt

# 4. 保存配置快照
cp .env.testnet emergency_config.backup
```

### 联系支持

如有严重问题：
1. 保存所有日志文件
2. 记录复现步骤
3. 截图系统状态
4. 查阅文档寻找解决方案

---

## ✅ 系统就绪检查清单

使用前请确认：

- [ ] Docker容器全部运行中
- [ ] `curl http://localhost:8000/health` 返回 `"status": "healthy"`
- [ ] `ai_orchestrator: true` (如果TRADING_ENABLED=true)
- [ ] API文档可访问 (http://localhost:8000/docs)
- [ ] 理解当前权限等级限制
- [ ] 知道如何紧急停止
- [ ] 已设置监控脚本
- [ ] 已准备好查看日志

---

## 🎉 开始测试！

系统已就绪，可以开始观察AI的决策过程！

**建议的测试流程**:
1. 运行 `./scripts/monitor_system.sh` 持续监控
2. 观察AI每5分钟的决策
3. 记录任何异常行为
4. 24小时后评估系统稳定性
5. 根据表现决定下一步

**祝测试顺利！** 🚀

---

**文档版本**: v2.0  
**最后更新**: 2025-10-31  
**下次更新**: 根据测试反馈

