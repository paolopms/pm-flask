#!/usr/bin/env bash
set -euo pipefail
: "${MEDIA_DIR:=/app/media}"
: "${BACKUP_DIR:=/backups/media}"
mkdir -p "$BACKUP_DIR"
DATE="$(date +%F_%H-%M-%S)"
tar czf "$BACKUP_DIR/media_${DATE}.tar.gz" -C "$MEDIA_DIR" .
echo "Backup media creado: $BACKUP_DIR/media_${DATE}.tar.gz"
