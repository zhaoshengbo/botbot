# 🚀 BotBot 部署指南

## 生产环境部署

### 服务器信息
- **IP 地址**: 47.83.230.114
- **域名**: botbot.biz
- **前端端口**: 3000
- **后端端口**: 8000
- **MongoDB 端口**: 27017

---

## 快速部署步骤

### 1. 服务器准备

```bash
# SSH 连接到服务器
ssh root@47.83.230.114

# 安装 Docker 和 Docker Compose
curl -fsSL https://get.docker.com | sh
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```

### 2. 克隆代码

```bash
cd /root
git clone git@github.com:zhaoshengbo/botbot.git
cd botbot
```

### 3. 配置环境变量

#### 后端配置 (be/.env)

```bash
cp be/.env.example be/.env
nano be/.env
```

编辑内容：
```env
# Application
APP_NAME=BotBot
DEBUG=false
API_PREFIX=/api

# Security
SECRET_KEY=your-super-secret-key-change-this-in-production-min-32-chars
JWT_SECRET_KEY=your-jwt-secret-key-change-this-min-32-chars
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
REFRESH_TOKEN_EXPIRE_MINUTES=43200

# Database
MONGODB_URL=mongodb://mongodb:27017
MONGODB_DB_NAME=botbot

# AI Service (Optional - for real AI analysis)
ANTHROPIC_API_KEY=your-claude-api-key-here

# CORS (允许前端域名访问)
CORS_ORIGINS=["http://botbot.biz:3000","http://47.83.230.114:3000","http://localhost:3000"]

# SMS (生产环境需配置真实短信服务)
SMS_PROVIDER=mock
```

#### 前端配置 (fe/.env.production)

```bash
nano fe/.env.production
```

编辑内容：
```env
# 使用域名（推荐）
NEXT_PUBLIC_API_URL=http://botbot.biz:8000

# 或使用 IP（如果域名 DNS 未配置）
# NEXT_PUBLIC_API_URL=http://47.83.230.114:8000

NEXT_PUBLIC_APP_NAME=BotBot
```

### 4. 启动服务

```bash
# 启动所有服务
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 5. 验证部署

```bash
# 检查后端健康
curl http://localhost:8000/api/auth/me

# 检查前端
curl http://localhost:3000

# 检查 MongoDB
docker-compose exec mongodb mongosh --eval "db.adminCommand('ping')"
```

---

## 访问地址

部署成功后，可以通过以下地址访问：

### 前端
- 🌐 域名访问: http://botbot.biz:3000
- 🌐 IP 访问: http://47.83.230.114:3000

### 后端 API
- 🔧 域名访问: http://botbot.biz:8000
- 🔧 IP 访问: http://47.83.230.114:8000
- 📚 API 文档: http://botbot.biz:8000/docs

---

## 常见问题排查

### 问题 1: 前端无法连接后端

**症状**: 登录时提示 "Login failed" 或控制台显示 "Network Error"

**原因**: 前端使用了错误的后端地址（如 localhost:8000）

**解决方案**:

```bash
# 1. 检查前端环境变量
cd /root/botbot
cat fe/.env.production

# 2. 确认后端地址正确
# 应该是: NEXT_PUBLIC_API_URL=http://botbot.biz:8000
# 或: NEXT_PUBLIC_API_URL=http://47.83.230.114:8000

# 3. 重新构建前端容器
docker-compose stop frontend
docker-compose build --no-cache frontend
docker-compose up -d frontend

# 4. 验证环境变量已生效
docker-compose exec frontend env | grep NEXT_PUBLIC
```

### 问题 2: CORS 错误

**症状**: 浏览器控制台显示 CORS policy 错误

**解决方案**:

```bash
# 编辑后端环境变量
nano be/.env

# 确保 CORS_ORIGINS 包含前端地址
CORS_ORIGINS=["http://botbot.biz:3000","http://47.83.230.114:3000"]

# 重启后端
docker-compose restart backend
```

### 问题 3: 端口被占用

**症状**: 启动失败，提示端口已被占用

**解决方案**:

```bash
# 查看端口占用
netstat -tlnp | grep -E '3000|8000|27017'

# 停止占用进程
kill -9 <PID>

# 或修改 docker-compose.yml 中的端口映射
```

### 问题 4: MongoDB 连接失败

**症状**: 后端日志显示 MongoDB 连接错误

**解决方案**:

```bash
# 检查 MongoDB 状态
docker-compose ps mongodb
docker-compose logs mongodb

# 重启 MongoDB
docker-compose restart mongodb

# 检查数据卷
docker volume ls | grep botbot
```

### 问题 5: 容器自动退出

**症状**: 服务启动后立即退出

**解决方案**:

```bash
# 查看容器日志
docker-compose logs backend
docker-compose logs frontend

# 检查环境变量配置
docker-compose config

# 重新构建
docker-compose down
docker-compose build
docker-compose up -d
```

---

## 生产环境优化

### 1. 使用 Nginx 反向代理

创建 `nginx.conf`:

```nginx
server {
    listen 80;
    server_name botbot.biz;

    # 前端
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }

    # 后端 API
    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
```

安装和启动 Nginx:

```bash
# 安装 Nginx
apt update
apt install nginx -y

# 复制配置
cp nginx.conf /etc/nginx/sites-available/botbot
ln -s /etc/nginx/sites-available/botbot /etc/nginx/sites-enabled/

# 测试配置
nginx -t

# 重启 Nginx
systemctl restart nginx

# 设置开机启动
systemctl enable nginx
```

这样就可以通过 http://botbot.biz 直接访问（无需端口号）。

### 2. 启用 HTTPS (SSL/TLS)

```bash
# 安装 Certbot
apt install certbot python3-certbot-nginx -y

# 获取 SSL 证书
certbot --nginx -d botbot.biz

# 自动续期
certbot renew --dry-run
```

### 3. 配置防火墙

```bash
# 安装 UFW
apt install ufw -y

# 配置规则
ufw allow ssh
ufw allow 80/tcp
ufw allow 443/tcp
ufw allow 3000/tcp  # 前端（如果直接访问）
ufw allow 8000/tcp  # 后端 API（如果直接访问）

# 启用防火墙
ufw enable

# 查看状态
ufw status
```

### 4. 数据备份

```bash
# 创建备份脚本
cat > /root/backup-botbot.sh << 'EOF'
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR=/root/botbot-backups

mkdir -p $BACKUP_DIR

# 备份 MongoDB
docker-compose exec -T mongodb mongodump --archive > $BACKUP_DIR/mongodb_$DATE.archive

# 备份代码和配置
tar -czf $BACKUP_DIR/botbot_$DATE.tar.gz /root/botbot --exclude=node_modules --exclude=__pycache__

# 保留最近 7 天的备份
find $BACKUP_DIR -name "*.archive" -mtime +7 -delete
find $BACKUP_DIR -name "*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /root/backup-botbot.sh

# 设置定时任务（每天凌晨 2 点）
crontab -e
# 添加: 0 2 * * * /root/backup-botbot.sh >> /var/log/botbot-backup.log 2>&1
```

### 5. 监控和日志

```bash
# 查看资源使用
docker stats

# 查看实时日志
docker-compose logs -f --tail=100

# 日志轮转配置
cat > /etc/docker/daemon.json << 'EOF'
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
EOF

systemctl restart docker
```

---

## 更新部署

```bash
cd /root/botbot

# 拉取最新代码
git pull origin main

# 重新构建和启动
docker-compose down
docker-compose build --no-cache
docker-compose up -d

# 验证
docker-compose ps
docker-compose logs -f
```

---

## 回滚部署

```bash
# 查看 Git 历史
git log --oneline -10

# 回滚到特定版本
git checkout <commit-hash>

# 重新部署
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## 性能优化建议

1. **数据库索引**: MongoDB 已自动创建必要索引
2. **静态资源缓存**: Nginx 配置缓存头
3. **API 限流**: 考虑使用 FastAPI 的限流中间件
4. **CDN**: 前端静态资源可使用 CDN 加速
5. **负载均衡**: 高流量时考虑多实例部署

---

## 安全建议

1. ✅ 修改默认密码和密钥
2. ✅ 启用防火墙限制端口访问
3. ✅ 使用 HTTPS 加密通信
4. ✅ 定期更新系统和 Docker 镜像
5. ✅ 配置日志监控和告警
6. ✅ 限制 MongoDB 只监听内网
7. ✅ 生产环境禁用 DEBUG 模式

---

## 支持

如有问题，请检查：
1. Docker 容器状态: `docker-compose ps`
2. 服务日志: `docker-compose logs`
3. 网络连接: `curl` 测试各服务
4. 环境变量: `docker-compose config`

**祝部署顺利！** 🚀
