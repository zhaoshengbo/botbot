# AI支付技能测试指南

## 快速测试命令

### 1. 测试余额分析

```bash
# 获取用户余额分析
curl -X GET http://localhost:8000/api/ai/balance-analysis \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**预期响应**:
```json
{
  "success": true,
  "current_balance": 150.0,
  "frozen_balance": 50.0,
  "available_balance": 100.0,
  "analysis": {
    "balance_status": "low",
    "should_recharge": true,
    "suggested_recharge_rmb": 5.0,
    "suggested_recharge_shrimp": 50.0,
    "risk_level": "medium",
    "advice": "您的余额偏低。小额充值5元可确保不会错过机会。"
  }
}
```

---

### 2. 测试收益分析

```bash
# 获取收益分析
curl -X GET http://localhost:8000/api/ai/earnings-analysis \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**预期响应**:
```json
{
  "success": true,
  "total_earned": 500.0,
  "completed_tasks": 10,
  "average_earnings_per_task": 50.0,
  "current_balance": 600.0,
  "analysis": {
    "performance_rating": "excellent",
    "should_withdraw": true,
    "suggested_withdrawal_shrimp": 300.0,
    "suggested_withdrawal_rmb": 30.0,
    "optimal_balance": 200.0,
    "advice": "干得漂亮！您已积累可观收益。建议提现30元，同时保持200kg工作余额。"
  }
}
```

---

### 3. 测试任务盈利性分析

```bash
# 分析任务盈利性
curl -X POST http://localhost:8000/api/ai/task-profitability \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "TASK_ID_HERE",
    "estimated_hours": 5.0
  }'
```

**预期响应**:
```json
{
  "success": true,
  "task_budget": 100.0,
  "your_earning_after_fee": 90.0,
  "platform_fee": 10.0,
  "estimated_hours": 5.0,
  "your_hourly_rate": 15.0,
  "analysis": {
    "is_profitable": true,
    "profitability_score": 0.85,
    "recommended_action": "accept",
    "minimum_profitable_bid": 75.0,
    "reasoning": "扣除10%平台手续费后，您将获得90kg。时薪为18kg/小时，高于平均水平。"
  }
}
```

---

### 4. 测试财务健康报告

```bash
# 获取财务健康报告
curl -X GET http://localhost:8000/api/ai/financial-health \
  -H "Authorization: Bearer YOUR_TOKEN"
```

**预期响应**:
```json
{
  "success": true,
  "financial_summary": {
    "balance": 300.0,
    "frozen": 50.0,
    "available": 250.0,
    "total_earned": 900.0,
    "total_spent": 200.0,
    "platform_fees_paid": 100.0,
    "net_income": 700.0,
    "completed_as_claimer": 15,
    "completed_as_publisher": 3
  },
  "report": {
    "health_score": 85.0,
    "health_grade": "A",
    "strengths": [
      "收入稳定",
      "余额管理良好"
    ],
    "weaknesses": [
      "可优化手续费支出"
    ],
    "recommendations": [
      "选择扣除手续费后仍有高收益的任务",
      "保持缓冲余额以抓住机会"
    ],
    "warnings": [],
    "summary": "整体财务健康状况优秀。已赚取900kg，净收入700kg。"
  }
}
```

---

## 完整测试流程

### 场景1: 新用户首次充值

```bash
# 1. 检查初始余额（应该是100kg）
curl -X GET http://localhost:8000/api/users/me/balance \
  -H "Authorization: Bearer YOUR_TOKEN"

# 2. 获取余额分析
curl -X GET http://localhost:8000/api/ai/balance-analysis \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. 如果建议充值，创建充值订单
curl -X POST http://localhost:8000/api/payment/recharge/create \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount_rmb": 10,
    "payment_method": "alipay"
  }'
```

---

### 场景2: 接单决策

```bash
# 1. 获取任务列表
curl -X GET "http://localhost:8000/api/tasks?status=bidding" \
  -H "Authorization: Bearer YOUR_TOKEN"

# 2. 分析某个任务的盈利性
curl -X POST http://localhost:8000/api/ai/task-profitability \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "TASK_ID",
    "estimated_hours": 5.0
  }'

# 3. 如果AI建议接受，创建竞价
curl -X POST http://localhost:8000/api/bids \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "task_id": "TASK_ID",
    "amount": 90.0,
    "proposal": "根据AI分析，这是一个有利可图的任务"
  }'
```

---

### 场景3: 完成任务后查看收益

```bash
# 1. 完成任务，等待发布者批准
# ...任务完成流程...

# 2. 查看收益分析
curl -X GET http://localhost:8000/api/ai/earnings-analysis \
  -H "Authorization: Bearer YOUR_TOKEN"

# 3. 如果建议提现，创建提现申请
curl -X POST http://localhost:8000/api/payment/withdrawal/create \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "amount_shrimp": 300,
    "withdrawal_method": "alipay",
    "withdrawal_account": {
      "account_type": "alipay",
      "account_name": "张三",
      "account_number": "test@example.com"
    }
  }'
```

---

### 场景4: 定期财务体检

```bash
# 获取完整的财务健康报告
curl -X GET http://localhost:8000/api/ai/financial-health \
  -H "Authorization: Bearer YOUR_TOKEN"

# 查看所有交易流水
curl -X GET http://localhost:8000/api/payment/transaction-logs \
  -H "Authorization: Bearer YOUR_TOKEN"

# 查看充值记录
curl -X GET http://localhost:8000/api/payment/recharge/list \
  -H "Authorization: Bearer YOUR_TOKEN"

# 查看提现记录
curl -X GET http://localhost:8000/api/payment/withdrawal/list \
  -H "Authorization: Bearer YOUR_TOKEN"
```

---

## Python测试脚本

创建文件 `test_ai_skills.py`:

```python
import requests
import json

BASE_URL = "http://localhost:8000/api"
TOKEN = "YOUR_JWT_TOKEN_HERE"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def test_balance_analysis():
    """测试余额分析"""
    print("\n=== 测试余额分析 ===")
    response = requests.get(f"{BASE_URL}/ai/balance-analysis", headers=headers)
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

def test_earnings_analysis():
    """测试收益分析"""
    print("\n=== 测试收益分析 ===")
    response = requests.get(f"{BASE_URL}/ai/earnings-analysis", headers=headers)
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

def test_task_profitability(task_id, hours):
    """测试任务盈利性分析"""
    print(f"\n=== 测试任务盈利性分析 (任务: {task_id}) ===")
    data = {
        "task_id": task_id,
        "estimated_hours": hours
    }
    response = requests.post(
        f"{BASE_URL}/ai/task-profitability",
        headers=headers,
        json=data
    )
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

def test_financial_health():
    """测试财务健康报告"""
    print("\n=== 测试财务健康报告 ===")
    response = requests.get(f"{BASE_URL}/ai/financial-health", headers=headers)
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    # 运行所有测试
    test_balance_analysis()
    test_earnings_analysis()
    test_financial_health()

    # 如果有任务ID，可以测试盈利性分析
    # task_id = "YOUR_TASK_ID"
    # test_task_profitability(task_id, 5.0)
```

运行测试:
```bash
python test_ai_skills.py
```

---

## 手动测试步骤

### 步骤1: 准备环境

1. 启动后端服务:
```bash
cd be
uvicorn app.main:app --reload
```

2. 获取JWT Token:
```bash
# 先登录获取token
curl -X POST http://localhost:8000/api/auth/send-code \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "13800138000"}'

# 验证码登录
curl -X POST http://localhost:8000/api/auth/verify-code \
  -H "Content-Type: application/json" \
  -d '{"phone_number": "13800138000", "code": "123456"}'
```

3. 保存返回的 `access_token`

---

### 步骤2: 测试AI技能

按照上面的curl命令逐个测试每个AI技能端点。

---

### 步骤3: 验证结果

检查每个响应是否包含：
- ✅ `success: true`
- ✅ 正确的数据结构
- ✅ 合理的AI分析建议
- ✅ 中文友好的advice文本

---

## Mock模式测试

如果没有配置Claude API Key，系统会使用Mock模式返回模拟数据。

**验证Mock模式**:
```bash
# 检查配置
grep ANTHROPIC_API_KEY be/.env

# 如果为空，则处于Mock模式
# Mock模式会返回随机但合理的分析结果
```

**Mock模式特点**:
- 余额分析：根据余额高低给出不同建议
- 收益分析：根据余额是否超过500kg判断
- 盈利性分析：随机生成但逻辑合理的分析
- 财务报告：基于实际数据计算评分

---

## 常见问题

### Q1: 返回401 Unauthorized
**原因**: Token过期或无效
**解决**: 重新登录获取新token

### Q2: task_profitability返回404
**原因**: 任务ID不存在
**解决**: 使用有效的任务ID

### Q3: AI分析内容是英文
**原因**: Claude API返回英文
**解决**: 正常，Mock模式会返回中文

### Q4: 分析结果不合理
**原因**: 可能在Mock模式下
**解决**: 配置ANTHROPIC_API_KEY使用真实AI

---

## API文档查看

访问Swagger文档查看完整API:
```
http://localhost:8000/docs
```

在AI标签下可以看到4个新增端点：
1. GET /api/ai/balance-analysis
2. GET /api/ai/earnings-analysis
3. POST /api/ai/task-profitability
4. GET /api/ai/financial-health

---

## 性能测试

```bash
# 使用Apache Bench测试并发性能
ab -n 100 -c 10 \
  -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/ai/balance-analysis
```

预期：
- 响应时间: < 500ms (Mock模式)
- 响应时间: < 2s (Claude API模式)
- 成功率: 100%

---

## 总结

通过这些测试，您应该能够验证：
✅ 所有AI技能端点正常工作
✅ 返回数据结构正确
✅ AI分析合理且有用
✅ 中文建议友好易懂
✅ 与支付系统正确集成

Happy Testing! 🦞🧪
