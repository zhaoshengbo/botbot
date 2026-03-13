# CORS 跨域配置说明

## 当前配置

BotBot 后端 API 已配置为**支持所有来源的跨域访问**。

## 配置位置

### 1. 代码层面 (`be/app/main.py`)

```python
# CORS middleware
cors_origins = settings.get_cors_origins()
allow_credentials = "*" not in cors_origins  # 允许所有来源时，自动禁用 credentials

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=allow_credentials,
    allow_methods=["*"],        # 允许所有 HTTP 方法
    allow_headers=["*"],        # 允许所有请求头
    expose_headers=["*"],       # 暴露所有响应头
)
```

### 2. Docker 配置 (`docker-compose.yml`)

```yaml
environment:
  - CORS_ORIGINS=*  # 允许所有来源
```

### 3. 环境变量 (`.env.example`)

```bash
# 开发和生产环境 - 允许所有来源访问
CORS_ORIGINS=*
```

## 支持的配置格式

在需要时，可以通过修改 `CORS_ORIGINS` 环境变量来调整策略：

1. **允许所有来源（当前配置）**
   ```bash
   CORS_ORIGINS=*
   ```

2. **指定多个域名（JSON 数组）**
   ```bash
   CORS_ORIGINS=["http://example.com","https://example.com","http://47.83.230.114:3000"]
   ```

3. **指定多个域名（逗号分隔）**
   ```bash
   CORS_ORIGINS=http://example.com,https://example.com,http://47.83.230.114:3000
   ```

4. **单个域名**
   ```bash
   CORS_ORIGINS=http://example.com
   ```

## 部署说明

### 开发环境

```bash
# 启动服务
docker-compose up -d

# 查看 CORS 配置日志
docker-compose logs backend | grep CORS
# 应该显示: 🌐 CORS Origins: ['*']
```

### 生产环境

当前配置已经支持所有来源访问，无需额外修改。

如果需要修改 CORS 策略：

1. **方式一：修改 docker-compose.yml**
   ```yaml
   environment:
     - CORS_ORIGINS=你的配置
   ```

2. **方式二：使用环境变量文件**
   ```bash
   # 在服务器上创建 .env 文件
   echo "CORS_ORIGINS=*" > be/.env

   # 重新部署
   ./redeploy.sh
   ```

## 验证 CORS 配置

### 方法 1：查看日志

```bash
docker-compose logs backend | grep "CORS Origins"
```

应该看到：
```
🌐 CORS Origins: ['*']
```

### 方法 2：测试跨域请求

```bash
# 使用 curl 测试 OPTIONS 预检请求
curl -X OPTIONS http://47.83.230.114:8000/api/auth/me \
  -H "Origin: http://any-domain.com" \
  -H "Access-Control-Request-Method: GET" \
  -i
```

响应头应该包含：
```
Access-Control-Allow-Origin: *
Access-Control-Allow-Methods: *
Access-Control-Allow-Headers: *
```

### 方法 3：浏览器控制台测试

```javascript
// 在任何网站的浏览器控制台执行
fetch('http://47.83.230.114:8000/api/auth/me')
  .then(r => r.json())
  .then(console.log)
  .catch(console.error)
```

如果配置正确，应该能够成功请求（可能返回 401 未授权，但不会出现 CORS 错误）。

## 技术细节

### 为什么 `allow_credentials=False`？

当 `allow_origins=["*"]` 时，根据浏览器的 CORS 安全策略，**不能**同时设置 `allow_credentials=True`。

代码已自动处理：
- 当 `CORS_ORIGINS=*` 时，`allow_credentials` 自动设为 `False`
- 当指定具体域名时，`allow_credentials` 设为 `True`（支持携带 Cookie）

### 安全说明

- ✅ **开发环境**：推荐使用 `CORS_ORIGINS=*` 方便调试
- ⚠️ **生产环境**：当前已按需求配置为允许所有来源
  - 如果 API 不包含敏感操作，允许所有来源是可接受的
  - 如果需要限制访问，建议明确指定允许的域名列表

## 故障排查

如果遇到 CORS 错误：

1. **检查环境变量是否生效**
   ```bash
   docker-compose exec backend env | grep CORS
   ```

2. **重启后端服务**
   ```bash
   docker-compose restart backend
   ```

3. **查看启动日志**
   ```bash
   docker-compose logs backend | head -20
   ```

4. **完全重建容器**
   ```bash
   docker-compose down
   docker-compose up -d --build backend
   ```

## 更新日期

2026-03-13
