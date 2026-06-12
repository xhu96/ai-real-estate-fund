# Backup and Restore Runbook

The default local deployment uses SQLite. Managed production deployments should use a managed database with automated snapshots.

## SQLite backup

```bash
python scripts/backup_sqlite.py --source data/app.db --dest-dir backups
python scripts/backup_sqlite.py --source data/audit.db --dest-dir backups
```

## SQLite restore

```bash
python scripts/restore_sqlite.py backups/app-YYYYMMDDTHHMMSSZ.db --dest data/app.db --yes
python scripts/restore_sqlite.py backups/audit-YYYYMMDDTHHMMSSZ.db --dest data/audit.db --yes
```

After restore:

```bash
python -m ai_real_estate_fund audit-verify --db data/audit.db --strict
python scripts/smoke_test.py
```
