# BotBot 生产环境部署指南

本文档描述如何在生产环境部署 BotBot，使用 Nginx 反向代理和 SSL/TLS 证书。

## 📋 前置要求

- 服务器：Ubuntu 20.04+ / CentOS 8+ / Debian 11+
- Docker 20.10+
- Docker Compose 2.0+
- 域名：botbot.biz（指向服务器 IP）
- 开放端口：80（HTTP）、443（HTTPS）

## 🚀 快速部署

### 1. 准备服务器

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y  # Ubuntu/Debian
# 或
sudo yum update -y  # CentOS

# 安装 Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 安装 Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```

### 2. 克隆项目

```bash
git clone https://github.com/your-org/botbot.git
cd botbot
```

### 3. 配置环境变量

```bash
# 创建生产环境配置
cp be/.env.example be/.env.prod
vim be/.env.prod
```

**最小必需配置**：
```bash
# 数据库
MONGODB_URL=mongodb://mongodb:27017
MONGODB_DB_NAME=botbot

# 安全密钥（重要：使用强随机密钥）
SECRET_KEY=<生成的强随机密钥>
JWT_SECRET_KEY=<生成的强随机密钥>

# AI 服务
ANTHROPIC_API_KEY=<你的 Anthropic API Key>

# 短信服务（阿里云）
ALIYUN_ACCESS_KEY_ID=<你的 Access Key ID>
ALIYUN_ACCESS_KEY_SECRET=<你的 Access Key Secret>
ALIYUN_SMS_SIGN_NAME=<短信签名>
ALIYUN_SMS_TEMPLATE_CODE=<短信模板代码>

# API URL
NEXT_PUBLIC_API_URL=https://botbot.biz
```

**生成强随机密钥**：
```bash
# 使用 OpenSSL 生成
openssl rand -hex 32

# 或使用 Python
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 4. 配置 SSL 证书

#### 方式 A：Let's Encrypt（推荐，免费）

```bash
# 安装 Certbot
sudo apt install certbot  # Ubuntu/Debian
sudo yum install certbot  # CentOS

# 停止可能占用 80 端口的服务
sudo systemctl stop nginx  # 如果有
docker-compose -f docker-compose.prod.yml down  # 如果已启动

# 获取证书
sudo certbot certonly --standalone \
  -d botbot.biz \
  -d www.botbot.biz \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email

# 证书位置：/etc/letsencrypt/live/botbot.biz/

# 复制证书到项目目录
sudo cp /etc/letsencrypt/live/botbot.biz/fullchain.pem nginx/certs/botbot.biz.crt
sudo cp /etc/letsencrypt/live/botbot.biz/privkey.pem nginx/certs/botbot.biz.key
sudo chown $USER:$USER nginx/certs/botbot.biz.*
chmod 600 nginx/certs/botbot.biz.key
chmod 644 nginx/certs/botbot.biz.crt
```

#### 方式 B：使用现有证书

如果你已有证书（从云服务商获取）：

```bash
# 将证书文件放到 nginx/certs/ 目录
cp /path/to/your/fullchain.pem nginx/certs/botbot.biz.crt
cp /path/to/your/privkey.pem nginx/certs/botbot.biz.key

# 设置权限
chmod 600 nginx/certs/botbot.biz.key
chmod 644 nginx/certs/botbot.biz.crt
```

### 5. 选择生产配置

```bash
# 使用生产环境 Nginx 配置（启用 HTTPS 重定向）
cd nginx/conf.d
mv botbot.conf botbot.dev.conf  # 备份开发配置
cp botbot.prod.conf botbot.conf  # 使用生产配置
```

### 6. 启动服务

```bash
# 使用生产环境 docker-compose
docker-compose -f docker-compose.prod.yml up -d

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f

# 查看服务状态
docker-compose -f docker-compose.prod.yml ps
```

### 7. 验证部署

```bash
# 测试 HTTPS
curl https://botbot.biz/health

# 测试 API
curl https://botbot.biz/api/health

# 检查 HTTP 到 HTTPS 重定向
curl -I http://botbot.biz
# 应该返回 301 重定向到 https://botbot.biz
```

### 8. 配置证书自动续期

Let's Encrypt 证书有效期 90 天，需要自动续期：

```bash
# 创建续期脚本
cat > /usr/local/bin/renew-botbot-cert.sh << 'EOF'
#!/bin/bash
cd /path/to/botbot
docker-compose -f docker-compose.prod.yml stop nginx
certbot renew --quiet
cp /etc/letsencrypt/live/botbot.biz/fullchain.pem nginx/certs/botbot.biz.crt
cp /etc/letsencrypt/live/botbot.biz/privkey.pem nginx/certs/botbot.biz.key
chown $USER:$USER nginx/certs/botbot.biz.*
docker-compose -f docker-compose.prod.yml start nginx
EOF

chmod +x /usr/local/bin/renew-botbot-cert.sh

# 添加 crontab
sudo crontab -e
# 添加以下行（每天凌晨 2 点检查）
0 2 * * * /usr/local/bin/renew-botbot-cert.sh
```

## 📝 生产环境配置说明

### docker-compose.prod.yml 关键差异

| 配置项 | 开发环境 | 生产环境 |
|-------|---------|---------|
| restart | unless-stopped | always |
| backend ports | expose 8000 | expose 8000 |
| frontend ports | expose 3000 | expose 3000 |
| nginx ports | 80, 443 | 80, 443 |
| backend command | --reload | --workers 4 |
| DEBUG | True | False |
| API_URL | http://botbot.biz | https://botbot.biz |

### Nginx 生产配置特性

**启用的功能**：
- ✅ 强制 HTTPS（HTTP 自动重定向到 HTTPS）
- ✅ HSTS（HTTP Strict Transport Security）
- ✅ 安全响应头（CSP、X-Frame-Options 等）
- ✅ 静态资源激进缓存（1年）
- ✅ OCSP Stapling
- ✅ Rate Limiting（可选）
- ✅ 日志轮转

**配置文件**：`nginx/conf.d/botbot.prod.conf`

## 🔒 安全加固

### 1. 防火墙配置

```bash
# Ubuntu/Debian (UFW)
sudo ufw allow 22/tcp    # SSH
sudo ufw allow 80/tcp    # HTTP
sudo ufw allow 443/tcp   # HTTPS
sudo ufw enable

# CentOS (firewalld)
sudo firewall-cmd --permanent --add-service=ssh
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --permanent --add-service=https
sudo firewall-cmd --reload
```

### 2. 启用 Rate Limiting

编辑 `nginx/conf.d/botbot.conf`，取消注释 rate limiting 相关行：

```nginx
# 在 server 块外添加
limit_req_zone $binary_remote_addr zone=api_limit:10m rate=10r/s;
limit_req_zone $binary_remote_addr zone=general_limit:10m rate=50r/s;

# 在 location 块内添加
location /api/ {
    limit_req zone=api_limit burst=20 nodelay;
    # ...
}
```

### 3. MongoDB 认证

编辑 `docker-compose.prod.yml`：

```yaml
mongodb:
  environment:
    MONGO_INITDB_ROOT_USERNAME: admin
    MONGO_INITDB_ROOT_PASSWORD: <strong-password>
```

更新 backend 连接字符串：
```bash
MONGODB_URL=mongodb://admin:<strong-password>@mongodb:27017
```

### 4. 定期备份

```bash
# MongoDB 备份脚本
cat > /usr/local/bin/backup-botbot-db.sh << 'EOF'
#!/bin/bash
BACKUP_DIR="/backup/botbot"
DATE=$(date +%Y%m%d_%H%M%S)
mkdir -p $BACKUP_DIR

docker exec botbot-mongodb-prod mongodump \
  --out=/tmp/backup \
  --db=botbot

docker cp botbot-mongodb-prod:/tmp/backup $BACKUP_DIR/$DATE
tar -czf $BACKUP_DIR/botbot_$DATE.tar.gz -C $BACKUP_DIR $DATE
rm -rf $BACKUP_DIR/$DATE

# 保留最近 7 天的备份
find $BACKUP_DIR -name "botbot_*.tar.gz" -mtime +7 -delete
EOF

chmod +x /usr/local/bin/backup-botbot-db.sh

# 每天凌晨 3 点备份
sudo crontab -e
# 添加：
0 3 * * * /usr/local/bin/backup-botbot-db.sh
```

## 📊 监控和日志

### 查看日志

```bash
# 所有服务日志
docker-compose -f docker-compose.prod.yml logs -f

# 单个服务日志
docker-compose -f docker-compose.prod.yml logs -f nginx
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend

# Nginx 访问日志
docker exec botbot-nginx-prod tail -f /var/log/nginx/access.log

# Nginx 错误日志
docker exec botbot-nginx-prod tail -f /var/log/nginx/error.log
```

### 健康检查

```bash
# 创建监控脚本
cat > /usr/local/bin/monitor-botbot.sh << 'EOF'
#!/bin/bash
HEALTH_URL="https://botbot.biz/health"
API_HEALTH_URL="https://botbot.biz/api/health"

# 检查 Nginx
if ! curl -sf $HEALTH_URL > /dev/null; then
    echo "$(date): Nginx health check failed" >> /var/log/botbot-monitor.log
    # 可以添加告警，如发送邮件或钉钉通知
fi

# 检查 Backend API
if ! curl -sf $API_HEALTH_URL > /dev/null; then
    echo "$(date): Backend health check failed" >> /var/log/botbot-monitor.log
fi
EOF

chmod +x /usr/local/bin/monitor-botbot.sh

# 每 5 分钟检查一次
crontab -e
# 添加：
*/5 * * * * /usr/local/bin/monitor-botbot.sh
```

## 🔄 更新和维护

### 更新应用

```bash
# 1. 拉取最新代码
git pull

# 2. 重新构建镜像
docker-compose -f docker-compose.prod.yml build

# 3. 滚动更新（零停机）
docker-compose -f docker-compose.prod.yml up -d --no-deps backend
docker-compose -f docker-compose.prod.yml up -d --no-deps frontend

# 4. 查看日志确认
docker-compose -f docker-compose.prod.yml logs -f backend frontend
```

### 重启服务

```bash
# 重启所有服务
docker-compose -f docker-compose.prod.yml restart

# 重启单个服务
docker-compose -f docker-compose.prod.yml restart nginx
docker-compose -f docker-compose.prod.yml restart backend
```

### 清理资源

```bash
# 清理未使用的 Docker 镜像
docker system prune -a

# 查看磁盘使用
docker system df
```

## 🐛 故障排查

### Nginx 启动失败

```bash
# 检查配置
docker exec botbot-nginx-prod nginx -t

# 查看错误日志
docker-compose -f docker-compose.prod.yml logs nginx
```

### Backend 连接失败

```bash
# 检查容器网络
docker network inspect botbot_botbot-network

# 进入 backend 容器调试
docker exec -it botbot-backend-prod bash
curl http://backend:8000/health
```

### SSL 证书问题

```bash
# 检查证书有效期
openssl x509 -in nginx/certs/botbot.biz.crt -noout -dates

# 测试 SSL 配置
openssl s_client -connect botbot.biz:443 -servername botbot.biz

# 在线测试 SSL 评级
# https://www.ssllabs.com/ssltest/analyze.html?d=botbot.biz
```

## 📚 相关文档

- [Nginx 配置说明](nginx/README.md)
- [SSL 证书配置](nginx/certs/README.md)
- [快速开始指南](QUICKSTART.md)
- [项目架构](CLAUDE.md)

## ✅ 部署检查清单

部署前检查：

- [ ] 服务器准备完毕（Docker、Docker Compose 已安装）
- [ ] 域名 DNS 已配置指向服务器 IP
- [ ] 防火墙已配置（开放 80、443 端口）
- [ ] 环境变量已配置（.env.prod）
- [ ] SSL 证书已获取并放置在正确位置
- [ ] 生产配置文件已启用（botbot.prod.conf）
- [ ] 数据库备份脚本已配置
- [ ] 证书自动续期已配置
- [ ] 监控脚本已配置
- [ ] 测试所有端点可访问

部署后验证：

- [ ] HTTPS 可正常访问：https://botbot.biz
- [ ] HTTP 自动重定向到 HTTPS
- [ ] API 可正常响应：https://botbot.biz/api/health
- [ ] SSL Labs 评级 A 或 A+
- [ ] 前端页面正常加载
- [ ] 用户注册/登录功能正常
- [ ] 日志正常记录
- [ ] 监控脚本正常运行
