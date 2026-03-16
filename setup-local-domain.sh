#!/bin/bash
# Setup local domain for BotBot development
# This script configures the local hosts file to point botbot.biz to localhost

set -e

DOMAIN="botbot.biz"
WWW_DOMAIN="www.botbot.biz"
HOSTS_FILE="/etc/hosts"
IP="127.0.0.1"

echo "🦞 BotBot Local Domain Setup"
echo "=============================="
echo ""

# Check if running with sudo
if [ "$EUID" -ne 0 ]; then
    echo "⚠️  This script needs sudo privileges to modify /etc/hosts"
    echo "Relaunching with sudo..."
    sudo "$0" "$@"
    exit $?
fi

# Backup hosts file
BACKUP_FILE="/etc/hosts.backup.$(date +%Y%m%d_%H%M%S)"
echo "📦 Creating backup: $BACKUP_FILE"
cp "$HOSTS_FILE" "$BACKUP_FILE"

# Check if domain already exists
if grep -q "$DOMAIN" "$HOSTS_FILE"; then
    echo "⚠️  Domain $DOMAIN already exists in hosts file"
    echo "Current entries:"
    grep "$DOMAIN" "$HOSTS_FILE"
    echo ""
    read -p "Do you want to remove old entries and add new ones? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "🧹 Removing old entries..."
        sed -i.bak "/$DOMAIN/d" "$HOSTS_FILE"
    else
        echo "❌ Cancelled. No changes made."
        exit 0
    fi
fi

# Add domain entries
echo "✏️  Adding domain entries to $HOSTS_FILE..."
echo "" >> "$HOSTS_FILE"
echo "# BotBot local development domain" >> "$HOSTS_FILE"
echo "$IP $DOMAIN" >> "$HOSTS_FILE"
echo "$IP $WWW_DOMAIN" >> "$HOSTS_FILE"

echo "✅ Domain entries added successfully!"
echo ""
echo "Added:"
echo "  $IP $DOMAIN"
echo "  $IP $WWW_DOMAIN"
echo ""

# Flush DNS cache based on OS
echo "🔄 Flushing DNS cache..."
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    dscacheutil -flushcache
    killall -HUP mDNSResponder 2>/dev/null || true
    echo "✅ DNS cache flushed (macOS)"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    if command -v systemd-resolve &> /dev/null; then
        systemd-resolve --flush-caches
        echo "✅ DNS cache flushed (Linux systemd)"
    else
        echo "ℹ️  DNS cache flush not needed (Linux)"
    fi
else
    echo "⚠️  Unknown OS. Please flush DNS cache manually if needed."
fi

echo ""
echo "🎉 Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Start Docker services:"
echo "     docker-compose up -d"
echo ""
echo "  2. Access the application:"
echo "     Frontend:  http://botbot.biz"
echo "     Backend:   http://botbot.biz/api"
echo "     API Docs:  http://botbot.biz/docs"
echo ""
echo "  3. Test the connection:"
echo "     curl http://botbot.biz/health"
echo ""
echo "Backup created at: $BACKUP_FILE"
