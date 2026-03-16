# Nginx SSL 配置完成总结

## ✅ 已完成的配置

### 1. 证书目录结构
```
nginx/certs/
├── .gitignore              # 保护私钥不被提交到 Git
└── README.md               # 详细的证书配置文档
```

### 2. Nginx HTTPS 配置
- ✅ 添加 443 端口 HTTPS 监听
- ✅ HTTP/2 支持
- ✅ TLS 1.2 & 1.3 协议
- ✅ 强加密套件配置
- ✅ SSL 会话缓存
- ✅ OCSP Stapling
- ✅ 安全响应头（HSTS, X-Frame-Options 等）
- ✅ 保留 HTTP (80) 端口向后兼容

### 3. Docker 配置
- ✅ 挂载证书目录到 Nginx 容器
- ✅ 同时暴露 80 和 443 端口

### 4. 自动化脚本
- ✅ `generate-dev-certs.sh` - 一键生成自签名证书

### 5. 文档
- ✅ `nginx/certs/README.md` - 完整的证书配置指南
- ✅ `QUICKSTART.md` - 更新了 HTTPS 设置说明

## 🚀 快速开始

### HTTP 访问（无需证书）

```bash
# 1. 配置域名
./setup-local-domain.sh

# 2. 启动服务
docker-compose up -d

# 3. 访问
open http://botbot.biz
```

### HTTPS 访问（推荐）

```bash
# 1. 配置域名
./setup-local-domain.sh

# 2. 生成证书
./generate-dev-certs.sh

# 3. （可选）信任证书
# macOS
sudo security add-trusted-cert -d -r trustRoot \
  -k /Library/Keychains/System.keychain nginx/certs/botbot.biz.crt

# 4. 启动服务
docker-compose up -d

# 5. 访问
open https://botbot.biz
```

## 📁 关键文件

| 文件 | 说明 |
|------|------|
| `nginx/conf.d/botbot.conf` | Nginx 站点配置（HTTP + HTTPS） |
| `nginx/certs/README.md` | 证书配置完整文档 |
| `nginx/certs/.gitignore` | 保护私钥安全 |
| `docker-compose.yml` | 挂载证书目录 |
| `generate-dev-certs.sh` | 自签名证书生成脚本 |
| `QUICKSTART.md` | 快速开始指南 |

## 🔒 证书类型

### 开发环境 - 自签名证书

**优点**：
- ✅ 免费
- ✅ 即时生成
- ✅ 完全本地化

**缺点**：
- ⚠️ 浏览器会显示警告（除非手动信任）
- ⚠️ 仅用于开发环境

**生成方式**：
```bash
./generate-dev-certs.sh
```

### 生产环境 - Let's Encrypt 证书

**优点**：
- ✅ 免费
- ✅ 浏览器信任
- ✅ 自动续期

**获取方式**：
```bash
# 使用 Certbot
sudo certbot certonly --standalone \
  -d botbot.biz \
  -d www.botbot.biz

# 证书位置
/etc/letsencrypt/live/botbot.biz/
  ├── fullchain.pem  # 使用这个作为 .crt
  └── privkey.pem    # 使用这个作为 .key
```

详见 `nginx/certs/README.md`

## 🔐 安全配置

### SSL 安全等级
- TLS 1.2 & 1.3
- 强加密套件（ECDHE、CHACHA20、AES-GCM）
- HSTS（强制 HTTPS）
- OCSP Stapling（在线证书状态检查）

### 安全响应头
```
Strict-Transport-Security: max-age=63072000
X-Frame-Options: SAMEORIGIN
X-Content-Type-Options: nosniff
X-XSS-Protection: 1; mode=block
```

### SSL Labs 评级
使用推荐配置，可以获得 **A+** 评级

测试地址：https://www.ssllabs.com/ssltest/

## 📝 访问地址

### HTTPS（需要证书）
- 前端：https://botbot.biz
- API：https://botbot.biz/api
- 文档：https://botbot.biz/docs

### HTTP（始终可用）
- 前端：http://botbot.biz
- API：http://botbot.biz/api
- 文档：http://botbot.biz/docs

## 🛠️ 故障排查

### Nginx 启动失败

**错误信息**：
```
cannot load certificate "/etc/nginx/certs/botbot.biz.crt"
```

**原因**：证书文件不存在

**解决方案**：
```bash
# 生成证书
./generate-dev-certs.sh

# 或者暂时禁用 HTTPS
# 编辑 nginx/conf.d/botbot.conf，注释掉 HTTPS server 块
```

### 浏览器显示"不安全"

**原因**：使用自签名证书

**解决方案**：

**选项 1：信任证书（推荐）**
```bash
# macOS
sudo security add-trusted-cert -d -r trustRoot \
  -k /Library/Keychains/System.keychain nginx/certs/botbot.biz.crt

# Linux (Ubuntu)
sudo cp nginx/certs/botbot.biz.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates
```

**选项 2：使用 HTTP**
```
访问 http://botbot.biz 而不是 https://botbot.biz
```

**选项 3：浏览器点击"继续前往"**
- Chrome/Edge：点击"高级" → "继续前往 botbot.biz（不安全）"
- Firefox：点击"高级" → "接受风险并继续"

### 证书过期

**检查有效期**：
```bash
openssl x509 -in nginx/certs/botbot.biz.crt -noout -dates
```

**重新生成**：
```bash
./generate-dev-certs.sh
docker-compose restart nginx
```

### 验证证书和私钥是否匹配

```bash
# 证书的 MD5
openssl x509 -noout -modulus -in nginx/certs/botbot.biz.crt | openssl md5

# 私钥的 MD5
openssl rsa -noout -modulus -in nginx/certs/botbot.biz.key | openssl md5

# 两个值应该相同
```

## 📚 相关文档

1. **完整证书配置指南**：`nginx/certs/README.md`
2. **Nginx 配置详解**：`nginx/README.md`
3. **快速开始**：`QUICKSTART.md`
4. **项目架构**：`CLAUDE.md`

## 🎯 生产环境部署

生产环境推荐使用 Let's Encrypt 免费证书：

```bash
# 1. 安装 Certbot
sudo apt-get install certbot  # Ubuntu/Debian
brew install certbot           # macOS

# 2. 停止服务（Certbot 需要 80 端口）
docker-compose down

# 3. 获取证书
sudo certbot certonly --standalone \
  -d botbot.biz \
  -d www.botbot.biz \
  --email your-email@example.com

# 4. 复制证书到项目（或直接挂载 /etc/letsencrypt）
sudo cp /etc/letsencrypt/live/botbot.biz/fullchain.pem nginx/certs/botbot.biz.crt
sudo cp /etc/letsencrypt/live/botbot.biz/privkey.pem nginx/certs/botbot.biz.key
sudo chown $USER:$USER nginx/certs/botbot.biz.*

# 5. 启动服务
docker-compose up -d

# 6. 设置自动续期（证书 90 天有效）
sudo crontab -e
# 添加：
0 2 * * * certbot renew --quiet --post-hook "cd /path/to/botbot && docker-compose restart nginx"
```

详细步骤见 `nginx/certs/README.md` 的"生产环境"部分。

## ✅ 检查清单

部署前检查：

- [ ] 域名已配置（hosts 文件或 DNS）
- [ ] 证书已生成并放置在 `nginx/certs/` 目录
- [ ] 证书权限正确（.key 文件 600，.crt 文件 644）
- [ ] docker-compose.yml 挂载了证书目录
- [ ] Nginx 配置中证书路径正确
- [ ] 测试 Nginx 配置：`docker exec botbot-nginx nginx -t`
- [ ] 服务启动成功：`docker-compose ps`
- [ ] HTTPS 可访问：`curl -k https://botbot.biz/health`
- [ ] 浏览器可以打开 https://botbot.biz

## 🎉 总结

现在 BotBot 已支持完整的 HTTPS 配置：

1. ✅ **开发环境**：使用 `./generate-dev-certs.sh` 生成自签名证书
2. ✅ **生产环境**：支持 Let's Encrypt 免费证书
3. ✅ **安全配置**：TLS 1.2/1.3、强加密、HSTS 等
4. ✅ **向后兼容**：同时支持 HTTP (80) 和 HTTPS (443)
5. ✅ **完整文档**：详细的配置和故障排查指南

开始使用：
```bash
./setup-local-domain.sh    # 配置域名
./generate-dev-certs.sh    # 生成证书
docker-compose up -d        # 启动服务
open https://botbot.biz     # 访问应用
```
