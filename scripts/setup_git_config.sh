#!/bin/bash
# Git Configuration Setup for Merge Best Practices
# This script configures git settings for optimal merge conflict handling

set -e

echo "================================================"
echo "Git Configuration Setup for SICO GRC Platform"
echo "================================================"
echo ""

# Function to set git config with confirmation
set_config() {
    local scope=$1
    local key=$2
    local value=$3
    local description=$4
    
    echo "Setting: $description"
    echo "  Config: $key = $value"
    
    if [ "$scope" = "local" ]; then
        git config "$key" "$value"
        echo "  ✓ Applied locally"
    else
        git config --global "$key" "$value"
        echo "  ✓ Applied globally"
    fi
    echo ""
}

# Ask for scope
echo "Where should these configurations be applied?"
echo "  1) Local (this repository only) - Recommended"
echo "  2) Global (all repositories)"
read -p "Enter choice [1]: " SCOPE_CHOICE
SCOPE_CHOICE=${SCOPE_CHOICE:-1}

if [ "$SCOPE_CHOICE" = "2" ]; then
    SCOPE="global"
    echo "Applying configurations globally..."
else
    SCOPE="local"
    echo "Applying configurations locally..."
fi
echo ""

# ============================================
# Core Merge Settings
# ============================================
echo "=== Core Merge Settings ==="
echo ""

set_config "$SCOPE" "merge.conflictstyle" "diff3" \
    "Show common ancestor in conflict markers (better context)"

set_config "$SCOPE" "pull.rebase" "false" \
    "Use merge strategy for pulls (not rebase)"

set_config "$SCOPE" "merge.ff" "false" \
    "Always create merge commit (preserves history)"

# ============================================
# Conflict Resolution Tools
# ============================================
echo "=== Conflict Resolution Tools ==="
echo ""

set_config "$SCOPE" "rerere.enabled" "true" \
    "Remember how conflicts were resolved (reuse later)"

set_config "$SCOPE" "rerere.autoupdate" "true" \
    "Automatically stage files after rerere resolution"

# ============================================
# Diff & Merge Algorithms
# ============================================
echo "=== Diff & Merge Algorithms ==="
echo ""

set_config "$SCOPE" "diff.algorithm" "histogram" \
    "Better diff algorithm for complex changes"

set_config "$SCOPE" "diff.colorMoved" "default" \
    "Highlight moved code blocks"

set_config "$SCOPE" "merge.conflictMarkerSize" "7" \
    "Show longer conflict markers for clarity"

# ============================================
# Language-specific Diff Drivers
# ============================================
echo "=== Language-specific Diff Drivers ==="
echo ""

# Python
set_config "$SCOPE" "diff.python.xfuncname" "^[ \t]*((class|def)[ \t].*)$" \
    "Better function context for Python diffs"

# JavaScript/TypeScript
set_config "$SCOPE" "diff.javascript.xfuncname" "^[ \t]*(((async[ \t]+)?function|class|const|let|var)[ \t].*)$" \
    "Better function context for JavaScript diffs"

# ============================================
# Merge Tool Configuration (Optional)
# ============================================
echo "=== Merge Tool Configuration ==="
echo ""

read -p "Do you want to configure a merge tool? [y/N]: " SETUP_MERGETOOL
if [[ "$SETUP_MERGETOOL" =~ ^[Yy]$ ]]; then
    echo ""
    echo "Available merge tools:"
    echo "  1) VSCode (code)"
    echo "  2) vim (vimdiff)"
    echo "  3) Meld"
    echo "  4) KDiff3"
    echo "  5) Skip"
    read -p "Enter choice [1]: " TOOL_CHOICE
    TOOL_CHOICE=${TOOL_CHOICE:-1}
    
    case $TOOL_CHOICE in
        1)
            set_config "$SCOPE" "merge.tool" "vscode" "Use VSCode as merge tool"
            set_config "$SCOPE" "mergetool.vscode.cmd" "code --wait --merge \$REMOTE \$LOCAL \$BASE \$MERGED" "VSCode merge command"
            ;;
        2)
            set_config "$SCOPE" "merge.tool" "vimdiff" "Use vim as merge tool"
            ;;
        3)
            set_config "$SCOPE" "merge.tool" "meld" "Use Meld as merge tool"
            ;;
        4)
            set_config "$SCOPE" "merge.tool" "kdiff3" "Use KDiff3 as merge tool"
            ;;
        *)
            echo "Skipping merge tool configuration"
            echo ""
            ;;
    esac
    
    if [ "$TOOL_CHOICE" != "5" ]; then
        set_config "$SCOPE" "mergetool.prompt" "false" "Don't prompt before launching merge tool"
        set_config "$SCOPE" "mergetool.keepBackup" "false" "Don't keep .orig backup files"
    fi
fi

# ============================================
# User Information (if not set)
# ============================================
echo "=== User Information ==="
echo ""

CURRENT_NAME=$(git config user.name 2>/dev/null || echo "")
CURRENT_EMAIL=$(git config user.email 2>/dev/null || echo "")

if [ -z "$CURRENT_NAME" ] || [ -z "$CURRENT_EMAIL" ]; then
    echo "User information not configured."
    read -p "Enter your name: " USER_NAME
    read -p "Enter your email: " USER_EMAIL
    
    set_config "$SCOPE" "user.name" "$USER_NAME" "User name for commits"
    set_config "$SCOPE" "user.email" "$USER_EMAIL" "User email for commits"
else
    echo "User information already configured:"
    echo "  Name:  $CURRENT_NAME"
    echo "  Email: $CURRENT_EMAIL"
    echo ""
fi

# ============================================
# Summary
# ============================================
echo "================================================"
echo "Configuration Complete!"
echo "================================================"
echo ""
echo "Applied configurations:"
if [ "$SCOPE" = "local" ]; then
    git config --list --local | grep -E "(merge|diff|rerere|pull)" || echo "  (configurations applied)"
else
    git config --list --global | grep -E "(merge|diff|rerere|pull)" || echo "  (configurations applied)"
fi
echo ""
echo "Additional recommendations:"
echo "  • Review .gitattributes for file-specific merge strategies"
echo "  • See docs/CONFLICT_RESOLUTION_GUIDE.md for detailed help"
echo "  • Use scripts/check_conflicts.sh before merging"
echo ""
echo "Test your configuration:"
echo "  git config --list | grep merge"
echo ""
