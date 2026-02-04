# Automation Scripts

## SICO GRC Platform Utility Scripts

This directory contains automation scripts for various platform operations.

## Available Scripts

### Database Management

#### `db-setup.sh`
Initialize database and run migrations.
```bash
./scripts/db-setup.sh
```

#### `db-backup.sh`
Create database backup.
```bash
./scripts/db-backup.sh [output_directory]
```

#### `db-restore.sh`
Restore database from backup.
```bash
./scripts/db-restore.sh [backup_file]
```

---

### Data Management

#### `import-controls.py`
Import control libraries from YAML/JSON files.
```bash
python scripts/import-controls.py --framework ecc --file data/controls/ecc-controls.yaml
```

#### `import-evidence.py`
Import evidence templates into the system.
```bash
python scripts/import-evidence.py --file data/evidence/evidence-catalog.yaml
```

#### `export-compliance-data.py`
Export compliance data for reporting or backup.
```bash
python scripts/export-compliance-data.py --format excel --output reports/compliance-export.xlsx
```

---

### AI/ML Operations

#### `build-knowledge-base.py`
Build and index the AI knowledge base.
```bash
python scripts/build-knowledge-base.py --source ai/knowledge-base/documents/ --output ai/knowledge-base/embeddings/
```

#### `train-adapter.py`
Train client-specific BERT adapter.
```bash
python scripts/train-adapter.py --client-id CLIENT_123 --data-path /path/to/training/data
```

#### `update-embeddings.py`
Update vector embeddings for new documents.
```bash
python scripts/update-embeddings.py --documents-path ai/knowledge-base/documents/
```

---

### Deployment & DevOps

#### `deploy.sh`
Deploy application to specified environment.
```bash
./scripts/deploy.sh [development|staging|production]
```

#### `health-check.sh`
Check health of all services.
```bash
./scripts/health-check.sh
```

#### `setup-dev-env.sh`
Setup complete development environment.
```bash
./scripts/setup-dev-env.sh
```

---

### Testing & Quality Assurance

#### `run-tests.sh`
Run complete test suite.
```bash
./scripts/run-tests.sh [backend|frontend|all]
```

#### `lint-code.sh`
Run linters on codebase.
```bash
./scripts/lint-code.sh
```

#### `generate-test-data.py`
Generate mock data for testing.
```bash
python scripts/generate-test-data.py --users 100 --controls 50 --evidence 200
```

---

### Reporting

#### `generate-compliance-report.py`
Generate compliance status report.
```bash
python scripts/generate-compliance-report.py --client-id CLIENT_123 --format pdf
```

#### `generate-executive-dashboard.py`
Generate executive dashboard data.
```bash
python scripts/generate-executive-dashboard.py --period monthly
```

---

### Maintenance

#### `cleanup-old-data.py`
Clean up old logs and temporary files.
```bash
python scripts/cleanup-old-data.py --days 90
```

#### `rotate-logs.sh`
Rotate application logs.
```bash
./scripts/rotate-logs.sh
```

#### `system-maintenance.sh`
Run system maintenance tasks.
```bash
./scripts/system-maintenance.sh
```

---

## Script Categories

### Production Scripts
Scripts safe to run in production environments.
- `db-backup.sh`
- `health-check.sh`
- `generate-compliance-report.py`

### Development Scripts
Scripts for development and testing only.
- `setup-dev-env.sh`
- `generate-test-data.py`
- `run-tests.sh`

### Administrative Scripts
Scripts requiring elevated privileges.
- `db-setup.sh`
- `deploy.sh`
- `system-maintenance.sh`

---

## Usage Guidelines

### Before Running Scripts

1. **Check Environment**: Ensure you're in the correct environment
2. **Backup Data**: Create backups before running destructive operations
3. **Review Parameters**: Verify all required parameters are provided
4. **Test First**: Test in development before running in production

### Security Considerations

- Store credentials in environment variables, not in scripts
- Use `.env` files for configuration
- Never commit credentials to version control
- Limit script execution to authorized users

### Error Handling

All scripts include:
- Input validation
- Error checking
- Logging
- Rollback capabilities (where applicable)

---

## Development

### Creating New Scripts

1. Follow naming convention: `action-subject.sh` or `action_subject.py`
2. Include header comment with purpose and usage
3. Add error handling
4. Document in this README
5. Make shell scripts executable: `chmod +x script.sh`

### Testing Scripts

```bash
# Test in isolated environment
docker run --rm -it -v $(pwd):/app python:3.11 bash
cd /app
./scripts/your-script.sh
```

---

**Last Updated**: February 2026
