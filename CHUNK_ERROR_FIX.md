# 🔧 Frontend Chunk Loading Error 修复指南

## 问题描述

```
ChunkLoadError: Loading chunk app/layout failed.
(timeout: http://47.83.230.114:3000/_next/static/chunks/app/layout.js)
```

## 根本原因

前端在生产环境使用 **开发模式** (`npm run dev`) 运行，导致：

1. ❌ 没有预构建优化的静态资源
2. ❌ Chunk 文件不稳定，加载超时
3. ❌ 性能差，启动慢
4. ❌ `.next` 目录被 volume 挂载，build 不持久化

## 解决方案

将前端切换到 **生产模式** (`npm run build` + `npm start`)

---

## 🚀 快速修复（推荐）

在生产服务器上运行：

```bash
cd /root/botbot
git pull origin main
./fix-chunk-error.sh
```

脚本会自动：
1. 停止所有服务
2. 清除旧的 build 缓存
3. 重新构建前端（生产模式）
4. 启动所有服务
5. 验证部署状态

---

## 🔍 手动修复步骤

### 1. 更新代码

```bash
cd /root/botbot
git pull origin main
```

### 2. 停止服务

```bash
docker-compose down
```

### 3. 清除缓存

```bash
rm -rf fe/.next
rm -rf fe/node_modules/.cache
```

### 4. 重新构建前端

```bash
docker-compose build --no-cache frontend
```

### 5. 启动服务

```bash
docker-compose up -d
```

### 6. 检查状态

```bash
docker-compose ps
docker-compose logs frontend | tail -30
```

---

## 📋 修改内容说明

### 1. **fe/Dockerfile** - 多阶段构建

**之前**（开发模式）:
```dockerfile
CMD ["npm", "run", "dev"]
```

**现在**（生产模式）:
```dockerfile
# 多阶段构建
FROM node:20-alpine AS builder
RUN npm run build

FROM node:20-alpine AS runner
CMD ["node", "server.js"]
```

优点：
- ✅ 预构建所有 chunks
- ✅ 优化资源体积
- ✅ 更快的加载速度
- ✅ 稳定的静态资源

### 2. **fe/next.config.js** - Standalone 输出

添加：
```javascript
output: 'standalone'
```

这会生成独立的生产构建，包含所有必需文件。

### 3. **docker-compose.yml** - 移除开发配置

**之前**:
```yaml
volumes:
  - ./fe:/app
  - /app/node_modules
  - /app/.next
command: npm run dev
```

**现在**:
```yaml
# 没有 volumes（使用容器内的构建）
# 没有 command（使用 Dockerfile CMD）
```

### 4. **新增文件**

- `docker-compose.dev.yml` - 本地开发环境配置
- `fe/Dockerfile.dev` - 开发模式 Dockerfile
- `fix-chunk-error.sh` - 一键修复脚本

---

## 🎯 验证修复

### 1. 检查容器状态

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

### 2. 检查前端日志

```bash
docker-compose logs frontend | tail -20
```

应该看到：
```
✓ Ready in XXXms
▲ Next.js 14.1.0
- Local:        http://localhost:3000
- Environment:  production
```

**关键**: `Environment: production` (不是 development)

### 3. 浏览器测试

1. **清除缓存**: Ctrl+Shift+Del，清除所有缓存
2. **访问**: http://47.83.230.114:3000
3. **打开开发者工具**: F12
4. **检查 Network 标签**:
   - `_next/static/chunks/app/layout.js` 应该 **200 OK**
   - 加载时间应该 < 1秒

### 4. curl 测试

```bash
curl -I http://47.83.230.114:3000/_next/static/chunks/app/layout.js
```

应该返回：
```
HTTP/1.1 200 OK
Content-Type: application/javascript
```

---

## 🌐 开发 vs 生产环境

### 生产环境（服务器）

```bash
# 使用默认配置
docker-compose up -d
```

- ✅ 运行优化的生产构建
- ✅ 更快的加载速度
- ✅ 稳定的静态资源
- ❌ 代码修改需要重新构建

### 开发环境（本地）

```bash
# 使用开发配置
docker-compose -f docker-compose.dev.yml up -d
```

- ✅ 代码热重载
- ✅ 更好的调试体验
- ✅ 即时看到修改
- ❌ 性能较慢

---

## ⚡ 性能对比

| 指标 | 开发模式 | 生产模式 |
|-----|---------|---------|
| 首次加载 | 2-5秒 | 0.5-1秒 |
| Chunk 大小 | 未优化 | 压缩优化 |
| 启动时间 | 10-15秒 | 3-5秒 |
| 稳定性 | 可能超时 | 稳定 |
| 内存占用 | 较高 | 较低 |

---

## 🐛 常见问题

### 问题 1: 构建失败

**错误**:
```
npm ERR! Failed at the build script
```

**解决**:
```bash
# 清除所有 node_modules
docker-compose down
docker volume prune
docker-compose build --no-cache frontend
```

### 问题 2: 浏览器还是显示旧版本

**原因**: 浏览器缓存

**解决**:
1. 清除浏览器缓存（Ctrl+Shift+Del）
2. 强制刷新（Ctrl+F5）
3. 或使用隐私模式访问

### 问题 3: 还是有 ChunkLoadError

**检查清单**:

```bash
# 1. 确认容器在运行
docker-compose ps

# 2. 确认是生产模式
docker-compose logs frontend | grep "Environment"
# 应该显示: Environment: production

# 3. 检查 .next 目录
docker-compose exec frontend ls -la .next/
# 应该有 standalone 目录

# 4. 测试静态资源
curl -I http://47.83.230.114:3000/_next/static/chunks/app/layout.js
```

### 问题 4: 502 Bad Gateway

**原因**: 前端容器未启动或崩溃

**解决**:
```bash
docker-compose logs frontend
docker-compose restart frontend
```

---

## 📊 监控和日志

### 实时查看日志

```bash
# 所有服务
docker-compose logs -f

# 仅前端
docker-compose logs -f frontend

# 仅后端
docker-compose logs -f backend
```

### 检查资源使用

```bash
docker stats botbot-frontend
```

---

## 🔄 回滚到开发模式（仅本地）

如果需要在服务器上临时使用开发模式：

```bash
cd /root/botbot

# 使用开发配置
docker-compose -f docker-compose.dev.yml up -d
```

**警告**: 不推荐在生产环境使用开发模式！

---

## ✅ 修复完成检查清单

- [ ] git pull 拉取最新代码
- [ ] docker-compose down 停止服务
- [ ] 清除 fe/.next 缓存
- [ ] docker-compose build --no-cache frontend 重新构建
- [ ] docker-compose up -d 启动服务
- [ ] 日志显示 "Environment: production"
- [ ] 浏览器访问正常，无 ChunkLoadError
- [ ] 清除浏览器缓存后再次测试
- [ ] API 功能正常（登录、创建任务等）

---

## 📞 需要帮助？

如果问题仍未解决，请提供：

1. **前端日志**:
   ```bash
   docker-compose logs frontend > frontend.log
   ```

2. **容器状态**:
   ```bash
   docker-compose ps
   ```

3. **浏览器错误截图**:
   - F12 → Console 标签
   - F12 → Network 标签（显示失败的请求）

4. **构建输出**:
   ```bash
   docker-compose build frontend 2>&1 | tee build.log
   ```

---

**修复完成后，ChunkLoadError 应该彻底解决！** 🎉
