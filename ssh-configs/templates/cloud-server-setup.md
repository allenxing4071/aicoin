# 云服务器初始化指南

## 📋 概述

本文档提供云服务器（阿里云、腾讯云、AWS 等）的标准化初始化流程，确保服务器安全、高效地运行 AIcoin 项目。

---

## 🎯 初始化检查清单

- [ ] 服务器已创建并获得公网 IP
- [ ] SSH 密钥已生成并配置
- [ ] 安全组/防火墙规则已配置
- [ ] 已记录服务器信息到 `ssh-configs/`
- [ ] 已测试 SSH 连接成功

---

## 🚀 快速开始

### 阶段 1：购买和基础配置（云平台控制台）

#### 1.1 选择服务器配置

**开发/测试环境推荐**：
- CPU: 2核
- 内存: 4GB
- 硬盘: 40GB SSD
- 带宽: 3Mbps
- 操作系统: Ubuntu 22.04 LTS

**生产环境推荐**：
- CPU: 4核+
- 内存: 8GB+
- 硬盘: 100GB SSD+
- 带宽: 5Mbps+
- 操作系统: Ubuntu 22.04 LTS

#### 1.2 配置 SSH 密钥

**方式 A：使用云平台生成的密钥**

1. 在创建服务器时选择"创建新密钥对"
2. 下载私钥文件（如 `aliyun-key.pem`）
3. 移动到项目目录：
```bash
mv ~/Downloads/aliyun-key.pem \
   ~/Documents/soft/AIcoin/ssh-configs/cloud-servers/aliyun/prod-server-01/
chmod 600 ~/Documents/soft/AIcoin/ssh-configs/cloud-servers/aliyun/prod-server-01/aliyun-key.pem
```

**方式 B：使用自己生成的密钥**

```bash
# 1. 生成密钥对
ssh-keygen -t rsa -b 4096 \
  -f ~/Documents/soft/AIcoin/ssh-configs/cloud-servers/aliyun/prod-server-01/aliyun-key.pem \
  -C "aliyun-prod-$(date +%Y%m%d)" \
  -m PEM

# 2. 在云平台控制台导入公钥
cat ~/Documents/soft/AIcoin/ssh-configs/cloud-servers/aliyun/prod-server-01/aliyun-key.pem.pub

# 3. 创建服务器时选择导入的公钥
```

#### 1.3 配置安全组/防火墙

**必须开放的端口**：
- 22 (SSH) - 限制来源 IP
- 80 (HTTP)
- 443 (HTTPS)

**可选端口**（仅开发/测试环境）：
- 3000 (前端开发服务器)
- 8000 (后端 API)

**禁止开放的端口**（仅内网访问）：
- 5432 (PostgreSQL)
- 6379 (Redis)

---

### 阶段 2：首次登录和系统配置

#### 2.1 首次 SSH 连接

```bash
# 使用下载的私钥连接
ssh -i ~/Documents/soft/AIcoin/ssh-configs/cloud-servers/aliyun/prod-server-01/aliyun-key.pem \
    root@your_server_ip

# 或配置 SSH config 后简化连接
ssh aliyun-prod-01
```

#### 2.2 更新系统

```bash
# Ubuntu/Debian
sudo apt update
sudo apt upgrade -y
sudo apt autoremove -y

# CentOS/RHEL
sudo yum update -y
sudo yum autoremove -y
```

#### 2.3 设置时区

```bash
# 查看当前时区
timedatectl

# 设置为中国时区
sudo timedatectl set-timezone Asia/Shanghai

# 验证
date
```

#### 2.4 配置主机名

```bash
# 设置主机名
sudo hostnamectl set-hostname aliyun-prod-01

# 编辑 hosts 文件
sudo vim /etc/hosts
# 添加：
# 127.0.0.1 aliyun-prod-01

# 验证
hostname
```

---

### 阶段 3：创建非 root 用户（推荐）

```bash
# 创建新用户
sudo adduser aicoin
sudo usermod -aG sudo aicoin  # Ubuntu
sudo usermod -aG wheel aicoin # CentOS

# 为新用户配置 SSH 密钥
sudo mkdir -p /home/aicoin/.ssh
sudo cp ~/.ssh/authorized_keys /home/aicoin/.ssh/
sudo chown -R aicoin:aicoin /home/aicoin/.ssh
sudo chmod 700 /home/aicoin/.ssh
sudo chmod 600 /home/aicoin/.ssh/authorized_keys

# 测试新用户登录
ssh -i ~/Documents/soft/AIcoin/ssh-configs/cloud-servers/aliyun/prod-server-01/aliyun-key.pem \
    aicoin@your_server_ip

# 禁用 root SSH 登录（在确认新用户可以登录后）
sudo vim /etc/ssh/sshd_config
# 修改：PermitRootLogin no
sudo systemctl restart sshd
```

---

### 阶段 4：SSH 安全加固

#### 4.1 配置 SSH

```bash
sudo vim /etc/ssh/sshd_config
```

**推荐配置**：

```bash
# 基础安全
Port 22                           # 可以改为非标准端口
Protocol 2                        # 使用 SSH 协议版本 2
PermitRootLogin no                # 禁止 root 直接登录

# 认证方式
PubkeyAuthentication yes          # 启用公钥认证
PasswordAuthentication no         # 禁用密码登录
PermitEmptyPasswords no           # 禁止空密码
ChallengeResponseAuthentication no

# 连接限制
MaxAuthTries 3                    # 最多 3 次登录尝试
MaxSessions 10                    # 最多 10 个并发会话
LoginGraceTime 60                 # 登录超时 60 秒

# 保持连接
ClientAliveInterval 300           # 5 分钟发送一次心跳
ClientAliveCountMax 2             # 最多 2 次心跳失败

# 其他安全选项
X11Forwarding no                  # 禁用 X11 转发
AllowTcpForwarding yes            # 允许 TCP 转发（Docker 需要）
AllowAgentForwarding no           # 禁用 SSH agent 转发
```

**重启 SSH 服务**：

```bash
# 验证配置
sudo sshd -t

# 重启服务
sudo systemctl restart sshd

# 确保 SSH 开机自启
sudo systemctl enable sshd
```

#### 4.2 配置防火墙（UFW）

```bash
# 安装 UFW
sudo apt install ufw -y

# 默认策略
sudo ufw default deny incoming
sudo ufw default allow outgoing

# 允许 SSH（重要：先允许 SSH，否则会被锁定）
sudo ufw allow 22/tcp
# 或限制来源 IP
sudo ufw allow from your_office_ip to any port 22

# 允许 HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 启用防火墙
sudo ufw enable

# 查看状态
sudo ufw status verbose
```

---

### 阶段 5：安装必要软件

#### 5.1 安装 Docker

```bash
# 安装 Docker
curl -fsSL https://get.docker.com | sudo sh

# 将当前用户添加到 docker 组
sudo usermod -aG docker $USER

# 启动 Docker
sudo systemctl start docker
sudo systemctl enable docker

# 验证安装
docker --version
docker run hello-world
```

#### 5.2 安装 Docker Compose

```bash
# 下载最新版本
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" \
  -o /usr/local/bin/docker-compose

# 添加执行权限
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker-compose --version
```

#### 5.3 安装其他工具

```bash
# 基础工具
sudo apt install -y \
  git \
  vim \
  curl \
  wget \
  htop \
  net-tools \
  unzip \
  tree

# 监控工具
sudo apt install -y \
  iotop \
  iftop \
  nethogs
```

---

### 阶段 6：配置 Swap（可选，内存较小时推荐）

```bash
# 检查是否已有 swap
sudo swapon --show
free -h

# 创建 4GB swap 文件
sudo fallocate -l 4G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 永久启用
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 优化 swap 使用
sudo sysctl vm.swappiness=10
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf

# 验证
free -h
```

---

### 阶段 7：部署 AIcoin 项目

#### 7.1 克隆项目

```bash
# 创建项目目录
mkdir -p ~/projects
cd ~/projects

# 克隆仓库
git clone https://github.com/your-org/AIcoin.git
cd AIcoin
```

#### 7.2 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
vim .env

# 填入真实的 API 密钥和配置
```

#### 7.3 启动服务

```bash
# 构建镜像
docker-compose build

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 检查服务状态
docker-compose ps
```

#### 7.4 验证部署

```bash
# 检查后端 API
curl http://localhost:8000/api/health

# 检查前端
curl http://localhost:3000

# 查看数据库
docker-compose exec postgres psql -U postgres -d aicoin
```

---

### 阶段 8：配置域名和 SSL（生产环境）

#### 8.1 配置域名解析

在域名服务商处添加 A 记录：
```
api.yourdomain.com  -> your_server_ip
www.yourdomain.com  -> your_server_ip
```

#### 8.2 安装 Nginx

```bash
sudo apt install nginx -y
sudo systemctl start nginx
sudo systemctl enable nginx
```

#### 8.3 配置 SSL（Let's Encrypt）

```bash
# 安装 Certbot
sudo apt install certbot python3-certbot-nginx -y

# 获取 SSL 证书
sudo certbot --nginx -d api.yourdomain.com -d www.yourdomain.com

# 自动续期
sudo certbot renew --dry-run
```

#### 8.4 配置 Nginx 反向代理

```bash
sudo vim /etc/nginx/sites-available/aicoin
```

```nginx
server {
    listen 80;
    server_name api.yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/api.yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.yourdomain.com/privkey.pem;

    # API
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 前端
    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

```bash
# 启用配置
sudo ln -s /etc/nginx/sites-available/aicoin /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl reload nginx
```

---

### 阶段 9：监控和日志

#### 9.1 配置日志轮转

```bash
sudo vim /etc/logrotate.d/aicoin
```

```
/home/aicoin/projects/AIcoin/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    notifempty
    create 0640 aicoin aicoin
    sharedscripts
    postrotate
        docker-compose restart > /dev/null
    endscript
}
```

#### 9.2 设置监控告警

```bash
# 安装监控脚本
cp scripts/monitor/monitor_system.sh ~/
chmod +x ~/monitor_system.sh

# 添加到 crontab
crontab -e
# 添加：每 5 分钟检查一次
*/5 * * * * ~/monitor_system.sh
```

---

### 阶段 10：备份策略

#### 10.1 数据库备份

```bash
# 创建备份脚本
vim ~/backup_db.sh
```

```bash
#!/bin/bash
BACKUP_DIR="/home/aicoin/backups"
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份数据库
docker-compose exec -T postgres pg_dump -U postgres aicoin | \
  gzip > $BACKUP_DIR/aicoin_db_$DATE.sql.gz

# 保留最近 7 天的备份
find $BACKUP_DIR -name "aicoin_db_*.sql.gz" -mtime +7 -delete

echo "Backup completed: aicoin_db_$DATE.sql.gz"
```

```bash
chmod +x ~/backup_db.sh

# 添加到 crontab（每天凌晨 2 点备份）
crontab -e
# 添加：
0 2 * * * ~/backup_db.sh
```

#### 10.2 文件备份

```bash
# 备份配置文件
tar -czf ~/backups/config_$(date +%Y%m%d).tar.gz \
  ~/projects/AIcoin/.env \
  ~/projects/AIcoin/docker-compose.yml
```

---

## ✅ 验证检查清单

完成初始化后，请逐项检查：

### 系统安全
- [ ] SSH 密钥认证正常工作
- [ ] 已禁用密码登录
- [ ] 已禁用 root 直接登录
- [ ] 防火墙已启用并正确配置
- [ ] 安全组规则已配置

### 服务状态
- [ ] Docker 运行正常
- [ ] Docker Compose 运行正常
- [ ] AIcoin 所有服务启动成功
- [ ] 数据库连接正常
- [ ] Redis 连接正常

### 网络配置
- [ ] 公网 IP 可以访问
- [ ] 域名解析正确（如果配置了域名）
- [ ] SSL 证书有效（如果配置了 HTTPS）
- [ ] Nginx 反向代理工作正常

### 监控和备份
- [ ] 日志轮转配置正确
- [ ] 监控脚本运行正常
- [ ] 数据库备份脚本测试成功
- [ ] 备份文件可以正常恢复

---

## 📖 相关文档

- [SSH 配置管理](../README.md)
- [部署指南](../../docs/07-部署运维/01-部署指南.md)
- [远程服务器部署手册](../../docs/07-部署运维/06-远程服务器部署手册.md)
- [敏感信息管理规范](../../docs/07-部署运维/00-敏感信息管理规范.md)

---

## 🆘 故障排查

### 问题 1: SSH 连接被拒绝

**可能原因**：
- 安全组未开放 22 端口
- 防火墙阻止了连接
- SSH 服务未启动

**解决方法**：
```bash
# 在云平台控制台检查安全组
# 通过 VNC 登录服务器检查 SSH 状态
sudo systemctl status sshd
sudo systemctl start sshd
```

### 问题 2: Docker 容器无法启动

**可能原因**：
- 端口被占用
- 环境变量配置错误
- 磁盘空间不足

**解决方法**：
```bash
# 检查端口占用
sudo netstat -tulpn | grep :8000

# 查看详细日志
docker-compose logs backend

# 检查磁盘空间
df -h
```

### 问题 3: 无法访问服务

**可能原因**：
- 防火墙未开放端口
- Nginx 配置错误
- 服务未启动

**解决方法**：
```bash
# 检查服务状态
docker-compose ps

# 检查 Nginx 配置
sudo nginx -t

# 检查防火墙
sudo ufw status
```

---

*最后更新: 2025-11-10*  
*版本: v1.0*  
*维护者: AIcoin 团队*

