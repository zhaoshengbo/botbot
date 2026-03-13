# 🔒 BotBot CORS 跨域问题完整解决方案

## 什么是 CORS 跨域问题？

**CORS (Cross-Origin Resource Sharing)** 是浏览器的安全机制，防止恶意网站访问其他网站的数据。

### 常见错误提示

```
Access to XMLHttpRequest at 'http://botbot.biz:8000/api/auth/direct-login'
from origin 'http://botbot.biz:3000' has been blocked by CORS policy:
No 'Access-Control-Allow-Origin' header is present on the requested resource.
```

或

```
CORS policy: Response to preflight request doesn't pass access control check
```

---

## 🎯 快速解决（3 步骤）

### 方法 1: 使用自动修复脚本（推荐）

```bash
cd /root/botbot
git pull origin main
./fix-production.sh
```

脚本会自动配置 CORS 设置。

### 方法 2: 手动配置

#### 步骤 1: 配置后端 CORS

编辑 `be/.env` 文件：

```bash
cd /root/botbot
nano be/.env
```

**生产环境配置** - 使用 JSON 数组格式（推荐）：

```env
# 方式 1: JSON 数组格式（推荐，清晰准确）
CORS_ORIGINS=["http://botbot.biz:3000","http://47.83.230.114:3000","http://localhost:3000"]
```

**或者** 使用逗号分隔格式：

```env
# 方式 2: 逗号分隔格式（简单，但要注意格式）
CORS_ORIGINS=http://botbot.biz:3000,http://47.83.230.114:3000,http://localhost:3000
```

**重要提示**:
- ✅ 包含你的域名（如 `http://botbot.biz:3000`）
- ✅ 包含你的 IP（如 `http://47.83.230.114:3000`）
- ✅ 协议要匹配（http 或 https）
- ✅ 端口号要正确（前端是 3000）
- ❌ 不要有多余空格
- ❌ URL 末尾不要加斜杠

#### 步骤 2: 重启后端服务

```bash
docker-compose restart backend

# 查看 CORS 配置是否生效（应该看到你配置的地址）
docker-compose logs backend | grep "CORS Origins"
```

#### 步骤 3: 验证修复

打开浏览器开发者工具（F12），刷新页面：
1. Network 标签中应该没有 CORS 错误
2. 登录功能应该正常工作

---

## 🔍 CORS 配置详解

### 支持的配置格式

BotBot 后端支持三种 CORS_ORIGINS 格式：

#### 1. JSON 数组格式（推荐）

```env
CORS_ORIGINS=["http://botbot.biz:3000","http://47.83.230.114:3000"]
```

✅ **优点**:
- 格式清晰，不易出错
- 支持特殊字符
- Python 直接解析

❌ **注意**:
- 必须是有效的 JSON 格式
- 使用双引号，不是单引号

#### 2. 逗号分隔格式

```env
CORS_ORIGINS=http://botbot.biz:3000,http://47.83.230.114:3000
```

✅ **优点**:
- 简单直观
- 不需要引号

❌ **注意**:
- URL 中不能包含逗号
- 不要有多余空格

#### 3. 单个地址

```env
CORS_ORIGINS=http://botbot.biz:3000
```

仅适用于只有一个前端地址的情况。

---

## 🌐 不同部署场景的 CORS 配置

### 场景 1: 本地开发

```env
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 场景 2: 服务器部署（使用 IP）

```env
CORS_ORIGINS=["http://47.83.230.114:3000","http://localhost:3000"]
```

### 场景 3: 服务器部署（使用域名）

```env
CORS_ORIGINS=["http://botbot.biz:3000","http://localhost:3000"]
```

### 场景 4: 同时支持域名和 IP

```env
CORS_ORIGINS=["http://botbot.biz:3000","http://47.83.230.114:3000","http://localhost:3000"]
```

### 场景 5: 使用 Nginx 反向代理（无端口号）

```env
CORS_ORIGINS=["http://botbot.biz","https://botbot.biz"]
```

### 场景 6: HTTPS 生产环境

```env
CORS_ORIGINS=["https://botbot.biz","http://botbot.biz:3000"]
```

---

## 🔧 高级配置

### 允许所有来源（仅开发环境！）

```env
CORS_ORIGINS=*
```

⚠️ **警告**: 不要在生产环境使用！有安全风险。

### 代码中动态配置

编辑 `be/app/core/config.py`:

```python
class Settings(BaseSettings):
    # ... 其他配置

    def get_cors_origins(self) -> List[str]:
        # 自定义逻辑
        if self.DEBUG:
            return ["*"]  # 开发环境允许所有
        else:
            return self.get_cors_origins()  # 生产环境使用配置
```

---

## 🐛 常见问题排查

### 问题 1: 配置后仍然有 CORS 错误

**原因**: 后端没有重启或配置格式错误

**解决**:

```bash
# 1. 检查配置文件格式
cat be/.env | grep CORS_ORIGINS

# 2. 验证 JSON 格式（如果使用 JSON 数组）
echo '["http://botbot.biz:3000"]' | python3 -m json.tool

# 3. 重启后端
docker-compose restart backend

# 4. 查看启动日志中的 CORS 配置
docker-compose logs backend | grep "CORS Origins"
# 应该看到: 🌐 CORS Origins: ['http://botbot.biz:3000', ...]
```

### 问题 2: 只有某些请求有 CORS 错误

**原因**: Preflight 请求（OPTIONS）被拒绝

**解决**: 确保 CORS 配置包含以下设置（已在代码中默认配置）：

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,      # 允许携带凭证
    allow_methods=["*"],          # 允许所有方法
    allow_headers=["*"],          # 允许所有头
)
```

### 问题 3: localhost 和 127.0.0.1 都需要配置吗？

**答**: 是的，浏览器认为它们是不同的源。

```env
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

### 问题 4: 使用域名后 IP 访问报 CORS 错误

**答**: 需要同时配置域名和 IP：

```env
CORS_ORIGINS=["http://botbot.biz:3000","http://47.83.230.114:3000"]
```

### 问题 5: 配置了正确的地址还是报错

**检查清单**:

```bash
# 1. URL 格式是否正确（协议、域名、端口）
# ✅ http://botbot.biz:3000
# ❌ http://botbot.biz:3000/
# ❌ http://botbot.biz:3000 (有空格)
# ❌ botbot.biz:3000 (缺少协议)

# 2. 检查前端实际使用的地址
# 浏览器地址栏显示的地址

# 3. 检查后端日志
docker-compose logs backend | grep -i cors

# 4. 测试 CORS
curl -H "Origin: http://botbot.biz:3000" \
     -H "Access-Control-Request-Method: POST" \
     -H "Access-Control-Request-Headers: Content-Type" \
     -X OPTIONS \
     --verbose \
     http://botbot.biz:8000/api/auth/direct-login
```

---

## 🎯 使用 Nginx 解决 CORS（高级）

如果配置后端 CORS 仍有问题，可以在 Nginx 层面处理：

```nginx
server {
    listen 80;
    server_name botbot.biz;

    # 添加 CORS 头
    add_header 'Access-Control-Allow-Origin' '$http_origin' always;
    add_header 'Access-Control-Allow-Credentials' 'true' always;
    add_header 'Access-Control-Allow-Methods' 'GET, POST, PUT, DELETE, OPTIONS, PATCH' always;
    add_header 'Access-Control-Allow-Headers' 'Accept,Authorization,Cache-Control,Content-Type,DNT,If-Modified-Since,Keep-Alive,Origin,User-Agent,X-Requested-With' always;

    # 处理 preflight 请求
    if ($request_method = 'OPTIONS') {
        return 204;
    }

    location /api {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        proxy_pass http://localhost:3000;
    }
}
```

---

## 📋 完整测试清单

修复 CORS 后，按以下步骤验证：

### 1. 后端配置检查

```bash
# 查看配置
cat be/.env | grep CORS_ORIGINS

# 重启后端
docker-compose restart backend

# 检查日志
docker-compose logs backend | head -50
# 应该看到: 🌐 CORS Origins: [...]
```

### 2. 浏览器测试

1. **清除缓存**: Ctrl+Shift+Del
2. **打开开发者工具**: F12
3. **访问网站**: http://botbot.biz:3000
4. **查看 Console**: 不应该有 CORS 错误
5. **查看 Network**:
   - 找到 API 请求
   - 查看 Response Headers
   - 应该有 `Access-Control-Allow-Origin: http://botbot.biz:3000`

### 3. 命令行测试

```bash
# 测试 CORS preflight
curl -i -X OPTIONS \
  -H "Origin: http://botbot.biz:3000" \
  -H "Access-Control-Request-Method: POST" \
  -H "Access-Control-Request-Headers: Content-Type" \
  http://botbot.biz:8000/api/auth/direct-login

# 应该返回:
# HTTP/1.1 200 OK
# access-control-allow-origin: http://botbot.biz:3000
# access-control-allow-credentials: true
```

### 4. 功能测试

- ✅ 登录功能正常
- ✅ 创建任务正常
- ✅ 浏览任务正常
- ✅ 所有 API 调用正常

---

## 📚 相关文档

- 🔧 **DEPLOYMENT.md** - 完整部署指南
- 🚀 **QUICK_FIX.md** - 快速修复生产问题
- 📖 **README.md** - 项目介绍

---

## 💡 最佳实践

### ✅ DO（推荐做法）

1. **明确配置允许的源**
   ```env
   CORS_ORIGINS=["http://botbot.biz:3000","http://47.83.230.114:3000"]
   ```

2. **使用 HTTPS（生产环境）**
   ```env
   CORS_ORIGINS=["https://botbot.biz"]
   ```

3. **开发和生产分离**
   ```env
   # .env.development
   CORS_ORIGINS=*

   # .env.production
   CORS_ORIGINS=["https://yourdomain.com"]
   ```

4. **记录 CORS 配置**
   ```python
   print(f"🌐 CORS Origins: {cors_origins}")
   ```

### ❌ DON'T（避免的做法）

1. **生产环境使用通配符**
   ```env
   CORS_ORIGINS=*  # ❌ 不安全！
   ```

2. **配置错误的协议**
   ```env
   # 前端用 https，后端配置 http
   CORS_ORIGINS=http://botbot.biz:3000  # ❌ 不匹配
   ```

3. **URL 末尾加斜杠**
   ```env
   CORS_ORIGINS=http://botbot.biz:3000/  # ❌ 不要加斜杠
   ```

4. **忘记端口号**
   ```env
   CORS_ORIGINS=http://botbot.biz  # ❌ 缺少端口 3000
   ```

---

## 🆘 仍然无法解决？

如果按照上述步骤仍无法解决 CORS 问题，请提供以下信息：

1. **后端 CORS 配置**:
   ```bash
   cat be/.env | grep CORS_ORIGINS
   ```

2. **后端启动日志**:
   ```bash
   docker-compose logs backend | grep -E "CORS|Origins"
   ```

3. **浏览器错误信息**:
   - F12 → Console 标签的完整错误
   - F12 → Network 标签中失败请求的详细信息

4. **访问地址**:
   - 前端地址（浏览器地址栏）
   - 后端地址（API 请求地址）

5. **curl 测试结果**:
   ```bash
   curl -i -X OPTIONS \
     -H "Origin: http://你的前端地址" \
     -H "Access-Control-Request-Method: POST" \
     http://你的后端地址/api/auth/direct-login
   ```

---

**CORS 配置完成后，所有跨域问题都应该解决！** 🎉
