# 🚨 生产环境登录问题快速修复

## 问题症状
- 在生产服务器 (http://botbot.biz:3000) 上无法登录
- 控制台显示请求 `http://localhost:8000/api/auth/direct-login`
- 错误信息: "Login failed" 或 "Network Error"

## 原因
前端配置使用了本地地址 `localhost:8000`，而不是生产服务器的后端地址。

---

## 🎯 快速修复（3 步骤）

### 在服务器上执行：

```bash
# 1. 进入项目目录
cd /root/botbot

# 2. 拉取最新代码
git pull origin main

# 3. 运行自动修复脚本
chmod +x fix-production.sh
./fix-production.sh
```

脚本会：
- ✅ 自动配置正确的后端地址
- ✅ 更新 CORS 设置
- ✅ 重新构建前端容器
- ✅ 重启所有服务

**完成！** 现在可以访问 http://botbot.biz:3000 测试登录了。

---

## 🔧 手动修复（如果自动脚本失败）

### 步骤 1: 更新前端配置

```bash
cd /root/botbot

# 创建生产环境配置
cat > fe/.env.production << 'EOF'
NEXT_PUBLIC_API_URL=http://botbot.biz:8000
NEXT_PUBLIC_APP_NAME=BotBot
EOF
```

### 步骤 2: 检查后端 CORS 配置

```bash
# 编辑后端环境变量
nano be/.env

# 确保包含以下配置
CORS_ORIGINS=["http://botbot.biz:3000","http://47.83.230.114:3000","http://localhost:3000"]
```

### 步骤 3: 重新部署

```bash
# 停止所有服务
docker-compose down

# 重新构建前端（清除缓存）
docker-compose build --no-cache frontend

# 启动服务
docker-compose up -d

# 查看启动状态
docker-compose ps

# 查看日志（如有问题）
docker-compose logs -f frontend
```

---

## ✅ 验证修复

### 1. 检查前端环境变量

```bash
# 进入前端容器查看环境变量
docker-compose exec frontend env | grep NEXT_PUBLIC_API_URL

# 应该输出: NEXT_PUBLIC_API_URL=http://botbot.biz:8000
```

### 2. 测试后端 API

```bash
# 测试后端健康检查
curl http://botbot.biz:8000/api/auth/me

# 或使用 IP
curl http://47.83.230.114:8000/api/auth/me
```

### 3. 浏览器测试

1. 访问 http://botbot.biz:3000
2. 按 F12 打开开发者工具
3. 切换到 "Network" 标签
4. 输入手机号并点击登录
5. 查看请求地址应该是 `http://botbot.biz:8000/api/auth/direct-login`

**成功标志**:
- ✅ 请求地址正确（不是 localhost）
- ✅ 返回状态码 200
- ✅ 成功跳转到首页

---

## 🔍 常见问题

### Q1: 修复后仍然失败？

```bash
# 清理浏览器缓存
# Chrome: Ctrl+Shift+Del → 清除缓存和 Cookie

# 或使用无痕模式测试
```

### Q2: 容器无法启动？

```bash
# 查看详细错误日志
docker-compose logs backend
docker-compose logs frontend

# 检查端口是否被占用
netstat -tlnp | grep -E '3000|8000'
```

### Q3: CORS 错误？

```bash
# 后端日志应该显示允许的源
docker-compose logs backend | grep CORS

# 确认 be/.env 中 CORS_ORIGINS 配置正确
cat be/.env | grep CORS_ORIGINS
```

### Q4: 前端构建失败？

```bash
# 清理并重新构建
docker-compose down
docker system prune -f
docker-compose build --no-cache
docker-compose up -d
```

---

## 📊 配置文件位置

```
botbot/
├── fe/.env.production          # 前端生产环境配置 ⭐
├── be/.env                     # 后端配置 ⭐
├── docker-compose.yml          # 开发环境
├── docker-compose.prod.yml     # 生产环境
├── fix-production.sh           # 自动修复脚本
└── DEPLOYMENT.md               # 完整部署指南
```

---

## 💡 最佳实践

### 使用域名（推荐）
```env
NEXT_PUBLIC_API_URL=http://botbot.biz:8000
```

✅ 优点:
- 更专业
- 便于记忆
- IP 变更无需修改

### 使用 IP 地址
```env
NEXT_PUBLIC_API_URL=http://47.83.230.114:8000
```

✅ 优点:
- 无需配置 DNS
- 直接访问

---

## 🎯 下一步优化

修复完成后，可以考虑：

1. **配置 Nginx 反向代理** - 隐藏端口号
2. **启用 HTTPS** - 使用 Let's Encrypt 免费证书
3. **配置域名 DNS** - 将 botbot.biz 解析到服务器
4. **设置防火墙** - 限制端口访问
5. **配置日志监控** - 及时发现问题

详细步骤见 `DEPLOYMENT.md`

---

## 📞 需要帮助？

如果问题仍未解决，请提供：
1. `docker-compose ps` 输出
2. `docker-compose logs frontend` 日志
3. 浏览器控制台错误截图
4. `fe/.env.production` 文件内容

**祝修复顺利！** 🚀
