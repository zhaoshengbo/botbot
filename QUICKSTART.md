# BotBot 快速开始指南

## 🚀 快速启动（通过域名访问）

### 1. 配置本地域名

```bash
# 自动配置 hosts 文件（需要 sudo 权限）
./setup-local-domain.sh
```

这将在 `/etc/hosts` 中添加：
```
127.0.0.1 botbot.biz
127.0.0.1 www.botbot.biz
```

### 2. 启动服务

```bash
# 启动所有服务（MongoDB + Backend + Frontend + Nginx）
docker-compose up -d

# 查看服务状态
docker-compose ps

# 查看日志
docker-compose logs -f
```

### 3. 访问应用

**通过域名访问（推荐）：**
- 🌐 **前端**: http://botbot.biz
- 🔌 **后端 API**: http://botbot.biz/api
- 📚 **API 文档**: http://botbot.biz/docs
- ❤️ **健康检查**: http://botbot.biz/health

**直接访问端口（备用）：**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- MongoDB: mongodb://localhost:27017

### 4. 验证配置

```bash
# 运行自动测试脚本
./test-nginx-setup.sh
```

## 📁 项目结构

```
botbot/
├── be/                         # 后端 (Python/FastAPI)
├── fe/                         # 前端 (Next.js/React)
├── nginx/                      # Nginx 反向代理配置
│   ├── nginx.conf             # 主配置
│   ├── conf.d/botbot.conf     # 站点配置
│   └── README.md              # 详细文档
├── docker-compose.yml          # Docker 编排
└── QUICKSTART.md              # 本文档
```

## 🌐 Nginx 架构

### 路由规则

```
客户端请求 → Nginx (80/443)
              │
              ├─ /api/*         → Backend:8000
              ├─ /docs          → Backend:8000
              └─ /*             → Frontend:3000
```

## 📝 常见操作

### 测试 API

```bash
# 健康检查
curl http://botbot.biz/health

# 后端 API
curl http://botbot.biz/api/health
```

## 📚 更多文档

- **Nginx 详细配置**: `nginx/README.md`
- **项目架构**: `CLAUDE.md`
- **API 文档**: http://botbot.biz/docs
