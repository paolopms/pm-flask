#!/usr/bin/env bash
set -euo pipefail
: "${BACKUP_DIR:=/backups/pg}"
mkdir -p "$BACKUP_DIR"
DATE="$(date +%F_%H-%M-%S)"
FILE="$BACKUP_DIR/${PGDATABASE:-petmaison}_${DATE}.dump"
pg_dump -F c -h "${PGHOST:-db}" -U "${PGUSER:-petmaison}" "${PGDATABASE:-petmaison}" > "$FILE"
echo "Backup DB creado: $FILE"
