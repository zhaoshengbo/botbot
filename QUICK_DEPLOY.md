# ⚡ 快速部署参考卡

## 🚨 遇到问题？选择对应的修复脚本

| 问题症状 | 使用脚本 | 说明 |
|---------|---------|------|
| `ChunkLoadError: Loading chunk failed` | `./fix-chunk-error.sh` | 前端资源加载超时 |
| `net::ERR_CONNECTION_REFUSED` | `./fix-api-url.sh` | API URL 配置错误 |
| CORS 跨域错误 | `./fix-production.sh` | 后端 CORS 配置 |

---

## 🎯 完整部署流程（服务器上执行）

```bash
cd /root/botbot
git pull origin main

# 一键修复所有问题
./fix-api-url.sh       # 配置 API URL
# 或
./fix-chunk-error.sh   # 包含 API URL 配置
```

---

## 📋 详细文档索引

| 文档 | 用途 |
|-----|------|
| **API_URL_FIX.md** | 修复 API 连接错误详细指南 |
| **CHUNK_ERROR_FIX.md** | 修复前端加载超时详细指南 |
| **CORS_FIX.md** | 修复跨域问题详细指南 |
| **DEPLOY_NOW.md** | 完整部署指南 |

---

## ⚡ 命令速查

### 检查状态

```bash
# 查看容器状态
docker-compose ps

# 查看前端日志
docker-compose logs -f frontend

# 查看后端日志
docker-compose logs -f backend

# 检查 API URL 配置
docker-compose exec frontend printenv | grep NEXT_PUBLIC_API_URL
```

### 重启服务

```bash
# 重启单个服务
docker-compose restart frontend
docker-compose restart backend

# 重启所有服务
docker-compose restart

# 停止并重新启动
docker-compose down
docker-compose up -d
```

### 强制重新构建

```bash
# 清除缓存
rm -rf fe/.next fe/node_modules/.cache

# 重新构建前端
export NEXT_PUBLIC_API_URL=http://botbot.biz:8000
docker-compose build --no-cache --build-arg NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL frontend

# 启动
docker-compose --env-file .env.production up -d
```

---

## ✅ 快速验证清单

部署后快速验证：

```bash
# 1. 容器运行中
docker-compose ps | grep "Up"

# 2. API URL 正确
docker-compose exec frontend printenv | grep NEXT_PUBLIC_API_URL

# 3. 前端是生产模式
docker-compose logs frontend | grep "Environment: production"

# 4. 后端正常启动
docker-compose logs backend | grep "Application startup complete"
```

浏览器验证：

1. ✅ 访问 http://47.83.230.114:3000 或 http://botbot.biz:3000
2. ✅ F12 → Network 标签，API 请求地址正确
3. ✅ 登录功能正常
4. ✅ 页面加载快速（< 2秒）

---

## 🆘 紧急修复

如果一切都不工作：

```bash
# 完全清理重来
docker-compose down -v
docker system prune -f
rm -rf fe/.next fe/node_modules/.cache

# 重新拉取代码
git fetch origin
git reset --hard origin/main

# 配置 API URL
echo 'NEXT_PUBLIC_API_URL=http://botbot.biz:8000' > .env.production

# 重新构建一切
export NEXT_PUBLIC_API_URL=http://botbot.biz:8000
docker-compose build --no-cache --build-arg NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL
docker-compose --env-file .env.production up -d

# 等待并查看日志
sleep 20
docker-compose logs --tail=50
```

---

## 📞 常见错误速查

| 错误 | 原因 | 解决 |
|-----|------|------|
| `ChunkLoadError: timeout` | 前端使用开发模式 | `./fix-chunk-error.sh` |
| `net::ERR_CONNECTION_REFUSED` | API URL = localhost | `./fix-api-url.sh` |
| `CORS policy blocked` | CORS 未配置 | 检查 be/.env 的 CORS_ORIGINS |
| `NameError: Optional not defined` | Python 导入缺失 | `git pull` 获取修复 |
| 502 Bad Gateway | 后端未启动 | `docker-compose restart backend` |
| 容器不断重启 | 启动脚本错误 | `docker-compose logs backend` |

---

## 🎓 关键知识点

### Next.js 环境变量

```bash
# ❌ 错误：运行时设置无效
docker-compose up -d

# ✅ 正确：构建时传入
docker-compose build --build-arg NEXT_PUBLIC_API_URL=http://botbot.biz:8000 frontend
```

### Docker 缓存

```bash
# 完全清除缓存重建
docker-compose build --no-cache frontend
```

### 环境文件优先级

```bash
# 使用指定的环境文件
docker-compose --env-file .env.production up -d
```

---

**保存此文件作为快速参考！** 📌
