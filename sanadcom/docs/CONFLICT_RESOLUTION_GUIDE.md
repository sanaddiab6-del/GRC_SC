# Git Merge Conflict Resolution Guide

## Overview

This guide provides best practices for preventing and resolving merge conflicts in the SICO GRC Platform repository.

## Table of Contents

- [Prevention Strategies](#prevention-strategies)
- [Detection Tools](#detection-tools)
- [Resolution Workflow](#resolution-workflow)
- [Common Conflict Scenarios](#common-conflict-scenarios)
- [Automated Tools](#automated-tools)
- [Best Practices](#best-practices)

## Prevention Strategies

### 1. Keep Branches Short-Lived

**✅ Recommended:**
- Feature branches should live for 1-3 days maximum
- Merge frequently to avoid divergence
- Use small, focused pull requests

**❌ Avoid:**
- Long-running feature branches (>1 week)
- Large pull requests with many file changes

### 2. Rebase Regularly

```bash
# Update your branch with latest main
git checkout main
git pull origin main
git checkout your-feature-branch
git rebase main

# If conflicts occur during rebase, resolve them step by step
# Then continue: git rebase --continue
```

### 3. Communication

- Coordinate with team when editing the same files
- Use branch protection rules to prevent direct pushes to main
- Review open PRs before starting work on related files

### 4. Modular Code Structure

The repository is organized to minimize conflicts:

```
src/
├── backend/
│   ├── controls/      # Control management (isolated)
│   ├── evidence/      # Evidence management (isolated)
│   ├── reporting/     # Reporting engine (isolated)
│   └── core/          # Shared utilities
```

Work in isolated modules when possible.

## Detection Tools

### Pre-Merge Conflict Detection

Run this command before creating a PR:

```bash
# Check if your branch will have conflicts with main
git fetch origin main
git merge-tree $(git merge-base HEAD origin/main) HEAD origin/main | grep -A 3 "<<<<<<< "
```

### CI/CD Integration

Our CI pipeline (`.github/workflows/ci.yml`) includes conflict detection:

```yaml
- name: Check for merge conflicts
  run: |
    git fetch origin main
    git merge-base HEAD origin/main
    # Fails if conflict markers exist
```

## Resolution Workflow

### Step 1: Identify Conflicting Files

```bash
# Start merge or rebase
git merge main  # or: git rebase main

# List files with conflicts
git status | grep "both modified"
# or
git diff --name-only --diff-filter=U
```

### Step 2: Understand the Conflict

```bash
# View the conflict in detail
git diff <file>

# See the changes from both sides
git show :1:<file>  # common ancestor
git show :2:<file>  # your changes (HEAD)
git show :3:<file>  # their changes (incoming)
```

### Step 3: Choose Resolution Strategy

#### A. Manual Resolution (Most Common)

1. Open the conflicting file in your editor
2. Look for conflict markers:
   ```
   <<<<<<< HEAD
   Your changes
   =======
   Their changes
   >>>>>>> branch-name
   ```
3. Decide which changes to keep:
   - Keep yours only
   - Keep theirs only
   - Keep both (merge manually)
   - Write new code that incorporates both

4. Remove conflict markers
5. Test the code
6. Mark as resolved:
   ```bash
   git add <file>
   ```

#### B. Accept Ours/Theirs (Simple Conflicts)

```bash
# Keep your version entirely
git checkout --ours <file>
git add <file>

# Keep their version entirely
git checkout --theirs <file>
git add <file>
```

#### C. Use Merge Tool (Complex Conflicts)

```bash
# Configure your preferred merge tool (one-time setup)
git config --global merge.tool vscode  # or: meld, kdiff3, vimdiff

# Launch the merge tool
git mergetool <file>
```

### Step 4: Complete the Merge

```bash
# After resolving all conflicts
git add .
git commit  # or: git rebase --continue

# Push the changes
git push origin your-branch
```

## Common Conflict Scenarios

### Scenario 1: Import Statement Conflicts (Python)

**Conflict:**
```python
<<<<<<< HEAD
from backend.controls.models import Control
from backend.evidence.models import Evidence
=======
from backend.controls.models import Control
from backend.reporting.models import Report
>>>>>>> feature-branch
```

**Resolution:**
```python
# Keep both imports
from backend.controls.models import Control
from backend.evidence.models import Evidence
from backend.reporting.models import Report
```

### Scenario 2: Database Migration Conflicts

**Problem:** Two migrations with the same revision number

**Resolution:**
```bash
# Rename the newer migration
cd src/backend/migrations/versions/

# Find conflicting migrations
ls -la | grep "002_"

# Renumber if needed
alembic revision --autogenerate -m "Combined migration"

# Review and test
alembic upgrade head
```

### Scenario 3: Package Dependency Conflicts

**Conflict in `requirements.txt`:**
```
<<<<<<< HEAD
fastapi==0.104.1
sqlalchemy==2.0.23
=======
fastapi==0.105.0
sqlalchemy==2.0.23
>>>>>>> feature-branch
```

**Resolution:**
```bash
# Choose the higher version (unless breaking changes exist)
fastapi==0.105.0
sqlalchemy==2.0.23

# Test thoroughly
pip install -r requirements.txt
pytest tests/
```

### Scenario 4: Frontend Component Conflicts

**Conflict:**
```tsx
<<<<<<< HEAD
<Button onClick={handleSubmit} variant="primary">
  {t('common.submit')}
</Button>
=======
<Button onClick={handleSave} variant="secondary">
  {t('common.save')}
</Button>
>>>>>>> feature-branch
```

**Resolution:** Consider the intent of both changes
```tsx
{/* Keep both handlers if they serve different purposes */}
<div className="button-group">
  <Button onClick={handleSubmit} variant="primary">
    {t('common.submit')}
  </Button>
  <Button onClick={handleSave} variant="secondary">
    {t('common.save')}
  </Button>
</div>
```

## Automated Tools

### 1. Use `.gitattributes` Merge Strategies

The repository includes a `.gitattributes` file with smart merge strategies:

- **Union merge** for imports and documentation
- **Ours strategy** for lock files (regenerate after merge)
- **Binary handling** for images and compiled files

### 2. Conflict Detection Script

Located at `scripts/check_conflicts.sh`:

```bash
# Run before creating a PR
./scripts/check_conflicts.sh main

# Output: Lists potential conflicts with main branch
```

### 3. Pre-commit Hooks

Set up pre-commit hooks to catch issues early:

```bash
# Install pre-commit
pip install pre-commit

# Install hooks
pre-commit install

# Hooks will run on: git commit
```

## Best Practices

### ✅ DO

1. **Pull/Rebase Frequently**
   ```bash
   # Daily routine
   git checkout main && git pull
   git checkout feature-branch && git rebase main
   ```

2. **Test After Resolution**
   ```bash
   # Backend tests
   cd src/backend && pytest tests/
   
   # Frontend tests
   cd src/frontend && npm test
   
   # Integration tests
   docker-compose up -d && make test
   ```

3. **Communicate Complex Merges**
   - Add detailed commit messages explaining conflict resolutions
   - Request review from the original author if unsure
   - Document non-obvious resolution choices in PR comments

4. **Use Atomic Commits**
   ```bash
   # One logical change per commit
   git add src/backend/controls/models.py
   git commit -m "Add validation to Control model"
   
   git add src/backend/controls/router.py
   git commit -m "Add validation to Control endpoints"
   ```

5. **Leverage Git Tools**
   ```bash
   # View conflict history
   git log --merge --left-right -p <file>
   
   # See who last modified conflicting lines
   git blame <file>
   
   # Compare branches
   git diff main...your-branch
   ```

### ❌ DON'T

1. **Don't Force Push After Merge**
   ```bash
   # ❌ Never do this after resolving conflicts
   git push --force
   
   # ✅ Instead
   git push origin your-branch
   ```

2. **Don't Ignore Conflict Markers**
   - Always search for `<<<<<<<` before committing
   - Use editor features to highlight conflicts
   - Run linters to catch syntax errors from partial resolutions

3. **Don't Resolve Without Understanding**
   - If you don't understand the conflict, ask the author
   - Never blindly accept "ours" or "theirs" without review
   - Check git blame to understand the context

4. **Don't Forget to Test**
   - Conflicts can introduce subtle bugs
   - Run the full test suite after major conflict resolutions
   - Manually test affected functionality

## Git Configuration Best Practices

Add these to your global or repository git config:

```bash
# Better conflict markers with more context
git config --global merge.conflictstyle diff3

# Enable rerere (reuse recorded resolution)
git config --global rerere.enabled true

# Better diff algorithm
git config --global diff.algorithm histogram

# Show original commit in conflict markers
git config --global merge.conflictMarkerSize 7

# Configure merge tool
git config --global merge.tool vscode  # or your preferred tool

# Auto-launch merge tool on conflicts
git config --global mergetool.prompt false
```

## Emergency Procedures

### Abort a Merge

```bash
# Cancel the merge and return to pre-merge state
git merge --abort

# Or for rebase
git rebase --abort
```

### Undo a Completed Merge

```bash
# Find the merge commit
git log --oneline --graph -5

# Reset to before the merge (preserves changes)
git reset --soft HEAD~1

# Or discard everything (use with caution)
git reset --hard HEAD~1
```

### Recover Lost Changes

```bash
# View reflog to find lost commits
git reflog

# Recover a lost commit
git checkout <commit-hash>
git checkout -b recovery-branch
```

## Bilingual Considerations (Arabic/English)

### String Conflicts

When resolving conflicts in bilingual content:

1. **Always preserve both languages:**
   ```json
   {
     "title_en": "Risk Assessment",
     "title_ar": "تقييم المخاطر"
   }
   ```

2. **Check RTL formatting:**
   - Ensure Arabic text has proper RTL directionality
   - Test UI in both languages after merge

3. **Validate translations:**
   ```bash
   # Check for missing translations
   cd src/frontend
   npm run check-i18n
   ```

## Resources

- **Git Documentation:** https://git-scm.com/docs/git-merge
- **Merge Strategies:** https://git-scm.com/docs/merge-strategies
- **Repository Structure:** [docs/architecture/README.md](architecture/README.md)
- **Contributing Guide:** [CONTRIBUTING.md](../CONTRIBUTING.md) _(to be created)_

## Quick Reference

```bash
# Conflict detection
git diff --name-only --diff-filter=U

# Accept ours/theirs
git checkout --ours <file>    # Keep your changes
git checkout --theirs <file>  # Keep their changes

# View changes from both sides
git show :2:<file>  # Your version
git show :3:<file>  # Their version

# Mark as resolved
git add <file>

# Continue merge/rebase
git merge --continue
git rebase --continue

# Abort
git merge --abort
git rebase --abort

# Test after resolution
make test                      # Run all tests
pytest tests/backend/          # Backend only
npm test --prefix src/frontend # Frontend only
```

## Support

If you encounter complex conflicts:

1. Check this guide's [Common Scenarios](#common-conflict-scenarios)
2. Review the specific module documentation
3. Consult with the code owner via GitHub PR comments
4. For urgent issues, contact the tech lead

---

**Last Updated:** 2026-02-04  
**Maintained By:** SICO Development Team
