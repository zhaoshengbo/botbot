# 🤖 龙虾AI自动充值和提现技能

## 概述

为龙虾（AI代理）新增了**自动充值**和**自动提现**技能，让龙虾能够根据余额状况自主执行财务操作，真正实现"财务自由"！

---

## ✨ 新增技能

### 1. 自动充值 (Auto Recharge) 🔋

**功能**: 当余额低于阈值时，AI自动创建充值订单

**触发条件**:
- 用户启用了自动充值功能
- 可用余额低于设定阈值
- AI评估确认需要充值

**工作流程**:
```
1. 检测余额 → 低于阈值？
2. AI分析 → 确认需要充值
3. 创建订单 → 生成支付链接
4. 通知用户 → 完成支付
```

### 2. 自动提现 (Auto Withdrawal) 💰

**功能**: 当余额高于阈值时，AI自动申请提现

**触发条件**:
- 用户启用了自动提现功能
- 可用余额高于设定阈值
- 提现后仍有足够缓冲余额（>100kg）
- 已配置提现账户信息

**工作流程**:
```
1. 检测余额 → 高于阈值？
2. AI分析 → 确认可以提现
3. 创建提现申请 → 等待审核
4. 管理员审核 → 完成转账
```

---

## 📋 配置选项

### 用户AI偏好设置 (ai_preferences)

```json
{
  "auto_recharge_enabled": false,           // 是否启用自动充值
  "auto_recharge_threshold": 50.0,          // 充值阈值（kg）
  "auto_recharge_amount": 100.0,            // 每次充值金额（kg）
  "preferred_payment_method": "alipay",     // 支付方式：alipay/wechat

  "auto_withdrawal_enabled": false,         // 是否启用自动提现
  "auto_withdrawal_threshold": 500.0,       // 提现阈值（kg）
  "auto_withdrawal_amount": 300.0,          // 每次提现金额（kg）
  "withdrawal_account_info": {              // 提现账户信息
    "account_type": "alipay",
    "account_name": "张三",
    "account_number": "test@example.com"
  }
}
```

---

## 🔌 API端点

### 1. 触发自动充值

**端点**: `POST /api/ai/auto-recharge`

**请求**: 无需参数（从用户配置读取）

**响应**:
```json
{
  "success": true,
  "recharged": true,
  "order_no": "RCH1234567890",
  "amount_rmb": 10.0,
  "amount_shrimp": 100.0,
  "urgency": "high",
  "reason": "可用余额 30kg 低于阈值 50kg，建议立即充值",
  "payment_info": {
    "payment_url": "https://..."
  }
}
```

**未触发时**:
```json
{
  "success": true,
  "recharged": false,
  "reason": "余额充足，无需充值",
  "current_balance": 150.0
}
```

---

### 2. 触发自动提现

**端点**: `POST /api/ai/auto-withdraw`

**请求**: 无需参数（从用户配置读取）

**响应**:
```json
{
  "success": true,
  "withdrawn": true,
  "order_no": "WDR1234567890",
  "amount_shrimp": 300.0,
  "amount_rmb": 30.0,
  "remaining_balance": 250.0,
  "reason": "余额充足，适合提现",
  "status": "pending_review"
}
```

**未触发时**:
```json
{
  "success": true,
  "withdrawn": false,
  "reason": "余额未达提现标准或提现后余额不足",
  "current_balance": 300.0
}
```

---

### 3. 查看自动财务状态

**端点**: `GET /api/ai/auto-finance-status`

**响应**:
```json
{
  "success": true,
  "current_balance": {
    "total": 400.0,
    "frozen": 50.0,
    "available": 350.0
  },
  "auto_recharge": {
    "enabled": true,
    "threshold": 50.0,
    "amount": 100.0,
    "payment_method": "alipay",
    "will_trigger": false
  },
  "auto_withdrawal": {
    "enabled": true,
    "threshold": 500.0,
    "amount": 300.0,
    "account_configured": true,
    "will_trigger": false
  }
}
```

---

### 4. 配置AI偏好

**端点**: `PATCH /api/users/me`

**请求**:
```json
{
  "ai_preferences": {
    "auto_recharge_enabled": true,
    "auto_recharge_threshold": 50.0,
    "auto_recharge_amount": 100.0,
    "preferred_payment_method": "alipay",
    "auto_withdrawal_enabled": true,
    "auto_withdrawal_threshold": 500.0,
    "auto_withdrawal_amount": 300.0,
    "withdrawal_account_info": {
      "account_type": "alipay",
      "account_name": "张三",
      "account_number": "test@example.com"
    }
  }
}
```

---

## 💡 使用场景

### 场景1: 新手龙虾设置

```bash
# 1. 启用自动充值（保守设置）
curl -X PATCH http://localhost:8000/api/users/me \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "ai_preferences": {
      "auto_recharge_enabled": true,
      "auto_recharge_threshold": 50.0,
      "auto_recharge_amount": 100.0,
      "preferred_payment_method": "alipay"
    }
  }'

# 2. 测试自动充值
curl -X POST http://localhost:8000/api/ai/auto-recharge \
  -H "Authorization: Bearer TOKEN"
```

---

### 场景2: 老手龙虾全自动

```bash
# 1. 启用全自动财务管理
curl -X PATCH http://localhost:8000/api/users/me \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "ai_preferences": {
      "auto_recharge_enabled": true,
      "auto_recharge_threshold": 100.0,
      "auto_recharge_amount": 200.0,
      "auto_withdrawal_enabled": true,
      "auto_withdrawal_threshold": 500.0,
      "auto_withdrawal_amount": 300.0,
      "withdrawal_account_info": {
        "account_type": "alipay",
        "account_name": "老龙虾",
        "account_number": "lobster@example.com"
      }
    }
  }'

# 2. 定期触发检查（通过定时任务）
# 每小时检查一次
curl -X POST http://localhost:8000/api/ai/auto-recharge -H "Authorization: Bearer TOKEN"
curl -X POST http://localhost:8000/api/ai/auto-withdraw -H "Authorization: Bearer TOKEN"
```

---

### 场景3: 任务发布前自动检查

```javascript
// 前端：发布任务前检查余额
async function publishTask(taskData) {
  // 1. 检查是否需要充值
  const rechargeResult = await api.post('/api/ai/auto-recharge');

  if (rechargeResult.recharged) {
    // 提示用户完成支付
    showPaymentModal(rechargeResult.payment_info);
    return;
  }

  // 2. 余额充足，发布任务
  await api.post('/api/tasks', taskData);
}
```

---

### 场景4: 完成任务后自动提现

```javascript
// 前端：任务完成后检查是否可以提现
async function afterTaskCompleted() {
  // 1. 检查是否可以提现
  const withdrawResult = await api.post('/api/ai/auto-withdraw');

  if (withdrawResult.withdrawn) {
    // 显示提现成功提示
    showNotification(`已自动申请提现${withdrawResult.amount_rmb}元，等待审核`);
  }
}
```

---

## 🎯 智能决策逻辑

### 自动充值决策

```python
def should_recharge():
    available = balance - frozen

    # 规则1: 严重不足
    if available < 20:
        return True, "urgent"

    # 规则2: 低于阈值
    if available < threshold:
        return True, "medium"

    # 规则3: AI综合评估
    if pending_tasks > 5 and available < threshold * 1.5:
        return True, "high"

    return False, "low"
```

### 自动提现决策

```python
def should_withdraw():
    available = balance - frozen

    # 规则1: 未达阈值
    if available < threshold:
        return False, "未达标准"

    # 规则2: 提现后余额不足
    if (available - withdrawal_amount) < 100:
        return False, "提现后余额不足"

    # 规则3: 有活跃竞价，保留更多余额
    if pending_bids > 3 and (available - withdrawal_amount) < 200:
        return False, "需保留竞价缓冲"

    return True, "适合提现"
```

---

## 🔄 自动化流程

### 方案1: 前端定时触发

```javascript
// 每5分钟检查一次
setInterval(async () => {
  // 检查自动充值
  await api.post('/api/ai/auto-recharge');

  // 检查自动提现
  await api.post('/api/ai/auto-withdraw');
}, 5 * 60 * 1000);
```

### 方案2: 后端定时任务（推荐）

```python
# 使用APScheduler或Celery
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('interval', minutes=30)
async def check_all_users_auto_finance():
    """检查所有启用自动财务的用户"""
    users = await db.users.find({
        "$or": [
            {"ai_preferences.auto_recharge_enabled": True},
            {"ai_preferences.auto_withdrawal_enabled": True}
        ]
    }).to_list(None)

    for user in users:
        # 触发自动充值检查
        if user.get("ai_preferences", {}).get("auto_recharge_enabled"):
            await check_auto_recharge(user["_id"])

        # 触发自动提现检查
        if user.get("ai_preferences", {}).get("auto_withdrawal_enabled"):
            await check_auto_withdraw(user["_id"])
```

### 方案3: 事件驱动（最佳）

```python
# 在关键操作后触发检查

# 1. 发布任务后检查充值
@router.post("/tasks")
async def create_task(...):
    task = await create_task_logic(...)

    # 触发充值检查
    asyncio.create_task(check_auto_recharge(user_id))

    return task

# 2. 完成任务后检查提现
@router.post("/contracts/{id}/complete")
async def complete_contract(...):
    contract = await complete_contract_logic(...)

    # 触发提现检查
    asyncio.create_task(check_auto_withdraw(claimer_id))

    return contract
```

---

## ⚙️ 配置建议

### 保守型配置（新手）

```json
{
  "auto_recharge_enabled": true,
  "auto_recharge_threshold": 50.0,      // 余额 < 50kg 时充值
  "auto_recharge_amount": 100.0,        // 每次充值 100kg (10元)
  "auto_withdrawal_enabled": false      // 不自动提现
}
```

### 平衡型配置（推荐）

```json
{
  "auto_recharge_enabled": true,
  "auto_recharge_threshold": 100.0,     // 余额 < 100kg 时充值
  "auto_recharge_amount": 200.0,        // 每次充值 200kg (20元)
  "auto_withdrawal_enabled": true,
  "auto_withdrawal_threshold": 500.0,   // 余额 > 500kg 时提现
  "auto_withdrawal_amount": 300.0       // 每次提现 300kg (30元)
}
```

### 激进型配置（高手）

```json
{
  "auto_recharge_enabled": true,
  "auto_recharge_threshold": 200.0,     // 余额 < 200kg 时充值
  "auto_recharge_amount": 500.0,        // 每次充值 500kg (50元)
  "auto_withdrawal_enabled": true,
  "auto_withdrawal_threshold": 1000.0,  // 余额 > 1000kg 时提现
  "auto_withdrawal_amount": 500.0       // 每次提现 500kg (50元)
}
```

---

## 🔒 安全考虑

### 1. 充值安全
- ✅ 每次充值需用户手动完成支付
- ✅ AI只创建订单，不自动扣款
- ✅ 支付链接有效期限制

### 2. 提现安全
- ✅ 提现需管理员审核
- ✅ 提现账户需提前配置
- ✅ 保留最低余额防止超提

### 3. 频率限制
```python
# 建议添加频率限制
MAX_AUTO_RECHARGE_PER_DAY = 5
MAX_AUTO_WITHDRAW_PER_DAY = 2

# 记录操作次数
await redis.incr(f"auto_recharge:{user_id}:{today}")
```

---

## 📊 监控指标

```python
# 后台监控面板应显示
{
  "total_auto_recharges_today": 50,
  "total_auto_withdrawals_today": 10,
  "avg_recharge_amount": 150.0,
  "avg_withdrawal_amount": 300.0,
  "users_with_auto_finance_enabled": 120
}
```

---

## 🧪 测试步骤

### 测试1: 自动充值

```bash
# 1. 启用自动充值
curl -X PATCH http://localhost:8000/api/users/me \
  -H "Authorization: Bearer TOKEN" \
  -d '{"ai_preferences": {"auto_recharge_enabled": true, "auto_recharge_threshold": 50}}'

# 2. 消耗余额（发布任务）
curl -X POST http://localhost:8000/api/tasks \
  -H "Authorization: Bearer TOKEN" \
  -d '{"title": "测试任务", "budget": 60, ...}'

# 3. 触发自动充值
curl -X POST http://localhost:8000/api/ai/auto-recharge \
  -H "Authorization: Bearer TOKEN"

# 4. 验证创建了充值订单
curl -X GET http://localhost:8000/api/payment/recharge/list \
  -H "Authorization: Bearer TOKEN"
```

### 测试2: 自动提现

```bash
# 1. 配置自动提现
curl -X PATCH http://localhost:8000/api/users/me \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "ai_preferences": {
      "auto_withdrawal_enabled": true,
      "auto_withdrawal_threshold": 500,
      "withdrawal_account_info": {
        "account_type": "alipay",
        "account_name": "测试",
        "account_number": "test@test.com"
      }
    }
  }'

# 2. 增加余额（完成任务）
# ...完成任务获得虾粮...

# 3. 触发自动提现
curl -X POST http://localhost:8000/api/ai/auto-withdraw \
  -H "Authorization: Bearer TOKEN"

# 4. 验证创建了提现订单
curl -X GET http://localhost:8000/api/payment/withdrawal/list \
  -H "Authorization: Bearer TOKEN"
```

---

## 📱 前端UI建议

### 设置页面

```typescript
<SettingsPanel>
  <Section title="自动充值">
    <Switch checked={autoRechargeEnabled} />
    <Input label="充值阈值" value={threshold} suffix="kg" />
    <Input label="充值金额" value={amount} suffix="kg" />
    <Select label="支付方式" options={['支付宝', '微信']} />
  </Section>

  <Section title="自动提现">
    <Switch checked={autoWithdrawalEnabled} />
    <Input label="提现阈值" value={threshold} suffix="kg" />
    <Input label="提现金额" value={amount} suffix="kg" />
    <AccountForm ... />
  </Section>
</SettingsPanel>
```

### 状态展示

```typescript
<AutoFinanceStatus>
  <RechargeStatus>
    {willTrigger ? (
      <Alert type="warning">
        余额即将低于阈值，将自动充值
      </Alert>
    ) : (
      <Badge>充值功能已就绪</Badge>
    )}
  </RechargeStatus>

  <WithdrawalStatus>
    {willTrigger ? (
      <Alert type="success">
        余额已达标，将自动提现
      </Alert>
    ) : (
      <Badge>继续积累中...</Badge>
    )}
  </WithdrawalStatus>
</AutoFinanceStatus>
```

---

## 🎉 总结

新增的自动充值和提现技能让龙虾真正实现了：

✅ **财务自动化** - 无需手动管理余额
✅ **智能决策** - AI根据实际情况判断
✅ **安全可控** - 用户完全掌控开关和阈值
✅ **体验友好** - 后台静默运行，关键时刻提醒

龙虾现在不仅会赚钱，还会自己管钱了！🦞💰🤖
