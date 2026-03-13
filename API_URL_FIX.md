# 🔧 前端 API URL 配置错误修复指南

## 问题描述

```
net::ERR_CONNECTION_REFUSED
http://localhost:8000/api/auth/send-code
```

或者在浏览器控制台看到：

```
Failed to fetch
POST http://localhost:8000/api/auth/send-code net::ERR_CONNECTION_REFUSED
```

## 根本原因

**问题**: 前端在生产环境使用了 `localhost:8000` 作为 API 地址

**原因**: Next.js 的环境变量是在构建时编译进代码的，如果构建时没有正确设置 `NEXT_PUBLIC_API_URL`，它会使用默认值 `http://localhost:8000`。

**影响**: 用户浏览器无法连接到后端 API（因为 localhost 指向用户自己的电脑，而不是服务器）

---

## 🚀 快速修复（一键）

在生产服务器上运行：

```bash
cd /root/botbot
git pull origin main
./fix-api-url.sh
```

脚本会：
1. ✅ 询问你的后端 API 地址
2. ✅ 创建正确的环境变量配置
3. ✅ 重新构建前端（传入正确的 API URL）
4. ✅ 重启所有服务

---

## 📋 手动修复步骤

### 1. 创建 .env.production 文件

在项目根目录创建 `.env.production`：

```bash
cd /root/botbot
nano .env.production
```

添加以下内容（根据你的实际情况选择）：

```env
# 使用域名（推荐）
NEXT_PUBLIC_API_URL=http://botbot.biz:8000

# 或使用 IP 地址
# NEXT_PUBLIC_API_URL=http://47.83.230.114:8000
```

### 2. 更新 fe/.env.production

```bash
nano fe/.env.production
```

```env
NEXT_PUBLIC_API_URL=http://botbot.biz:8000
NEXT_PUBLIC_APP_NAME=BotBot
```

### 3. 停止并清除缓存

```bash
docker-compose down
rm -rf fe/.next
rm -rf fe/node_modules/.cache
```

### 4. 重新构建前端

**重要**: 必须传入 build argument！

```bash
# 导出环境变量
export NEXT_PUBLIC_API_URL=http://botbot.biz:8000

# 重新构建（传入 build arg）
docker-compose build --no-cache \
  --build-arg NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL \
  frontend
```

### 5. 启动服务

```bash
docker-compose --env-file .env.production up -d
```

### 6. 验证配置

```bash
# 检查容器内的环境变量
docker-compose exec frontend printenv | grep NEXT_PUBLIC_API_URL

# 应该输出: NEXT_PUBLIC_API_URL=http://botbot.biz:8000
```

---

## 🔍 为什么需要在构建时设置？

Next.js 的 `NEXT_PUBLIC_*` 环境变量有特殊行为：

### ❌ 错误理解

```bash
# 这样不会生效！
docker-compose up -d  # 只在运行时设置环境变量
```

### ✅ 正确做法

```bash
# 必须在构建时传入！
docker-compose build --build-arg NEXT_PUBLIC_API_URL=http://botbot.biz:8000 frontend
docker-compose --env-file .env.production up -d
```

### 原因

Next.js 在构建时会：
1. 读取 `NEXT_PUBLIC_*` 环境变量
2. 将它们**硬编码**到生成的 JavaScript 代码中
3. 生成静态资源文件

所以运行时改变环境变量无效，必须重新构建！

---

## 🎯 验证修复

### 1. 检查构建配置

```bash
# 查看 Dockerfile 是否接收 build arg
grep "ARG NEXT_PUBLIC_API_URL" fe/Dockerfile
# 应该输出: ARG NEXT_PUBLIC_API_URL

# 查看 docker-compose.yml 是否传入 build arg
grep -A 5 "build:" docker-compose.yml | grep args
```

### 2. 检查容器环境变量

```bash
docker-compose exec frontend printenv | grep NEXT_PUBLIC_API_URL
```

应该输出你配置的 API URL，例如：
```
NEXT_PUBLIC_API_URL=http://botbot.biz:8000
```

### 3. 浏览器测试

1. **打开浏览器开发者工具** (F12)
2. **清除缓存** (Ctrl+Shift+Del)
3. **访问网站**
4. **打开 Network 标签**
5. **尝试登录**
6. **查看 API 请求**

应该看到：
```
POST http://botbot.biz:8000/api/auth/send-code
Status: 200 OK
```

**不应该看到**:
```
POST http://localhost:8000/api/auth/send-code
Status: net::ERR_CONNECTION_REFUSED
```

---

## 🐛 常见问题

### 问题 1: 构建后还是 localhost

**原因**: 构建时没有传入 build argument

**解决**:
```bash
# 确保使用 --build-arg
export NEXT_PUBLIC_API_URL=http://botbot.biz:8000
docker-compose build --build-arg NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL frontend
```

### 问题 2: docker-compose up 后又变回 localhost

**原因**: 每次 up 都会使用默认环境变量

**解决**:
```bash
# 使用 --env-file 指定环境文件
docker-compose --env-file .env.production up -d
```

### 问题 3: 已经设置了环境变量但不生效

**原因**: Next.js 缓存了旧的构建

**解决**:
```bash
# 完全清除缓存
docker-compose down
rm -rf fe/.next fe/node_modules/.cache
docker rmi botbot-frontend  # 删除旧镜像

# 重新构建
export NEXT_PUBLIC_API_URL=http://botbot.biz:8000
docker-compose build --no-cache --build-arg NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL frontend
docker-compose --env-file .env.production up -d
```

### 问题 4: 浏览器还是显示 localhost

**原因**: 浏览器缓存了旧的 JavaScript 文件

**解决**:
1. 清除浏览器缓存 (Ctrl+Shift+Del)
2. 勾选 "缓存的图像和文件"
3. 清除数据
4. 关闭浏览器
5. 重新打开并访问

---

## 📊 配置流程图

```
1. 创建 .env.production
   ↓
2. 设置 NEXT_PUBLIC_API_URL=http://botbot.biz:8000
   ↓
3. docker-compose build --build-arg NEXT_PUBLIC_API_URL=...
   ↓
4. Next.js 编译时将 API URL 编译进代码
   ↓
5. 生成包含正确 API URL 的静态文件
   ↓
6. docker-compose --env-file .env.production up -d
   ↓
7. 浏览器访问，JavaScript 代码使用正确的 API URL
   ↓
8. ✅ API 请求成功！
```

---

## 🎓 技术说明

### Next.js 环境变量的两种类型

#### 1. 服务端环境变量（不需要 NEXT_PUBLIC 前缀）

```env
DATABASE_URL=...
SECRET_KEY=...
```

- ✅ 只在服务端可用
- ✅ 不会暴露给浏览器
- ✅ 可以在运行时修改

#### 2. 浏览器环境变量（需要 NEXT_PUBLIC 前缀）

```env
NEXT_PUBLIC_API_URL=...
NEXT_PUBLIC_APP_NAME=...
```

- ✅ 在浏览器中可用
- ⚠️ 会暴露给用户
- ❌ 构建时固定，运行时不能修改
- **必须在构建时设置！**

---

## ✅ 完整修复检查清单

部署前检查：

- [ ] 已创建 `.env.production` 文件
- [ ] 已设置正确的 `NEXT_PUBLIC_API_URL`
- [ ] `fe/Dockerfile` 包含 `ARG NEXT_PUBLIC_API_URL`
- [ ] `docker-compose.yml` 在 build args 中传入环境变量
- [ ] 已运行 `git pull origin main` 获取最新代码

构建和部署：

- [ ] 已停止旧容器 `docker-compose down`
- [ ] 已清除缓存 `rm -rf fe/.next`
- [ ] 使用 `--build-arg` 构建前端
- [ ] 使用 `--env-file` 启动服务
- [ ] 容器内环境变量正确

验证：

- [ ] `docker-compose exec frontend printenv` 显示正确 API URL
- [ ] 浏览器 Network 标签显示正确 API 地址
- [ ] 登录功能正常
- [ ] 没有 ERR_CONNECTION_REFUSED 错误

---

## 📚 相关文档

- **CHUNK_ERROR_FIX.md** - ChunkLoadError 修复
- **CORS_FIX.md** - CORS 跨域问题
- **DEPLOY_NOW.md** - 完整部署指南

---

## 🆘 仍然无法解决？

提供以下信息：

```bash
# 1. 环境变量配置
cat .env.production

# 2. 容器环境变量
docker-compose exec frontend printenv | grep NEXT_PUBLIC

# 3. 构建日志
docker-compose build frontend 2>&1 | tail -50

# 4. 运行日志
docker-compose logs frontend | tail -50

# 5. 浏览器 Network 请求截图
# F12 → Network 标签，显示失败的 API 请求
```

---

**正确配置 API URL 后，所有 API 请求都应该正常工作！** 🎉
