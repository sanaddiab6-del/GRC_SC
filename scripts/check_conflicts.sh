#!/bin/bash
# Conflict Detection Script
# Checks if current branch will have conflicts when merged with target branch

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Default values
TARGET_BRANCH="${1:-main}"
CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
VERBOSE="${2:-false}"

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}Git Merge Conflict Detection Tool${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "Current branch: ${GREEN}${CURRENT_BRANCH}${NC}"
echo -e "Target branch:  ${GREEN}${TARGET_BRANCH}${NC}"
echo ""

# Check if target branch exists locally or remotely
if ! git rev-parse --verify "${TARGET_BRANCH}" >/dev/null 2>&1; then
    if ! git rev-parse --verify "origin/${TARGET_BRANCH}" >/dev/null 2>&1; then
        echo -e "${YELLOW}⚠️  Target branch '${TARGET_BRANCH}' not found locally or remotely${NC}"
        echo -e "${YELLOW}Available branches:${NC}"
        git branch -a | grep -v "HEAD" | sed 's/^/  /'
        echo ""
        echo -e "${BLUE}ℹ️  This is normal if you're on a feature branch${NC}"
        echo -e "${BLUE}ℹ️  No conflicts to check - your branch is independent${NC}"
        exit 0
    fi
    TARGET_REF="origin/${TARGET_BRANCH}"
else
    TARGET_REF="${TARGET_BRANCH}"
fi

# Fetch latest changes
echo -e "${YELLOW}Fetching latest changes...${NC}"
if git fetch origin "${TARGET_BRANCH}" 2>/dev/null; then
    echo -e "${GREEN}✓ Successfully fetched ${TARGET_BRANCH}${NC}"
else
    echo -e "${YELLOW}⚠️  Could not fetch from remote, using local version${NC}"
fi
echo ""

# Find common ancestor
echo -e "${YELLOW}Finding common ancestor...${NC}"
MERGE_BASE=$(git merge-base HEAD "${TARGET_REF}" 2>/dev/null)

if [ -z "$MERGE_BASE" ]; then
    echo -e "${YELLOW}⚠️  Could not find common ancestor${NC}"
    echo -e "${BLUE}ℹ️  Branches may have independent histories${NC}"
    exit 0
fi

echo -e "Common ancestor: ${GREEN}${MERGE_BASE:0:8}${NC}"
echo ""

# Perform merge tree analysis
echo -e "${YELLOW}Analyzing potential conflicts...${NC}"
MERGE_TREE_OUTPUT=$(git merge-tree "$MERGE_BASE" HEAD "${TARGET_REF}" 2>/dev/null)

# Check for conflict markers
if echo "$MERGE_TREE_OUTPUT" | grep -q "^<<<<<<<"; then
    echo -e "${RED}❌ CONFLICTS DETECTED!${NC}"
    echo ""
    
    # Extract conflicting files
    CONFLICTING_FILES=$(echo "$MERGE_TREE_OUTPUT" | grep -B 5 "^<<<<<<<" | grep "^+++ " | sed 's/^+++ b\///' | sort -u)
    
    echo -e "${RED}Conflicting files:${NC}"
    echo "$CONFLICTING_FILES" | while read -r file; do
        if [ -n "$file" ]; then
            echo -e "  ${RED}•${NC} $file"
        fi
    done
    
    echo ""
    
    if [ "$VERBOSE" = "true" ] || [ "$VERBOSE" = "-v" ]; then
        echo -e "${YELLOW}Detailed conflict preview:${NC}"
        echo -e "${YELLOW}----------------------------------------${NC}"
        echo "$MERGE_TREE_OUTPUT" | grep -A 10 "^<<<<<<<" | head -50
        echo -e "${YELLOW}----------------------------------------${NC}"
        echo ""
    fi
    
    echo -e "${YELLOW}Recommendations:${NC}"
    echo -e "  1. Review the conflicts before merging"
    echo -e "  2. Consider rebasing: ${BLUE}git rebase ${TARGET_BRANCH}${NC}"
    echo -e "  3. Coordinate with authors of conflicting changes"
    echo -e "  4. See docs/CONFLICT_RESOLUTION_GUIDE.md for help"
    echo ""
    
    # Return exit code 1 to indicate conflicts
    exit 1
else
    echo -e "${GREEN}✓ No conflicts detected!${NC}"
    echo ""
    
    # Show files that will be changed
    CHANGED_FILES=$(git diff --name-only "$MERGE_BASE" HEAD)
    NUM_CHANGES=$(echo "$CHANGED_FILES" | wc -l)
    
    if [ -n "$CHANGED_FILES" ] && [ "$CHANGED_FILES" != "" ]; then
        echo -e "${BLUE}Files changed in your branch:${NC} $NUM_CHANGES"
        
        if [ "$VERBOSE" = "true" ] || [ "$VERBOSE" = "-v" ]; then
            echo "$CHANGED_FILES" | while read -r file; do
                if [ -n "$file" ]; then
                    echo -e "  ${BLUE}•${NC} $file"
                fi
            done
        fi
    fi
    
    # Show summary statistics
    echo ""
    echo -e "${GREEN}Merge should be clean!${NC}"
    AHEAD_COUNT=$(git rev-list --count HEAD ^"${TARGET_REF}" 2>/dev/null || echo "0")
    BEHIND_COUNT=$(git rev-list --count "${TARGET_REF}" ^HEAD 2>/dev/null || echo "0")
    echo -e "  • Commits ahead: ${AHEAD_COUNT}"
    echo -e "  • Commits behind: ${BEHIND_COUNT}"
    echo ""
    
    exit 0
fi
