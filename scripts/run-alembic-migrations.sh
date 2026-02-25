#!/bin/bash
# ============================================================================
# SICO GRC Platform - Alembic Migration Runner (Linux/Mac/CI)
# Safely handles multiple heads and migration conflicts
# ============================================================================

set -e  # Exit on error

COMMAND="${1:-upgrade}"
CHECK_ONLY="${2:-false}"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
NC='\033[0m' # No Color

echo -e "${CYAN}🔄 SICO GRC - Database Migration Manager${NC}"
echo -e "${CYAN}========================================${NC}\n"

# Navigate to backend directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/../src/backend"

cd "$BACKEND_DIR"
echo -e "${YELLOW}📍 Working Directory: $BACKEND_DIR${NC}\n"

# Step 1: Check Alembic installation
echo -e "${GREEN}✓ Step 1: Verifying Alembic installation...${NC}"
if ! ALEMBIC_VERSION=$(python -m alembic --version 2>&1); then
    echo -e "${RED}❌ ERROR: Alembic is not installed!${NC}"
    echo -e "${YELLOW}   Run: pip install alembic${NC}"
    exit 1
fi
echo -e "${GRAY}   Alembic Version: $ALEMBIC_VERSION${NC}\n"

# Step 2: Check for multiple heads
echo -e "${GREEN}✓ Step 2: Checking for multiple head revisions...${NC}"

# Count heads (filter empty lines and system messages)
HEAD_COUNT=$(python -m alembic heads 2>/dev/null | grep -c -E "^[a-z0-9_]+" || echo "0")

if [ "$HEAD_COUNT" -eq 0 ]; then
    echo -e "${YELLOW}   No heads found - database may not be initialized${NC}"
    HEAD_COUNT=1  # Treat as single head to allow first migration
elif [ "$HEAD_COUNT" -gt 1 ]; then
    echo -e "${YELLOW}   ⚠️  WARNING: Multiple heads detected ($HEAD_COUNT heads)${NC}"
    echo -e "\n${YELLOW}   Current heads:${NC}"
    python -m alembic heads -v
    
    echo -e "\n${CYAN}   📖 To merge heads manually:${NC}"
    echo -e "${GRAY}      cd src/backend${NC}"
    echo -e "${GRAY}      python -m alembic merge -m 'merge heads' heads${NC}"
    echo -e "${GRAY}      python -m alembic upgrade head${NC}\n"
    
    if [ "$CHECK_ONLY" != "true" ]; then
        echo -e "${YELLOW}   Attempting automatic merge...${NC}"
        if python -m alembic merge -m "auto merge multiple heads" heads 2>&1; then
            echo -e "${GREEN}   ✓ Merge migration created successfully${NC}\n"
        else
            echo -e "${RED}   ❌ Auto-merge failed. Please merge manually.${NC}\n"
            exit 1
        fi
    else
        exit 1
    fi
else
    echo -e "${GREEN}   ✓ Single head found (healthy state)${NC}\n"
fi

if [ "$CHECK_ONLY" = "true" ]; then
    echo -e "${GREEN}✅ Migration check completed successfully${NC}\n"
    exit 0
fi

# Step 3: Show migration history
echo -e "${GREEN}✓ Step 3: Current migration status...${NC}"
python -m alembic current 2>/dev/null || echo "No current version"
echo ""

# Step 4: Run the migration
case "$COMMAND" in
    upgrade)
        echo -e "${GREEN}✓ Step 4: Running database upgrade...${NC}"
        if python -m alembic upgrade head; then
            echo -e "\n${GREEN}✅ Database migrations completed successfully!${NC}"
        else
            EXIT_CODE=$?
            echo -e "\n${RED}❌ Migration failed with exit code $EXIT_CODE${NC}"
            exit $EXIT_CODE
        fi
        ;;
    downgrade)
        echo -e "${GREEN}✓ Step 4: Running database downgrade...${NC}"
        python -m alembic downgrade -1
        ;;
    history)
        echo -e "${GREEN}✓ Step 4: Showing migration history...${NC}"
        python -m alembic history
        ;;
    *)
        echo -e "${RED}❌ Unknown command: $COMMAND${NC}"
        echo -e "${YELLOW}   Valid commands: upgrade, downgrade, history${NC}"
        exit 1
        ;;
esac

echo -e "\n${CYAN}📊 Final migration status:${NC}"
python -m alembic current -v 2>/dev/null || echo "No current version"

echo -e "\n${GREEN}✅ All operations completed successfully!${NC}\n"
