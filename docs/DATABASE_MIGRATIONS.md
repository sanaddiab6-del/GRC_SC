# Database Migration Quick Reference

## ⚡ Quick Start

### Windows PowerShell
```powershell
# Run migrations (recommended method)
.\scripts\run-alembic-migrations.ps1

# Check for multiple heads without migrating
.\scripts\run-alembic-migrations.ps1 -CheckOnly

# Show migration history
.\scripts\run-alembic-migrations.ps1 -Command history
```

### Linux/Mac/CI
```bash
# Run migrations (recommended method)
bash scripts/run-alembic-migrations.sh upgrade

# Check for multiple heads without migrating
bash scripts/run-alembic-migrations.sh upgrade true

# Show migration history
bash scripts/run-alembic-migrations.sh history
```

## 🔧 Manual Alembic Commands

If you need to use Alembic directly:

### Check Installation
```powershell
# Windows
python -m alembic --version

# Linux/Mac
alembic --version
```

### Common Operations
```powershell
cd src/backend

# List current migration heads
python -m alembic heads

# Show current database version
python -m alembic current

# Show migration history
python -m alembic history

# Upgrade to latest
python -m alembic upgrade head

# Downgrade one revision
python -m alembic downgrade -1
```

## 🔀 Handling Multiple Heads

### Check for Multiple Heads
```powershell
cd src/backend
python -m alembic heads -v
```

### Merge Multiple Heads
If you see multiple heads, merge them:

```powershell
cd src/backend

# Merge all heads automatically
python -m alembic merge -m "merge multiple heads" heads

# Then upgrade
python -m alembic upgrade head
```

### Manual Merge (if auto-merge fails)
```powershell
cd src/backend

# Get the revision IDs of the heads
python -m alembic heads

# Merge specific heads (replace with actual revision IDs)
python -m alembic merge -m "merge heads" <revision1> <revision2>

# Upgrade
python -m alembic upgrade head
```

## 🛠️ Creating New Migrations

### Auto-generate from Model Changes
```powershell
cd src/backend
python -m alembic revision --autogenerate -m "description of changes"
```

### Create Empty Migration
```powershell
cd src/backend
python -m alembic revision -m "description of changes"
```

## ❌ Troubleshooting

### Error: "alembic is not recognized"
**Solution:** Use `python -m alembic` instead of just `alembic`

```powershell
# ❌ Don't use this
alembic upgrade head

# ✅ Use this instead
python -m alembic upgrade head

# ✅ Or use the helper script
.\scripts\run-alembic-migrations.ps1
```

### Error: "Multiple head revisions are present"
**Solution:** Use the migration scripts or merge manually:

```powershell
# Option 1: Use helper script (easiest)
.\scripts\run-alembic-migrations.ps1

# Option 2: Merge manually
cd src/backend
python -m alembic merge -m "merge heads" heads
python -m alembic upgrade head
```

### Error: "Can't locate revision identified by 'head'"
**Solution:** Initialize the database first:

```powershell
cd src/backend
python -m alembic stamp head
python -m alembic upgrade head
```

### Error: Migration fails with foreign key constraint
**Solutions:**
1. Check migration order - dependencies must be created first
2. Drop the database and recreate: `alembic upgrade head`
3. Fix migration file ordering (see example in migration 009_backup_dr.py)

## 📁 Migration File Structure

Migrations are located in: `src/backend/migrations/versions/`

### File Naming Convention
```
XXX_description.py

Where:
- XXX = sequential number (001, 002, 003, etc.)
- description = brief description of migration
```

### Migration File Template
```python
"""Description of migration

Revision ID: XXX_description
Revises: XXX_previous_migration
Create Date: YYYY-MM-DD

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = 'XXX_description'
down_revision = 'XXX_previous_migration'  # Must point to correct parent!
branch_labels = None
depends_on = None

def upgrade() -> None:
    # Your upgrade logic here
    pass

def downgrade() -> None:
    # Your downgrade logic here
    pass
```

## ⚠️ Important Notes

1. **Always check for multiple heads** before deploying to production
2. **Never skip migrations** - run them in order
3. **Test migrations** on a copy of production data first
4. **Backup database** before running migrations in production
5. **Use the helper scripts** - they handle edge cases automatically

## 🚀 CI/CD Integration

The GitHub Actions workflow automatically:
- Checks for multiple heads
- Merges heads if needed
- Runs migrations safely

See: `.github/workflows/ci.yml`

## 📖 Additional Resources

- Official Alembic Documentation: https://alembic.sqlalchemy.org/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/
- Project Database Documentation: `docs/DATABASE_README.md`
