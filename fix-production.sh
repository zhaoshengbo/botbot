#!/bin/bash

# BotBot 生产环境快速修复脚本
# 解决前端无法连接后端的问题

echo "🔧 BotBot 生产环境修复脚本"
echo "================================"
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否在项目目录
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ 错误: 请在 botbot 项目根目录运行此脚本${NC}"
    exit 1
fi

echo "1️⃣  检查当前配置..."
echo ""

# 显示当前前端环境变量
if [ -f "fe/.env" ]; then
    echo "📄 当前 fe/.env 配置:"
    cat fe/.env | grep NEXT_PUBLIC_API_URL || echo "   未找到 NEXT_PUBLIC_API_URL"
    echo ""
fi

if [ -f "fe/.env.production" ]; then
    echo "📄 当前 fe/.env.production 配置:"
    cat fe/.env.production | grep NEXT_PUBLIC_API_URL
    echo ""
fi

# 询问用户选择后端地址
echo "2️⃣  请选择后端 API 地址:"
echo "   1) http://botbot.biz:8000 (域名，推荐)"
echo "   2) http://47.83.230.114:8000 (IP 地址)"
echo "   3) 自定义地址"
echo ""
read -p "请输入选项 (1/2/3): " choice

case $choice in
    1)
        API_URL="http://botbot.biz:8000"
        ;;
    2)
        API_URL="http://47.83.230.114:8000"
        ;;
    3)
        read -p "请输入后端 API 地址 (如 http://your-domain:8000): " API_URL
        ;;
    *)
        echo -e "${RED}❌ 无效选项${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ 将使用后端地址: $API_URL${NC}"
echo ""

# 更新前端环境变量
echo "3️⃣  更新前端配置..."

# 创建或更新 .env.production
cat > fe/.env.production << EOF
# Production Environment Variables for BotBot Frontend
NEXT_PUBLIC_API_URL=$API_URL
NEXT_PUBLIC_APP_NAME=BotBot
EOF

echo -e "${GREEN}✅ 已更新 fe/.env.production${NC}"
echo ""

# 也更新开发环境配置（如果用户想在服务器上用开发模式）
if [ -f "fe/.env" ]; then
    sed -i "s|NEXT_PUBLIC_API_URL=.*|NEXT_PUBLIC_API_URL=$API_URL|g" fe/.env
    echo -e "${GREEN}✅ 已更新 fe/.env${NC}"
fi

# 检查后端 CORS 配置
echo ""
echo "4️⃣  检查后端 CORS 配置..."

if [ -f "be/.env" ]; then
    if grep -q "CORS_ORIGINS" be/.env; then
        echo "📄 当前 CORS 配置:"
        grep "CORS_ORIGINS" be/.env
        echo ""
        echo -e "${YELLOW}⚠️  请确保 CORS_ORIGINS 包含您的前端地址:${NC}"
        echo "   http://botbot.biz:3000"
        echo "   http://47.83.230.114:3000"
        echo ""
        read -p "是否需要自动更新 CORS 配置? (y/n): " update_cors

        if [ "$update_cors" = "y" ]; then
            # 更新 CORS 配置
            sed -i 's|CORS_ORIGINS=.*|CORS_ORIGINS=["http://botbot.biz:3000","http://47.83.230.114:3000","http://localhost:3000"]|g' be/.env
            echo -e "${GREEN}✅ 已更新 CORS 配置${NC}"
        fi
    else
        echo -e "${YELLOW}⚠️  be/.env 中未找到 CORS_ORIGINS 配置${NC}"
        echo "添加 CORS 配置..."
        echo 'CORS_ORIGINS=["http://botbot.biz:3000","http://47.83.230.114:3000","http://localhost:3000"]' >> be/.env
        echo -e "${GREEN}✅ 已添加 CORS 配置${NC}"
    fi
fi

echo ""
echo "5️⃣  重新部署服务..."
echo ""

# 停止服务
echo "停止现有服务..."
docker-compose down

echo ""
echo "重新构建前端（清除缓存）..."
docker-compose build --no-cache frontend

echo ""
echo "启动所有服务..."
docker-compose up -d

echo ""
echo "等待服务启动 (10秒)..."
sleep 10

echo ""
echo "6️⃣  验证部署状态..."
echo ""

# 检查容器状态
docker-compose ps

echo ""
echo "================================"
echo -e "${GREEN}✅ 修复完成！${NC}"
echo ""
echo "📋 请验证以下访问地址:"
echo "   前端: http://botbot.biz:3000"
echo "   前端: http://47.83.230.114:3000"
echo "   后端: $API_URL"
echo "   API文档: $API_URL/docs"
echo ""
echo "🔍 如果还有问题，请查看日志:"
echo "   docker-compose logs -f frontend"
echo "   docker-compose logs -f backend"
echo ""
echo "💡 提示: 在浏览器中按 F12 打开开发者工具，"
echo "   检查 Network 标签中的 API 请求地址是否正确"
echo ""
