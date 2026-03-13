#!/bin/bash

# 强制完全重新构建脚本
# 用于清除所有缓存并从头构建

echo "🔨 强制完全重新构建"
echo "========================================"
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# 检查是否在项目目录
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ 错误: 请在 botbot 项目根目录运行此脚本${NC}"
    exit 1
fi

echo -e "${YELLOW}⚠️  警告: 此操作将删除所有 Docker 镜像和缓存${NC}"
read -p "确定继续? (y/n): " confirm

if [ "$confirm" != "y" ]; then
    echo "已取消"
    exit 0
fi

echo ""
echo "1️⃣  停止并删除所有容器..."
docker-compose down -v

echo ""
echo "2️⃣  删除前端 Docker 镜像..."
docker rmi botbot-frontend 2>/dev/null || echo "   镜像不存在，跳过"
docker rmi $(docker images | grep botbot-frontend | awk '{print $3}') 2>/dev/null || echo "   没有相关镜像"

echo ""
echo "3️⃣  清除所有前端缓存..."
rm -rf fe/.next
rm -rf fe/node_modules/.cache
rm -rf fe/.next/cache
rm -rf fe/node_modules/.pnpm
echo "   ✅ 前端缓存已清除"

echo ""
echo "4️⃣  确认环境变量配置..."
if [ ! -f ".env.production" ]; then
    echo -e "${YELLOW}⚠️  .env.production 不存在${NC}"
    echo "请选择后端 API 地址:"
    echo "   1) http://botbot.biz:8000"
    echo "   2) http://47.83.230.114:8000"
    echo "   3) 自定义"
    read -p "选择 (1/2/3): " choice

    case $choice in
        1)
            API_URL="http://botbot.biz:8000"
            ;;
        2)
            API_URL="http://47.83.230.114:8000"
            ;;
        3)
            read -p "输入 API URL: " API_URL
            ;;
        *)
            API_URL="http://botbot.biz:8000"
            ;;
    esac

    cat > .env.production << EOF
NEXT_PUBLIC_API_URL=$API_URL
EOF
    cat > fe/.env.production << EOF
NEXT_PUBLIC_API_URL=$API_URL
NEXT_PUBLIC_APP_NAME=BotBot
EOF
    echo -e "${GREEN}✅ 已创建 .env.production: $API_URL${NC}"
else
    API_URL=$(grep NEXT_PUBLIC_API_URL .env.production | cut -d'=' -f2)
    echo -e "${GREEN}✅ 使用现有配置: $API_URL${NC}"
fi

echo ""
echo "5️⃣  重新构建前端（完全无缓存）..."
export NEXT_PUBLIC_API_URL=$API_URL
docker-compose build --no-cache --pull \
  --build-arg NEXT_PUBLIC_API_URL=$API_URL \
  frontend

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 构建失败！${NC}"
    echo ""
    echo "常见问题排查:"
    echo "1. 检查代码是否是最新的: git pull origin main"
    echo "2. 检查 ESLint 错误: cat fe/.eslintrc.json"
    echo "3. 查看构建日志"
    exit 1
fi

echo ""
echo "6️⃣  启动所有服务..."
docker-compose --env-file .env.production up -d

echo ""
echo "7️⃣  等待服务启动 (20秒)..."
sleep 20

echo ""
echo "8️⃣  检查服务状态..."
docker-compose ps

echo ""
echo "9️⃣  查看前端日志..."
docker-compose logs --tail=30 frontend

echo ""
echo "🔟  验证配置..."
echo ""
echo "API URL (容器内):"
docker-compose exec -T frontend printenv NEXT_PUBLIC_API_URL 2>/dev/null || echo "   无法获取（容器可能未运行）"

echo ""
echo "前端运行模式:"
docker-compose logs frontend 2>/dev/null | grep "Environment:" | tail -1 || echo "   未找到"

echo ""
echo "========================================"
echo -e "${GREEN}✅ 重新构建完成！${NC}"
echo ""
echo "📋 下一步:"
echo "   1. 检查上述日志是否有错误"
echo "   2. 访问前端: http://$(hostname -I | awk '{print $1}'):3000"
echo "   3. 清除浏览器缓存 (Ctrl+Shift+Del)"
echo "   4. 测试登录功能"
echo ""
echo "🔍 如果还有问题:"
echo "   - 查看完整日志: docker-compose logs -f frontend"
echo "   - 运行检查脚本: ./check-deployment.sh"
echo ""
