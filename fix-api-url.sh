#!/bin/bash

# 快速修复前端 API URL 配置问题
# 解决: net::ERR_CONNECTION_REFUSED 错误

echo "🔧 修复前端 API URL 配置"
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

echo "当前问题: 前端访问 http://localhost:8000 导致连接被拒绝"
echo "解决方案: 配置正确的生产服务器 API 地址"
echo ""

# 询问 API 地址
echo "请选择后端 API 地址:"
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
        read -p "请输入后端 API 地址: " API_URL
        ;;
    *)
        echo -e "${RED}❌ 无效选项${NC}"
        exit 1
        ;;
esac

echo ""
echo -e "${GREEN}✅ 将使用 API 地址: $API_URL${NC}"
echo ""

# 创建 .env.production
cat > .env.production << EOF
# Production Environment Variables
NEXT_PUBLIC_API_URL=$API_URL
EOF

echo "✅ 已创建 .env.production"

# 更新 fe/.env.production
cat > fe/.env.production << EOF
# Production Environment Variables for BotBot Frontend
NEXT_PUBLIC_API_URL=$API_URL
NEXT_PUBLIC_APP_NAME=BotBot
EOF

echo "✅ 已更新 fe/.env.production"
echo ""

# 停止服务
echo "⏸️  停止当前服务..."
docker-compose down

# 清除前端缓存
echo "🗑️  清除前端构建缓存..."
rm -rf fe/.next
rm -rf fe/node_modules/.cache

# 重新构建前端
echo ""
echo "🔨 重新构建前端 (传入正确的 API URL)..."
echo "   这可能需要 2-3 分钟..."
export NEXT_PUBLIC_API_URL=$API_URL
docker-compose build --no-cache --build-arg NEXT_PUBLIC_API_URL=$API_URL frontend

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 构建失败！${NC}"
    exit 1
fi

# 启动服务
echo ""
echo "🚀 启动所有服务..."
docker-compose --env-file .env.production up -d

# 等待启动
echo ""
echo "⏳ 等待服务启动 (15秒)..."
sleep 15

# 检查状态
echo ""
echo "📊 服务状态:"
docker-compose ps

echo ""
echo "📋 前端日志 (最近20行):"
docker-compose logs --tail=20 frontend

echo ""
echo "========================================"
echo -e "${GREEN}✅ 修复完成！${NC}"
echo ""
echo "🌐 API URL 已设置为: $API_URL"
echo ""
echo "🎯 下一步:"
echo "   1. 打开浏览器访问你的前端"
echo "   2. 清除浏览器缓存 (Ctrl+Shift+Del)"
echo "   3. 硬刷新页面 (Ctrl+F5)"
echo "   4. 打开开发者工具 (F12)"
echo "   5. 查看 Network 标签，确认 API 请求地址正确"
echo ""
echo "✅ 现在前端应该能正确访问后端 API 了！"
echo ""
