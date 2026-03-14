# BotBot 应用部署指南

**项目**: BotBot - AI驱动的任务市场平台
**技术栈**: FastAPI + Next.js + MongoDB + Docker
**更新时间**: 2026-03-14

---

## 📋 目录

1. [快速开始](#快速开始)
2. [本地开发部署](#本地开发部署)
3. [生产环境部署](#生产环境部署)
4. [配置说明](#配置说明)
5. [常见问题](#常见问题)
6. [监控和维护](#监控和维护)

---

## 🚀 快速开始

### 前置要求

- Docker 20.10+
- Docker Compose 1.29+
- Git
- 至少2GB可用内存
- 至少5GB可用磁盘空间

### 一键启动（本地开发）

```bash
# 1. 克隆项目
git clone git@github.com:zhaoshengbo/botbot.git
cd botbot

# 2. 复制环境配置
cp be/.env.example be/.env
cp fe/.env.example fe/.env

# 3. 启动所有服务
docker-compose up -d

# 4. 查看服务状态
docker-compose ps

# 5. 查看日志
docker-compose logs -f
```

**访问地址：**
- 前端: http://localhost:3000
- 后端API: http://localhost:8000
- API文档: http://localhost:8000/docs

---

## 💻 本地开发部署

### 1. 环境准备

```bash
# 检查Docker版本
docker --version
docker-compose --version

# 确保Docker服务运行
docker ps
```

### 2. 配置环境变量

**后端配置** (`be/.env`):
```bash
# MongoDB配置
MONGODB_URL=mongodb://mongodb:27017
MONGODB_DB_NAME=botbot

# 应用配置
DEBUG=True
API_PREFIX=/api

# 安全密钥（开发环境）
SECRET_KEY=dev-secret-key-change-in-production
JWT_SECRET_KEY=dev-jwt-secret-key-change-in-production

# CORS配置
CORS_ORIGINS=*

# AI服务（可选）
ANTHROPIC_API_KEY=your-api-key-here
CLAUDE_MODEL=claude-3-5-sonnet-20241022
```

**前端配置** (`fe/.env`):
```bash
NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 3. 启动开发环境

```bash
# 构建并启动所有服务
docker-compose up -d --build

# 查看服务状态
docker-compose ps

# 查看实时日志
docker-compose logs -f backend    # 后端日志
docker-compose logs -f frontend   # 前端日志
docker-compose logs -f mongodb    # 数据库日志
```

### 4. 验证部署

```bash
# 测试后端健康检查
curl http://localhost:8000/

# 测试前端
curl http://localhost:3000/

# 测试API
curl http://localhost:8000/api/auth/me
```

### 5. 开发工作流

```bash
# 重启单个服务
docker-compose restart backend

# 查看服务日志
docker-compose logs -f backend

# 进入容器调试
docker exec -it botbot-backend bash
docker exec -it botbot-frontend sh

# 停止所有服务
docker-compose down

# 停止并清理数据
docker-compose down -v
```

---

## 🌐 生产环境部署

### 方案1: 使用Docker Compose（推荐单机部署）

#### 1. 服务器准备

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# 安装Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# 验证安装
docker --version
docker-compose --version
```

#### 2. 部署步骤

```bash
# 1. 克隆项目到服务器
git clone git@github.com:zhaoshengbo/botbot.git
cd botbot

# 2. 创建生产环境配置
cat > be/.env << EOF
# MongoDB配置
MONGODB_URL=mongodb://mongodb:27017
MONGODB_DB_NAME=botbot

# 应用配置
DEBUG=False
API_PREFIX=/api

# 安全密钥（必须修改！）
SECRET_KEY=$(openssl rand -hex 32)
JWT_SECRET_KEY=$(openssl rand -hex 32)

# CORS配置（改为你的域名）
CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com

# AI服务
ANTHROPIC_API_KEY=your-production-api-key

# 阿里云SMS（可选）
ALIYUN_ACCESS_KEY_ID=your-key-id
ALIYUN_ACCESS_KEY_SECRET=your-key-secret
EOF

cat > fe/.env.production << EOF
NEXT_PUBLIC_API_URL=https://api.yourdomain.com
EOF

# 3. 创建生产环境docker-compose
cat > docker-compose.prod.yml << EOF
version: '3.8'

services:
  mongodb:
    image: mongo:6.0
    container_name: botbot-mongodb-prod
    restart: always
    ports:
      - "127.0.0.1:27017:27017"
    environment:
      MONGO_INITDB_DATABASE: botbot
    volumes:
      - mongodb_data:/data/db
    networks:
      - botbot-network

  backend:
    build:
      context: ./be
      dockerfile: Dockerfile
    container_name: botbot-backend-prod
    restart: always
    ports:
      - "127.0.0.1:8000:8000"
    env_file:
      - ./be/.env
    depends_on:
      - mongodb
    networks:
      - botbot-network
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4

  frontend:
    build:
      context: ./fe
      dockerfile: Dockerfile.simple
    container_name: botbot-frontend-prod
    restart: always
    ports:
      - "127.0.0.1:3000:3000"
    environment:
      - NODE_ENV=production
    depends_on:
      - backend
    networks:
      - botbot-network

volumes:
  mongodb_data:

networks:
  botbot-network:
    driver: bridge
EOF

# 4. 启动生产环境
docker-compose -f docker-compose.prod.yml up -d --build

# 5. 检查服务状态
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs
```

#### 3. 配置Nginx反向代理

```bash
# 安装Nginx
sudo apt install nginx -y

# 创建配置文件
sudo nano /etc/nginx/sites-available/botbot

# 添加以下配置
```

```nginx
# 后端API
server {
    listen 80;
    server_name api.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}

# 前端应用
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

```bash
# 启用站点
sudo ln -s /etc/nginx/sites-available/botbot /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# 配置SSL（使用Let's Encrypt）
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com -d api.yourdomain.com
```

#### 4. 配置防火墙

```bash
# 允许必要端口
sudo ufw allow 22/tcp      # SSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw enable

# 检查状态
sudo ufw status
```

### 方案2: 云平台部署

#### AWS ECS / Azure Container Instances / Google Cloud Run

1. **准备Docker镜像**

```bash
# 构建镜像
docker build -t botbot-backend:latest ./be
docker build -t botbot-frontend:latest ./fe

# 推送到容器仓库（以AWS ECR为例）
aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 123456789.dkr.ecr.us-east-1.amazonaws.com

docker tag botbot-backend:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/botbot-backend:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/botbot-backend:latest

docker tag botbot-frontend:latest 123456789.dkr.ecr.us-east-1.amazonaws.com/botbot-frontend:latest
docker push 123456789.dkr.ecr.us-east-1.amazonaws.com/botbot-frontend:latest
```

2. **配置云数据库**

使用托管MongoDB服务：
- AWS DocumentDB
- MongoDB Atlas
- Azure Cosmos DB

3. **部署容器**

根据云平台文档部署容器服务。

---

## ⚙️ 配置说明

### 后端环境变量详解

| 变量名 | 说明 | 默认值 | 必需 |
|--------|------|--------|------|
| `MONGODB_URL` | MongoDB连接字符串 | `mongodb://mongodb:27017` | ✅ |
| `MONGODB_DB_NAME` | 数据库名称 | `botbot` | ✅ |
| `DEBUG` | 调试模式 | `True` | ❌ |
| `SECRET_KEY` | 应用密钥 | - | ✅ |
| `JWT_SECRET_KEY` | JWT签名密钥 | - | ✅ |
| `API_PREFIX` | API路径前缀 | `/api` | ❌ |
| `CORS_ORIGINS` | CORS允许的源 | `*` | ❌ |
| `ANTHROPIC_API_KEY` | Claude API密钥 | - | ❌ |
| `CLAUDE_MODEL` | Claude模型名称 | `claude-3-5-sonnet-20241022` | ❌ |

### 前端环境变量

| 变量名 | 说明 | 示例 |
|--------|------|------|
| `NEXT_PUBLIC_API_URL` | 后端API地址 | `http://localhost:8000` |

### 生产环境安全配置检查清单

- [ ] 修改所有默认密钥和密码
- [ ] 设置 `DEBUG=False`
- [ ] 配置正确的 `CORS_ORIGINS`
- [ ] 启用HTTPS（SSL证书）
- [ ] 配置防火墙规则
- [ ] 设置MongoDB认证
- [ ] 定期备份数据库
- [ ] 配置日志轮转
- [ ] 设置资源限制
- [ ] 配置监控告警

---

## 🔧 常见问题

### 1. 服务启动失败

```bash
# 查看详细日志
docker-compose logs backend
docker-compose logs frontend

# 检查端口占用
sudo lsof -i :8000
sudo lsof -i :3000

# 清理并重启
docker-compose down
docker-compose up -d --build
```

### 2. MongoDB连接失败

```bash
# 检查MongoDB状态
docker-compose ps mongodb
docker-compose logs mongodb

# 进入MongoDB容器
docker exec -it botbot-mongodb mongo botbot
```

### 3. 前端无法连接后端

```bash
# 检查环境变量
docker-compose exec frontend printenv | grep API_URL

# 检查网络
docker network ls
docker network inspect botbot_botbot-network
```

### 4. 内存不足

```bash
# 检查内存使用
docker stats

# 限制容器内存（在docker-compose.yml中）
services:
  backend:
    deploy:
      resources:
        limits:
          memory: 1G
```

### 5. 磁盘空间不足

```bash
# 清理Docker
docker system prune -a
docker volume prune

# 查看磁盘使用
df -h
docker system df
```

---

## 📊 监控和维护

### 1. 日志管理

```bash
# 查看最近日志
docker-compose logs --tail=100 -f

# 导出日志
docker-compose logs > logs.txt

# 配置日志轮转（docker-compose.yml）
services:
  backend:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

### 2. 数据备份

```bash
# 备份MongoDB
docker exec botbot-mongodb mongodump --db botbot --out /backup
docker cp botbot-mongodb:/backup ./mongodb-backup-$(date +%Y%m%d)

# 自动化备份脚本
cat > backup.sh << 'EOF'
#!/bin/bash
BACKUP_DIR=/backups/mongodb
DATE=$(date +%Y%m%d_%H%M%S)
docker exec botbot-mongodb mongodump --db botbot --out /backup
docker cp botbot-mongodb:/backup $BACKUP_DIR/backup-$DATE
# 保留最近7天的备份
find $BACKUP_DIR -name "backup-*" -mtime +7 -exec rm -rf {} \;
EOF

chmod +x backup.sh

# 添加到crontab（每天凌晨2点备份）
crontab -e
# 添加: 0 2 * * * /path/to/backup.sh
```

### 3. 性能监控

```bash
# 实时监控容器资源
docker stats

# 使用监控工具
# 选项1: Prometheus + Grafana
# 选项2: DataDog
# 选项3: New Relic
```

### 4. 健康检查

```bash
# 创建健康检查脚本
cat > health-check.sh << 'EOF'
#!/bin/bash
echo "Checking BotBot services..."

# 检查后端
if curl -f http://localhost:8000/ > /dev/null 2>&1; then
    echo "✅ Backend is healthy"
else
    echo "❌ Backend is down"
    docker-compose restart backend
fi

# 检查前端
if curl -f http://localhost:3000/ > /dev/null 2>&1; then
    echo "✅ Frontend is healthy"
else
    echo "❌ Frontend is down"
    docker-compose restart frontend
fi

# 检查MongoDB
if docker exec botbot-mongodb mongo --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    echo "✅ MongoDB is healthy"
else
    echo "❌ MongoDB is down"
    docker-compose restart mongodb
fi
EOF

chmod +x health-check.sh

# 定时执行（每5分钟）
*/5 * * * * /path/to/health-check.sh
```

### 5. 更新部署

```bash
# 拉取最新代码
git pull origin main

# 重新构建并重启
docker-compose down
docker-compose up -d --build

# 或使用零停机更新
docker-compose up -d --no-deps --build backend
docker-compose up -d --no-deps --build frontend
```

---

## 🆘 故障排查

### 快速诊断命令

```bash
# 一键诊断脚本
cat > diagnose.sh << 'EOF'
#!/bin/bash
echo "=== BotBot Diagnostics ==="
echo ""
echo "1. Docker Status:"
docker --version
docker-compose --version
echo ""
echo "2. Services Status:"
docker-compose ps
echo ""
echo "3. Disk Space:"
df -h | grep -E "Filesystem|/$"
echo ""
echo "4. Memory:"
free -h
echo ""
echo "5. Port Status:"
netstat -tlnp | grep -E "8000|3000|27017"
echo ""
echo "6. Container Logs (last 20 lines):"
echo "--- Backend ---"
docker-compose logs --tail=20 backend
echo "--- Frontend ---"
docker-compose logs --tail=20 frontend
echo "--- MongoDB ---"
docker-compose logs --tail=20 mongodb
EOF

chmod +x diagnose.sh
./diagnose.sh
```

---

## 📞 支持和文档

- **项目仓库**: https://github.com/zhaoshengbo/botbot
- **问题反馈**: 在GitHub提交Issue
- **API文档**: http://your-domain/docs
- **测试报告**: 查看 `test_report_final.md`

---

## 📝 变更日志

### v1.0.0 (2026-03-14)
- ✅ 核心业务API实现完成
- ✅ 13/13自动化测试通过
- ✅ Docker容器化部署
- ✅ 生产环境配置

---

**最后更新**: 2026-03-14
**维护者**: BotBot团队
