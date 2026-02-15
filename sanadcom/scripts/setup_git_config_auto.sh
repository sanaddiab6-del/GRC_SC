#!/bin/bash
# Automated Git Configuration Setup (Non-interactive)
# Configures git settings for optimal merge conflict handling
# Suitable for CI/CD and automated environments

set -e

echo "================================================"
echo "Git Configuration Setup (Automated)"
echo "================================================"
echo ""

# Apply to local repository only
SCOPE="local"

# Function to set git config
set_config() {
    local key=$1
    local value=$2
    local description=$3
    
    echo "✓ $description"
    if [ "$SCOPE" = "local" ]; then
        git config "$key" "$value" 2>/dev/null || true
    else
        git config --global "$key" "$value" 2>/dev/null || true
    fi
}

echo "Applying merge conflict best practices..."
echo ""

# Core Merge Settings
set_config "merge.conflictstyle" "diff3" \
    "Show common ancestor in conflict markers"

set_config "pull.rebase" "false" \
    "Use merge strategy for pulls"

set_config "merge.ff" "false" \
    "Always create merge commit"

# Conflict Resolution Tools
set_config "rerere.enabled" "true" \
    "Remember conflict resolutions"

set_config "rerere.autoupdate" "true" \
    "Auto-stage rerere resolutions"

# Diff & Merge Algorithms
set_config "diff.algorithm" "histogram" \
    "Better diff algorithm"

set_config "diff.colorMoved" "default" \
    "Highlight moved code"

set_config "merge.conflictMarkerSize" "7" \
    "Longer conflict markers"

# Language-specific Diff
set_config "diff.python.xfuncname" "^[ \t]*((class|def)[ \t].*)$" \
    "Python function context"

set_config "diff.javascript.xfuncname" "^[ \t]*(((async[ \t]+)?function|class|const|let|var)[ \t].*)$" \
    "JavaScript function context"

# Merge Tool (default to vimdiff for automation)
set_config "merge.tool" "vimdiff" \
    "Default merge tool"

set_config "mergetool.prompt" "false" \
    "No prompts for merge tool"

set_config "mergetool.keepBackup" "false" \
    "No .orig backup files"

echo ""
echo "================================================"
echo "Configuration Complete!"
echo "================================================"
echo ""
echo "Applied configurations:"
git config --list --local | grep -E "(merge|diff|rerere|pull)" 2>/dev/null || echo "  Configurations applied"
echo ""
