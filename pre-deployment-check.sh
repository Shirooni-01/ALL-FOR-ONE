#!/bin/bash

# Pre-deployment checklist script for ONE FOR ALL
# Run this before deploying to production

set -e

echo "========================================="
echo "ONE FOR ALL - Pre-Deployment Checklist"
echo "========================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASS=0
FAIL=0
WARN=0

check_pass() {
    echo -e "${GREEN}✓${NC} $1"
    ((PASS++))
}

check_fail() {
    echo -e "${RED}✗${NC} $1"
    ((FAIL++))
}

check_warn() {
    echo -e "${YELLOW}⚠${NC} $1"
    ((WARN++))
}

# 1. Check if .env file exists
echo "1. Checking configuration files..."
if [ -f ".env" ]; then
    check_pass ".env file exists"
else
    check_fail ".env file not found"
fi

# 2. Check SECRET_KEY
if grep -q "SECRET_KEY=" .env 2>/dev/null; then
    SECRET_KEY=$(grep "SECRET_KEY=" .env | cut -d= -f2 | tr -d ' ' | tr -d "'")
    if [ ${#SECRET_KEY} -gt 20 ]; then
        check_pass "SECRET_KEY is strong (${#SECRET_KEY} characters)"
    else
        check_warn "SECRET_KEY might be too short (${#SECRET_KEY} characters, recommend 32+)"
    fi
else
    check_fail "SECRET_KEY not configured"
fi

# 3. Check required environment variables
echo ""
echo "2. Checking required environment variables..."
for var in GOOGLE_API_KEY GOOGLE_AI_API_KEY; do
    if grep -q "$var=" .env 2>/dev/null; then
        check_pass "$var is configured"
    else
        check_warn "$var is not configured (may be optional)"
    fi
done

# 4. Check database
echo ""
echo "3. Checking database..."
if [ -f "users.db" ]; then
    DB_SIZE=$(du -h users.db | cut -f1)
    check_pass "Database exists (size: $DB_SIZE)"
else
    check_warn "Database not found (will be created on first run)"
fi

# 5. Check dependencies
echo ""
echo "4. Checking Python dependencies..."
if command -v python3 &> /dev/null; then
    check_pass "Python 3 is installed"
    if python3 -c "import flask" 2>/dev/null; then
        check_pass "Required packages are installed"
    else
        check_fail "Required packages are not installed (run: pip install -r requirements.txt)"
    fi
else
    check_fail "Python 3 is not installed"
fi

# 6. Check static files
echo ""
echo "5. Checking static files..."
if [ -d "static" ]; then
    check_pass "Static directory exists"
    if [ -f "static/style.css" ]; then
        check_pass "CSS files found"
    else
        check_warn "Some CSS files might be missing"
    fi
else
    check_fail "Static directory not found"
fi

# 7. Check templates
echo ""
echo "6. Checking templates..."
if [ -d "templates" ]; then
    TEMPLATE_COUNT=$(find templates -name "*.html" | wc -l)
    check_pass "Templates directory exists ($TEMPLATE_COUNT HTML files)"
else
    check_fail "Templates directory not found"
fi

# 8. Check if running on production or development
echo ""
echo "7. Checking deployment configuration..."
if grep -q "FLASK_ENV=production" .env 2>/dev/null; then
    check_pass "FLASK_ENV is set to production"
else
    check_warn "FLASK_ENV is not set to production (for development only)"
fi

# 9. Check if app.py has debug=False
echo ""
echo "8. Checking application configuration..."
if grep -q "debug=debug" app.py; then
    check_pass "Debug mode uses environment variable"
else
    check_warn "Debug mode configuration might need review"
fi

# 10. Check gunicorn is installed
echo ""
echo "9. Checking production server..."
if command -v gunicorn &> /dev/null; then
    GUNICORN_VERSION=$(gunicorn --version 2>&1 | head -1)
    check_pass "Gunicorn is installed ($GUNICORN_VERSION)"
else
    check_warn "Gunicorn not installed (run: pip install gunicorn)"
fi

# 11. Check logs directory
echo ""
echo "10. Checking logs configuration..."
if [ -d "logs" ]; then
    check_pass "Logs directory exists"
else
    check_warn "Logs directory not found (will be created at runtime)"
fi

# 12. Check git
echo ""
echo "11. Checking version control..."
if [ -d ".git" ]; then
    check_pass "Git repository initialized"
    if git status > /dev/null 2>&1; then
        if git diff-index --quiet HEAD -- 2>/dev/null; then
            check_pass "All changes committed"
        else
            check_warn "There are uncommitted changes"
        fi
    fi
else
    check_warn "Not a git repository"
fi

# 12. Check .gitignore
echo ""
echo "12. Checking security (.gitignore)..."
if grep -q "^\.env$" .gitignore 2>/dev/null; then
    check_pass ".env is in .gitignore"
else
    check_fail ".env is not in .gitignore (security risk!)"
fi

if grep -q "^__pycache__" .gitignore 2>/dev/null; then
    check_pass "__pycache__ is in .gitignore"
else
    check_warn "__pycache__ is not in .gitignore"
fi

# Summary
echo ""
echo "========================================="
echo "Summary:"
echo -e "  ${GREEN}Passed: $PASS${NC}"
echo -e "  ${YELLOW}Warnings: $WARN${NC}"
echo -e "  ${RED}Failed: $FAIL${NC}"
echo "========================================="

if [ $FAIL -gt 0 ]; then
    echo -e "${RED}DEPLOYMENT NOT RECOMMENDED${NC} - Please fix the failures above"
    exit 1
elif [ $WARN -gt 0 ]; then
    echo -e "${YELLOW}READY WITH WARNINGS${NC} - Please review the warnings above"
    exit 0
else
    echo -e "${GREEN}READY FOR DEPLOYMENT${NC}"
    exit 0
fi
