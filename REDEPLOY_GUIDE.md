# 🔄 BotBot 重新部署指南

## 📋 可用的部署脚本

| 脚本 | 用途 | 使用场景 |
|-----|------|---------|
| `./redeploy.sh` | 智能重新部署 | **代码更新后的常规部署（推荐）** |
| `./fix-api-url.sh` | 修复 API URL | 首次部署或 API 地址变更 |
| `./force-rebuild.sh` | 强制完全重建 | 构建出问题时完全重来 |
| `./check-deployment.sh` | 检查部署状态 | 验证部署是否成功 |

---

## 🚀 快速重新部署（推荐）

### 使用场景
- 修复了 bug 并推送了代码
- 添加了新功能
- 更新了配置
- 定期更新部署

### 使用方法

```bash
cd /root/botbot
./redeploy.sh
```

### 脚本会做什么

1. ✅ **检查 Git 状态** - 确认是否有更新
2. ✅ **拉取最新代码** - `git pull origin main`
3. ✅ **智能检测变更** - 自动识别前端/后端变更
4. ✅ **选择性重建** - 只重建变更的服务（节省时间）
5. ✅ **启动服务** - 使用正确的环境变量
6. ✅ **验证部署** - 检查容器状态和日志
7. ✅ **错误提示** - 显示错误日志（如果有）

---

## 📖 详细使用示例

### 示例 1: 前端代码更新

```bash
# 在服务器上
cd /root/botbot
./redeploy.sh
```

**输出**:
```
🚀 BotBot 重新部署脚本
========================================

1️⃣  检查 Git 状态...
⚠️  检测到远程有更新

2️⃣  拉取最新代码...
✅ 代码已更新到最新版本
   最新提交: c133af3 Fix React ESLint errors

3️⃣  分析代码变更...
📦 检测到前端代码变更

4️⃣  准备重新部署...
   前端 API URL: http://47.83.230.114:8000

确认开始部署? (y/n): y

5️⃣  停止相关服务...
Stopping botbot-frontend...

6️⃣  重新构建服务...
🔨 重新构建前端...
✅ 前端构建成功

7️⃣  启动服务...
Starting botbot-frontend...

8️⃣  等待服务启动 (15秒)...

9️⃣  检查服务状态...
NAME                STATUS
botbot-frontend     Up

🔟  验证部署...
📦 前端状态:
   ✅ 前端容器运行中
   ✅ 前端已启动
      ready - started server on 0.0.0.0:3000

========================================
✅ 重新部署完成！
```

### 示例 2: 后端代码更新

脚本会自动检测并只重建后端：

```bash
./redeploy.sh
```

**输出会显示**:
```
3️⃣  分析代码变更...
🔧 检测到后端代码变更

6️⃣  重新构建服务...
🔨 重新构建后端...
✅ 后端构建成功
```

### 示例 3: 前端和后端都更新

```bash
./redeploy.sh
```

脚本会重建两个服务。

### 示例 4: 没有检测到变更

如果代码没有变化，脚本会询问：

```
3️⃣  分析代码变更...
⚠️  未检测到代码变更，请选择要重新部署的服务:
   1) 仅前端
   2) 仅后端
   3) 前端和后端
   4) 取消
请选择 (1/2/3/4):
```

---

## 🎯 脚本特性

### 1. 智能变更检测

脚本会分析 Git 提交，自动识别：
- `fe/` 目录变更 → 重建前端
- `be/` 目录变更 → 重建后端
- `docker-compose.yml` 或 `.env` 变更 → 重启所有服务

### 2. 安全检查

- 部署前确认
- 本地未推送提交警告
- 构建失败自动停止

### 3. 环境变量处理

- 自动读取 `.env.production`
- 前端构建时传入 `NEXT_PUBLIC_API_URL`
- 支持环境变量覆盖

### 4. 部署验证

部署后自动检查：
- 容器运行状态
- 服务启动日志
- 错误日志（如果有）

---

## ⚙️ 高级用法

### 强制重新部署（没有变更）

```bash
./redeploy.sh
# 当提示"已是最新版本"时，输入 y 强制部署
```

### 仅重新部署前端

```bash
./redeploy.sh
# 选择选项 1
```

### 仅重新部署后端

```bash
./redeploy.sh
# 选择选项 2
```

### 查看详细日志

```bash
# 部署完成后
docker-compose logs -f frontend  # 前端日志
docker-compose logs -f backend   # 后端日志
docker-compose logs -f           # 所有日志
```

---

## 🐛 常见问题

### 问题 1: Git pull 失败

**错误**:
```
❌ Git pull 失败
```

**原因**: 本地有未提交的更改

**解决**:
```bash
# 查看本地更改
git status

# 选项 1: 提交本地更改
git add .
git commit -m "Local changes"
git push

# 选项 2: 放弃本地更改
git reset --hard origin/main

# 然后重新运行
./redeploy.sh
```

### 问题 2: 构建失败

**错误**:
```
❌ 前端构建失败！
```

**解决**:
```bash
# 查看详细构建日志
docker-compose build frontend

# 如果是依赖问题，使用强制重建
./force-rebuild.sh
```

### 问题 3: 服务启动但无响应

**症状**: 容器运行但访问不了

**解决**:
```bash
# 检查日志
docker-compose logs frontend | tail -50

# 检查端口
netstat -tuln | grep ":3000"

# 重启服务
docker-compose restart frontend
```

### 问题 4: API URL 不正确

**症状**: 前端连接不到后端

**解决**:
```bash
# 修复 API URL
./fix-api-url.sh

# 或手动修改
nano .env.production
# 改为: NEXT_PUBLIC_API_URL=http://47.83.230.114:8000

# 然后重新部署
./redeploy.sh
```

---

## 📊 部署流程图

```
开始
  ↓
检查 Git 状态
  ↓
有远程更新？ ──No──→ 询问是否强制部署
  ↓ Yes
git pull
  ↓
分析代码变更
  ↓
前端变更？后端变更？
  ↓
停止相关服务
  ↓
重建变更的服务
  ↓
启动所有服务
  ↓
等待启动（15秒）
  ↓
检查容器状态
  ↓
验证服务启动
  ↓
显示部署结果
  ↓
完成
```

---

## ✅ 部署后检查清单

使用 `./check-deployment.sh` 验证：

- [ ] 所有容器运行中（3 个 Up）
- [ ] 前端运行在生产模式
- [ ] 后端无错误日志
- [ ] API URL 配置正确
- [ ] 端口监听正常（3000, 8000）
- [ ] 浏览器可以访问
- [ ] 登录功能正常

---

## 🔧 与其他脚本的对比

### redeploy.sh vs fix-api-url.sh

| 特性 | redeploy.sh | fix-api-url.sh |
|-----|------------|---------------|
| 拉取最新代码 | ✅ | ✅ |
| 智能检测变更 | ✅ | ❌ |
| 配置 API URL | ✅ | ✅ (交互式) |
| 只重建变更部分 | ✅ | ❌ (总是重建前端) |
| 验证部署 | ✅ | ❌ |

**建议**:
- 首次部署 → `fix-api-url.sh`
- 代码更新 → `redeploy.sh`

### redeploy.sh vs force-rebuild.sh

| 特性 | redeploy.sh | force-rebuild.sh |
|-----|------------|-----------------|
| 智能重建 | ✅ | ❌ |
| 完全清除缓存 | ❌ | ✅ |
| 删除 Docker 镜像 | ❌ | ✅ |
| 速度 | 快 | 慢 |

**建议**:
- 常规更新 → `redeploy.sh`
- 出问题时 → `force-rebuild.sh`

---

## 💡 最佳实践

### 1. 开发流程

```bash
# 本地开发
git add .
git commit -m "Add new feature"
git push origin main

# 服务器部署
ssh root@47.83.230.114
cd /root/botbot
./redeploy.sh
```

### 2. 快速回滚

```bash
# 回滚到上一个版本
git reset --hard HEAD~1
./redeploy.sh
```

### 3. 定期更新

```bash
# 每天/每周运行一次
./redeploy.sh
```

### 4. 部署前测试

```bash
# 在本地测试
docker-compose -f docker-compose.dev.yml up

# 确认无误后推送
git push origin main

# 然后在服务器部署
./redeploy.sh
```

---

## 📞 需要帮助？

如果重新部署遇到问题：

```bash
# 收集诊断信息
./check-deployment.sh > deploy-status.log
docker-compose logs > docker-logs.log

# 查看日志
cat deploy-status.log
cat docker-logs.log
```

---

**使用 `./redeploy.sh` 让部署变得简单快捷！** 🚀
