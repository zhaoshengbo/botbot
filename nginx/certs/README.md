# SSL 证书目录

此目录用于存放 BotBot 项目的 SSL/TLS 证书。

## 目录结构

```
certs/
├── README.md           # 本文档
├── botbot.biz.crt     # SSL 证书（公钥）
├── botbot.biz.key     # SSL 私钥
└── dhparam.pem        # Diffie-Hellman 参数（可选，用于增强安全性）
```

## 开发环境 - 自签名证书

### 生成自签名证书（用于本地开发）

```bash
# 进入证书目录
cd nginx/certs

# 生成自签名证书（有效期 365 天）
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout botbot.biz.key \
  -out botbot.biz.crt \
  -subj "/C=CN/ST=Shanghai/L=Shanghai/O=BotBot/OU=Development/CN=botbot.biz"

# 生成 DH 参数（可选，增强安全性，需要几分钟）
openssl dhparam -out dhparam.pem 2048

# 设置私钥权限
chmod 600 botbot.biz.key
chmod 644 botbot.biz.crt
```

### 一键生成脚本

或者直接运行项目根目录的脚本：
```bash
./generate-dev-certs.sh
```

### 浏览器信任自签名证书

**macOS:**
```bash
# 将证书添加到系统钥匙串
sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain nginx/certs/botbot.biz.crt
```

**Linux:**
```bash
# Ubuntu/Debian
sudo cp nginx/certs/botbot.biz.crt /usr/local/share/ca-certificates/
sudo update-ca-certificates

# CentOS/RHEL
sudo cp nginx/certs/botbot.biz.crt /etc/pki/ca-trust/source/anchors/
sudo update-ca-trust
```

**Windows:**
- 双击 `botbot.biz.crt` 文件
- 点击"安装证书"
- 选择"本地计算机"
- 选择"将所有证书放入下列存储"
- 选择"受信任的根证书颁发机构"

**浏览器:**
- Chrome/Edge: 访问 https://botbot.biz 时，点击"高级" → "继续前往 botbot.biz（不安全）"
- Firefox: 需要单独添加例外

## 生产环境 - Let's Encrypt 证书

### 方法 1: 使用 Certbot（推荐）

```bash
# 安装 Certbot
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install certbot

# CentOS/RHEL
sudo yum install certbot

# macOS
brew install certbot

# 停止现有服务（Certbot 需要使用 80 端口）
docker-compose down

# 生成证书
sudo certbot certonly --standalone \
  -d botbot.biz \
  -d www.botbot.biz \
  --email your-email@example.com \
  --agree-tos \
  --no-eff-email

# 证书将生成在 /etc/letsencrypt/live/botbot.biz/
# - fullchain.pem  # 完整证书链（使用这个）
# - privkey.pem    # 私钥
# - cert.pem       # 证书
# - chain.pem      # 证书链

# 复制到项目目录（可选）
sudo cp /etc/letsencrypt/live/botbot.biz/fullchain.pem nginx/certs/botbot.biz.crt
sudo cp /etc/letsencrypt/live/botbot.biz/privkey.pem nginx/certs/botbot.biz.key
sudo chown $USER:$USER nginx/certs/botbot.biz.*

# 或者直接在 docker-compose.yml 中挂载 /etc/letsencrypt
```

### 方法 2: 使用其他 CA

如果使用其他证书颁发机构（如阿里云、腾讯云），将获得的证书文件重命名为：
- `botbot.biz.crt` - 证书文件（通常是 .crt 或 .pem）
- `botbot.biz.key` - 私钥文件（通常是 .key）

如果有中间证书，需要合并：
```bash
cat your-cert.crt intermediate.crt > botbot.biz.crt
```

### 自动续期（Let's Encrypt）

Let's Encrypt 证书有效期 90 天，需要定期续期：

```bash
# 测试续期（不实际执行）
sudo certbot renew --dry-run

# 实际续期
sudo certbot renew

# 设置自动续期（crontab）
sudo crontab -e
# 添加以下行（每天凌晨 2 点检查）
0 2 * * * certbot renew --quiet --post-hook "docker-compose -f /path/to/botbot/docker-compose.yml restart nginx"
```

## Docker 配置

### docker-compose.yml 配置

确保 docker-compose.yml 中的 nginx 服务包含证书挂载：

```yaml
nginx:
  image: nginx:alpine
  volumes:
    - ./nginx/certs:/etc/nginx/certs:ro  # 挂载证书目录
    # 或者挂载系统证书目录
    # - /etc/letsencrypt:/etc/letsencrypt:ro
```

### Nginx 配置文件

证书在 `nginx/conf.d/botbot.conf` 中引用：

```nginx
server {
    listen 443 ssl http2;
    server_name botbot.biz www.botbot.biz;

    # SSL 证书配置
    ssl_certificate /etc/nginx/certs/botbot.biz.crt;
    ssl_certificate_key /etc/nginx/certs/botbot.biz.key;

    # SSL 优化配置...
}
```

## 安全注意事项

### ⚠️ 重要：私钥保护

1. **永远不要提交私钥到 Git**
   - `.gitignore` 已配置忽略 `*.key` 文件
   - 生产环境私钥应妥善保管

2. **设置正确的文件权限**
   ```bash
   chmod 600 nginx/certs/*.key  # 私钥仅所有者可读
   chmod 644 nginx/certs/*.crt  # 证书公开可读
   ```

3. **使用环境变量或密钥管理服务**
   - 生产环境考虑使用 Docker Secrets
   - 或使用云服务商的密钥管理（如 AWS KMS、阿里云 KMS）

### SSL 配置最佳实践

在 `nginx/conf.d/botbot.conf` 中已配置：
- ✅ TLS 1.2 和 1.3
- ✅ 强加密套件
- ✅ HSTS（HTTP Strict Transport Security）
- ✅ OCSP Stapling
- ✅ HTTP/2

## 验证证书

### 检查证书信息

```bash
# 查看证书内容
openssl x509 -in nginx/certs/botbot.biz.crt -text -noout

# 查看证书有效期
openssl x509 -in nginx/certs/botbot.biz.crt -noout -dates

# 验证证书和私钥是否匹配
openssl x509 -noout -modulus -in nginx/certs/botbot.biz.crt | openssl md5
openssl rsa -noout -modulus -in nginx/certs/botbot.biz.key | openssl md5
# 两个 MD5 值应该相同
```

### 测试 HTTPS 连接

```bash
# 使用 curl 测试
curl -v https://botbot.biz

# 使用 openssl 测试
openssl s_client -connect botbot.biz:443 -servername botbot.biz

# 在线 SSL 测试（生产环境）
# https://www.ssllabs.com/ssltest/
```

## 故障排查

### 问题：Nginx 启动失败 "cannot load certificate"

**原因**：证书文件不存在或路径不正确

**解决**：
```bash
# 检查证书文件是否存在
ls -l nginx/certs/

# 检查 Nginx 容器内的路径
docker exec botbot-nginx ls -l /etc/nginx/certs/

# 查看 Nginx 错误日志
docker-compose logs nginx
```

### 问题：浏览器提示"证书不受信任"

**原因**：使用自签名证书

**解决**：
- 开发环境：按上述步骤将证书添加到系统信任列表
- 生产环境：使用正规 CA 签发的证书（如 Let's Encrypt）

### 问题：证书过期

**解决**：
```bash
# 检查证书有效期
openssl x509 -in nginx/certs/botbot.biz.crt -noout -dates

# 重新生成（开发环境）
./generate-dev-certs.sh

# 续期（Let's Encrypt）
sudo certbot renew
docker-compose restart nginx
```

## 文件清单

- ✅ `botbot.biz.crt` - SSL 证书（必需）
- ✅ `botbot.biz.key` - SSL 私钥（必需）
- ⚪ `dhparam.pem` - DH 参数（可选，推荐）
- ⚪ `botbot.biz.csr` - 证书签名请求（申请证书时需要）

## 相关文档

- [Nginx SSL 配置文档](http://nginx.org/en/docs/http/ngx_http_ssl_module.html)
- [Let's Encrypt 文档](https://letsencrypt.org/docs/)
- [Mozilla SSL 配置生成器](https://ssl-config.mozilla.org/)
- [SSL Labs 测试](https://www.ssllabs.com/ssltest/)
