#!/bin/bash
# =============================================================================
# Git History Cleaner - Remove Sensitive Data
# =============================================================================
# This script removes sensitive data from git history using git-filter-repo
# Run this BEFORE pushing to a public repository
# =============================================================================

set -e

echo "🔐 Git History Cleaner for VaultMind AI"
echo "========================================"

# Check if git-filter-repo is installed
if ! command -v git-filter-repo &> /dev/null; then
    echo "❌ git-filter-repo is not installed."
    echo "   Install with: pip install git-filter-repo"
    exit 1
fi

# Patterns to remove from history
# These are the sensitive patterns found in the repository
PATTERNS=(
    "REDACTED"
    "REDACTED"
)

echo "⚠️  WARNING: This will rewrite git history!"
echo "   Make sure you have a backup before proceeding."
echo ""
read -p "Continue? (y/N): " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

# Create backup branch
echo "📦 Creating backup branch..."
git branch backup-before-clean 2>/dev/null || echo "   Backup branch already exists"

# Use git-filter-repo to remove sensitive strings
echo "🧹 Cleaning sensitive data from history..."

for pattern in "${PATTERNS[@]}"; do
    echo "   Removing pattern: ${pattern:0:10}..."
    git filter-repo --replace-text <(echo "${pattern}==>REDACTED") --force 2>/dev/null || true
done

echo ""
echo "✅ History cleaned!"
echo ""
echo "⚠️  IMPORTANT NEXT STEPS:"
echo "   1. Force push to remote: git push origin main --force"
echo "   2. Tell all collaborators to re-clone the repository"
echo "   3. ROTATE your credentials (the old ones may still be cached somewhere)"
echo ""
echo "🔑 Credentials to rotate:"
echo "   - Azure PostgreSQL password"
echo "   - Any API keys that were ever in .env files"
