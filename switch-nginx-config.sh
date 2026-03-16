#!/bin/bash
# Switch between development and production Nginx configurations
# Usage: ./switch-nginx-config.sh [dev|prod]

set -e

CONF_DIR="nginx/conf.d"
DEV_CONF="botbot.conf"
PROD_CONF="botbot.prod.conf"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "🔧 Nginx Configuration Switcher"
echo "================================"
echo ""

# Check if running from project root
if [ ! -d "$CONF_DIR" ]; then
    echo -e "${RED}Error: Must run from project root directory${NC}"
    echo "Current directory: $(pwd)"
    exit 1
fi

# Function to switch to dev config
switch_to_dev() {
    echo "Switching to DEVELOPMENT configuration..."
    echo ""

    cd "$CONF_DIR"

    # Disable production config if active
    if [ -f "$PROD_CONF" ]; then
        echo "  • Disabling $PROD_CONF"
        mv "$PROD_CONF" "$PROD_CONF.disabled"
    fi

    # Enable dev config
    if [ -f "$DEV_CONF.disabled" ]; then
        echo "  • Enabling $DEV_CONF"
        mv "$DEV_CONF.disabled" "$DEV_CONF"
    elif [ -f "$DEV_CONF" ]; then
        echo "  • $DEV_CONF already active"
    else
        echo -e "${RED}Error: $DEV_CONF not found${NC}"
        cd - > /dev/null
        exit 1
    fi

    cd - > /dev/null

    echo ""
    echo -e "${GREEN}✓ Switched to development configuration${NC}"
    echo ""
    echo "Active config: $DEV_CONF"
    echo "Features:"
    echo "  • HTTP and HTTPS both supported"
    echo "  • No forced HTTPS redirect"
    echo "  • Suitable for local development"
    echo ""
    echo "Next steps:"
    echo "  docker-compose restart nginx"
}

# Function to switch to prod config
switch_to_prod() {
    echo "Switching to PRODUCTION configuration..."
    echo ""

    cd "$CONF_DIR"

    # Disable dev config if active
    if [ -f "$DEV_CONF" ]; then
        echo "  • Disabling $DEV_CONF"
        mv "$DEV_CONF" "$DEV_CONF.disabled"
    fi

    # Enable production config
    if [ -f "$PROD_CONF.disabled" ]; then
        echo "  • Enabling $PROD_CONF"
        mv "$PROD_CONF.disabled" "$PROD_CONF"
    elif [ -f "$PROD_CONF" ]; then
        echo "  • $PROD_CONF already active"
    else
        echo -e "${RED}Error: $PROD_CONF not found${NC}"
        cd - > /dev/null
        exit 1
    fi

    cd - > /dev/null

    echo ""
    echo -e "${GREEN}✓ Switched to production configuration${NC}"
    echo ""
    echo "Active config: $PROD_CONF"
    echo "Features:"
    echo "  • HTTPS enforced (HTTP → HTTPS redirect)"
    echo "  • Enhanced security headers (HSTS, CSP)"
    echo "  • Aggressive static asset caching (1 year)"
    echo "  • Rate limiting support"
    echo ""
    echo -e "${YELLOW}⚠️  Important:${NC}"
    echo "  1. Ensure SSL certificates are installed in nginx/certs/"
    echo "  2. Use production docker-compose file:"
    echo "     docker-compose -f docker-compose.prod.yml restart nginx"
}

# Function to show current status
show_status() {
    echo "Current Nginx configuration status:"
    echo ""

    cd "$CONF_DIR"

    if [ -f "$DEV_CONF" ]; then
        echo -e "  ${GREEN}●${NC} $DEV_CONF (ACTIVE - Development)"
    elif [ -f "$DEV_CONF.disabled" ]; then
        echo -e "  ${YELLOW}○${NC} $DEV_CONF.disabled (Disabled)"
    else
        echo -e "  ${RED}✗${NC} $DEV_CONF (MISSING)"
    fi

    if [ -f "$PROD_CONF" ]; then
        echo -e "  ${GREEN}●${NC} $PROD_CONF (ACTIVE - Production)"
    elif [ -f "$PROD_CONF.disabled" ]; then
        echo -e "  ${YELLOW}○${NC} $PROD_CONF.disabled (Disabled)"
    else
        echo -e "  ${RED}✗${NC} $PROD_CONF (MISSING)"
    fi

    cd - > /dev/null
    echo ""

    # Check if multiple configs are active
    active_count=0
    [ -f "$CONF_DIR/$DEV_CONF" ] && ((active_count++))
    [ -f "$CONF_DIR/$PROD_CONF" ] && ((active_count++))

    if [ $active_count -gt 1 ]; then
        echo -e "${RED}⚠️  WARNING: Multiple configurations are active!${NC}"
        echo "This will cause Nginx to fail with 'duplicate upstream' error."
        echo "Please switch to only one configuration."
        echo ""
    elif [ $active_count -eq 0 ]; then
        echo -e "${YELLOW}⚠️  WARNING: No configuration is active!${NC}"
        echo "Nginx will not have BotBot configuration."
        echo ""
    fi
}

# Main logic
case "$1" in
    dev|development)
        switch_to_dev
        ;;
    prod|production)
        switch_to_prod
        ;;
    status|"")
        show_status
        echo "Usage: $0 [dev|prod|status]"
        echo ""
        echo "Commands:"
        echo "  dev, development  - Switch to development configuration"
        echo "  prod, production  - Switch to production configuration"
        echo "  status           - Show current configuration status"
        ;;
    *)
        echo -e "${RED}Error: Unknown command '$1'${NC}"
        echo ""
        echo "Usage: $0 [dev|prod|status]"
        echo ""
        echo "Commands:"
        echo "  dev, development  - Switch to development configuration"
        echo "  prod, production  - Switch to production configuration"
        echo "  status           - Show current configuration status"
        exit 1
        ;;
esac
