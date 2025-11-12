#!/bin/bash

set -e

# Configuration
BACKUP_DIR="/backups/ilift"

if [ -z "$1" ]; then
    echo "Usage: $0 <backup_date>"
    echo "Example: $0 20240101_120000"
    exit 1
fi

BACKUP_DATE=$1

echo "Starting restore process from backup: ${BACKUP_DATE}"

# Check if backup files exist
DB_BACKUP="${BACKUP_DIR}/db_${BACKUP_DATE}.sql.gz"
REDIS_BACKUP="${BACKUP_DIR}/redis_${BACKUP_DATE}.rdb"

if [ ! -f "${DB_BACKUP}" ]; then
    echo "Error: Database backup not found: ${DB_BACKUP}"
    exit 1
fi

# Restore database
echo "Restoring database..."
gunzip -c ${DB_BACKUP} | docker-compose exec -T postgres psql -U postgres ilift_db

# Restore Redis
if [ -f "${REDIS_BACKUP}" ]; then
    echo "Restoring Redis..."
    docker cp ${REDIS_BACKUP} $(docker-compose ps -q redis):/data/dump.rdb
    docker-compose exec -T redis redis-cli CONFIG SET stop-writes-on-bgsave-error no
    docker-compose restart redis
fi

echo "Restore completed successfully!"

