#!/bin/bash

# 部署状态检查脚本
# 用于验证 BotBot 部署是否成功

echo "🔍 BotBot 部署状态检查"
echo "========================================"
echo ""

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查是否在项目目录
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ 错误: 请在 botbot 项目根目录运行此脚本${NC}"
    exit 1
fi

# 1. 检查容器状态
echo "1️⃣  检查容器状态..."
echo ""
docker-compose ps

# 计算运行中的容器数量
RUNNING_COUNT=$(docker-compose ps | grep "Up" | wc -l)
if [ $RUNNING_COUNT -eq 3 ]; then
    echo -e "${GREEN}✅ 所有 3 个容器正在运行${NC}"
else
    echo -e "${RED}❌ 只有 $RUNNING_COUNT 个容器运行，预期 3 个${NC}"
fi
echo ""

# 2. 检查前端环境变量
echo "2️⃣  检查前端 API URL 配置..."
API_URL=$(docker-compose exec -T frontend printenv NEXT_PUBLIC_API_URL 2>/dev/null || echo "未找到")
if [[ $API_URL == *"localhost"* ]]; then
    echo -e "${RED}❌ API URL 配置错误: $API_URL${NC}"
    echo "   应该配置为生产服务器地址，而不是 localhost"
elif [[ $API_URL == "未找到" ]]; then
    echo -e "${YELLOW}⚠️  无法获取前端环境变量（容器可能未运行）${NC}"
else
    echo -e "${GREEN}✅ API URL 配置正确: $API_URL${NC}"
fi
echo ""

# 3. 检查前端运行模式
echo "3️⃣  检查前端运行模式..."
FRONTEND_ENV=$(docker-compose logs frontend 2>/dev/null | grep -o "Environment: [a-z]*" | tail -1 || echo "未找到")
if [[ $FRONTEND_ENV == *"production"* ]]; then
    echo -e "${GREEN}✅ 前端运行在生产模式${NC}"
elif [[ $FRONTEND_ENV == *"development"* ]]; then
    echo -e "${RED}❌ 前端运行在开发模式（应该是生产模式）${NC}"
else
    echo -e "${YELLOW}⚠️  无法确定前端运行模式${NC}"
fi
echo ""

# 4. 检查后端启动状态
echo "4️⃣  检查后端启动状态..."
BACKEND_STARTUP=$(docker-compose logs backend 2>/dev/null | grep "Application startup complete" | tail -1)
if [ -n "$BACKEND_STARTUP" ]; then
    echo -e "${GREEN}✅ 后端启动成功${NC}"
else
    echo -e "${RED}❌ 后端启动失败或未完成${NC}"
    echo "   查看错误日志："
    docker-compose logs backend 2>/dev/null | tail -20
fi
echo ""

# 5. 检查 CORS 配置
echo "5️⃣  检查后端 CORS 配置..."
CORS_CONFIG=$(docker-compose logs backend 2>/dev/null | grep "CORS Origins:" | tail -1)
if [ -n "$CORS_CONFIG" ]; then
    echo -e "${GREEN}✅ CORS 已配置:${NC}"
    echo "   $CORS_CONFIG"
else
    echo -e "${YELLOW}⚠️  未找到 CORS 配置日志${NC}"
fi
echo ""

# 6. 检查端口监听
echo "6️⃣  检查端口监听..."
if netstat -tuln 2>/dev/null | grep -q ":3000 "; then
    echo -e "${GREEN}✅ 前端端口 3000 正在监听${NC}"
else
    echo -e "${RED}❌ 前端端口 3000 未监听${NC}"
fi

if netstat -tuln 2>/dev/null | grep -q ":8000 "; then
    echo -e "${GREEN}✅ 后端端口 8000 正在监听${NC}"
else
    echo -e "${RED}❌ 后端端口 8000 未监听${NC}"
fi
echo ""

# 7. 测试后端 API
echo "7️⃣  测试后端 API 连接..."
BACKEND_URL="http://localhost:8000"
API_RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" $BACKEND_URL/docs 2>/dev/null || echo "000")
if [ "$API_RESPONSE" == "200" ]; then
    echo -e "${GREEN}✅ 后端 API 可访问 ($BACKEND_URL/docs)${NC}"
else
    echo -e "${RED}❌ 后端 API 不可访问 (HTTP $API_RESPONSE)${NC}"
fi
echo ""

# 8. 检查最近的错误
echo "8️⃣  检查最近的错误日志..."
echo ""
echo "--- 前端错误 ---"
FRONTEND_ERRORS=$(docker-compose logs frontend 2>&1 | grep -i "error" | tail -5)
if [ -z "$FRONTEND_ERRORS" ]; then
    echo -e "${GREEN}✅ 无错误${NC}"
else
    echo -e "${YELLOW}⚠️  发现错误:${NC}"
    echo "$FRONTEND_ERRORS"
fi

echo ""
echo "--- 后端错误 ---"
BACKEND_ERRORS=$(docker-compose logs backend 2>&1 | grep -i "error\|traceback" | tail -5)
if [ -z "$BACKEND_ERRORS" ]; then
    echo -e "${GREEN}✅ 无错误${NC}"
else
    echo -e "${YELLOW}⚠️  发现错误:${NC}"
    echo "$BACKEND_ERRORS"
fi
echo ""

# 总结
echo "========================================"
echo "📊 部署检查总结"
echo "========================================"
echo ""

# 统计通过的检查
PASS_COUNT=0
TOTAL_COUNT=7

[ $RUNNING_COUNT -eq 3 ] && ((PASS_COUNT++))
[[ $API_URL != *"localhost"* ]] && [[ $API_URL != "未找到" ]] && ((PASS_COUNT++))
[[ $FRONTEND_ENV == *"production"* ]] && ((PASS_COUNT++))
[ -n "$BACKEND_STARTUP" ] && ((PASS_COUNT++))
[ -n "$CORS_CONFIG" ] && ((PASS_COUNT++))
netstat -tuln 2>/dev/null | grep -q ":3000 " && ((PASS_COUNT++))
[ "$API_RESPONSE" == "200" ] && ((PASS_COUNT++))

echo "通过检查: $PASS_COUNT / $TOTAL_COUNT"
echo ""

if [ $PASS_COUNT -eq $TOTAL_COUNT ]; then
    echo -e "${GREEN}✅ 所有检查通过！部署成功！${NC}"
    echo ""
    echo "🌐 访问地址:"
    echo "   前端: http://localhost:3000"
    echo "   后端: http://localhost:8000/docs"
    exit 0
elif [ $PASS_COUNT -ge 5 ]; then
    echo -e "${YELLOW}⚠️  部分检查未通过，但基本可用${NC}"
    echo ""
    echo "💡 建议:"
    echo "   - 查看上述失败的检查项"
    echo "   - 运行 docker-compose logs 查看详细日志"
    exit 1
else
    echo -e "${RED}❌ 多项检查失败，部署可能有问题${NC}"
    echo ""
    echo "🔧 修复建议:"
    echo "   1. 检查 .env 配置文件"
    echo "   2. 运行 ./fix-api-url.sh 修复 API URL"
    echo "   3. 查看日志: docker-compose logs -f"
    exit 2
fi
