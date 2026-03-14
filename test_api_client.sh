#!/bin/bash

# API接口测试脚本 - 验证前端API调用与后端接口匹配

API_URL="http://localhost:8000"
echo "=== BotBot API 接口测试 ==="
echo "API URL: $API_URL"
echo ""

# 颜色定义
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 健康检查
echo "1️⃣  健康检查"
response=$(curl -s -o /dev/null -w "%{http_code}" $API_URL/)
if [ "$response" = "200" ]; then
    echo -e "${GREEN}✅ GET / - 200 OK${NC}"
else
    echo -e "${RED}❌ GET / - $response${NC}"
fi
echo ""

# 2. 认证接口测试
echo "2️⃣  认证接口"
phone="1380000$(date +%s | tail -c 5)"

# Direct login
echo "测试 Direct Login..."
response=$(curl -s -X POST "$API_URL/api/auth/direct-login" \
  -H "Content-Type: application/json" \
  -d "{\"phone_number\": \"$phone\"}")

if echo "$response" | jq -e '.access_token' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ POST /api/auth/direct-login - Success${NC}"
    access_token=$(echo "$response" | jq -r '.access_token')
else
    echo -e "${RED}❌ POST /api/auth/direct-login - Failed${NC}"
    echo "$response"
    exit 1
fi
echo ""

# 3. 用户接口测试
echo "3️⃣  用户接口"
response=$(curl -s -o /dev/null -w "%{http_code}" "$API_URL/api/auth/me" \
  -H "Authorization: Bearer $access_token")
if [ "$response" = "200" ]; then
    echo -e "${GREEN}✅ GET /api/auth/me - 200 OK${NC}"
else
    echo -e "${RED}❌ GET /api/auth/me - $response${NC}"
fi
echo ""

# 4. 任务接口测试
echo "4️⃣  任务接口"

# 创建任务
echo "测试创建任务..."
task_response=$(curl -s -X POST "$API_URL/api/tasks/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer $access_token" \
  -d '{
    "title": "测试任务-接口验证",
    "description": "这是一个用于验证API接口的测试任务",
    "budget": 50.0,
    "deadline": "2026-03-20T00:00:00Z",
    "category": "测试",
    "tags": ["test", "api"]
  }')

if echo "$task_response" | jq -e '._id' > /dev/null 2>&1; then
    echo -e "${GREEN}✅ POST /api/tasks/ - Success${NC}"
    task_id=$(echo "$task_response" | jq -r '._id')
else
    echo -e "${RED}❌ POST /api/tasks/ - Failed${NC}"
    echo "$task_response"
fi
echo ""

# 5. 竞标接口测试（新接口）
if [ ! -z "$task_id" ]; then
    echo "5️⃣  竞标接口（更新后）"

    # 创建第二个用户用于竞标
    phone2="1390000$(date +%s | tail -c 5)"
    user2_response=$(curl -s -X POST "$API_URL/api/auth/direct-login" \
      -H "Content-Type: application/json" \
      -d "{\"phone_number\": \"$phone2\"}")
    access_token2=$(echo "$user2_response" | jq -r '.access_token')

    # 测试新的竞标接口
    echo "测试 POST /api/bids/ (前端更新后使用)..."
    bid_response=$(curl -s -X POST "$API_URL/api/bids/" \
      -H "Content-Type: application/json" \
      -H "Authorization: Bearer $access_token2" \
      -d "{
        \"task_id\": \"$task_id\",
        \"amount\": 45.0,
        \"proposal\": \"我可以完成这个任务\"
      }")

    if echo "$bid_response" | jq -e '._id' > /dev/null 2>&1; then
        echo -e "${GREEN}✅ POST /api/bids/ - Success${NC}"
        bid_id=$(echo "$bid_response" | jq -r '._id')
    else
        echo -e "${RED}❌ POST /api/bids/ - Failed${NC}"
        echo "$bid_response"
    fi

    # 测试获取任务竞标列表
    echo "测试 GET /api/tasks/{task_id}/bids (前端更新后使用)..."
    bids_response=$(curl -s "$API_URL/api/tasks/$task_id/bids")

    if echo "$bids_response" | jq -e 'type == "array"' > /dev/null 2>&1; then
        bid_count=$(echo "$bids_response" | jq 'length')
        echo -e "${GREEN}✅ GET /api/tasks/$task_id/bids - Success (找到 $bid_count 个竞标)${NC}"
    else
        echo -e "${RED}❌ GET /api/tasks/$task_id/bids - Failed${NC}"
        echo "$bids_response"
    fi
    echo ""

    # 6. 合同接口测试
    if [ ! -z "$bid_id" ]; then
        echo "6️⃣  合同接口（更新后）"

        # 接受竞标创建合同
        echo "测试接受竞标..."
        contract_response=$(curl -s -X POST "$API_URL/api/bids/$bid_id/accept" \
          -H "Authorization: Bearer $access_token")

        if echo "$contract_response" | jq -e '._id' > /dev/null 2>&1; then
            echo -e "${GREEN}✅ POST /api/bids/$bid_id/accept - Success${NC}"
            contract_id=$(echo "$contract_response" | jq -r '._id')
        else
            echo -e "${RED}❌ POST /api/bids/$bid_id/accept - Failed${NC}"
            echo "$contract_response"
        fi

        # 测试提交成果（新接口）
        if [ ! -z "$contract_id" ]; then
            echo "测试 POST /api/contracts/{id}/submit (前端更新后使用)..."
            submit_response=$(curl -s -X POST "$API_URL/api/contracts/$contract_id/submit" \
              -H "Content-Type: application/json" \
              -H "Authorization: Bearer $access_token2" \
              -d '{
                "deliverable_url": "https://example.com/deliverable",
                "notes": "任务已完成"
              }')

            if echo "$submit_response" | jq -e '.deliverable_submitted == true' > /dev/null 2>&1; then
                echo -e "${GREEN}✅ POST /api/contracts/$contract_id/submit - Success${NC}"
            else
                echo -e "${RED}❌ POST /api/contracts/$contract_id/submit - Failed${NC}"
                echo "$submit_response"
            fi
        fi
    fi
fi

echo ""
echo "=== 接口测试完成 ==="
echo ""
echo -e "${YELLOW}📝 前端API调用已更新:${NC}"
echo "  1. createBid: POST /api/bids/ (传入 task_id)"
echo "  2. getTaskBids: GET /api/tasks/{taskId}/bids"
echo "  3. submitDeliverables: POST /api/contracts/{id}/submit (使用 deliverable_url)"
echo ""
echo -e "${YELLOW}🌐 环境配置:${NC}"
echo "  - 开发环境: fe/.env (localhost:8000)"
echo "  - 生产环境: fe/.env.production (47.83.230.114:8000)"
echo "  - 后端生产配置: be/.env.production"
