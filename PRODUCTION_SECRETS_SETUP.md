# 🔐 生产环境密钥配置指南

## 快速配置（3步）

### 第1步：生成强密钥

在服务器上执行以下命令生成两个随机密钥：

```bash
# 生成 SECRET_KEY
echo "SECRET_KEY=$(openssl rand -hex 32)"

# 生成 JWT_SECRET_KEY
echo "JWT_SECRET_KEY=$(openssl rand -hex 32)"
```

**输出示例**：
```
SECRET_KEY=a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456
JWT_SECRET_KEY=9876543210fedcba0987654321fedcba0987654321fedcba0987654321fedcba
```

### 第2步：更新 .env 文件

编辑 `be/.env` 文件（如果没有，从 `.env.example` 复制）：

```bash
cd be
cp .env.example .env
nano .env  # 或使用 vim、vi 等编辑器
```

修改以下配置项：

```bash
# Application
APP_NAME=BotBot
DEBUG=False  # ⚠️ 生产环境必须设置为 False
SECRET_KEY=a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456  # 使用第1步生成的密钥
API_PREFIX=/api

# MongoDB - 使用生产数据库地址
MONGODB_URL=mongodb://username:password@your-mongodb-host:27017
MONGODB_DB_NAME=botbot

# JWT
JWT_SECRET_KEY=9876543210fedcba0987654321fedcba0987654321fedcba0987654321fedcba  # 使用第1步生成的密钥
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=10080
REFRESH_TOKEN_EXPIRE_MINUTES=43200

# CORS - 限制为你的域名
CORS_ORIGINS=["https://yourdomain.com","https://www.yourdomain.com"]

# 其他配置...
```

### 第3步：验证配置

重启服务并检查是否有安全警告：

```bash
docker-compose down
docker-compose up -d --build
docker-compose logs be | grep -E "SECURITY|CRITICAL"
```

**成功输出**（无 CRITICAL 错误）：
```
✅ Security configuration check passed
```

---

## 完整的生产环境 .env 配置模板

```bash
# ================================
# APPLICATION SETTINGS
# ================================
APP_NAME=BotBot
DEBUG=False
SECRET_KEY=<生成的64字符密钥>
API_PREFIX=/api

# ================================
# DATABASE
# ================================
# 使用认证的 MongoDB 连接
MONGODB_URL=mongodb://botbot_user:strong_password@your-db-host:27017/botbot?authSource=admin
MONGODB_DB_NAME=botbot

# ================================
# JWT AUTHENTICATION
# ================================
JWT_SECRET_KEY=<生成的64字符密钥>
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440    # 24小时（推荐）
REFRESH_TOKEN_EXPIRE_MINUTES=10080  # 7天

# ================================
# SMS SERVICE (阿里云)
# ================================
ALIYUN_ACCESS_KEY_ID=LTAI5t...
ALIYUN_ACCESS_KEY_SECRET=xxxxx...
ALIYUN_SMS_SIGN_NAME=你的短信签名
ALIYUN_SMS_TEMPLATE_CODE=SMS_12345678

# ================================
# CLAUDE AI
# ================================
ANTHROPIC_API_KEY=sk-ant-api03-xxxxx...
CLAUDE_MODEL=claude-3-5-sonnet-20241022

# ================================
# CORS (跨域配置)
# ================================
# 生产环境：只允许你的域名
CORS_ORIGINS=["https://botbot.example.com","https://www.botbot.example.com"]

# ================================
# RATE LIMITING
# ================================
RATE_LIMIT_PER_MINUTE=100

# ================================
# PAYMENT CONFIGURATION
# ================================
RECHARGE_EXCHANGE_RATE=10.0
WITHDRAWAL_EXCHANGE_RATE=10.0
PLATFORM_FEE_RATE=0.10
MIN_RECHARGE_AMOUNT=1.0
MIN_WITHDRAWAL_AMOUNT=100.0

# ================================
# ADMIN CONFIGURATION
# ================================
SUPER_ADMIN_PHONE=13800138000  # 超级管理员手机号
MIN_PLATFORM_WITHDRAWAL_AMOUNT=1000.0

# ================================
# ALIPAY (支付宝)
# ================================
ALIPAY_APP_ID=2021xxxxxxxxxxxxx
ALIPAY_PRIVATE_KEY_PATH=/app/certs/alipay_private_key.pem
ALIPAY_PUBLIC_KEY_PATH=/app/certs/alipay_public_key.pem
ALIPAY_NOTIFY_URL=https://api.botbot.example.com/api/payment/alipay/notify
ALIPAY_RETURN_URL=https://botbot.example.com/recharge/success
ALIPAY_GATEWAY=https://openapi.alipay.com/gateway.do

# ================================
# WECHAT PAY (微信支付)
# ================================
WECHAT_APP_ID=wx1234567890abcdef
WECHAT_MCH_ID=1234567890
WECHAT_API_KEY=32位密钥
WECHAT_APICLIENT_CERT_PATH=/app/certs/apiclient_cert.pem
WECHAT_APICLIENT_KEY_PATH=/app/certs/apiclient_key.pem
WECHAT_NOTIFY_URL=https://api.botbot.example.com/api/payment/wechat/notify
```

---

## 密钥生成方法（多种方式）

### 方法1：OpenSSL（推荐）

```bash
# 生成64字符十六进制字符串
openssl rand -hex 32
```

### 方法2：Python

```bash
python3 -c "import secrets; print(secrets.token_hex(32))"
```

### 方法3：在线生成器（不推荐生产环境）

访问：https://randomkeygen.com/
选择 "CodeIgniter Encryption Keys" (64 characters)

⚠️ **注意**：生产环境建议在服务器本地生成，不要使用在线工具。

### 方法4：Node.js

```bash
node -e "console.log(require('crypto').randomBytes(32).toString('hex'))"
```

---

## 安全检查清单

在部署生产环境前，请确认：

### 必须项 ✅

- [ ] `DEBUG=False`
- [ ] `SECRET_KEY` 使用强随机密钥（至少32字符）
- [ ] `JWT_SECRET_KEY` 使用强随机密钥（至少32字符）
- [ ] 两个密钥**不能相同**
- [ ] MongoDB 使用认证连接
- [ ] CORS 限制为你的域名（不使用 `*`）
- [ ] `.env` 文件权限设置为 600

### 推荐项 ⭐

- [ ] 使用环境变量管理工具（如 AWS Secrets Manager、HashiCorp Vault）
- [ ] 定期轮换密钥（建议每6个月）
- [ ] 启用 HTTPS
- [ ] 配置真实的 SMS 服务
- [ ] 配置真实的支付网关
- [ ] 设置合理的 token 过期时间
- [ ] 配置日志监控和告警

---

## 文件权限设置

生产环境务必限制 `.env` 文件权限：

```bash
# 设置为仅所有者可读写
chmod 600 be/.env

# 验证权限
ls -la be/.env
# 应该显示：-rw------- 1 user user
```

---

## Docker 环境变量配置

如果使用 Docker Compose，你也可以通过环境变量传递密钥（更安全）：

### 方法1：在 docker-compose.yml 中引用

```yaml
services:
  be:
    environment:
      - DEBUG=False
      - SECRET_KEY=${SECRET_KEY}
      - JWT_SECRET_KEY=${JWT_SECRET_KEY}
      - MONGODB_URL=${MONGODB_URL}
```

然后在主机上导出环境变量：

```bash
export SECRET_KEY=$(openssl rand -hex 32)
export JWT_SECRET_KEY=$(openssl rand -hex 32)
export MONGODB_URL=mongodb://user:pass@host:27017/botbot

docker-compose up -d
```

### 方法2：使用 Docker secrets（Docker Swarm）

```bash
# 创建 secrets
echo "$(openssl rand -hex 32)" | docker secret create secret_key -
echo "$(openssl rand -hex 32)" | docker secret create jwt_secret_key -

# 在 docker-compose.yml 中使用
secrets:
  secret_key:
    external: true
  jwt_secret_key:
    external: true
```

---

## 密钥轮换

建议每6个月更换一次密钥：

### 轮换步骤：

1. **生成新密钥**：
   ```bash
   NEW_SECRET=$(openssl rand -hex 32)
   NEW_JWT_SECRET=$(openssl rand -hex 32)
   ```

2. **逐步替换**（避免中断服务）：
   - 先更新 `JWT_SECRET_KEY`，等待旧 token 过期
   - 再更新 `SECRET_KEY`

3. **验证**：
   ```bash
   docker-compose restart be
   docker-compose logs be | grep "Security"
   ```

4. **通知用户**（如果需要重新登录）

---

## 常见错误

### 错误1：仍然显示 CRITICAL 错误

**原因**：密钥长度不足或仍在使用弱密钥

**解决**：
```bash
# 检查密钥长度
echo -n "your-secret-key" | wc -c
# 应该 >= 32

# 重新生成
openssl rand -hex 32
```

### 错误2：服务启动后立即退出

**原因**：`.env` 文件格式错误或缺失必要配置

**解决**：
```bash
# 检查日志
docker-compose logs be

# 验证 .env 格式（不应有空格）
# ✅ 正确：SECRET_KEY=abc123
# ❌ 错误：SECRET_KEY = abc123
```

### 错误3：MongoDB 连接失败

**原因**：`MONGODB_URL` 配置错误

**解决**：
```bash
# 确认格式
MONGODB_URL=mongodb://username:password@host:port/database

# 测试连接
docker exec -it botbot-mongodb mongosh -u username -p password
```

---

## 验证配置

运行以下脚本验证配置是否正确：

```bash
#!/bin/bash
# verify_config.sh

echo "🔍 检查生产环境配置..."

# 读取 .env
source be/.env

# 检查 DEBUG
if [ "$DEBUG" = "False" ]; then
    echo "✅ DEBUG mode is disabled"
else
    echo "❌ DEBUG should be False in production"
fi

# 检查 SECRET_KEY 长度
if [ ${#SECRET_KEY} -ge 32 ]; then
    echo "✅ SECRET_KEY length is sufficient (${#SECRET_KEY} chars)"
else
    echo "❌ SECRET_KEY is too short (${#SECRET_KEY} chars)"
fi

# 检查 JWT_SECRET_KEY 长度
if [ ${#JWT_SECRET_KEY} -ge 32 ]; then
    echo "✅ JWT_SECRET_KEY length is sufficient (${#JWT_SECRET_KEY} chars)"
else
    echo "❌ JWT_SECRET_KEY is too short (${#JWT_SECRET_KEY} chars)"
fi

# 检查密钥是否相同
if [ "$SECRET_KEY" = "$JWT_SECRET_KEY" ]; then
    echo "⚠️  WARNING: SECRET_KEY and JWT_SECRET_KEY should be different"
else
    echo "✅ Keys are different"
fi

# 检查 CORS
if [[ "$CORS_ORIGINS" == *"*"* ]]; then
    echo "⚠️  WARNING: CORS allows all origins (*)"
else
    echo "✅ CORS is restricted"
fi

echo ""
echo "📝 Configuration check complete!"
```

使用方法：
```bash
chmod +x verify_config.sh
./verify_config.sh
```

---

## 总结

### 最小生产配置（3个必须修改的配置）

```bash
DEBUG=False
SECRET_KEY=$(openssl rand -hex 32)  # 运行命令获取实际值
JWT_SECRET_KEY=$(openssl rand -hex 32)  # 运行命令获取实际值
```

### 推荐生产配置（完整安全配置）

1. ✅ 关闭 DEBUG
2. ✅ 使用强密钥
3. ✅ 配置认证的数据库
4. ✅ 限制 CORS
5. ✅ 配置 HTTPS
6. ✅ 限制文件权限

---

## 相关文档

- [SECURITY.md](./SECURITY.md) - 完整安全指南
- [DEPLOYMENT.md](./DEPLOYMENT.md) - 部署指南
- [QUICKSTART.md](./QUICKSTART.md) - 快速启动指南

---

**记住**：生产环境的密钥就像你家的钥匙，一旦泄露，必须立即更换！🔐
