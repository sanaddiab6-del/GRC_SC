# Deployment Configuration

## SICO GRC Platform Deployment

This directory contains deployment configurations for various environments and platforms.

## Supported Deployment Methods

### 1. Docker Compose (Development & Testing)
Simple multi-container deployment for local development.

**Files**:
- `docker-compose.yml` - Main compose configuration
- `docker-compose.override.yml` - Development overrides
- `docker-compose.prod.yml` - Production overrides

**Usage**:
```bash
# Development
docker-compose up -d

# Production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 2. Kubernetes (Production)
Scalable, highly-available production deployment.

**Files**:
- `kubernetes/` - K8s manifests
  - `namespace.yaml`
  - `configmap.yaml`
  - `secrets.yaml`
  - `backend-deployment.yaml`
  - `frontend-deployment.yaml`
  - `postgres-statefulset.yaml`
  - `redis-deployment.yaml`
  - `ingress.yaml`
  - `hpa.yaml` - Horizontal Pod Autoscaler

**Usage**:
```bash
# Apply configurations
kubectl apply -f kubernetes/

# Check status
kubectl get pods -n sico-grc

# Scale
kubectl scale deployment backend --replicas=3 -n sico-grc
```

### 3. Cloud Platforms

#### AWS
- ECS/Fargate for containers
- RDS for PostgreSQL
- ElastiCache for Redis
- S3 for file storage
- CloudFront for CDN
- ALB for load balancing

#### Azure
- AKS for Kubernetes
- Azure Database for PostgreSQL
- Azure Cache for Redis
- Azure Blob Storage
- Azure CDN
- Application Gateway

#### GCP
- GKE for Kubernetes
- Cloud SQL for PostgreSQL
- Memorystore for Redis
- Cloud Storage
- Cloud CDN
- Cloud Load Balancing

## Architecture Overview

```
                    ┌──────────────────────┐
                    │   Load Balancer      │
                    │   (Ingress/ALB)      │
                    └──────────┬───────────┘
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
    ┌──────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐
    │  Frontend   │    │  Frontend   │    │  Frontend   │
    │  (Next.js)  │    │  (Next.js)  │    │  (Next.js)  │
    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
           │                   │                   │
           └───────────────────┼───────────────────┘
                               │
                    ┌──────────▼───────────┐
                    │   API Gateway        │
                    └──────────┬───────────┘
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
    ┌──────▼──────┐    ┌──────▼──────┐    ┌──────▼──────┐
    │   Backend   │    │   Backend   │    │   Backend   │
    │  (FastAPI)  │    │  (FastAPI)  │    │  (FastAPI)  │
    └──────┬──────┘    └──────┬──────┘    └──────┬──────┘
           │                   │                   │
           └───────────────────┼───────────────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
         ┌──────▼──────┐ ┌────▼─────┐ ┌─────▼──────┐
         │ PostgreSQL  │ │  Redis   │ │  Vector DB │
         │  (Primary)  │ │ (Cache)  │ │  (Chroma)  │
         └─────────────┘ └──────────┘ └────────────┘
```

## Resource Requirements

### Minimum (Development)
- CPU: 4 cores
- RAM: 8 GB
- Storage: 50 GB
- Network: 100 Mbps

### Recommended (Small Production)
- CPU: 8 cores
- RAM: 16 GB
- Storage: 200 GB SSD
- Network: 1 Gbps
- Load Balancer: Yes
- Database: Managed service (RDS/Cloud SQL)

### Enterprise (Large Production)
- CPU: 32+ cores (across multiple nodes)
- RAM: 64+ GB
- Storage: 1+ TB SSD
- Network: 10 Gbps
- High Availability: Multi-AZ/Multi-region
- CDN: Yes
- Auto-scaling: Yes

## Environment-Specific Configuration

### Development
- Single-instance deployment
- SQLite or local PostgreSQL
- No SSL/TLS
- Debug mode enabled
- Mock external services

### Staging
- Multi-instance with load balancer
- Managed database
- SSL/TLS certificates
- Production-like configuration
- Limited external integrations

### Production
- High availability (multi-AZ)
- Managed databases with backups
- SSL/TLS with auto-renewal
- Monitoring and alerting
- Full external integrations
- DDoS protection
- WAF enabled

## Security Considerations

### Network Security
- Private subnets for databases
- Security groups/firewall rules
- VPN/private connectivity for admin access
- DDoS protection

### Data Security
- Encryption at rest (database, storage)
- Encryption in transit (TLS 1.3)
- Secrets management (Vault, AWS Secrets Manager)
- Regular security updates

### Access Control
- IAM/RBAC policies
- Principle of least privilege
- MFA for administrative access
- Audit logging

## Monitoring & Observability

### Metrics
- Prometheus for metrics collection
- Grafana for visualization
- Key metrics:
  - Request rate & latency
  - Error rate
  - CPU/Memory usage
  - Database connections
  - Cache hit rate

### Logging
- Centralized logging (ELK stack, CloudWatch)
- Structured logging (JSON format)
- Log retention policies
- Log levels per environment

### Alerting
- Critical: Page on-call engineer
- High: Notify team channel
- Medium: Email notification
- Low: Dashboard only

### Health Checks
- Liveness probes (is service running?)
- Readiness probes (is service ready to accept traffic?)
- Startup probes (has service completed initialization?)

## Backup & Disaster Recovery

### Database Backups
- Automated daily backups
- Point-in-time recovery (7-30 days)
- Cross-region replication for DR
- Regular backup testing

### Application Backups
- Configuration backups
- Uploaded files backup
- Vector database backups

### Recovery Time Objective (RTO)
- Development: 24 hours
- Staging: 4 hours
- Production: 1 hour

### Recovery Point Objective (RPO)
- Development: 24 hours
- Staging: 1 hour
- Production: 15 minutes

## Scaling Strategies

### Horizontal Scaling
- Application servers: Scale based on CPU/memory
- Auto-scaling groups
- Load balancer distribution

### Vertical Scaling
- Database: Scale instance size as needed
- Cache: Increase memory allocation

### Database Scaling
- Read replicas for read-heavy workloads
- Connection pooling (PgBouncer)
- Query optimization

## Deployment Process

### CI/CD Pipeline
```
Code Push → Build → Test → Security Scan → Deploy to Staging → 
Integration Tests → Manual Approval → Deploy to Production → 
Smoke Tests → Monitor
```

### Deployment Strategies

#### Blue-Green Deployment
- Zero-downtime deployments
- Quick rollback capability
- Higher resource cost

#### Rolling Deployment
- Gradual rollout
- Lower resource requirements
- Slower rollback

#### Canary Deployment
- Test with small percentage of traffic
- Gradual traffic shift
- Safe production testing

---

**Last Updated**: February 2026
