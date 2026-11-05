#!/usr/bin/env bash
# Cópia do banco da Torre (pg_dump compactado), com 14 dias de retenção.
# Agendar no cron do root:  15 3 * * * /opt/torre/repo/deploy/backup.sh >> /var/log/torre-backup.log 2>&1
# Fase 2: enviar também para fora da VPS (rclone).
set -euo pipefail
cd "$(dirname "$0")"
DEST="${TORRE_BACKUP_DIR:-/opt/torre/backups}"
mkdir -p "$DEST"
ARQ="$DEST/torre-$(date +%Y%m%d-%H%M).sql.gz"
docker compose exec -T db pg_dump -U torre -d torre --no-owner | gzip > "$ARQ"
[ -s "$ARQ" ] || { echo "backup vazio: $ARQ"; exit 1; }
find "$DEST" -name 'torre-*.sql.gz' -mtime +14 -delete
echo "$(date -Iseconds) ok $ARQ"
