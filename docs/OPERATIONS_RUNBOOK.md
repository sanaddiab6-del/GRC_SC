# 🔧 SICO GRC Platform - Operations Runbook

## Emergency Contacts

| Role | Name | Phone | Email |
|------|------|-------|-------|
| **Primary On-Call** | [Name] | [Phone] | [Email] |
| **Secondary On-Call** | [Name] | [Phone] | [Email] |
| **Engineering Manager** | [Name] | [Phone] | [Email] |
| **Security Team** | [Name] | [Phone] | [Email] |
| **Database Admin** | [Name] | [Phone] | [Email] |

**Escalation Path**: On-Call → Manager → Director → CTO

---

## Service Overview

### Architecture

```
Load Balancer (443)
    ↓
Frontend (Next.js) + Backend (FastAPI)
    ↓
PostgreSQL + Redis + Chroma
```

### Critical Services

| Service | Port | Health Check | Recovery Time |
|---------|------|--------------|---------------|
| Frontend | 3000 | GET / | < 2 min |
| Backend API | 8000 | GET /api/v1/health | < 2 min |
| PostgreSQL | 5432 | pg_isready | < 5 min |
| Redis | 6379 | PING | < 1 min |
| Chroma | 8001 | GET /api/v1/heartbeat | < 2 min |

### SLAs

- **Uptime**: 99.9% (< 8.76 hours downtime/year)
- **Response Time**: < 500ms (95th percentile)
- **Recovery Time Objective (RTO)**: 1 hour
- **Recovery Point Objective (RPO)**: 4 hours

---

## Standard Operating Procedures

### 1. Service Restart

**When**: Service unresponsive, high memory usage, after config change

**Steps**:
```bash
# Check service status
docker compose ps

# Restart specific service
docker compose restart backend  # or frontend, postgres, redis, chroma

# Verify health
curl https://your-domain.com/api/v1/health

# Check logs
docker compose logs -f backend --tail=100
```

**Post-Restart Checks**:
- [ ] Health check returns 200 OK
- [ ] Users can login
- [ ] Database connections active
- [ ] No error spikes in logs

### 2. Database Backup

**Schedule**: Daily at 2 AM (automated via cron)

**Manual Backup**:
```bash
# Create backup
sudo /opt/sico-grc/scripts/backup.sh

# Verify backup
ls -lh /var/backups/sico/
gpg --list-packets /var/backups/sico/db-$(date +%Y%m%d)*.gpg

# Upload to offsite storage
aws s3 cp /var/backups/sico/ s3://your-backup-bucket/$(date +%Y%m%d)/ --recursive
```

**Backup Verification** (weekly):
```bash
# Test restore to staging
./scripts/restore_backup.sh db-20260210-020000.sql.gz --target=staging
```

### 3. Database Restore

**When**: Data corruption, accidental deletion, disaster recovery

**Steps**:
```bash
# 1. Stop application
docker compose stop backend frontend

# 2. Backup current state (if possible)
docker compose exec postgres pg_dump -U sico_admin sico_grc > /tmp/current_backup.sql

# 3. Identify backup file
ls -lh /var/backups/sico/ | grep db-

# 4. Restore backup
./scripts/restore_backup.sh /var/backups/sico/db-20260210-020000.sql.gz

# 5. Verify restoration
docker compose exec postgres psql -U sico_admin -d sico_grc -c "SELECT COUNT(*) FROM users;"

# 6. Start application
docker compose start backend frontend

# 7. Verify functionality
curl https://your-domain.com/api/v1/health
```

**Post-Restore Checks**:
- [ ] User count matches expected
- [ ] Recent data present
- [ ] Login works
- [ ] Control counts correct

### 4. Certificate Renewal

**When**: Certificate expires in < 30 days

**Steps**:
```bash
# 1. Check expiry
openssl x509 -in /etc/ssl/certs/sico-grc.crt -noout -dates

# 2. Renew with Let's Encrypt
sudo certbot renew --force-renewal

# 3. Copy renewed certificates
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem /etc/ssl/certs/sico-grc.crt
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem /etc/ssl/private/sico-grc.key
sudo chmod 600 /etc/ssl/private/sico-grc.key

# 4. Restart web server
sudo systemctl restart nginx

# 5. Verify certificate
echo | openssl s_client -connect your-domain.com:443 2>/dev/null | openssl x509 -noout -dates
```

### 5. Key Rotation (Quarterly)

**When**: Every 90 days (compliance requirement)

**Steps**:
```bash
# 1. Generate new keys
python3 scripts/production_setup.py --generate

# 2. Backup current .env
cp .env .env.backup.$(date +%Y%m%d)

# 3. Update .env with new keys from generated file
# Copy SECRET_KEY and ENCRYPTION_KEY from .env.production

# 4. Update Azure Key Vault (if used)
az keyvault secret set --vault-name your-vault --name SECRET-KEY --value "new-key"
az keyvault secret set --vault-name your-vault --name ENCRYPTION-KEY --value "new-key"

# 5. Rolling restart (zero downtime)
docker compose up -d --force-recreate --no-deps backend

# 6. Test functionality
curl -X POST https://your-domain.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"TestPass123!"}'

# 7. Monitor for issues
docker compose logs -f backend | grep -i error
```

**Rollback** (if issues):
```bash
cp .env.backup.YYYYMMDD .env
docker compose restart backend
```

### 6. Scaling Up

**When**: CPU > 80%, Memory > 80%, Response time > 1s

**Vertical Scaling** (increase resources):
```bash
# 1. Update docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '4'  # Increase from 2
          memory: 8G  # Increase from 4G

# 2. Recreate service
docker compose up -d --force-recreate backend
```

**Horizontal Scaling** (add replicas):
```bash
# 1. Update docker-compose.yml
services:
  backend:
    deploy:
      replicas: 3  # Add multiple instances

# 2. Configure load balancer
# Add backend instances to nginx upstream

# 3. Deploy
docker compose up -d --scale backend=3
```

### 7. Disk Space Management

**When**: Disk usage > 80%

**Steps**:
```bash
# 1. Check disk usage
df -h

# 2. Identify large directories
du -sh /* | sort -hr | head -10

# 3. Clean Docker artifacts
docker system prune -a --volumes

# 4. Clean old backups (keep 90 days)
find /var/backups/sico -name "*.gz" -mtime +90 -delete

# 5. Clean old logs
find /var/log/sico -name "*.log" -mtime +30 -delete

# 6. Rotate logs
sudo logrotate /etc/logrotate.d/sico-grc

# 7. Verify space freed
df -h
```

---

## Incident Response Procedures

### Severity Levels

| Severity | Definition | Response Time | Example |
|----------|------------|---------------|---------|
| **P0 - Critical** | Service down | 15 minutes | Complete outage |
| **P1 - High** | Major degradation | 1 hour | Database down |
| **P2 - Medium** | Minor degradation | 4 hours | Slow performance |
| **P3 - Low** | Cosmetic issue | 1 business day | UI glitch |

### P0 - Service Down

**Symptoms**: Users cannot access platform

**Initial Response** (within 15 minutes):
```bash
# 1. Acknowledge incident
echo "P0 incident at $(date)" | tee -a /var/log/sico/incidents.log

# 2. Check service status
docker compose ps
systemctl status nginx

# 3. Check logs for errors
docker compose logs --tail=100 backend | grep -i error
docker compose logs --tail=100 frontend | grep -i error

# 4. Attempt quick fix
docker compose restart backend frontend

# 5. Notify stakeholders
# Send email/SMS to management
```

**Investigation**:
```bash
# Check system resources
top
free -h
df -h

# Check network connectivity
ping your-database-host
telnet your-database-host 5432

# Check database
docker compose exec postgres psql -U sico_admin -d sico_grc -c "SELECT 1;"

# Check external dependencies
curl -I https://api.dga.gov.sa/pdpl
```

**Resolution Paths**:

1. **If backend crashed**:
   - Check logs for stack trace
   - Restart backend: `docker compose restart backend`
   - If persists, restore from backup

2. **If database unresponsive**:
   - Check connections: `docker compose exec postgres psql -U postgres -c "SELECT * FROM pg_stat_activity;"`
   - Kill long queries if needed
   - Restart PostgreSQL: `docker compose restart postgres`

3. **If TLS certificate expired**:
   - Renew certificate (see procedure above)
   - Restart nginx

**Post-Incident**:
- [ ] Document incident timeline
- [ ] Update runbook with lessons learned
- [ ] Schedule post-mortem meeting
- [ ] Implement preventive measures

### P1 - Database Connectivity Issues

**Symptoms**: Intermittent database errors

**Response**:
```bash
# 1. Check connection pool
docker compose exec backend python -c "
from src.backend.core.database import engine
print(engine.pool.status())
"

# 2. Check active connections
docker compose exec postgres psql -U postgres -c "
SELECT count(*) FROM pg_stat_activity;
"

# 3. Kill idle connections if pool exhausted
docker compose exec postgres psql -U postgres -c "
SELECT pg_terminate_backend(pid) 
FROM pg_stat_activity 
WHERE state = 'idle' AND state_change < now() - interval '10 minutes';
"

# 4. Increase pool size if needed
# Edit src/backend/core/database.py
# pool_size=20 → pool_size=40

# 5. Restart backend
docker compose restart backend
```

### P2 - High Memory Usage

**Symptoms**: Memory usage > 80%

**Response**:
```bash
# 1. Identify memory-intensive processes
docker stats --no-stream

# 2. Check for memory leaks
docker compose exec backend python -c "
import psutil
process = psutil.Process()
print(f'Memory: {process.memory_info().rss / 1024 / 1024:.2f} MB')
"

# 3. Restart highest memory consumer
docker compose restart backend  # or whichever service

# 4. Monitor memory after restart
watch -n 5 'docker stats --no-stream'

# 5. If persists, scale up resources
# See "Scaling Up" procedure above
```

### Security Incident Response

**When**: Suspected breach, unauthorized access, malware

**Immediate Actions** (within 1 hour):
```bash
# 1. Isolate affected systems
docker compose stop backend  # Stop accepting new connections

# 2. Preserve evidence
cp -r /var/log/sico /tmp/incident-$(date +%Y%m%d-%H%M%S)
docker compose exec postgres pg_dump sico_grc > /tmp/incident-db.sql

# 3. Review audit logs
docker compose exec postgres psql -U sico_admin -d sico_grc -c "
SELECT * FROM audit_logs 
WHERE timestamp > now() - interval '24 hours' 
ORDER BY timestamp DESC 
LIMIT 1000;
" > /tmp/incident-audit.log

# 4. Check for suspicious activity
grep "failed_login" /var/log/sico/audit/*.log | wc -l
grep "unauthorized" /var/log/sico/audit/*.log
```

**Investigation**:
1. Identify breach vector
2. Assess data exposure
3. Determine scope of compromise
4. Document timeline

**Remediation**:
```bash
# 1. Disable compromised accounts
docker compose exec backend python -c "
from src.backend.auth.models import User
# Disable user
"

# 2. Rotate all keys
python3 scripts/production_setup.py --generate
# Update .env and restart

# 3. Force password reset for all users
docker compose exec postgres psql -U sico_admin -d sico_grc -c "
UPDATE users SET password_must_change = TRUE;
"

# 4. Review and patch vulnerabilities
apt update && apt upgrade -y
docker compose pull  # Update images
```

**Notification** (within 72 hours - PDPL Article 27):
1. Notify SDAIA: https://sdaia.gov.sa
2. Inform affected data subjects
3. Report to management
4. Document in incident log

---

## Monitoring & Alerts

### Key Metrics

Monitor these metrics continuously:

| Metric | Threshold | Alert |
|--------|-----------|-------|
| API Response Time | > 1s | Warning |
| API Error Rate | > 1% | Critical |
| CPU Usage | > 80% | Warning |
| Memory Usage | > 80% | Warning |
| Disk Space | < 20% | Critical |
| Database Connections | > 90% pool | Warning |
| Failed Logins | > 10/min | Security |
| Backup Age | > 25 hours | Critical |

### Setting Up Alerts

**Prometheus Alerts**:
```yaml
# /etc/prometheus/alerts.yml
groups:
  - name: sico_grc_alerts
    rules:
      - alert: HighAPILatency
        expr: histogram_quantile(0.95, rate(http_request_duration_seconds_bucket[5m])) > 1
        for: 5m
        annotations:
          summary: "API response time > 1s"
          
      - alert: HighErrorRate
        expr: rate(http_requests_total{status=~"5.."}[5m]) > 0.01
        for: 5m
        annotations:
          summary: "Error rate > 1%"
          
      - alert: DatabaseConnectionPoolExhausted
        expr: database_connection_pool_usage > 0.9
        for: 2m
        annotations:
          summary: "Connection pool > 90%"
```

### Health Check Script

**Run every 5 minutes via cron**:
```bash
#!/bin/bash
# /opt/sico-grc/scripts/health_check.sh

# Check API health
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" https://your-domain.com/api/v1/health)
if [ $HTTP_CODE -ne 200 ]; then
    echo "ALERT: API health check failed (HTTP $HTTP_CODE)" | mail -s "SICO GRC Alert" ops@yourdomain.com
fi

# Check database
if ! docker compose exec -T postgres pg_isready -U sico_admin > /dev/null 2>&1; then
    echo "ALERT: Database health check failed" | mail -s "SICO GRC Alert" ops@yourdomain.com
fi

# Check disk space
DISK_USAGE=$(df -h / | awk 'NR==2 {print $5}' | sed 's/%//')
if [ $DISK_USAGE -gt 80 ]; then
    echo "ALERT: Disk usage at ${DISK_USAGE}%" | mail -s "SICO GRC Alert" ops@yourdomain.com
fi

# Check backup age
BACKUP_AGE=$(find /var/backups/sico -name "db-*.gz" -mtime -1 | wc -l)
if [ $BACKUP_AGE -eq 0 ]; then
    echo "ALERT: No recent backup found" | mail -s "SICO GRC Alert" ops@yourdomain.com
fi
```

---

## Maintenance Windows

### Scheduled Maintenance

**Frequency**: Monthly (first Sunday, 2 AM - 4 AM local time)

**Pre-Maintenance Checklist**:
- [ ] Announce maintenance window (72 hours advance notice)
- [ ] Create full backup
- [ ] Test rollback procedure
- [ ] Prepare rollback plan
- [ ] Notify on-call team

**Maintenance Tasks**:
1. Apply security patches
2. Update Docker images
3. Optimize database
4. Rotate logs
5. Review and clean up old data
6. Test backup restoration

**Post-Maintenance**:
- [ ] Verify all services healthy
- [ ] Run smoke tests
- [ ] Monitor for 1 hour
- [ ] Send completion notification

---

## Troubleshooting Common Issues

### Issue: "Connection pool exhausted"

**Cause**: Too many concurrent database connections

**Fix**:
```bash
# Increase pool size in config
# src/backend/core/database.py
pool_size=40  # Increase from 20
max_overflow=80  # Increase from 40

# Restart backend
docker compose restart backend
```

### Issue: "JWT token expired"

**Cause**: Token lifetime too short for user activity

**Fix**:
```bash
# Increase token expiry in .env
ACCESS_TOKEN_EXPIRE_MINUTES=60  # Increase from 30

# Restart backend
docker compose restart backend
```

### Issue: "Storage backend unreachable" (Chroma)

**Cause**: Chroma vector database unresponsive

**Fix**:
```bash
# Restart Chroma
docker compose restart chroma

# Verify health
curl http://localhost:8001/api/v1/heartbeat

# If data corrupted, rebuild from controls
docker compose exec backend python scripts/rebuild_vectordb.py
```

---

## Disaster Recovery

### Full System Recovery

**Scenario**: Complete data center failure

**Recovery Steps**:

1. **Provision new infrastructure** (2 hours):
   - New server with Ubuntu 22.04
   - Install Docker
   - Configure network/DNS

2. **Restore code** (30 minutes):
   ```bash
   git clone https://github.com/sonaiso/sanadcom.git /opt/sico-grc
   cd /opt/sico-grc
   ```

3. **Restore configuration** (15 minutes):
   - Copy .env from secure storage
   - Install TLS certificates

4. **Restore database** (1 hour):
   ```bash
   # Get latest backup from S3/Azure
   aws s3 cp s3://your-backup-bucket/latest/db.sql.gz /tmp/

   # Restore
   ./scripts/restore_backup.sh /tmp/db.sql.gz
   ```

5. **Start services** (15 minutes):
   ```bash
   docker compose up -d
   ```

6. **Verify recovery** (30 minutes):
   - Test login
   - Verify data integrity
   - Run smoke tests
   - Enable monitoring

**Total Recovery Time**: ~4 hours (within RTO)

---

**Document Version**: 1.0  
**Last Updated**: 2026-02-10  
**Review Schedule**: Quarterly
