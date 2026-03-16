#!/bin/bash

# BotBot Security Test Script
# Tests basic security configurations

echo "🔒 BotBot Security Configuration Test"
echo "======================================"
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0
WARNINGS=0

# Check if .env exists
echo "1. Checking environment configuration..."
if [ ! -f "be/.env" ]; then
    echo -e "${YELLOW}⚠️  WARNING: be/.env file not found. Using .env.example${NC}"
    WARNINGS=$((WARNINGS + 1))
else
    # Check DEBUG mode
    if grep -q "DEBUG=True" be/.env; then
        echo -e "${YELLOW}⚠️  WARNING: DEBUG=True in .env (should be False in production)${NC}"
        WARNINGS=$((WARNINGS + 1))
    else
        echo -e "${GREEN}✅ DEBUG mode check passed${NC}"
        PASSED=$((PASSED + 1))
    fi

    # Check SECRET_KEY
    if grep -q "your-secret-key-change-this" be/.env; then
        echo -e "${RED}❌ CRITICAL: Using default SECRET_KEY!${NC}"
        FAILED=$((FAILED + 1))
    elif grep -E "SECRET_KEY=.{32,}" be/.env > /dev/null; then
        echo -e "${GREEN}✅ SECRET_KEY strength check passed${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}❌ CRITICAL: SECRET_KEY too short (minimum 32 characters)${NC}"
        FAILED=$((FAILED + 1))
    fi

    # Check JWT_SECRET_KEY
    if grep -q "your-jwt-secret-key-change-this" be/.env; then
        echo -e "${RED}❌ CRITICAL: Using default JWT_SECRET_KEY!${NC}"
        FAILED=$((FAILED + 1))
    elif grep -E "JWT_SECRET_KEY=.{32,}" be/.env > /dev/null; then
        echo -e "${GREEN}✅ JWT_SECRET_KEY strength check passed${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}❌ CRITICAL: JWT_SECRET_KEY too short${NC}"
        FAILED=$((FAILED + 1))
    fi

    # Check CORS
    if grep -q "CORS_ORIGINS=\*" be/.env; then
        echo -e "${YELLOW}⚠️  WARNING: CORS allows all origins (*)${NC}"
        WARNINGS=$((WARNINGS + 1))
    else
        echo -e "${GREEN}✅ CORS configuration check passed${NC}"
        PASSED=$((PASSED + 1))
    fi
fi

echo ""
echo "2. Checking security files..."

# Check if security files exist
if [ -f "SECURITY.md" ]; then
    echo -e "${GREEN}✅ SECURITY.md exists${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌ SECURITY.md missing${NC}"
    FAILED=$((FAILED + 1))
fi

if [ -f "SECURITY_AUDIT_REPORT.md" ]; then
    echo -e "${GREEN}✅ SECURITY_AUDIT_REPORT.md exists${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌ SECURITY_AUDIT_REPORT.md missing${NC}"
    FAILED=$((FAILED + 1))
fi

if [ -f "be/app/core/security_checks.py" ]; then
    echo -e "${GREEN}✅ Security checks module exists${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌ security_checks.py missing${NC}"
    FAILED=$((FAILED + 1))
fi

echo ""
echo "3. Checking code for security issues..."

# Check for direct login endpoint (should be disabled)
if grep -q "def direct_login_or_register" be/app/api/routes/auth.py; then
    if grep -q "# SECURITY: Direct login endpoint disabled" be/app/api/routes/auth.py; then
        echo -e "${GREEN}✅ Direct login endpoint properly disabled${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "${RED}❌ Direct login endpoint exists and not disabled${NC}"
        FAILED=$((FAILED + 1))
    fi
fi

# Check for rate limiting implementation
if grep -q "verification_failed_attempts" be/app/services/auth_service.py; then
    echo -e "${GREEN}✅ Rate limiting implemented${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌ Rate limiting not found${NC}"
    FAILED=$((FAILED + 1))
fi

# Check for phone validation
if grep -q "validate_phone_number" be/app/schemas/auth.py; then
    echo -e "${GREEN}✅ Phone number validation implemented${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌ Phone number validation missing${NC}"
    FAILED=$((FAILED + 1))
fi

# Check for security headers
if grep -q "add_security_headers" be/app/main.py; then
    echo -e "${GREEN}✅ Security headers middleware implemented${NC}"
    PASSED=$((PASSED + 1))
else
    echo -e "${RED}❌ Security headers middleware missing${NC}"
    FAILED=$((FAILED + 1))
fi

echo ""
echo "4. Checking sensitive files..."

# Check .gitignore
if [ -f ".gitignore" ]; then
    if grep -q "*.pem" .gitignore && grep -q ".env" .gitignore; then
        echo -e "${GREEN}✅ .gitignore properly configured${NC}"
        PASSED=$((PASSED + 1))
    else
        echo -e "${YELLOW}⚠️  WARNING: .gitignore may not exclude sensitive files${NC}"
        WARNINGS=$((WARNINGS + 1))
    fi
else
    echo -e "${RED}❌ .gitignore missing${NC}"
    FAILED=$((FAILED + 1))
fi

# Check for accidentally committed secrets
if git rev-parse --git-dir > /dev/null 2>&1; then
    if git log --all --full-history --source -- "*private*key*" "*.pem" | grep -q "commit"; then
        echo -e "${RED}❌ WARNING: Private keys may be in git history!${NC}"
        FAILED=$((FAILED + 1))
    else
        echo -e "${GREEN}✅ No private keys found in git history${NC}"
        PASSED=$((PASSED + 1))
    fi
fi

echo ""
echo "======================================"
echo "Security Test Results:"
echo "======================================"
echo -e "${GREEN}✅ Passed: $PASSED${NC}"
echo -e "${RED}❌ Failed: $FAILED${NC}"
echo -e "${YELLOW}⚠️  Warnings: $WARNINGS${NC}"
echo ""

if [ $FAILED -gt 0 ]; then
    echo -e "${RED}❌ SECURITY TEST FAILED${NC}"
    echo "Please fix the issues above before deploying to production."
    echo "See SECURITY.md for detailed guidelines."
    exit 1
elif [ $WARNINGS -gt 0 ]; then
    echo -e "${YELLOW}⚠️  SECURITY TEST PASSED WITH WARNINGS${NC}"
    echo "Review the warnings above and fix them for production."
    exit 0
else
    echo -e "${GREEN}✅ SECURITY TEST PASSED${NC}"
    echo "All security checks passed!"
    exit 0
fi
