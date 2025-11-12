# Deployment Guide

## Overview

این راهنما مراحل استقرار IntelliLift AI Dashboard را در محیط production توضیح می‌دهد.

## پیش‌نیازها

### Infrastructure Requirements

- **Server**: Ubuntu 20.04+ یا CentOS 8+
- **CPU**: 4+ cores
- **RAM**: 16GB+ (32GB recommended)
- **Storage**: 500GB+ SSD
- **Network**: Stable internet connection

### Software Requirements

- Docker 20.10+
- Docker Compose 2.0+
- PostgreSQL 15+ with TimescaleDB
- Redis 7+
- Nginx (برای reverse proxy)

## Deployment Options

### Option 1: Docker Compose (Recommended for Small/Medium)

#### 1. Clone Repository

```bash
git clone <repository-url>
cd i-lift---AI-Powered-Artificial-Lift-Management-Dashboard
```

#### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env with production values
nano .env
```

**Important Environment Variables:**

```env
# Database
DATABASE_URL=postgresql://user:password@postgres:5432/ilift_db

# Redis
REDIS_URL=redis://redis:6379/0

# Security
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256

# CORS
CORS_ORIGINS=https://yourdomain.com
```

#### 3. Build and Start

```bash
# Build images
docker-compose build

# Start services
docker-compose up -d

# Check status
docker-compose ps

# View logs
docker-compose logs -f
```

#### 4. Run Migrations

```bash
docker-compose exec backend alembic upgrade head
```

#### 5. Create Admin User

```bash
docker-compose exec backend python scripts/create_admin.py
```

### Option 2: Kubernetes (Recommended for Large Scale)

#### 1. Create Namespace

```bash
kubectl create namespace ilift
```

#### 2. Deploy PostgreSQL

```bash
kubectl apply -f k8s/postgresql.yaml
```

#### 3. Deploy Redis

```bash
kubectl apply -f k8s/redis.yaml
```

#### 4. Deploy Backend

```bash
kubectl apply -f k8s/backend.yaml
```

#### 5. Deploy Frontend

```bash
kubectl apply -f k8s/frontend.yaml
```

#### 6. Deploy Ingress

```bash
kubectl apply -f k8s/ingress.yaml
```

## Production Configuration

### Nginx Configuration

```nginx
upstream backend {
    server localhost:8000;
}

upstream frontend {
    server localhost:3000;
}

server {
    listen 80;
    server_name yourdomain.com;

    # Redirect to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com;

    ssl_certificate /etc/ssl/certs/yourdomain.crt;
    ssl_certificate_key /etc/ssl/private/yourdomain.key;

    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Backend API
    location /api {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # WebSocket support
    location /ws {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
    }
}
```

### Database Configuration

#### TimescaleDB Setup

```sql
-- Connect to database
\c ilift_db

-- Create TimescaleDB extension
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- Create hypertable
SELECT create_hypertable('sensor_readings', 'timestamp');
```

#### Database Backup

```bash
# Backup script
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
pg_dump -U postgres ilift_db > backup_$DATE.sql

# Restore
psql -U postgres ilift_db < backup_$DATE.sql
```

### Redis Configuration

```bash
# Redis configuration for production
maxmemory 2gb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
save 60 10000
```

### Monitoring Setup

#### Prometheus Configuration

```yaml
global:
  scrape_interval: 15s

scrape_configs:
  - job_name: 'backend'
    static_configs:
      - targets: ['backend:8000']
    metrics_path: '/api/v1/monitoring/metrics'
```

#### Grafana Dashboard

1. Import Prometheus data source
2. Import pre-built dashboards
3. Configure alerts

## Security Hardening

### 1. Firewall Configuration

```bash
# Allow only necessary ports
ufw allow 22/tcp   # SSH
ufw allow 80/tcp   # HTTP
ufw allow 443/tcp  # HTTPS
ufw enable
```

### 2. SSL/TLS Certificates

```bash
# Using Let's Encrypt
certbot --nginx -d yourdomain.com
```

### 3. Database Security

- Use strong passwords
- Enable SSL connections
- Restrict network access
- Regular backups

### 4. Application Security

- Strong SECRET_KEY
- Enable CORS restrictions
- Rate limiting
- Input validation
- SQL injection prevention

## Backup Strategy

### Database Backups

```bash
# Daily backup script
#!/bin/bash
DATE=$(date +%Y%m%d)
pg_dump -U postgres ilift_db | gzip > /backups/db_$DATE.sql.gz

# Keep last 30 days
find /backups -name "db_*.sql.gz" -mtime +30 -delete
```

### Application Backups

```bash
# Backup application data
tar -czf /backups/app_$(date +%Y%m%d).tar.gz /var/lib/ilift
```

## Monitoring & Alerts

### Health Checks

```bash
# Backend health
curl http://localhost:8000/api/v1/monitoring/health

# Database health
docker-compose exec postgres pg_isready
```

### Log Management

```bash
# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Log rotation
logrotate /etc/logrotate.d/ilift
```

## Scaling

### Horizontal Scaling

```bash
# Scale backend services
docker-compose up -d --scale backend=3

# Load balancer configuration
# Use Nginx or HAProxy for load balancing
```

### Database Scaling

- Read replicas for TimescaleDB
- Connection pooling
- Query optimization

## Troubleshooting

### Common Issues

#### Database Connection Error

```bash
# Check database status
docker-compose ps postgres

# Check connection
docker-compose exec backend python -c "from app.core.database import engine; engine.connect()"
```

#### High Memory Usage

```bash
# Check memory usage
docker stats

# Restart services
docker-compose restart
```

#### Slow Queries

```bash
# Enable query logging
# Check database indexes
# Optimize queries
```

## Maintenance

### Updates

```bash
# Pull latest changes
git pull

# Rebuild and restart
docker-compose build
docker-compose up -d

# Run migrations
docker-compose exec backend alembic upgrade head
```

### Cleanup

```bash
# Remove old containers
docker-compose down

# Remove old images
docker image prune -a

# Clean volumes (careful!)
docker volume prune
```

## Disaster Recovery

### Recovery Plan

1. **Database Recovery**: Restore from backup
2. **Application Recovery**: Redeploy from repository
3. **Data Recovery**: Restore from backups

### RTO/RPO Targets

- **RTO**: 4 hours
- **RPO**: 24 hours

## Support

برای مشکلات deployment:
- Check logs: `docker-compose logs`
- Review documentation
- Contact support team

