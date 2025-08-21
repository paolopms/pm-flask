#!/usr/bin/env bash
set -euo pipefail
# Uso: restore_db.sh /backups/pg/petmaison_YYYY-MM-DD_HH-MM-SS.dump
FILE="$1"
pg_restore -h "${PGHOST:-db}" -U "${PGUSER:-petmaison}" -d "${PGDATABASE:-petmaison}" -c "$FILE"
echo "Restore DB desde: $FILE OK"
