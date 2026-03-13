#!/bin/bash

# BotBot 重新部署脚本
# 用于代码变更后快速重新部署

echo "🚀 BotBot 重新部署脚本"
echo "========================================"
echo ""

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;36m'
NC='\033[0m'

# 检查是否在项目目录
if [ ! -f "docker-compose.yml" ]; then
    echo -e "${RED}❌ 错误: 请在 botbot 项目根目录运行此脚本${NC}"
    exit 1
fi

# 检查 git 状态
echo "1️⃣  检查 Git 状态..."
git fetch origin main

# 比较本地和远程的差异
LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})
BASE=$(git merge-base @ @{u})

if [ $LOCAL = $REMOTE ]; then
    echo -e "${GREEN}✅ 已是最新版本${NC}"
    read -p "是否强制重新部署? (y/n): " force_deploy
    if [ "$force_deploy" != "y" ]; then
        echo "取消部署"
        exit 0
    fi
elif [ $LOCAL = $BASE ]; then
    echo -e "${YELLOW}⚠️  检测到远程有更新${NC}"
else
    echo -e "${RED}❌ 本地有未推送的提交${NC}"
    read -p "是否放弃本地更改并拉取最新代码? (y/n): " reset_local
    if [ "$reset_local" = "y" ]; then
        git reset --hard origin/main
    else
        echo "请先处理本地更改"
        exit 1
    fi
fi

echo ""
echo "2️⃣  拉取最新代码..."
git pull origin main

if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Git pull 失败${NC}"
    exit 1
fi

echo -e "${GREEN}✅ 代码已更新到最新版本${NC}"
LATEST_COMMIT=$(git log --oneline -1)
echo "   最新提交: $LATEST_COMMIT"
echo ""

# 检查哪些部分有变更
echo "3️⃣  分析代码变更..."
FRONTEND_CHANGED=false
BACKEND_CHANGED=false
CONFIG_CHANGED=false

# 检查最近的变更
CHANGED_FILES=$(git diff --name-only HEAD~1 HEAD 2>/dev/null || git diff --name-only HEAD)

if echo "$CHANGED_FILES" | grep -q "^fe/"; then
    FRONTEND_CHANGED=true
    echo -e "${BLUE}📦 检测到前端代码变更${NC}"
fi

if echo "$CHANGED_FILES" | grep -q "^be/"; then
    BACKEND_CHANGED=true
    echo -e "${BLUE}🔧 检测到后端代码变更${NC}"
fi

if echo "$CHANGED_FILES" | grep -q "docker-compose\|\.env"; then
    CONFIG_CHANGED=true
    echo -e "${BLUE}⚙️  检测到配置文件变更${NC}"
fi

# 如果没有检测到变更，询问用户要部署什么
if [ "$FRONTEND_CHANGED" = false ] && [ "$BACKEND_CHANGED" = false ]; then
    echo ""
    echo -e "${YELLOW}⚠️  未检测到代码变更，请选择要重新部署的服务:${NC}"
    echo "   1) 仅前端"
    echo "   2) 仅后端"
    echo "   3) 前端和后端"
    echo "   4) 取消"
    read -p "请选择 (1/2/3/4): " deploy_choice

    case $deploy_choice in
        1)
            FRONTEND_CHANGED=true
            ;;
        2)
            BACKEND_CHANGED=true
            ;;
        3)
            FRONTEND_CHANGED=true
            BACKEND_CHANGED=true
            ;;
        4)
            echo "取消部署"
            exit 0
            ;;
        *)
            echo -e "${RED}❌ 无效选项${NC}"
            exit 1
            ;;
    esac
fi

echo ""
echo "4️⃣  准备重新部署..."

# 确认 API URL 配置
if [ "$FRONTEND_CHANGED" = true ]; then
    if [ -f ".env.production" ]; then
        API_URL=$(grep NEXT_PUBLIC_API_URL .env.production | cut -d'=' -f2)
        echo "   前端 API URL: $API_URL"
    else
        echo -e "${YELLOW}⚠️  .env.production 不存在${NC}"
        read -p "请输入后端 API URL (默认: http://47.83.230.114:8000): " API_URL
        API_URL=${API_URL:-http://47.83.230.114:8000}
        cat > .env.production << EOF
NEXT_PUBLIC_API_URL=$API_URL
EOF
    fi
fi

echo ""
read -p "确认开始部署? (y/n): " confirm
if [ "$confirm" != "y" ]; then
    echo "取消部署"
    exit 0
fi

# 开始部署
echo ""
echo "5️⃣  停止相关服务..."

if [ "$FRONTEND_CHANGED" = true ] && [ "$BACKEND_CHANGED" = true ]; then
    docker-compose stop frontend backend
elif [ "$FRONTEND_CHANGED" = true ]; then
    docker-compose stop frontend
elif [ "$BACKEND_CHANGED" = true ]; then
    docker-compose stop backend
fi

echo ""
echo "6️⃣  重新构建服务..."

# 重新构建前端
if [ "$FRONTEND_CHANGED" = true ]; then
    echo -e "${BLUE}🔨 重新构建前端...${NC}"

    # 清除前端缓存
    rm -rf fe/.next 2>/dev/null

    # 构建前端
    export NEXT_PUBLIC_API_URL=${API_URL:-http://47.83.230.114:8000}
    docker-compose build --no-cache \
      --build-arg NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL \
      frontend

    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ 前端构建失败！${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ 前端构建成功${NC}"
fi

# 重新构建后端
if [ "$BACKEND_CHANGED" = true ]; then
    echo -e "${BLUE}🔨 重新构建后端...${NC}"
    docker-compose build backend

    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ 后端构建失败！${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ 后端构建成功${NC}"
fi

echo ""
echo "7️⃣  启动服务..."

if [ -f ".env.production" ]; then
    docker-compose --env-file .env.production up -d
else
    docker-compose up -d
fi

echo ""
echo "8️⃣  等待服务启动 (15秒)..."
sleep 15

echo ""
echo "9️⃣  检查服务状态..."
echo ""
docker-compose ps

echo ""
echo "🔟  验证部署..."
echo ""

# 检查前端
if [ "$FRONTEND_CHANGED" = true ]; then
    echo "📦 前端状态:"
    FRONTEND_STATUS=$(docker-compose ps frontend | grep "Up" | wc -l)
    if [ $FRONTEND_STATUS -eq 1 ]; then
        echo -e "   ${GREEN}✅ 前端容器运行中${NC}"

        # 检查日志
        FRONTEND_READY=$(docker-compose logs frontend 2>&1 | grep -i "ready\|started server" | tail -1)
        if [ -n "$FRONTEND_READY" ]; then
            echo -e "   ${GREEN}✅ 前端已启动${NC}"
            echo "      $FRONTEND_READY"
        else
            echo -e "   ${YELLOW}⚠️  前端启动中...${NC}"
        fi
    else
        echo -e "   ${RED}❌ 前端容器未运行${NC}"
    fi
    echo ""
fi

# 检查后端
if [ "$BACKEND_CHANGED" = true ]; then
    echo "🔧 后端状态:"
    BACKEND_STATUS=$(docker-compose ps backend | grep "Up" | wc -l)
    if [ $BACKEND_STATUS -eq 1 ]; then
        echo -e "   ${GREEN}✅ 后端容器运行中${NC}"

        # 检查日志
        BACKEND_READY=$(docker-compose logs backend 2>&1 | grep "Application startup complete" | tail -1)
        if [ -n "$BACKEND_READY" ]; then
            echo -e "   ${GREEN}✅ 后端已启动${NC}"
        else
            echo -e "   ${YELLOW}⚠️  后端启动中...${NC}"
        fi
    else
        echo -e "   ${RED}❌ 后端容器未运行${NC}"
    fi
    echo ""
fi

# 显示最近的错误日志
echo "📋 最近的日志（如有错误）:"
if [ "$FRONTEND_CHANGED" = true ]; then
    FRONTEND_ERRORS=$(docker-compose logs frontend 2>&1 | grep -i "error" | tail -3)
    if [ -n "$FRONTEND_ERRORS" ]; then
        echo -e "${YELLOW}前端错误:${NC}"
        echo "$FRONTEND_ERRORS"
    fi
fi

if [ "$BACKEND_CHANGED" = true ]; then
    BACKEND_ERRORS=$(docker-compose logs backend 2>&1 | grep -i "error\|traceback" | tail -3)
    if [ -n "$BACKEND_ERRORS" ]; then
        echo -e "${YELLOW}后端错误:${NC}"
        echo "$BACKEND_ERRORS"
    fi
fi

echo ""
echo "========================================"
echo -e "${GREEN}✅ 重新部署完成！${NC}"
echo ""
echo "🌐 访问地址:"
echo "   前端: http://47.83.230.114:3000"
echo "   后端: http://47.83.230.114:8000/docs"
echo ""
echo "📊 查看日志:"
echo "   所有服务: docker-compose logs -f"
echo "   仅前端: docker-compose logs -f frontend"
echo "   仅后端: docker-compose logs -f backend"
echo ""
echo "🔍 运行完整检查:"
echo "   ./check-deployment.sh"
echo ""
