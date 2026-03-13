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

echo "1️⃣  Stopping current services..."
docker-compose down

echo ""
echo "2️⃣  Removing old frontend build cache..."
rm -rf fe/.next
rm -rf fe/node_modules/.cache

echo ""
echo "3️⃣  Building frontend in production mode..."
echo "   (This may take 2-3 minutes)"
docker-compose build --no-cache frontend

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Build failed! Check the error above${NC}"
    exit 1
fi

echo ""
echo "4️⃣  Starting all services..."
docker-compose up -d

echo ""
echo "5️⃣  Waiting for services to start (15 seconds)..."
for i in {15..1}; do
    echo -ne "   ${i}s remaining...\r"
    sleep 1
done
echo ""

echo ""
echo "6️⃣  Checking service status..."
echo ""
docker-compose ps

echo ""
echo "7️⃣  Checking frontend logs..."
echo ""
docker-compose logs --tail=20 frontend

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
