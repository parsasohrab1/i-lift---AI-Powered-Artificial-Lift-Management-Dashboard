#!/bin/bash

set -e

# Configuration
BACKUP_DIR="/backups/ilift"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=30

# Create backup directory
mkdir -p ${BACKUP_DIR}

echo "Starting backup process..."

# Database backup
echo "Backing up database..."
docker-compose exec -T postgres pg_dump -U postgres ilift_db | gzip > ${BACKUP_DIR}/db_${DATE}.sql.gz

# Redis backup
echo "Backing up Redis..."
docker-compose exec -T redis redis-cli SAVE
docker cp $(docker-compose ps -q redis):/data/dump.rdb ${BACKUP_DIR}/redis_${DATE}.rdb

# Application data backup
echo "Backing up application data..."
tar -czf ${BACKUP_DIR}/app_data_${DATE}.tar.gz \
    backend/logs \
    frontend/.next \
    2>/dev/null || true

# MLflow artifacts backup
echo "Backing up MLflow artifacts..."
docker-compose exec -T mlflow tar -czf - /mlflow/artifacts > ${BACKUP_DIR}/mlflow_${DATE}.tar.gz 2>/dev/null || true

# Cleanup old backups
echo "Cleaning up old backups (older than ${RETENTION_DAYS} days)..."
find ${BACKUP_DIR} -name "*.sql.gz" -mtime +${RETENTION_DAYS} -delete
find ${BACKUP_DIR} -name "*.rdb" -mtime +${RETENTION_DAYS} -delete
find ${BACKUP_DIR} -name "*.tar.gz" -mtime +${RETENTION_DAYS} -delete

echo "Backup completed successfully!"
echo "Backup location: ${BACKUP_DIR}"

