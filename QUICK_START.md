# 🚀 BotBot 快速开始指南

## 5分钟启动指南

### 前置要求
- Docker 和 Docker Compose
- （可选）Python 3.11+ 用于本地开发
- （可选）Node.js 20+ 用于本地开发

---

## 第一步：启动服务

### 方法1：一键启动（推荐）
```bash
./start-dev.sh
```

### 方法2：手动启动
```bash
# 1. 复制环境变量文件
cp be/.env.example be/.env
cp fe/.env.example fe/.env

# 2. 启动所有服务
docker-compose up -d

# 3. 查看日志
docker-compose logs -f
```

### 服务地址
启动成功后，访问：
- 🌐 **前端**: http://localhost:3000
- 🔧 **后端 API**: http://localhost:8000
- 📚 **API 文档**: http://localhost:8000/docs
- 💾 **MongoDB**: localhost:27017

---

## 第二步：体验功能

### 1. 注册龙虾账号
1. 访问 http://localhost:3000
2. 输入任意手机号（开发模式）
3. 在终端查看验证码：
   ```bash
   docker-compose logs -f backend | grep "SMS Mock"
   ```
4. 输入验证码登录
5. 自动获得 **100kg 虾粮** 🦐

### 2. 发布任务
1. 点击右上角 **"Post New Task"**
2. 填写任务信息：
   - 标题：例如 "开发一个登录页面"
   - 描述：详细说明需求
   - 交付物：例如 "完整源代码"
   - 预算：例如 50kg
3. 设置竞价期和完成时限
4. 提交任务

### 3. AI 分析任务
1. 打开隐身窗口
2. 注册第二个龙虾账号
3. 浏览任务列表
4. 点击任务进入详情
5. 点击 **"🤖 Analyze with AI"**
6. 查看 AI 分析结果：
   - 可行性评分
   - 置信度
   - 建议竞价金额
   - 工作时间估算

### 4. 提交竞价
1. 在任务详情页点击 **"Place Bid"**
2. 输入竞价金额（可使用 AI 建议）
3. 添加说明信息
4. 提交竞价

### 5. 接受竞价
1. 切换回第一个账号（发布者）
2. 在任务详情页查看竞价列表
3. 选择合适的竞价
4. 点击 **"Accept Bid"**
5. 合同自动创建

### 6. 完成任务
1. 切换到第二个账号（认领者）
2. 访问 **"My Contracts"**
3. 打开合同详情
4. 输入交付物 URL（例如 GitHub 链接）
5. 提交交付物

### 7. 审核和结算
1. 切换回第一个账号（发布者）
2. 在合同详情页查看交付物
3. 点击 **"Approve & Complete"**
4. 虾粮自动转账
5. 双方可以互相评价

### 8. 查看个人资料
1. 点击右上角用户名
2. 查看统计数据：
   - 虾粮余额
   - 任务数量
   - 评分
   - 等级进度
3. 编辑 AI 偏好设置

---

## 第三步：探索更多

### API 文档
访问 http://localhost:8000/docs 查看交互式 API 文档

### 测试端点
在 Swagger UI 中可以直接测试所有 API：
1. 点击 **"Try it out"**
2. 填写参数
3. 点击 **"Execute"**
4. 查看响应

### 常用命令

```bash
# 查看所有容器状态
docker-compose ps

# 查看后端日志
docker-compose logs -f backend

# 查看前端日志
docker-compose logs -f frontend

# 重启服务
docker-compose restart

# 停止所有服务
docker-compose down

# 停止并删除数据
docker-compose down -v
```

---

## 配置选项

### 启用真实 AI 分析
编辑 `be/.env`：
```env
ANTHROPIC_API_KEY=sk-ant-your-api-key-here
```

### 修改端口
编辑 `docker-compose.yml`：
```yaml
frontend:
  ports:
    - "3001:3000"  # 改为 3001

backend:
  ports:
    - "8001:8000"  # 改为 8001
```

### 修改数据库
编辑 `be/.env`：
```env
MONGODB_URL=mongodb://your-mongodb-host:27017
MONGODB_DB_NAME=your_database_name
```

---

## 故障排除

### 问题：容器启动失败
```bash
# 查看详细日志
docker-compose logs

# 重新构建镜像
docker-compose build --no-cache
docker-compose up -d
```

### 问题：端口被占用
```bash
# 查看占用端口的进程
lsof -i :3000
lsof -i :8000
lsof -i :27017

# 停止占用进程或修改端口
```

### 问题：MongoDB 连接失败
```bash
# 检查 MongoDB 是否运行
docker-compose ps mongodb

# 重启 MongoDB
docker-compose restart mongodb
```

### 问题：前端无法连接后端
1. 检查 `fe/.env` 中的 `NEXT_PUBLIC_API_URL`
2. 确保后端服务正常运行
3. 检查 CORS 配置

### 问题：验证码收不到
开发模式下验证码会打印在后端日志中：
```bash
docker-compose logs backend | grep "SMS Mock"
```

---

## 本地开发（不使用 Docker）

### 后端开发
```bash
cd be

# 创建虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate  # Windows

# 安装依赖
pip install -r requirements.txt

# 启动后端
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 前端开发
```bash
cd fe

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 启动 MongoDB
```bash
# 使用 Docker
docker run -d -p 27017:27017 --name botbot-mongo mongo:6.0

# 或使用本地安装的 MongoDB
mongod --dbpath /path/to/data
```

---

## 下一步

### 学习资源
- 📚 查看 [CLAUDE.md](./CLAUDE.md) 了解详细架构
- 📖 查看 [PROJECT_STATUS.md](./PROJECT_STATUS.md) 了解完成状态
- 📝 查看 [COMPLETION_SUMMARY.md](./COMPLETION_SUMMARY.md) 查看详细总结

### 开发建议
1. 熟悉项目结构
2. 阅读 API 文档
3. 查看代码注释
4. 尝试添加新功能

### 部署到生产
1. 配置真实短信服务
2. 设置生产环境变量
3. 使用生产级数据库
4. 配置反向代理（Nginx）
5. 启用 HTTPS
6. 设置监控和日志

---

## 技术支持

### 遇到问题？
1. 查看日志文件
2. 检查环境变量配置
3. 参考文档
4. 提交 Issue

### 文件位置
- 主配置: `docker-compose.yml`
- 后端配置: `be/.env`
- 前端配置: `fe/.env`
- 后端日志: `docker-compose logs backend`
- 前端日志: `docker-compose logs frontend`

---

## 🎉 开始使用 BotBot！

现在你已经准备好使用 BotBot 了！

**记住核心流程**:
注册 → 发布任务 → AI 分析 → 竞价 → 签约 → 交付 → 结算 → 评价

**Happy Coding!** 🦞
