# Nginx 反向代理配置

本目录包含 BotBot 项目的 Nginx 配置，用于通过域名 `botbot.biz` 访问前后端服务。

## 目录结构

```
nginx/
├── nginx.conf              # 主配置文件
├── conf.d/
│   └── botbot.conf        # BotBot 站点配置
└── README.md              # 本文档
```

## 本地开发配置

### 1. 配置 hosts 文件

在本地开发环境中，需要将域名指向本地：

**macOS / Linux:**
```bash
sudo vim /etc/hosts
```

添加以下行：
```
127.0.0.1 botbot.biz
127.0.0.1 www.botbot.biz
```

**Windows:**
```powershell
# 以管理员身份运行记事本
notepad C:\Windows\System32\drivers\etc\hosts
```

添加相同的行。

### 2. 启动服务

```bash
# 启动所有服务（包括 nginx）
docker-compose up -d

# 查看日志
docker-compose logs -f nginx

# 查看所有服务状态
docker-compose ps
```

### 3. 访问应用

- **前端**: http://botbot.biz
- **后端 API**: http://botbot.biz/api
- **API 文档**: http://botbot.biz/docs
- **健康检查**: http://botbot.biz/health

### 4. 测试连接

```bash
# 测试 Nginx 健康检查
curl http://botbot.biz/health

# 测试后端 API
curl http://botbot.biz/api/health

# 测试前端
curl http://botbot.biz
```

## 架构说明

### 服务端口映射

- **外部访问** (通过 Nginx):
  - HTTP: `80` → Nginx
  - HTTPS: `443` → Nginx (预留，生产环境使用)

- **内部服务** (仅容器网络可访问):
  - Backend: `8000` (不对外暴露)
  - Frontend: `3000` (不对外暴露)
  - MongoDB: `27017` (对外暴露，用于本地调试)

### 请求流程

```
客户端 → Nginx (80) → 根据路径路由:
                     ├─ /api/*      → Backend (8000)
                     ├─ /docs       → Backend (8000)
                     ├─ /openapi.json → Backend (8000)
                     └─ /*          → Frontend (3000)
```

## 配置详情

### nginx.conf

主配置文件，包含：
- Worker 进程配置
- 日志格式
- Gzip 压缩
- 文件上传大小限制 (20MB)

### conf.d/botbot.conf

站点配置文件，包含：
- Upstream 定义 (backend, frontend)
- 反向代理规则
- CORS 头设置
- WebSocket 支持 (用于 Next.js HMR)
- 静态资源缓存

## 生产环境配置

### HTTPS 证书配置 (生产环境)

1. **获取 SSL 证书**:
```bash
# 使用 Let's Encrypt Certbot
certbot certonly --standalone -d botbot.biz -d www.botbot.biz
```

2. **更新 botbot.conf**，添加 HTTPS server 块:
```nginx
server {
    listen 443 ssl http2;
    server_name botbot.biz www.botbot.biz;

    ssl_certificate /etc/letsencrypt/live/botbot.biz/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/botbot.biz/privkey.pem;
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers HIGH:!aNULL:!MD5;

    # ... 其余配置同 HTTP server 块
}

# HTTP 重定向到 HTTPS
server {
    listen 80;
    server_name botbot.biz www.botbot.biz;
    return 301 https://$server_name$request_uri;
}
```

3. **挂载证书到容器**，更新 docker-compose.yml:
```yaml
nginx:
  volumes:
    - /etc/letsencrypt:/etc/letsencrypt:ro
```

### 环境变量

更新 `.env` 文件：
```bash
# 生产环境 API URL
NEXT_PUBLIC_API_URL=https://botbot.biz
```

## 故障排查

### 查看 Nginx 日志
```bash
# 访问日志
docker-compose logs nginx

# 进入容器查看详细日志
docker exec -it botbot-nginx sh
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log
```

### 测试配置
```bash
# 测试 Nginx 配置语法
docker exec botbot-nginx nginx -t

# 重载配置（不重启）
docker exec botbot-nginx nginx -s reload
```

### 常见问题

**1. 502 Bad Gateway**
- 检查 backend/frontend 服务是否运行: `docker-compose ps`
- 检查容器网络连接: `docker network inspect botbot_botbot-network`

**2. CORS 错误**
- 检查 backend CORS 配置
- 查看浏览器控制台的具体错误信息

**3. 无法访问 botbot.biz**
- 确认 hosts 文件已正确配置
- 清除浏览器缓存和 DNS 缓存:
  ```bash
  # macOS
  sudo dscacheutil -flushcache; sudo killall -HUP mDNSResponder

  # Linux
  sudo systemd-resolve --flush-caches

  # Windows
  ipconfig /flushdns
  ```

**4. Next.js HMR 不工作**
- 确认 WebSocket 连接正常
- 检查 Nginx upstream 配置中的 `Connection "upgrade"` 设置

## 性能优化

当前配置已包含：
- ✅ Gzip 压缩
- ✅ 静态资源缓存 (30天)
- ✅ Keepalive 连接
- ✅ TCP 优化 (tcp_nopush, tcp_nodelay)

可选优化：
- 启用 HTTP/2
- 配置浏览器缓存策略
- 添加 CDN (生产环境)
- 配置 Rate Limiting

## 维护

### 更新配置后重启
```bash
# 重启 Nginx
docker-compose restart nginx

# 或重新构建并启动所有服务
docker-compose down
docker-compose up -d
```

### 查看服务状态
```bash
docker-compose ps
docker stats
```

### 清理日志
```bash
# 清空 Nginx 日志卷
docker volume rm botbot_nginx_logs
docker-compose up -d
```
