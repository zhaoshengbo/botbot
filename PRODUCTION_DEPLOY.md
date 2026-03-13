# 生产环境部署指南

## 快速部署

### 使用生产配置文件部署

```bash
# 1. 设置环境变量（可选，如有敏感信息）
export SECRET_KEY="your-production-secret-key"
export JWT_SECRET_KEY="your-production-jwt-secret-key"
export ANTHROPIC_API_KEY="your-anthropic-api-key"
export ALIYUN_ACCESS_KEY_ID="your-aliyun-access-key"
export ALIYUN_ACCESS_KEY_SECRET="your-aliyun-access-secret"

# 2. 使用生产配置启动
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build

# 3. 查看服务状态
docker-compose -f docker-compose.prod.yml ps

# 4. 查看日志
docker-compose -f docker-compose.prod.yml logs -f
```

## 配置说明

### CORS 跨域配置

生产环境已配置为 **支持所有来源的跨域访问**：

```yaml
environment:
  - CORS_ORIGINS=*
```

#### 如果需要限制特定域名

编辑 `docker-compose.prod.yml`，修改 `CORS_ORIGINS`：

```yaml
# 方式 1: 逗号分隔
- CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com,http://47.83.230.114:3000

# 方式 2: JSON 数组
- CORS_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]
```

### 环境变量

生产环境支持以下环境变量：

| 变量名 | 说明 | 默认值 | 是否必需 |
|--------|------|--------|----------|
| `SECRET_KEY` | 应用密钥 | `prod-secret-key-change-this` | ⚠️ 建议修改 |
| `JWT_SECRET_KEY` | JWT 签名密钥 | `prod-jwt-secret-key-change-this` | ⚠️ 建议修改 |
| `CORS_ORIGINS` | 允许的跨域来源 | `*` | ✅ 已配置 |
| `ANTHROPIC_API_KEY` | Claude API 密钥 | 空 | AI 功能需要 |
| `ALIYUN_ACCESS_KEY_ID` | 阿里云访问密钥 | 空 | SMS 功能需要 |
| `ALIYUN_ACCESS_KEY_SECRET` | 阿里云密钥 | 空 | SMS 功能需要 |
| `ALIYUN_SMS_SIGN_NAME` | 短信签名 | 空 | SMS 功能需要 |
| `ALIYUN_SMS_TEMPLATE_CODE` | 短信模板代码 | 空 | SMS 功能需要 |

### 设置环境变量的方式

#### 方式 1: 使用 export（推荐）

```bash
export SECRET_KEY="your-strong-secret-key-min-32-chars"
export JWT_SECRET_KEY="your-strong-jwt-secret-key-min-32-chars"
docker-compose -f docker-compose.prod.yml up -d
```

#### 方式 2: 在命令行直接指定

```bash
SECRET_KEY="your-key" JWT_SECRET_KEY="your-jwt-key" \
  docker-compose -f docker-compose.prod.yml up -d
```

#### 方式 3: 使用 .env 文件

```bash
# 创建 .env 文件
cat > .env << 'EOF'
SECRET_KEY=your-strong-secret-key-min-32-chars
JWT_SECRET_KEY=your-strong-jwt-secret-key-min-32-chars
ANTHROPIC_API_KEY=sk-ant-xxx
ALIYUN_ACCESS_KEY_ID=LTAI5xxx
ALIYUN_ACCESS_KEY_SECRET=xxx
EOF

# 部署
docker-compose -f docker-compose.prod.yml up -d
```

## 生产环境特性

### 与开发环境的区别

| 特性 | 开发环境 | 生产环境 |
|------|---------|---------|
| 重启策略 | `unless-stopped` | `always` |
| 热重载 | ✅ 启用 | ❌ 禁用 |
| Worker 数量 | 1 | 4 |
| 代码挂载 | ✅ 挂载本地代码 | ❌ 使用镜像内代码 |
| DEBUG 模式 | `True` | `False` |
| CORS | 所有来源 | 所有来源 |

### 性能优化

生产环境使用 4 个 Uvicorn worker：

```bash
command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

根据服务器 CPU 核心数，可以调整 `--workers` 数量：
- 推荐值：`2-4 × CPU 核心数`
- 最小值：2
- 最大值：根据内存限制

## 验证部署

### 1. 检查服务状态

```bash
docker-compose -f docker-compose.prod.yml ps
```

所有服务应该显示为 `Up`。

### 2. 检查后端健康状态

```bash
curl http://localhost:8000/health
# 应返回: {"status":"healthy"}
```

### 3. 检查前端

```bash
curl -I http://localhost:3000
# 应返回: HTTP/1.1 200 OK
```

### 4. 验证 CORS 配置

```bash
curl -X OPTIONS http://localhost:8000/api/auth/me \
  -H "Origin: http://any-domain.com" \
  -H "Access-Control-Request-Method: GET" \
  -i

# 检查响应头应包含:
# Access-Control-Allow-Origin: *
```

### 5. 查看 CORS 日志

```bash
docker-compose -f docker-compose.prod.yml logs backend | grep "CORS Origins"
# 应显示: 🌐 CORS Origins: ['*']
```

## 更新部署

### 使用 redeploy.sh 脚本

```bash
# 1. 拉取最新代码
git pull origin main

# 2. 使用生产配置重新部署
docker-compose -f docker-compose.prod.yml down
docker-compose -f docker-compose.prod.yml up -d --build

# 3. 查看日志
docker-compose -f docker-compose.prod.yml logs -f
```

### 仅更新后端

```bash
docker-compose -f docker-compose.prod.yml stop backend
docker-compose -f docker-compose.prod.yml build backend
docker-compose -f docker-compose.prod.yml up -d backend
```

### 仅更新前端

```bash
docker-compose -f docker-compose.prod.yml stop frontend
docker-compose -f docker-compose.prod.yml build --no-cache frontend
docker-compose -f docker-compose.prod.yml up -d frontend
```

## 常用运维命令

### 查看日志

```bash
# 所有服务
docker-compose -f docker-compose.prod.yml logs -f

# 仅后端
docker-compose -f docker-compose.prod.yml logs -f backend

# 仅前端
docker-compose -f docker-compose.prod.yml logs -f frontend

# 最近 100 行
docker-compose -f docker-compose.prod.yml logs --tail=100
```

### 重启服务

```bash
# 重启所有服务
docker-compose -f docker-compose.prod.yml restart

# 重启指定服务
docker-compose -f docker-compose.prod.yml restart backend
docker-compose -f docker-compose.prod.yml restart frontend
```

### 停止服务

```bash
# 停止所有服务
docker-compose -f docker-compose.prod.yml down

# 停止并删除数据卷（危险操作！）
docker-compose -f docker-compose.prod.yml down -v
```

### 进入容器

```bash
# 进入后端容器
docker-compose -f docker-compose.prod.yml exec backend bash

# 进入前端容器
docker-compose -f docker-compose.prod.yml exec frontend sh

# 进入 MongoDB 容器
docker-compose -f docker-compose.prod.yml exec mongodb mongosh
```

### 清理资源

```bash
# 清理未使用的镜像
docker image prune -a

# 清理未使用的卷
docker volume prune

# 清理所有未使用的资源
docker system prune -a
```

## 数据备份

### 备份 MongoDB

```bash
# 创建备份目录
mkdir -p ./backups

# 备份数据库
docker-compose -f docker-compose.prod.yml exec -T mongodb \
  mongodump --db botbot --archive > ./backups/botbot-$(date +%Y%m%d-%H%M%S).archive

# 恢复数据库
docker-compose -f docker-compose.prod.yml exec -T mongodb \
  mongorestore --db botbot --archive < ./backups/botbot-20260313-120000.archive
```

## 安全建议

### 1. 修改默认密钥

⚠️ **务必修改以下密钥**：
- `SECRET_KEY`
- `JWT_SECRET_KEY`

生成强密钥的方法：

```bash
# 生成 32 字节随机密钥
openssl rand -hex 32

# 或使用 Python
python3 -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 2. MongoDB 认证

生产环境建议启用 MongoDB 认证。取消 `docker-compose.prod.yml` 中的注释：

```yaml
mongodb:
  environment:
    MONGO_INITDB_ROOT_USERNAME: admin
    MONGO_INITDB_ROOT_PASSWORD: your-strong-password
```

然后更新 backend 的 MongoDB URL：

```yaml
backend:
  environment:
    - MONGODB_URL=mongodb://admin:your-strong-password@mongodb:27017
```

### 3. 防火墙配置

确保服务器防火墙只开放必要的端口：
- 3000 (前端)
- 8000 (后端 API)
- 22 (SSH)

```bash
# 示例：使用 ufw
sudo ufw allow 22
sudo ufw allow 3000
sudo ufw allow 8000
sudo ufw enable
```

### 4. HTTPS 配置

生产环境建议使用 Nginx 或 Caddy 作为反向代理，配置 SSL/TLS：

```nginx
# Nginx 配置示例
server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    # 前端
    location / {
        proxy_pass http://localhost:3000;
    }

    # 后端 API
    location /api {
        proxy_pass http://localhost:8000;
    }
}
```

## 监控和告警

### 检查容器健康状态

```bash
# 每分钟检查一次
watch -n 60 'docker-compose -f docker-compose.prod.yml ps'
```

### 监控日志错误

```bash
# 实时监控错误日志
docker-compose -f docker-compose.prod.yml logs -f | grep -i error
```

### 资源使用情况

```bash
# 查看容器资源使用
docker stats
```

## 故障排查

### 问题 1: 服务无法启动

```bash
# 查看详细错误日志
docker-compose -f docker-compose.prod.yml logs backend
docker-compose -f docker-compose.prod.yml logs frontend

# 检查端口占用
netstat -tulpn | grep -E '3000|8000|27017'

# 重新构建
docker-compose -f docker-compose.prod.yml build --no-cache
docker-compose -f docker-compose.prod.yml up -d
```

### 问题 2: CORS 错误

```bash
# 1. 检查 CORS 配置
docker-compose -f docker-compose.prod.yml logs backend | grep CORS

# 2. 重启后端
docker-compose -f docker-compose.prod.yml restart backend

# 3. 验证 CORS 响应头
curl -I -X OPTIONS http://your-server:8000/api/auth/me \
  -H "Origin: http://test.com"
```

### 问题 3: MongoDB 连接失败

```bash
# 检查 MongoDB 状态
docker-compose -f docker-compose.prod.yml ps mongodb

# 进入 MongoDB 测试连接
docker-compose -f docker-compose.prod.yml exec mongodb mongosh

# 检查后端日志
docker-compose -f docker-compose.prod.yml logs backend | grep -i mongo
```

## 更新记录

- 2026-03-13: 初始版本，配置全局 CORS 支持

## 相关文档

- [CORS 配置说明](./CORS_CONFIG.md)
- [部署指南](./REDEPLOY_GUIDE.md)
- [项目说明](./CLAUDE.md)
