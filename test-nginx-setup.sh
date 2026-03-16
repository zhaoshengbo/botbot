#!/bin/bash
# Test Nginx setup for BotBot
# This script validates the Nginx configuration and tests connectivity

set -e

DOMAIN="botbot.biz"
FRONTEND_URL="http://$DOMAIN"
API_URL="http://$DOMAIN/api"
DOCS_URL="http://$DOMAIN/docs"
HEALTH_URL="http://$DOMAIN/health"

echo "🦞 BotBot Nginx Setup Test"
echo "=========================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test function
test_url() {
    local url=$1
    local description=$2
    local expected_code=${3:-200}

    echo -n "Testing $description... "

    http_code=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null || echo "000")

    if [ "$http_code" = "$expected_code" ]; then
        echo -e "${GREEN}✓${NC} (HTTP $http_code)"
        return 0
    else
        echo -e "${RED}✗${NC} (HTTP $http_code, expected $expected_code)"
        return 1
    fi
}

# Check if domain resolves to localhost
echo "1. Checking DNS configuration..."
echo -n "   Domain resolution: "
if grep -q "$DOMAIN" /etc/hosts 2>/dev/null; then
    echo -e "${GREEN}✓${NC} (found in /etc/hosts)"
else
    echo -e "${RED}✗${NC} (not found in /etc/hosts)"
    echo ""
    echo -e "${YELLOW}Please run: ./setup-local-domain.sh${NC}"
    exit 1
fi
echo ""

# Check if Docker services are running
echo "2. Checking Docker services..."
if ! docker ps --format '{{.Names}}' | grep -q "botbot-nginx"; then
    echo -e "   ${RED}✗${NC} Nginx container not running"
    echo ""
    echo -e "${YELLOW}Please run: docker-compose up -d${NC}"
    exit 1
else
    echo -e "   ${GREEN}✓${NC} Nginx container running"
fi

if ! docker ps --format '{{.Names}}' | grep -q "botbot-backend"; then
    echo -e "   ${YELLOW}⚠${NC} Backend container not running"
    BACKEND_RUNNING=false
else
    echo -e "   ${GREEN}✓${NC} Backend container running"
    BACKEND_RUNNING=true
fi

if ! docker ps --format '{{.Names}}' | grep -q "botbot-frontend"; then
    echo -e "   ${YELLOW}⚠${NC} Frontend container not running"
    FRONTEND_RUNNING=false
else
    echo -e "   ${GREEN}✓${NC} Frontend container running"
    FRONTEND_RUNNING=true
fi
echo ""

# Test Nginx configuration
echo "3. Testing Nginx configuration..."
echo -n "   Nginx config syntax: "
if docker exec botbot-nginx nginx -t 2>&1 | grep -q "successful"; then
    echo -e "${GREEN}✓${NC}"
else
    echo -e "${RED}✗${NC}"
    docker exec botbot-nginx nginx -t
    exit 1
fi
echo ""

# Test endpoints
echo "4. Testing HTTP endpoints..."
TESTS_PASSED=0
TESTS_FAILED=0

# Test health endpoint
if test_url "$HEALTH_URL" "Health check" 200; then
    ((TESTS_PASSED++))
else
    ((TESTS_FAILED++))
fi

# Test frontend
if [ "$FRONTEND_RUNNING" = true ]; then
    if test_url "$FRONTEND_URL" "Frontend (root)" 200; then
        ((TESTS_PASSED++))
    else
        ((TESTS_FAILED++))
    fi
else
    echo -e "Testing Frontend (root)... ${YELLOW}⊘${NC} (container not running)"
fi

# Test backend API
if [ "$BACKEND_RUNNING" = true ]; then
    if test_url "$API_URL/health" "Backend API health" 200; then
        ((TESTS_PASSED++))
    else
        ((TESTS_FAILED++))
    fi

    if test_url "$DOCS_URL" "API documentation" 200; then
        ((TESTS_PASSED++))
    else
        ((TESTS_FAILED++))
    fi
else
    echo -e "Testing Backend API health... ${YELLOW}⊘${NC} (container not running)"
    echo -e "Testing API documentation... ${YELLOW}⊘${NC} (container not running)"
fi
echo ""

# Summary
echo "=========================="
echo "Test Summary:"
echo -e "  Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "  Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 All tests passed!${NC}"
    echo ""
    echo "You can now access BotBot at:"
    echo "  • Frontend:  $FRONTEND_URL"
    echo "  • API:       $API_URL"
    echo "  • API Docs:  $DOCS_URL"
    echo ""
    exit 0
else
    echo -e "${RED}❌ Some tests failed${NC}"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check service logs:"
    echo "     docker-compose logs -f nginx"
    echo "     docker-compose logs -f backend"
    echo "     docker-compose logs -f frontend"
    echo ""
    echo "  2. Verify all containers are running:"
    echo "     docker-compose ps"
    echo ""
    echo "  3. Restart services:"
    echo "     docker-compose restart"
    echo ""
    exit 1
fi
