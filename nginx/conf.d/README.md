# Nginx 配置文件说明

## 文件说明

### 活动配置
- **`botbot.conf`** - 开发环境配置（当前使用）
  - HTTP 和 HTTPS 同时支持
  - 不强制 HTTPS 重定向
  - 适合本地开发

### 备用配置
- **`botbot.prod.conf.disabled`** - 生产环境配置（已禁用）
  - 强制 HTTPS（HTTP 自动重定向）
  - 增强安全配置
  - 静态资源激进缓存
  - Rate limiting 支持

## 为什么要禁用一个配置？

Nginx 会自动加载 `conf.d/` 目录下所有的 `.conf` 文件。

如果同时存在 `botbot.conf` 和 `botbot.prod.conf`，会导致：
- ❌ 重复定义 upstream（backend、frontend）
- ❌ Nginx 启动失败：`duplicate upstream "backend"`

**解决方案**：将不使用的配置文件重命名为 `.disabled` 后缀。

## 如何切换配置？

### 切换到开发环境配置

```bash
cd nginx/conf.d

# 禁用生产配置
mv botbot.prod.conf botbot.prod.conf.disabled

# 启用开发配置
mv botbot.conf.disabled botbot.conf  # 如果之前禁用了

# 重启 Nginx
docker-compose restart nginx
```

### 切换到生产环境配置

```bash
cd nginx/conf.d

# 禁用开发配置
mv botbot.conf botbot.conf.disabled

# 启用生产配置
mv botbot.prod.conf.disabled botbot.prod.conf

# 重启 Nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

## 快速命令

### 使用开发配置
```bash
cd /Users/saulzhao/git/botbot/nginx/conf.d
[ -f botbot.prod.conf ] && mv botbot.prod.conf botbot.prod.conf.disabled
[ -f botbot.conf.disabled ] && mv botbot.conf.disabled botbot.conf
docker-compose restart nginx
```

### 使用生产配置
```bash
cd /Users/saulzhao/git/botbot/nginx/conf.d
[ -f botbot.conf ] && mv botbot.conf botbot.conf.disabled
[ -f botbot.prod.conf.disabled ] && mv botbot.prod.conf.disabled botbot.prod.conf
docker-compose -f docker-compose.prod.yml restart nginx
```

## 配置差异对比

| 功能 | 开发配置 (botbot.conf) | 生产配置 (botbot.prod.conf) |
|------|----------------------|---------------------------|
| **HTTPS** | 可选 | 强制（HTTP → HTTPS） |
| **HTTP/2** | ✅ | ✅ |
| **HSTS** | 基础 | 增强（2年有效期） |
| **CSP** | ❌ | ✅ 完整 CSP 策略 |
| **静态缓存** | 30天 | 1年 |
| **Rate Limiting** | ❌ | ✅ 支持（需启用）|
| **ACME 支持** | ❌ | ✅ Let's Encrypt |
| **安全响应头** | 基础 | 完整 |

## 验证配置

```bash
# 测试配置语法
docker exec botbot-nginx nginx -t

# 查看当前使用的配置
ls -l nginx/conf.d/*.conf

# 查看 Nginx 日志
docker-compose logs nginx
```

## 故障排查

### 错误：duplicate upstream "backend"

**原因**：同时存在多个 .conf 文件定义了相同的 upstream

**解决**：
```bash
cd nginx/conf.d
ls -la *.conf
# 确保只有一个 .conf 文件，其他的应该是 .disabled
```

### 警告：listen ... http2 directive is deprecated

**原因**：旧版本 HTTP/2 语法

**已修复**：现在使用新语法
```nginx
# 旧语法（已废弃）
listen 443 ssl http2;

# 新语法（推荐）
listen 443 ssl;
http2 on;
```

## 建议的工作流程

### 本地开发
1. 使用 `botbot.conf`
2. HTTP 和 HTTPS 都可用
3. 使用自签名证书或不用证书

### 生产部署
1. 切换到 `botbot.prod.conf`
2. 配置 Let's Encrypt 证书
3. 启用 HTTPS 强制重定向
4. 可选启用 Rate Limiting

## 相关文档

- [Nginx 主配置说明](../README.md)
- [SSL 证书配置](../certs/README.md)
- [生产部署指南](../../PRODUCTION_DEPLOYMENT.md)
- [快速开始](../../QUICKSTART.md)
