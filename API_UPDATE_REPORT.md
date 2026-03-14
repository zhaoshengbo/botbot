# BotBot API 接口更新报告

**更新时间**: 2026-03-14
**更新内容**: 前端API调用与后端接口对齐

---

## 📝 更新摘要

根据最新的后端API实现，对前端API客户端进行了以下调整，确保前端调用与后端接口完全匹配。

---

## 🔄 前端API调用更新

### 1. 竞标接口更新

#### ❌ 旧版本 (不匹配)
```typescript
// 创建竞标
async createBid(taskId: string, bidData: { amount: number; message?: string }) {
  await this.client.post(`/bids/${taskId}/bids`, bidData);
}

// 获取任务竞标列表
async getTaskBids(taskId: string) {
  await this.client.get(`/bids/${taskId}/bids`);
}
```

#### ✅ 新版本 (已修复)
```typescript
// 创建竞标 - 使用 POST /api/bids/
async createBid(taskId: string, bidData: { amount: number; message?: string }) {
  await this.client.post('/bids/', {
    task_id: taskId,
    ...bidData,
  });
}

// 获取任务竞标列表 - 使用 GET /api/tasks/{taskId}/bids
async getTaskBids(taskId: string) {
  await this.client.get(`/tasks/${taskId}/bids`);
  // 返回格式: { bids: Bid[], total: number }
}
```

### 2. 合同接口更新

#### ❌ 旧版本 (字段名不匹配)
```typescript
async submitDeliverables(contractId: string, deliverablesUrl: string) {
  await this.client.post(`/contracts/${contractId}/deliverables`, {
    deliverables_url: deliverablesUrl,  // 后端优先使用 deliverable_url
  });
}
```

#### ✅ 新版本 (已修复)
```typescript
async submitDeliverables(contractId: string, deliverablesUrl: string, notes?: string) {
  await this.client.post(`/contracts/${contractId}/submit`, {
    deliverable_url: deliverablesUrl,  // 使用后端首选字段名
    notes,
  });
}
```

### 3. 新增接口

#### 接受竞标接口
```typescript
// 接受竞标 - 返回简化的响应
async acceptBid(bidId: string): Promise<{ message: string; contract_id: string; bid_id: string }> {
  const { data } = await this.client.post(`/bids/${bidId}/accept`);
  return data;
}
```

---

## 🌐 环境配置更新

### 开发环境配置

**文件**: `fe/.env`
```bash
# Backend API URL - Local development
NEXT_PUBLIC_API_URL=http://localhost:8000

# App Name
NEXT_PUBLIC_APP_NAME=BotBot
```

### 生产环境配置

**文件**: `fe/.env.production`
```bash
# Backend API URL - Production IP address
NEXT_PUBLIC_API_URL=http://47.83.230.114:8000

# App Name
NEXT_PUBLIC_APP_NAME=BotBot
```

### 后端生产环境配置

**文件**: `be/.env.production`
```bash
# MongoDB配置
MONGODB_URL=mongodb://mongodb:27017
MONGODB_DB_NAME=botbot

# 应用配置
DEBUG=False
API_PREFIX=/api

# 安全密钥（生产环境必须修改！）
SECRET_KEY=your-production-secret-key-here-change-this
JWT_SECRET_KEY=your-production-jwt-secret-key-here-change-this

# CORS配置
CORS_ORIGINS=http://47.83.230.114:3000,http://47.83.230.114:8000

# AI服务配置
ANTHROPIC_API_KEY=your-anthropic-api-key-here
```

---

## ✅ 后端API端点总览

### 认证 (Auth)
- `POST /api/auth/send-code` - 发送验证码
- `POST /api/auth/verify-code` - 验证码登录
- `POST /api/auth/direct-login` - 直接登录（开发模式）
- `POST /api/auth/refresh` - 刷新token
- `GET /api/auth/me` - 获取当前用户信息

### 用户 (Users)
- `GET /api/users/{user_id}` - 获取用户信息
- `PATCH /api/users/me` - 更新当前用户
- `GET /api/users/me/balance` - 查询余额
- `GET /api/users/me/ratings` - 查询我的评分

### 任务 (Tasks)
- `POST /api/tasks/` - 创建任务
- `GET /api/tasks/` - 获取任务列表
- `GET /api/tasks/{task_id}` - 获取任务详情
- `PATCH /api/tasks/{task_id}` - 更新任务
- `DELETE /api/tasks/{task_id}` - 取消任务
- `GET /api/tasks/my/tasks` - 获取我的任务
- `GET /api/tasks/{task_id}/bids` - 获取任务竞标列表 ⭐

### 竞标 (Bids)
- `POST /api/bids/` - 创建竞标 ⭐
- `GET /api/bids/{bid_id}` - 获取竞标详情
- `DELETE /api/bids/{bid_id}` - 撤回竞标
- `GET /api/bids/my-bids` - 获取我的竞标
- `POST /api/bids/{bid_id}/accept` - 接受竞标 ⭐

### 合同 (Contracts)
- `POST /api/contracts/` - 创建合同
- `GET /api/contracts/` - 获取合同列表
- `GET /api/contracts/{contract_id}` - 获取合同详情
- `POST /api/contracts/{contract_id}/submit` - 提交成果 ⭐
- `POST /api/contracts/{contract_id}/deliverables` - 提交成果（别名）
- `POST /api/contracts/{contract_id}/complete` - 确认完成

### 评分 (Ratings)
- `POST /api/ratings/` - 创建评分
- `GET /api/ratings/my-ratings` - 获取我的评分
- `GET /api/ratings/users/{user_id}/ratings` - 获取用户评分

### AI 服务 (AI)
- `POST /api/ai/analyze-task` - AI分析任务

⭐ 标记表示前端API调用已更新

---

## 🧪 测试验证

运行测试脚本验证接口：

```bash
./test_api_client.sh
```

### 测试结果
```
✅ POST /api/auth/direct-login - Success
✅ GET /api/auth/me - 200 OK
✅ POST /api/tasks/ - Success
✅ POST /api/bids/ - Success (前端更新后)
✅ GET /api/tasks/{task_id}/bids - Success (前端更新后)
✅ POST /api/bids/{bid_id}/accept - Success
✅ POST /api/contracts/{id}/submit - Success (前端更新后)
```

---

## 📦 更新的文件清单

### 前端 (Frontend)
1. `fe/src/lib/api.ts` - API客户端核心文件
   - 更新 `createBid()` 方法
   - 更新 `getTaskBids()` 方法
   - 更新 `submitDeliverables()` 方法
   - 新增 `acceptBid()` 方法

2. `fe/.env` - 开发环境配置（新建）
3. `fe/.env.production` - 生产环境配置（已存在）

### 后端 (Backend)
1. `be/.env.production` - 生产环境配置（新建）

### 测试和文档
1. `test_api_client.sh` - API接口测试脚本（新建）
2. `API_UPDATE_REPORT.md` - 本文档（新建）

---

## 🚀 部署指引

### 本地开发
```bash
# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 访问
前端: http://localhost:3000
后端: http://localhost:8000
API文档: http://localhost:8000/docs
```

### 生产部署

#### 1. 复制环境配置
```bash
# 后端
cp be/.env.production be/.env
# 编辑 be/.env，设置正确的密钥和API keys

# 前端
cp fe/.env.production fe/.env.local
```

#### 2. 构建和部署
```bash
# 使用 Docker Compose
docker-compose -f docker-compose.prod.yml up -d --build

# 或使用单独构建
docker build -t botbot-backend:prod ./be
docker build -t botbot-frontend:prod ./fe
```

#### 3. 配置反向代理
参考 `DEPLOYMENT_GUIDE.md` 配置 Nginx 反向代理和 SSL 证书。

---

## ⚠️ 注意事项

### 生产环境必须配置

1. **安全密钥**
   ```bash
   # 生成新密钥
   openssl rand -hex 32
   ```

2. **CORS配置**
   ```bash
   # 不要在生产环境使用 *
   CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
   ```

3. **MongoDB认证**
   ```bash
   # 配置MongoDB用户名密码
   MONGODB_URL=mongodb://username:password@mongodb:27017
   ```

4. **API密钥**
   ```bash
   # Claude API密钥
   ANTHROPIC_API_KEY=sk-ant-...

   # 阿里云SMS密钥
   ALIYUN_ACCESS_KEY_ID=...
   ALIYUN_ACCESS_KEY_SECRET=...
   ```

---

## 📚 相关文档

- `DEPLOYMENT_GUIDE.md` - 完整部署指南
- `test_report_final.md` - 功能测试报告
- `CLAUDE.md` - 项目开发指南
- `/api/docs` - 在线API文档 (Swagger UI)

---

## ✨ 更新完成

所有前端API调用已与后端接口对齐，生产环境配置文件已创建。系统已准备好部署到生产环境。

**最后更新**: 2026-03-14 20:30
**状态**: ✅ 完成
