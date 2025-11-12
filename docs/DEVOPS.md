# DevOps Documentation

راهنمای کامل DevOps و Deployment

## Overview

این مستندات شامل تمام اطلاعات لازم برای استقرار و مدیریت IntelliLift AI Dashboard در محیط production است.

## Deployment Options

### 1. Docker Compose (Recommended for Small/Medium)

#### Quick Start

```bash
# Copy environment file
cp .env.example .env
# Edit .env with your configuration

# Deploy
./scripts/deploy.sh production
```

#### Configuration

فایل `docker-compose.prod.yml` شامل:
- Health checks برای تمام services
- Resource limits
- Restart policies
- Volume management
- Network configuration

### 2. Kubernetes (Recommended for Large Scale)

#### Prerequisites

- Kubernetes cluster (1.24+)
- kubectl configured
- Helm (optional)

#### Deployment

```bash
# Create namespace
kubectl apply -f k8s/namespace.yaml

# Create secrets
kubectl create secret generic postgres-secret \
  --from-literal=username=postgres \
  --from-literal=password=your-password \
  -n ilift

kubectl create secret generic backend-secret \
  --from-literal=database-url=postgresql://... \
  --from-literal=secret-key=your-secret-key \
  -n ilift

# Deploy services
kubectl apply -f k8s/postgresql.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml
kubectl apply -f k8s/ingress.yaml
```

## CI/CD Pipeline

### GitHub Actions

Pipeline شامل:
1. **Build**: Build Docker images
2. **Test**: Run tests
3. **Push**: Push to container registry
4. **Deploy**: Deploy to production

### Workflow Files

- `.github/workflows/test.yml` - Test pipeline
- `.github/workflows/deploy.yml` - Deployment pipeline

## Monitoring

### Prometheus

- Metrics collection
- Service discovery
- Alerting rules

### Grafana

- Pre-built dashboards
- Custom visualizations
- Alert notifications

### Health Checks

```bash
# Run health checks
./scripts/health-check.sh

# Check service status
docker-compose ps
kubectl get pods -n ilift
```

## Backup & Recovery

### Automated Backups

```bash
# Run backup
./scripts/backup.sh

# Schedule with cron
0 2 * * * /path/to/scripts/backup.sh
```

### Manual Backup

```bash
# Database
docker-compose exec postgres pg_dump -U postgres ilift_db > backup.sql

# Redis
docker-compose exec redis redis-cli SAVE
docker cp $(docker-compose ps -q redis):/data/dump.rdb backup.rdb
```

### Recovery

```bash
# Restore from backup
./scripts/restore.sh 20240101_120000
```

## Scaling

### Horizontal Scaling

#### Docker Compose

```bash
docker-compose up -d --scale backend=3 --scale frontend=2
```

#### Kubernetes

```bash
kubectl scale deployment backend --replicas=5 -n ilift
```

### Vertical Scaling

Edit resource limits in:
- `docker-compose.prod.yml` (deploy.resources)
- `k8s/*.yaml` (resources.requests/limits)

## Security

### SSL/TLS

- Let's Encrypt certificates
- Auto-renewal
- HSTS headers

### Secrets Management

- Environment variables
- Kubernetes secrets
- Docker secrets (Swarm)

### Network Security

- Firewall rules
- Network policies
- VPN access

## Troubleshooting

### Common Issues

#### Services Not Starting

```bash
# Check logs
docker-compose logs backend
kubectl logs -n ilift deployment/backend

# Check resource usage
docker stats
kubectl top pods -n ilift
```

#### Database Connection Issues

```bash
# Test connection
docker-compose exec backend python -c "from app.core.database import engine; engine.connect()"

# Check database status
docker-compose exec postgres pg_isready
```

#### High Memory Usage

```bash
# Check memory
docker stats
free -h

# Restart services
docker-compose restart
```

## Maintenance

### Updates

```bash
# Pull latest code
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

# Remove unused images
docker image prune -a

# Clean volumes (careful!)
docker volume prune
```

## Best Practices

1. **Always backup before updates**
2. **Use health checks**
3. **Monitor resource usage**
4. **Keep logs organized**
5. **Test in staging first**
6. **Document changes**
7. **Use version control**
8. **Automate everything possible**

## Resources

- [Docker Documentation](https://docs.docker.com/)
- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Prometheus Documentation](https://prometheus.io/docs/)
- [Grafana Documentation](https://grafana.com/docs/)

