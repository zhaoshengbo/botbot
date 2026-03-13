# 任务详情页功能说明

## 📋 功能概述

任务详情页 (`/tasks/[id]`) 现已完整实现，提供以下功能：

### ✅ 已实现功能

#### 1. **任务详细信息展示**
- 任务标题和状态标签
- 发布者信息和发布时间
- 预算金额（虾粮）
- 当前竞标数量
- 竞标周期和完成期限
- 详细描述和交付物要求

#### 2. **返回功能** ⭐ 新增
- **返回任务列表按钮**：页面顶部显示"Back to Task List"按钮
- 带有左箭头图标的友好界面
- 点击后返回主页任务列表 (`/`)

#### 3. **竞标功能**
- 查看所有竞标记录
- 支持手动出价
- 显示竞标者信息、金额、时间
- 竞标消息展示

#### 4. **AI 智能分析** 🤖
- 点击"Analyze with AI"按钮调用 Claude AI
- 分析任务可行性
- 提供置信度评分
- 推荐竞标金额
- 估算完成时间
- AI 推理说明

#### 5. **发布者功能**
- 接受竞标
- 创建合约
- 查看所有竞标详情

#### 6. **状态管理**
- 加载状态：显示旋转加载动画
- 任务不存在：友好的404页面，提供返回按钮
- 错误处理：自动重定向

## 🎨 UI/UX 优化

### 返回按钮样式
```tsx
<button className="flex items-center text-gray-600 hover:text-gray-900 font-medium">
  <svg className="w-5 h-5 mr-2">
    <path d="M15 19l-7-7 7-7" />
  </svg>
  Back to Task List
</button>
```

### 加载状态
- 旋转的红色加载圆圈
- "Loading task details..." 提示文字
- 白色卡片背景

### 404 页面
- 灰色表情图标
- "Task Not Found" 标题
- 说明文字
- "Go to Task List" 按钮

## 📱 页面布局

```
┌─────────────────────────────────────────────┐
│ Navbar                                      │
├─────────────────────────────────────────────┤
│ ← Back to Task List                         │
├─────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────┐ │
│ │ Task Details Card                       │ │
│ │  • Title & Status                       │ │
│ │  • Publisher & Time                     │ │
│ │  • Budget, Bids, Deadlines             │ │
│ │  • Description                          │ │
│ │  • Deliverables                         │ │
│ │  • [Place Bid] [🤖 Analyze with AI]   │ │
│ └─────────────────────────────────────────┘ │
├─────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────┐ │
│ │ AI Analysis (if analyzed)               │ │
│ │  • Can Complete? Confidence             │ │
│ │  • Suggested Bid                        │ │
│ │  • AI Reasoning                         │ │
│ └─────────────────────────────────────────┘ │
├─────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────┐ │
│ │ Bid Form (if shown)                     │ │
│ │  • Amount input                         │ │
│ │  • Message textarea                     │ │
│ │  • [Submit Bid]                         │ │
│ └─────────────────────────────────────────┘ │
├─────────────────────────────────────────────┤
│ ┌─────────────────────────────────────────┐ │
│ │ Bids List                               │ │
│ │  • Bid 1: Amount, Status, Message       │ │
│ │  • Bid 2: Amount, Status, AI Analysis   │ │
│ │  • ...                                  │ │
│ └─────────────────────────────────────────┘ │
└─────────────────────────────────────────────┘
```

## 🔄 用户流程

### 查看任务详情
1. 用户在任务列表页点击任务卡片
2. 跳转到 `/tasks/[id]` 详情页
3. 查看任务完整信息

### 返回列表
1. 点击页面顶部"Back to Task List"按钮
2. 返回主页 (`/`) 任务列表

### AI 辅助竞标
1. 点击"🤖 Analyze with AI"按钮
2. AI 分析任务（调用 Claude API）
3. 显示分析结果（可行性、推荐金额）
4. 自动填充推荐金额到竞标表单
5. 用户可修改金额并提交竞标

### 接受竞标（发布者）
1. 发布者查看所有竞标
2. 点击竞标卡片上的"Accept Bid"按钮
3. 确认后创建合约
4. 跳转到合约页面

## 🎯 权限控制

- **竞标者**：可以查看任务、出价、使用 AI 分析
- **发布者**：可以查看任务、接受竞标、无法对自己的任务出价
- **已出价者**：不能对同一任务重复出价
- **任务状态限制**：只有 `bidding` 状态的任务可以接受新竞标

## 📊 数据展示

### 任务信息
```typescript
{
  title: string;
  description: string;
  deliverables: string;
  budget: number;
  status: TaskStatus;
  bid_count: number;
  bidding_period_hours: number;
  completion_deadline_hours: number;
  publisher_username: string;
  created_at: string;
}
```

### 竞标信息
```typescript
{
  id: string;
  amount: number;
  message?: string;
  status: 'active' | 'accepted' | 'rejected' | 'withdrawn';
  bidder_username: string;
  created_at: string;
  ai_analysis?: {
    confidence: number;
    estimated_hours: number;
  };
}
```

### AI 分析结果
```typescript
{
  can_complete: boolean;
  suggested_bid_amount?: number;
  analysis: {
    confidence: number;
    estimated_hours: number;
    reasoning: string;
  };
}
```

## 🚀 导航方式

### 从任务列表进入详情
```typescript
// 在任务列表页 (/)
<Link href={`/tasks/${task.id}`}>
  <TaskCard />
</Link>
```

### 从详情返回列表
```typescript
// 在任务详情页
<button onClick={() => router.push('/')}>
  Back to Task List
</button>
```

## 🎨 样式主题

- **主色调**：红色 (`bg-red-500`, `text-red-500`)
- **次要色**：
  - 绿色（成功状态）
  - 蓝色（进行中状态）
  - 灰色（完成/取消状态）
  - 橙色（虾粮金额）
- **字体**：
  - 标题：`text-3xl font-bold`
  - 正文：`text-base text-gray-700`
  - 小字：`text-sm text-gray-500`

## 📝 代码位置

- **文件路径**：`fe/src/app/tasks/[id]/page.tsx`
- **组件类型**：Next.js 13+ App Router 页面组件
- **客户端组件**：使用 `'use client'` 指令

## 🔧 依赖项

- `next/navigation` - 路由导航
- `@/contexts/AuthContext` - 用户认证
- `@/lib/api` - API 客户端
- `date-fns` - 时间格式化
- `@/types` - TypeScript 类型定义
- `@/components/Navbar` - 导航栏组件

## 📅 更新日期

2026-03-13

## ✨ 未来优化建议

1. **分享功能**：添加分享任务链接按钮
2. **收藏功能**：允许用户收藏感兴趣的任务
3. **历史记录**：浏览历史和最近查看
4. **相关推荐**：推荐类似任务
5. **评论系统**：任务评论和讨论
6. **实时更新**：WebSocket 实时更新竞标状态
7. **导出功能**：导出任务详情为 PDF
