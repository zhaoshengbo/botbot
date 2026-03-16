# BotBot 生产环境部署指南

## 📋 部署前检查清单

### 1. 服务器要求
- ✅ Docker Engine 20.10+
- ✅ Docker Compose 2.0+
- ✅ 至少 2GB RAM
- ✅ 至少 10GB 磁盘空间
- ✅ 端口 3000, 8000, 27017 可用
- ✅ 互联网连接（用于拉取镜像和支付回调）

### 2. 必需的环境变量
- ✅ SECRET_KEY (至少32字符)
- ✅ JWT_SECRET_KEY (至少32字符)
- ✅ MONGO_PASSWORD (强密码)
- ✅ ANTHROPIC_API_KEY (Claude AI)
- ✅ 支付配置（微信/支付宝）

### 3. 可选的环境变量
- 📧 阿里云短信服务（用户注册验证码）

## 🚀 快速部署步骤

### Step 1: 准备环境变量

```bash
# 1. 复制环境变量模板
cp .env.prod.example .env.prod

# 2. 生成安全密钥
openssl rand -hex 32  # 用于 SECRET_KEY
openssl rand -hex 32  # 用于 JWT_SECRET_KEY

# 3. 编辑 .env.prod，填入实际值
nano .env.prod
```

**必须修改的值：**
```bash
BACKEND_URL=http://YOUR_SERVER_IP:8000
FRONTEND_URL=http://YOUR_SERVER_IP:3000
MONGO_PASSWORD=strong-password-here
SECRET_KEY=generated-key-from-step-2
JWT_SECRET_KEY=generated-key-from-step-2
ANTHROPIC_API_KEY=sk-ant-api03-your-actual-key

# 支付配置（至少配置一个）
WECHAT_PAY_MCHID=your-mchid
WECHAT_PAY_KEY=your-key
# ... 或 ...
ALIPAY_APP_ID=your-app-id
ALIPAY_PRIVATE_KEY=your-private-key
```

### Step 2: 使用修复后的配置文件

```bash
# 方案 A: 备份并替换原文件（推荐）
mv docker-compose.prod.yml docker-compose.prod.yml.backup
mv docker-compose.prod.yml.fixed docker-compose.prod.yml

# 方案 B: 直接使用修复后的文件
# docker-compose -f docker-compose.prod.yml.fixed --env-file .env.prod up -d
```

### Step 3: 部署应用

```bash
# 1. 启动所有服务
docker-compose -f docker-compose.prod.yml --env-file .env.prod up -d

# 2. 查看日志
docker-compose -f docker-compose.prod.yml logs -f

# 3. 检查服务状态
docker-compose -f docker-compose.prod.yml ps
```

### Step 4: 验证部署

```bash
# 1. 检查 Backend 健康状态
curl http://localhost:8000/api/health
# 预期输出: {"status": "healthy"}

# 2. 检查 Frontend
curl http://localhost:3000
# 预期输出: HTML content

# 3. 检查 MongoDB 连接
docker exec botbot-backend python -c "from motor.motor_asyncio import AsyncIOMotorClient; print('MongoDB OK')"
```

### Step 5: 初始化数据（可选）

```bash
# 创建测试用户
curl -X POST http://localhost:8000/api/auth/direct-login \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "13800138000"}'
```

## 🔧 配置文件对比

### 主要改进点

#### 1. **MongoDB 安全性** ✅
```yaml
# 原配置：无认证
environment:
  MONGO_INITDB_DATABASE: botbot

# 修复后：启用认证
environment:
  MONGO_INITDB_DATABASE: botbot
  MONGO_INITDB_ROOT_USERNAME: ${MONGO_USERNAME}
  MONGO_INITDB_ROOT_PASSWORD: ${MONGO_PASSWORD}
```

#### 2. **CORS 安全性** ✅
```yaml
# 原配置：允许所有域
- CORS_ORIGINS=*

# 修复后：限制为前端域名
- CORS_ORIGINS=${FRONTEND_URL}
```

#### 3. **支付配置** ✅
```yaml
# 新增：微信支付
- WECHAT_PAY_MCHID=${WECHAT_PAY_MCHID}
- WECHAT_PAY_KEY=${WECHAT_PAY_KEY}
- WECHAT_PAY_APIV3_KEY=${WECHAT_PAY_APIV3_KEY}
- WECHAT_PAY_SERIAL_NO=${WECHAT_PAY_SERIAL_NO}
- WECHAT_PAY_NOTIFY_URL=${BACKEND_URL}/api/payment/callback/wechat

# 新增：支付宝
- ALIPAY_APP_ID=${ALIPAY_APP_ID}
- ALIPAY_PRIVATE_KEY=${ALIPAY_PRIVATE_KEY}
- ALIPAY_NOTIFY_URL=${BACKEND_URL}/api/payment/callback/alipay
```

#### 4. **健康检查** ✅
```yaml
# 新增：服务健康检查
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/api/health"]
  interval: 30s
  timeout: 10s
  retries: 3
```

#### 5. **依赖管理** ✅
```yaml
# 原配置：简单依赖
depends_on:
  - mongodb

# 修复后：等待服务健康
depends_on:
  mongodb:
    condition: service_healthy
```

## ⚠️ 已知问题和解决方案

### 问题 1: Frontend 构建失败 - 找不到 .env.production

**原因：** Dockerfile 中 `COPY .env.production .env.production` 失败

**解决方案：**
```bash
# 确保文件存在
ls -la fe/.env.production

# 如果不存在，创建它
cat > fe/.env.production << EOF
NEXT_PUBLIC_API_URL=${BACKEND_URL}
NEXT_PUBLIC_APP_NAME=BotBot
EOF
```

### 问题 2: Backend 无法连接 MongoDB

**原因：** MongoDB 认证失败或连接字符串不正确

**解决方案：**
```bash
# 1. 检查 MongoDB 日志
docker-compose -f docker-compose.prod.yml logs mongodb

# 2. 验证连接字符串格式
# 正确格式: mongodb://username:password@host:port/database?authSource=admin
```

### 问题 3: 支付回调失败

**原因：** 回调 URL 无法从外网访问

**解决方案：**
```bash
# 1. 确保服务器防火墙开放端口 8000
sudo ufw allow 8000/tcp

# 2. 配置回调 URL 为公网 IP 或域名
BACKEND_URL=http://YOUR_PUBLIC_IP:8000
# 或
BACKEND_URL=https://api.yourdomain.com
```

### 问题 4: 支付宝/微信支付私钥格式错误

**原因：** 多行私钥在环境变量中格式不正确

**解决方案 A: 使用 Base64 编码**
```bash
# 编码私钥
cat wechat_private_key.pem | base64 > wechat_private_key.b64

# 在 .env.prod 中
WECHAT_PAY_PRIVATE_KEY_BASE64=LS0tLS1CRUdJTi...

# 修改后端代码解码
import base64
private_key = base64.b64decode(os.getenv("WECHAT_PAY_PRIVATE_KEY_BASE64"))
```

**解决方案 B: 使用 Docker Secrets（推荐）**
```yaml
secrets:
  wechat_private_key:
    file: ./secrets/wechat_private_key.pem

services:
  backend:
    secrets:
      - wechat_private_key
```

## 🔐 安全最佳实践

### 1. 密钥管理
```bash
# ❌ 不要这样做
SECRET_KEY=123456

# ✅ 应该这样做
SECRET_KEY=$(openssl rand -hex 32)
```

### 2. MongoDB 安全
```bash
# ✅ 启用认证
# ✅ 使用强密码
# ✅ 限制外部访问
# ✅ 定期备份
```

### 3. CORS 配置
```bash
# ❌ 不要在生产环境使用
CORS_ORIGINS=*

# ✅ 限制为具体域名
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

### 4. 支付密钥
```bash
# ✅ 使用环境变量或 Docker secrets
# ✅ 不要提交到 Git
# ✅ 定期轮换
# ✅ 限制回调 IP 白名单
```

## 📊 监控和维护

### 查看日志
```bash
# 所有服务
docker-compose -f docker-compose.prod.yml logs -f

# 特定服务
docker-compose -f docker-compose.prod.yml logs -f backend
docker-compose -f docker-compose.prod.yml logs -f frontend
docker-compose -f docker-compose.prod.yml logs -f mongodb
```

### 备份 MongoDB
```bash
# 创建备份
docker exec botbot-mongodb mongodump --out /data/backup

# 复制到主机
docker cp botbot-mongodb:/data/backup ./mongodb_backup_$(date +%Y%m%d)
```

### 更新应用
```bash
# 1. 拉取最新代码
git pull origin main

# 2. 重新构建镜像
docker-compose -f docker-compose.prod.yml build

# 3. 重启服务
docker-compose -f docker-compose.prod.yml up -d
```

### 清理资源
```bash
# 停止服务
docker-compose -f docker-compose.prod.yml down

# 清理所有（包括数据卷）
docker-compose -f docker-compose.prod.yml down -v

# 清理未使用的镜像
docker image prune -a
```

## 🌐 使用域名（推荐）

### 1. 配置 Nginx 反向代理
```nginx
# /etc/nginx/sites-available/botbot
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}

server {
    listen 80;
    server_name app.yourdomain.com;

    location / {
        proxy_pass http://localhost:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

### 2. 配置 SSL (Let's Encrypt)
```bash
# 安装 certbot
sudo apt-get install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d api.yourdomain.com -d app.yourdomain.com
```

### 3. 更新环境变量
```bash
BACKEND_URL=https://api.yourdomain.com
FRONTEND_URL=https://app.yourdomain.com
```

## 📞 故障排查

### Backend 无法启动
```bash
# 检查日志
docker-compose -f docker-compose.prod.yml logs backend

# 常见问题：
# 1. MongoDB 连接失败 → 检查 MONGODB_URL
# 2. 端口被占用 → 修改端口映射
# 3. 依赖缺失 → 重新构建镜像
```

### Frontend 白屏
```bash
# 检查日志
docker-compose -f docker-compose.prod.yml logs frontend

# 常见问题：
# 1. API_URL 配置错误 → 检查 NEXT_PUBLIC_API_URL
# 2. 构建失败 → 检查构建日志
# 3. 内存不足 → 增加服务器内存
```

### 支付功能不工作
```bash
# 检查配置
docker exec botbot-backend env | grep WECHAT
docker exec botbot-backend env | grep ALIPAY

# 测试回调 URL
curl -X POST https://api.yourdomain.com/api/payment/callback/wechat
```

## 📚 相关文档

- [Docker Compose 官方文档](https://docs.docker.com/compose/)
- [FastAPI 部署指南](https://fastapi.tiangolo.com/deployment/)
- [Next.js 生产部署](https://nextjs.org/docs/deployment)
- [MongoDB 安全检查清单](https://docs.mongodb.com/manual/administration/security-checklist/)

## ✅ 部署成功标志

当你看到以下输出时，说明部署成功：

```bash
$ docker-compose -f docker-compose.prod.yml ps
NAME                COMMAND                  SERVICE             STATUS              PORTS
botbot-backend      "uvicorn app.main:ap…"   backend             Up 5 minutes (healthy)   0.0.0.0:8000->8000/tcp
botbot-frontend     "docker-entrypoint.s…"   frontend            Up 5 minutes (healthy)   0.0.0.0:3000->3000/tcp
botbot-mongodb      "docker-entrypoint.s…"   mongodb             Up 5 minutes (healthy)   0.0.0.0:27017->27017/tcp
```

访问 http://YOUR_SERVER_IP:3000 应该能看到 BotBot 登录页面 🎉

---

**需要帮助？**
- GitHub Issues: https://github.com/yourusername/botbot/issues
- 部署问题请附带完整日志
