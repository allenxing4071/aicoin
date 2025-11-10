# SSH 服务器连接配置管理

## 📋 目录说明

本目录统一管理 AIcoin 项目所有服务器的 SSH 连接配置，包括内网服务器和云服务器。

```
ssh-configs/
├── README.md                    # 本文件
├── templates/                   # 配置模板（纳入版本控制）
│   ├── connection-template.txt  # 连接信息模板
│   ├── ssh-config-template      # SSH config 模板
│   └── cloud-server-setup.md    # 云服务器初始化指南
├── local-servers/               # 内网服务器配置（不纳入版本控制）
│   ├── dev-server/              # 开发服务器
│   └── test-server/             # 测试服务器
└── cloud-servers/               # 云服务器配置（不纳入版本控制）
    ├── aliyun/                  # 阿里云
    ├── tencent/                 # 腾讯云
    ├── aws/                     # AWS
    └── other/                   # 其他云平台
```

---

## 🔒 安全说明

### Git 版本控制策略

- ✅ **纳入版本控制**：
  - `ssh-configs/README.md`（本文件）
  - `ssh-configs/templates/`（所有模板文件）

- ❌ **不纳入版本控制**（已在 `.gitignore` 中配置）：
  - `ssh-configs/local-servers/`（所有内网服务器配置）
  - `ssh-configs/cloud-servers/`（所有云服务器配置）

### 文件权限要求

```bash
# 私钥文件必须设置为 600
chmod 600 ssh-configs/*/*/*.pem

# 公钥文件可以是 644
chmod 644 ssh-configs/*/*/*.pem.pub

# 连接信息文件建议 600
chmod 600 ssh-configs/*/*/连接信息.txt
```

---

## 🚀 快速开始

### 1. 添加新的内网服务器

```bash
# 创建服务器目录
mkdir -p ssh-configs/local-servers/your-server-name

# 复制模板
cp ssh-configs/templates/connection-template.txt \
   ssh-configs/local-servers/your-server-name/连接信息.txt

# 编辑连接信息
vim ssh-configs/local-servers/your-server-name/连接信息.txt

# 复制私钥文件（如果有）
cp ~/path/to/your-key.pem \
   ssh-configs/local-servers/your-server-name/

# 设置权限
chmod 600 ssh-configs/local-servers/your-server-name/*.pem
```

### 2. 添加新的云服务器

```bash
# 创建云服务器目录（以阿里云为例）
mkdir -p ssh-configs/cloud-servers/aliyun/prod-server-01

# 复制模板
cp ssh-configs/templates/connection-template.txt \
   ssh-configs/cloud-servers/aliyun/prod-server-01/连接信息.txt

# 编辑连接信息
vim ssh-configs/cloud-servers/aliyun/prod-server-01/连接信息.txt

# 复制密钥文件
cp ~/path/to/aliyun-key.pem \
   ssh-configs/cloud-servers/aliyun/prod-server-01/

# 设置权限
chmod 600 ssh-configs/cloud-servers/aliyun/prod-server-01/*.pem
```

### 3. 配置 SSH Config

编辑 `~/.ssh/config`：

```bash
# 内网开发服务器
Host dev-server
    HostName 192.168.31.185
    User allenxing07
    Port 22
    IdentityFile ~/Documents/soft/AIcoin/ssh-configs/local-servers/dev-server/dev-server-key.pem
    ServerAliveInterval 60
    ServerAliveCountMax 3

# 阿里云生产服务器
Host aliyun-prod
    HostName your.aliyun.ip
    User root
    Port 22
    IdentityFile ~/Documents/soft/AIcoin/ssh-configs/cloud-servers/aliyun/prod-server-01/aliyun-key.pem
    ServerAliveInterval 60
    ServerAliveCountMax 3
```

然后可以简化连接：

```bash
ssh dev-server
ssh aliyun-prod
```

---

## 📁 目录结构详解

### local-servers/ - 内网服务器

用于存放局域网内的开发、测试服务器配置。

**典型场景**：
- 开发环境服务器
- 测试环境服务器
- 内网数据库服务器
- 办公室内部服务器

**命名规范**：
```
local-servers/
├── dev-server/          # 开发服务器
├── test-server/         # 测试服务器
├── staging-server/      # 预发布服务器
└── db-server/           # 数据库服务器
```

### cloud-servers/ - 云服务器

用于存放云平台上的生产、备份服务器配置。

**按云平台分类**：
```
cloud-servers/
├── aliyun/              # 阿里云
│   ├── prod-web-01/     # 生产Web服务器1
│   ├── prod-web-02/     # 生产Web服务器2
│   └── prod-db-01/      # 生产数据库服务器
├── tencent/             # 腾讯云
│   ├── backup-01/       # 备份服务器
│   └── cdn-01/          # CDN节点
├── aws/                 # AWS
│   └── global-01/       # 全球节点
└── other/               # 其他云平台
    └── custom-01/       # 自定义服务器
```

**命名规范**：
- 使用小写字母和连字符
- 包含用途和编号：`{purpose}-{type}-{number}`
- 例如：`prod-web-01`、`backup-db-02`

### templates/ - 配置模板

提供标准化的配置模板，纳入版本控制，团队共享。

**包含文件**：
- `connection-template.txt` - 连接信息标准模板
- `ssh-config-template` - SSH config 配置模板
- `cloud-server-setup.md` - 云服务器初始化指南
- `security-checklist.md` - 安全配置检查清单

---

## 🛡️ 安全最佳实践

### 1. 密钥管理

- ✅ 每个服务器使用独立的密钥对
- ✅ 定期轮换密钥（建议 3-6 个月）
- ✅ 将密钥备份到安全的密码管理器
- ❌ 不要在多个服务器间共用同一密钥
- ❌ 不要通过邮件或聊天工具传输私钥

### 2. 文件权限

```bash
# 检查所有私钥权限
find ssh-configs -name "*.pem" -exec ls -l {} \;

# 批量修正权限
find ssh-configs -name "*.pem" -exec chmod 600 {} \;
```

### 3. 访问控制

- 生产服务器使用独立的密钥
- 限制可以访问生产服务器的人员
- 记录所有密钥的分发情况
- 离职人员立即轮换相关密钥

### 4. 审计日志

在服务器端启用 SSH 审计：

```bash
# 查看 SSH 登录日志
sudo tail -f /var/log/auth.log  # Ubuntu/Debian
sudo tail -f /var/log/secure    # CentOS/RHEL
```

---

## 🔧 常用操作

### 连接服务器

```bash
# 使用 SSH config 别名
ssh dev-server

# 直接使用密钥文件
ssh -i ssh-configs/local-servers/dev-server/dev-server-key.pem user@host
```

### 文件传输

```bash
# 上传文件
scp -i ssh-configs/local-servers/dev-server/dev-server-key.pem \
    local-file.txt user@host:~/

# 下载文件
scp -i ssh-configs/local-servers/dev-server/dev-server-key.pem \
    user@host:~/remote-file.txt ./

# 上传目录
scp -r -i ssh-configs/local-servers/dev-server/dev-server-key.pem \
    local-folder/ user@host:~/
```

### 端口转发

```bash
# 本地端口转发（访问远程服务）
ssh -i ssh-configs/local-servers/dev-server/dev-server-key.pem \
    -L 8080:localhost:3000 user@host

# 远程端口转发（让远程访问本地）
ssh -i ssh-configs/local-servers/dev-server/dev-server-key.pem \
    -R 9000:localhost:3000 user@host
```

### 批量操作

```bash
# 批量连接测试
for server in dev-server test-server prod-server; do
    echo "Testing $server..."
    ssh -o ConnectTimeout=5 $server "echo OK" || echo "Failed: $server"
done

# 批量执行命令
for server in dev-server test-server; do
    ssh $server "uptime"
done
```

---

## 📊 服务器清单

### 内网服务器

| 服务器名称 | IP 地址 | 用途 | 状态 | 负责人 |
|-----------|---------|------|------|--------|
| dev-server | 192.168.31.185 | 开发环境 | ✅ 运行中 | - |
| test-server | - | 测试环境 | ⏸️ 待配置 | - |

### 云服务器

| 云平台 | 服务器名称 | IP 地址 | 用途 | 状态 | 负责人 |
|--------|-----------|---------|------|------|--------|
| 阿里云 | - | - | 生产环境 | ⏸️ 待部署 | - |
| 腾讯云 | - | - | 备份环境 | ⏸️ 待部署 | - |

> 💡 **提示**：请在添加新服务器后更新此清单

---

## 🔄 密钥轮换流程

### 定期轮换（每 3-6 个月）

```bash
# 1. 在服务器上生成新密钥对
ssh-keygen -t rsa -b 4096 -f ~/.ssh/new-key-$(date +%Y%m%d) -m PEM

# 2. 添加新公钥到 authorized_keys
cat ~/.ssh/new-key-*.pub >> ~/.ssh/authorized_keys

# 3. 下载新私钥到本地
scp user@host:~/.ssh/new-key-* ssh-configs/local-servers/dev-server/

# 4. 测试新密钥
ssh -i ssh-configs/local-servers/dev-server/new-key-* user@host

# 5. 更新 SSH config

# 6. 删除服务器上的旧公钥（从 authorized_keys 中移除）

# 7. 归档旧密钥
mkdir -p ssh-configs/archived/
mv ssh-configs/local-servers/dev-server/old-key* ssh-configs/archived/
```

### 紧急轮换（密钥泄露）

```bash
# 1. 立即在服务器上删除泄露的公钥
ssh user@host "sed -i '/leaked-key-fingerprint/d' ~/.ssh/authorized_keys"

# 2. 生成新密钥
ssh-keygen -t rsa -b 4096 -f ssh-configs/local-servers/dev-server/emergency-key -m PEM

# 3. 通过其他方式（如云平台控制台）添加新公钥

# 4. 测试连接

# 5. 检查服务器日志是否有异常访问
```

---

## 📖 相关文档

- [敏感信息管理规范](../docs/07-部署运维/00-敏感信息管理规范.md)
- [远程服务器部署手册](../docs/07-部署运维/06-远程服务器部署手册.md)
- [服务器连接配置模板](../docs/07-部署运维/10-服务器连接配置模板.md)
- [云平台配置快速参考表](../docs/07-部署运维/09-云平台配置快速参考表.md)

---

## ❓ 常见问题

### Q1: 为什么要将 SSH 配置放在项目根目录？

**A**: 
- 便于团队成员快速找到服务器连接信息
- 统一管理内网和云服务器配置
- 与项目代码保持关联，方便部署操作
- 通过 `.gitignore` 保护敏感信息

### Q2: 如何在团队中共享服务器访问权限？

**A**:
1. 为每个团队成员生成独立的密钥对
2. 将所有成员的公钥添加到服务器的 `authorized_keys`
3. 通过安全方式（如加密 U盘）分发私钥
4. 记录密钥分发情况

### Q3: 云服务器和内网服务器配置有什么区别？

**A**:
- **内网服务器**：通常使用固定 IP，访问速度快，安全性依赖内网隔离
- **云服务器**：使用公网 IP，需要更严格的安全配置（防火墙、安全组）
- **建议**：云服务器禁用密码登录，只允许密钥认证

### Q4: 如何备份 SSH 配置？

**A**:
```bash
# 备份整个 ssh-configs 目录（排除模板）
tar -czf ssh-configs-backup-$(date +%Y%m%d).tar.gz \
    --exclude='ssh-configs/templates' \
    ssh-configs/

# 加密备份（推荐）
tar -czf - ssh-configs/ | openssl enc -aes-256-cbc -salt -out ssh-configs-backup.tar.gz.enc

# 解密恢复
openssl enc -aes-256-cbc -d -in ssh-configs-backup.tar.gz.enc | tar -xzf -
```

---

## ✅ 检查清单

在添加新服务器配置前，请确认：

- [ ] 已创建对应的服务器目录
- [ ] 已从模板复制配置文件
- [ ] 已填写完整的连接信息
- [ ] 私钥文件权限设置为 600
- [ ] 已在 `~/.ssh/config` 中添加配置
- [ ] 已测试 SSH 连接成功
- [ ] 已更新本文档的服务器清单
- [ ] 已将私钥备份到安全位置

---

*最后更新: 2025-11-10*  
*版本: v1.0*  
*维护者: AIcoin 团队*

