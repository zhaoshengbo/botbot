# 🚀 BotBot 生产环境部署指南

## ✅ 所有问题已修复

最新代码已经修复了所有已知问题：

1. ✅ **ChunkLoadError** - 前端加载超时
2. ✅ **net::ERR_CONNECTION_REFUSED** - API URL 配置错误
3. ✅ **Backend NameError** - Optional 导入缺失
4. ✅ **CORS parsing error** - Pydantic 无法解析 JSON 数组
5. ✅ **React ESLint errors** - useEffect 依赖和引号转义

---

## 📦 一键部署（推荐）

SSH 到生产服务器，执行以下命令：

```bash
cd /root/botbot
git pull origin main
./fix-api-url.sh
```

### 脚本会做什么：

1. 询问你的后端 API 地址（域名或 IP）
2. 配置环境变量
3. 停止旧服务
4. 清除构建缓存
5. 重新构建前端（传入正确的 API URL）
6. 启动所有服务
7. 验证部署状态

### API 地址选择：

**选项 1: 使用域名（推荐）**
```
http://botbot.biz:8000
```

**选项 2: 使用 IP 地址**
```
http://47.83.230.114:8000
```

---

## 🔍 部署后检查

### 1. 运行自动检查脚本

```bash
./check-deployment.sh
```

这个脚本会自动验证：
- ✅ 容器运行状态（应该有 3 个容器 Up）
- ✅ API URL 配置（不应该是 localhost）
- ✅ 前端运行模式（应该是 production）
- ✅ 后端启动状态
- ✅ CORS 配置
- ✅ 端口监听（3000 和 8000）
- ✅ API 连接测试
- ✅ 错误日志检查

### 2. 手动验证

#### 检查容器状态

```bash
docker-compose ps
```

应该看到：
```
NAME                 STATUS
botbot-frontend      Up
botbot-backend       Up
botbot-mongodb       Up
```

#### 检查前端配置

```bash
# 查看 API URL（不应该是 localhost）
docker-compose exec frontend printenv NEXT_PUBLIC_API_URL

# 查看运行模式（应该是 production）
docker-compose logs frontend | grep "Environment:"
```

#### 查看日志

```bash
# 前端日志
docker-compose logs -f frontend

# 后端日志
docker-compose logs -f backend
```

---

## 🎯 预期结果

### 前端日志应该显示：

```
✓ Ready in 234ms
▲ Next.js 14.1.0
- Local:        http://localhost:3000
- Environment:  production

ready - started server on 0.0.0.0:3000
```

**关键点**:
- ✅ `Environment: production`（不是 development）
- ✅ 启动时间快（< 1 秒）

### 后端日志应该显示：

```
🌐 CORS Origins: ['http://botbot.biz:3000', 'http://47.83.230.114:3000']
INFO:     Started server process [1]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

**关键点**:
- ✅ CORS Origins 包含你的域名/IP
- ✅ Application startup complete
- ✅ 没有 NameError 或其他错误

### 浏览器测试应该：

1. **访问前端**: http://47.83.230.114:3000 或 http://botbot.biz:3000
2. **F12 打开开发者工具**
3. **清除缓存**: Ctrl+Shift+Del
4. **硬刷新**: Ctrl+F5
5. **查看 Network 标签**
6. **尝试登录**

**应该看到**:
```
✅ POST http://botbot.biz:8000/api/auth/send-code
✅ Status: 200 OK
✅ Response time: < 500ms
✅ No CORS errors
✅ No ChunkLoadError
```

**不应该看到**:
```
❌ POST http://localhost:8000/api/auth/send-code
❌ net::ERR_CONNECTION_REFUSED
❌ ChunkLoadError: Loading chunk failed
❌ CORS policy blocked
```

---

## 🛠️ 可用工具

| 脚本 | 用途 | 使用场景 |
|-----|------|---------|
| `./fix-api-url.sh` | 修复 API URL 配置 | 前端连接不到后端 |
| `./fix-chunk-error.sh` | 修复 ChunkLoadError | 前端资源加载超时 |
| `./check-deployment.sh` | 检查部署状态 | 验证部署是否成功 |
| `./fix-production.sh` | 修复 CORS 配置 | 跨域错误 |

---

## 🐛 常见问题

### 问题 1: 前端构建失败

**错误**:
```
Failed to compile
Error: ...
```

**原因**: 代码有语法错误或 ESLint 错误

**解决**:
```bash
# 拉取最新代码（已修复所有 ESLint 错误）
git pull origin main

# 清除缓存
rm -rf fe/.next fe/node_modules/.cache

# 重新构建
docker-compose build --no-cache frontend
```

### 问题 2: 后端启动失败

**错误**:
```
pydantic_settings.sources.SettingsError: error parsing value for field "CORS_ORIGINS"
```

**原因**: CORS_ORIGINS 配置格式错误

**解决**:
```bash
# 检查配置
cat be/.env | grep CORS_ORIGINS

# 确保使用以下格式之一：
# 格式 1: JSON 数组
CORS_ORIGINS=["http://botbot.biz:3000","http://47.83.230.114:3000"]

# 格式 2: 逗号分隔
CORS_ORIGINS=http://botbot.biz:3000,http://47.83.230.114:3000

# 格式 3: 单个地址
CORS_ORIGINS=http://botbot.biz:3000

# 重启后端
docker-compose restart backend
```

### 问题 3: API 请求还是 localhost

**错误**:
```
POST http://localhost:8000/api/auth/send-code
net::ERR_CONNECTION_REFUSED
```

**原因**: 前端构建时没有传入正确的 API URL

**解决**:
```bash
# 使用修复脚本（会重新构建）
./fix-api-url.sh
```

### 问题 4: 浏览器缓存旧版本

**症状**: 修复后浏览器还是显示旧的错误

**解决**:
1. 清除浏览器缓存（Ctrl+Shift+Del）
2. 勾选"缓存的图像和文件"
3. 清除数据
4. 关闭浏览器
5. 重新打开并访问

---

## 📊 性能指标

部署成功后，应该达到以下性能指标：

| 指标 | 目标值 | 如何测试 |
|-----|-------|---------|
| 首次加载时间 | < 2秒 | 浏览器 Network 标签 |
| API 响应时间 | < 500ms | 浏览器 Network 标签 |
| Chunk 加载成功率 | 100% | 无 ChunkLoadError |
| 容器启动时间 | < 30秒 | `time docker-compose up -d` |
| 内存占用（前端） | < 200MB | `docker stats botbot-frontend` |
| 内存占用（后端） | < 300MB | `docker stats botbot-backend` |

---

## ✅ 完整检查清单

部署完成后，确认所有项目：

**代码和配置**:
- [ ] `git pull origin main` 成功，代码是最新的
- [ ] `.env.production` 文件存在且配置正确
- [ ] `be/.env` 中 CORS_ORIGINS 配置正确

**构建和部署**:
- [ ] 前端构建成功（没有 ESLint 错误）
- [ ] 后端启动成功（没有 Python 错误）
- [ ] 所有容器正在运行（docker-compose ps 显示 3 个 Up）

**功能验证**:
- [ ] 前端环境变量正确（不是 localhost）
- [ ] 前端运行在生产模式（Environment: production）
- [ ] 后端 CORS 配置显示在日志中
- [ ] 没有 ChunkLoadError
- [ ] 没有 CORS 错误
- [ ] 没有 API 连接错误

**浏览器测试**:
- [ ] 可以访问前端页面
- [ ] 登录功能正常
- [ ] API 请求地址正确（不是 localhost）
- [ ] 页面加载速度快（< 2秒）
- [ ] Network 标签没有错误

**性能测试**:
- [ ] 首次加载 < 2 秒
- [ ] API 响应 < 500ms
- [ ] 容器内存占用正常

---

## 📚 相关文档

| 文档 | 用途 |
|-----|------|
| **QUICK_DEPLOY.md** | 快速部署参考卡 |
| **API_URL_FIX.md** | API 连接错误详细修复 |
| **CHUNK_ERROR_FIX.md** | ChunkLoadError 详细修复 |
| **CORS_FIX.md** | CORS 跨域问题解决 |

---

## 🆘 需要帮助？

如果部署遇到问题，运行诊断脚本：

```bash
# 收集完整的诊断信息
echo "=== Git Info ===" > deploy-debug.log
git log --oneline -5 >> deploy-debug.log
echo "" >> deploy-debug.log

echo "=== Container Status ===" >> deploy-debug.log
docker-compose ps >> deploy-debug.log
echo "" >> deploy-debug.log

echo "=== Environment Variables ===" >> deploy-debug.log
cat .env.production >> deploy-debug.log
echo "" >> deploy-debug.log

echo "=== Frontend Logs ===" >> deploy-debug.log
docker-compose logs --tail=100 frontend >> deploy-debug.log
echo "" >> deploy-debug.log

echo "=== Backend Logs ===" >> deploy-debug.log
docker-compose logs --tail=100 backend >> deploy-debug.log

cat deploy-debug.log
```

---

## 🎉 部署成功！

如果所有检查都通过，恭喜你成功部署了 BotBot！

**访问地址**:
- 前端: http://47.83.230.114:3000 或 http://botbot.biz:3000
- 后端 API 文档: http://47.83.230.114:8000/docs 或 http://botbot.biz:8000/docs

**后续工作**:
- 配置 Nginx 反向代理（可选）
- 设置 HTTPS（推荐）
- 配置域名 DNS
- 设置自动备份
- 监控日志和性能

享受你的 AI 虾粮龙虾市场吧！🦞🍤
