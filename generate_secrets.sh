#!/bin/bash
# 生产环境密钥生成脚本

echo "🔐 BotBot 生产环境密钥生成工具"
echo "=================================="
echo ""

# 生成 SECRET_KEY
echo "📝 生成 SECRET_KEY..."
SECRET_KEY=$(openssl rand -hex 32)
echo "SECRET_KEY=$SECRET_KEY"
echo ""

# 生成 JWT_SECRET_KEY
echo "📝 生成 JWT_SECRET_KEY..."
JWT_SECRET_KEY=$(openssl rand -hex 32)
echo "JWT_SECRET_KEY=$JWT_SECRET_KEY"
echo ""

echo "=================================="
echo "✅ 密钥生成完成！"
echo ""
echo "📋 请将以上密钥复制到 be/.env 文件中："
echo ""
echo "1. 打开文件："
echo "   nano be/.env"
echo ""
echo "2. 找到并替换："
echo "   DEBUG=False"
echo "   SECRET_KEY=<粘贴上面的 SECRET_KEY>"
echo "   JWT_SECRET_KEY=<粘贴上面的 JWT_SECRET_KEY>"
echo ""
echo "3. 保存并退出（Ctrl+X, Y, Enter）"
echo ""
echo "4. 设置文件权限："
echo "   chmod 600 be/.env"
echo ""
echo "5. 重启服务："
echo "   docker-compose restart be"
echo ""
echo "⚠️  重要提示："
echo "   - 请妥善保管这些密钥"
echo "   - 不要提交到 Git"
echo "   - 定期更换（建议每6个月）"
echo ""
