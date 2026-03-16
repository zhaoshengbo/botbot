# 🚀 BotBot 快速启动指南

## 前置条件

- Docker & Docker Compose
- Git

## 快速启动（5分钟）

### 1. 克隆项目

```bash
git clone <your-repo-url>
cd botbot
```

### 2. 配置环境变量

**后端配置**:
```bash
cd be
cp .env.example .env
# .env 文件已配置为开发模式（DEBUG=True），可以直接使用
```

**前端配置**:
```bash
cd ../fe
cp .env.example .env
# 默认配置已经可用，指向 http://localhost:8000
```

### 3. 启动服务

返回项目根目录并启动所有服务：

```bash
cd ..
docker-compose up -d
```

### 4. 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 只查看后端日志
docker-compose logs -f be

# 只查看前端日志
docker-compose logs -f fe
```

### 5. 访问应用

- **前端**: http://localhost:3000
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

## 开发模式特性

在 `DEBUG=True` 模式下：

✅ **无需真实配置**：
- SMS 服务使用 Mock（验证码固定为 `123456`）
- AI 服务如果没有 API key 会使用 Mock 数据
- 支付服务可以不配置

⚠️ **安全警告**：
- 使用默认密钥会显示警告，但不会阻止启动
- CORS 允许所有来源
- 这些配置仅用于开发，生产环境必须修改

## 常见问题

### 问题1: "ModuleNotFoundError: No module named 'alipay.aop'"

**解决方案**: 已修复！确保使用最新代码。

### 问题2: "CRITICAL SECURITY ERRORS - APPLICATION STARTUP BLOCKED"

**原因**: 生产模式下使用了弱密钥。

**解决方案**:
- **开发环境**: 确保 `.env` 中 `DEBUG=True`
- **生产环境**: 生成强密钥
  ```bash
  # 生成 SECRET_KEY
  openssl rand -hex 32

  # 生成 JWT_SECRET_KEY
  openssl rand -hex 32

  # 更新 .env 文件
  SECRET_KEY=<生成的密钥1>
  JWT_SECRET_KEY=<生成的密钥2>
  DEBUG=False
  ```

### 问题3: MongoDB 连接失败

**检查**:
```bash
docker-compose ps
# 确保 mongodb 容器正在运行

docker-compose logs mongodb
# 查看 MongoDB 日志
```

### 问题4: 前端无法连接后端

**检查 API 地址**:
```bash
# 前端 .env 文件
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 停止服务

```bash
# 停止但保留数据
docker-compose stop

# 停止并删除容器（数据卷保留）
docker-compose down

# 停止并删除所有数据
docker-compose down -v
```

## 重新构建

如果修改了依赖（requirements.txt 或 package.json）：

```bash
# 重新构建所有服务
docker-compose build

# 重新构建特定服务
docker-compose build be
docker-compose build fe

# 重新构建并启动
docker-compose up -d --build
```

## 测试登录

1. 访问 http://localhost:3000
2. 点击"登录"
3. 输入任意手机号（例如：`13800138000`）
4. 验证码使用 `123456`（DEBUG 模式固定）
5. 成功登录！

## 测试 AI 功能

默认情况下，AI 功能会使用 Mock 数据。

**如果要使用真实 Claude AI**:

1. 获取 Anthropic API Key: https://console.anthropic.com/
2. 更新 `be/.env`:
   ```bash
   ANTHROPIC_API_KEY=sk-ant-api03-xxxxx
   ```
3. 重启后端:
   ```bash
   docker-compose restart be
   ```

## 测试支付功能（可选）

支付功能在开发环境下是可选的。如果要测试真实支付：

### Alipay 配置

1. 注册支付宝开放平台账号
2. 创建应用并获取:
   - App ID
   - 应用私钥
   - 支付宝公钥
3. 更新 `be/.env`:
   ```bash
   ALIPAY_APP_ID=你的AppID
   ALIPAY_PRIVATE_KEY_PATH=/path/to/private_key.pem
   ALIPAY_PUBLIC_KEY_PATH=/path/to/public_key.pem
   ALIPAY_NOTIFY_URL=https://your-domain.com/api/payment/alipay/notify
   ```

### WeChat Pay 配置

类似 Alipay，配置微信支付参数。

## 下一步

- 📚 阅读 [CLAUDE.md](./CLAUDE.md) 了解项目架构
- 🧪 阅读 [TESTING.md](./TESTING.md) 了解测试方法
- 🔒 阅读 [SECURITY.md](./SECURITY.md) 了解安全最佳实践
- 🚀 阅读 [DEPLOYMENT.md](./DEPLOYMENT.md) 了解生产部署

## 需要帮助？

- 查看 API 文档: http://localhost:8000/docs
- 查看日志: `docker-compose logs -f`
- 提交 Issue: [GitHub Issues](https://github.com/your-repo/issues)

---

Happy Coding! 🦞💪
