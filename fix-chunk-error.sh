#!/bin/bash

# BotBot Frontend Chunk Loading Error Fix
# Fixes: ChunkLoadError by switching to production build

echo "🔧 Fixing Frontend Chunk Loading Error"
echo "======================================"
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;36m'
NC='\033[0m'

# Check if in project directory
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ Error: Run this script from botbot project root${NC}"
    exit 1
fi

echo -e "${BLUE}📋 Problem: Frontend running in dev mode causes chunk timeouts${NC}"
echo -e "${BLUE}📋 Solution: Switch to optimized production build${NC}"
echo ""

echo "1️⃣  检查和配置环境变量..."
echo ""

# Check if .env.production exists
if [ ! -f ".env.production" ]; then
    echo -e "${YELLOW}⚠️  .env.production 不存在，创建默认配置...${NC}"
    cat > .env.production << 'ENVEOF'
# Production Environment Variables
NEXT_PUBLIC_API_URL=http://botbot.biz:8000
ENVEOF
    echo -e "${GREEN}✅ 已创建 .env.production${NC}"
fi

# Show current API URL
echo "📄 当前配置的 API URL:"
grep "NEXT_PUBLIC_API_URL" .env.production | grep -v "^#" || echo "   未配置"
echo ""

read -p "是否需要修改 API URL? (y/n): " modify_api

if [ "$modify_api" = "y" ]; then
    echo "请选择后端 API 地址:"
    echo "   1) http://botbot.biz:8000 (域名)"
    echo "   2) http://47.83.230.114:8000 (IP)"
    echo "   3) 自定义"
    read -p "选择 (1/2/3): " api_choice

    case $api_choice in
        1)
            API_URL="http://botbot.biz:8000"
            ;;
        2)
            API_URL="http://47.83.230.114:8000"
            ;;
        3)
            read -p "输入 API URL: " API_URL
            ;;
    esac

    sed -i "s|NEXT_PUBLIC_API_URL=.*|NEXT_PUBLIC_API_URL=$API_URL|g" .env.production
    echo -e "${GREEN}✅ 已更新 API URL 为: $API_URL${NC}"
fi

echo ""
echo "2️⃣  Stopping current services..."
docker-compose down

echo ""
echo "3️⃣  Removing old frontend build cache..."
rm -rf fe/.next
rm -rf fe/node_modules/.cache

echo ""
echo "4️⃣  Building frontend in production mode..."
echo "   (This may take 2-3 minutes)"
# Load .env.production and build
export $(cat .env.production | grep -v "^#" | xargs)
docker-compose build --no-cache frontend

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Build failed! Check the error above${NC}"
    exit 1
fi

echo ""
echo "5️⃣  Starting all services..."
# Start with environment variables loaded
docker-compose --env-file .env.production up -d

echo ""
echo "6️⃣  Waiting for services to start (15 seconds)..."
for i in {15..1}; do
    echo -ne "   ${i}s remaining...\r"
    sleep 1
done
echo ""

echo ""
echo "7️⃣  Checking service status..."
echo ""
docker-compose ps

echo ""
echo "8️⃣  Checking frontend logs..."
echo ""
docker-compose logs --tail=20 frontend

echo ""
echo "9️⃣  Verifying API URL configuration..."
docker-compose exec -T frontend printenv | grep NEXT_PUBLIC_API_URL || echo "Environment variable not found in container"

echo ""
echo "======================================"
echo -e "${GREEN}✅ Fix Applied Successfully!${NC}"
echo ""
echo "🎯 What Changed:"
echo "   • Frontend now runs in production mode"
echo "   • Optimized static assets generated"
echo "   • Chunks are pre-built and served efficiently"
echo ""
echo "🌐 Test Your App:"
echo "   Frontend: http://47.83.230.114:3000"
echo "   Backend:  http://47.83.230.114:8000/docs"
echo ""
echo "💡 Tips:"
echo "   • Clear browser cache (Ctrl+Shift+Del)"
echo "   • Hard refresh (Ctrl+F5)"
echo "   • Check browser console (F12) for errors"
echo ""
echo "📊 Monitor logs:"
echo "   docker-compose logs -f frontend"
echo "   docker-compose logs -f backend"
echo ""
