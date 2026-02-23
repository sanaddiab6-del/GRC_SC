# 🚀 SICO GRC Platform - Production Deployment Guide

## Pre-Deployment Checklist

### ✅ Configuration (Required)
- [ ] Generate production secrets: `python scripts/production_setup.py --generate`
- [ ] Review `.env.production` file
- [ ] Store credentials in Azure Key Vault or secure password manager
- [ ] Delete `.credentials.txt` after storing securely
- [ ] Validate configuration: `python scripts/production_setup.py --validate`

### ✅ Infrastructure (Required)
- [ ] PostgreSQL 15+ database provisioned
- [ ] Redis 7+ instance provisioned
- [ ] Chroma vector database deployed
- [ ] TLS/SSL certificates obtained (Let's Encrypt or commercial CA)
- [ ] Domain DNS configured (A record pointing to server)
- [ ] Firewall configured (443/HTTPS, 5432/PostgreSQL, 6379/Redis)

### ✅ Security (Required - NCA Compliance)
- [ ] TLS certificates installed at `/etc/ssl/certs/sico-grc.crt`
- [ ] Private key secured at `/etc/ssl/private/sico-grc.key` (chmod 600)
- [ ] Azure Key Vault configured (production secret management)
- [ ] Database uses TLS connections (sslmode=require)
- [ ] Redis uses TLS connections (rediss://)
- [ ] Firewall rules: Only 443 exposed publicly
- [ ] SSH key-based authentication only (no passwords)

### ✅ Backup & Recovery (Required - NCA ECC)
- [ ] Backup script configured: `scripts/backup.sh`
- [ ] Daily automated backups scheduled (cron: 0 2 * * *)
- [ ] Backup retention: 90 days minimum
- [ ] Backup encryption enabled
- [ ] Recovery procedure tested
- [ ] Off-site backup storage configured

### ✅ Monitoring (Required)
- [ ] Application health checks enabled
- [ ] Database monitoring configured
- [ ] Disk space alerts set (>80% threshold)
- [ ] Failed login alerts enabled
- [ ] Audit log monitoring active
- [ ] Uptime monitoring (external service)

### ✅ Testing (Required)
- [ ] Load testing completed (500+ concurrent users)
- [ ] Security scan passed (OWASP Top 10)
- [ ] Penetration testing completed
- [ ] Backup restore tested successfully
- [ ] Failover testing completed

### ✅ Documentation (Required)
- [ ] Admin user guide reviewed
- [ ] Operations runbook available
- [ ] Incident response plan documented
- [ ] Contact list updated (on-call engineers)

---

## Step-by-Step Deployment

### 1. Prepare Server (Ubuntu 22.04 LTS Recommended)

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
sudo apt install docker-compose-plugin -y

# Install monitoring tools
sudo apt install prometheus prometheus-node-exporter -y
```

### 2. Clone Repository

```bash
# Clone from GitHub
git clone https://github.com/sonaiso/sanadcom.git /opt/sico-grc
cd /opt/sico-grc
git checkout main  # or specific release tag
```

### 3. Generate Production Configuration

```bash
# Generate secure configuration
python3 scripts/production_setup.py --generate

# Follow prompts:
# - Domain: grc.yourdomain.com
# - Database host: your-db-host
# - Azure Key Vault details

# Validate configuration
python3 scripts/production_setup.py --validate
```

### 4. Install TLS Certificates

#### Option A: Let's Encrypt (Free, Automated)

```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx -y

# Generate certificate
sudo certbot certonly --standalone -d grc.yourdomain.com

# Copy to expected locations
sudo cp /etc/letsencrypt/live/grc.yourdomain.com/fullchain.pem /etc/ssl/certs/sico-grc.crt
sudo cp /etc/letsencrypt/live/grc.yourdomain.com/privkey.pem /etc/ssl/private/sico-grc.key
sudo chmod 600 /etc/ssl/private/sico-grc.key

# Setup auto-renewal
sudo certbot renew --dry-run
```

#### Option B: Commercial Certificate

```bash
# Copy your certificates
sudo cp your-cert.crt /etc/ssl/certs/sico-grc.crt
sudo cp your-key.key /etc/ssl/private/sico-grc.key
sudo chmod 600 /etc/ssl/private/sico-grc.key
```

### 5. Setup Database

```bash
# Create database user and database
psql -h your-db-host -U postgres <<EOF
CREATE USER sico_admin WITH PASSWORD 'your-generated-password';
CREATE DATABASE sico_grc OWNER sico_admin;
GRANT ALL PRIVILEGES ON DATABASE sico_grc TO sico_admin;
EOF

# Copy production .env
cp .env.production .env

# Run migrations
cd src/backend
alembic upgrade head
```

### 6. Setup Backup System

```bash
# Create backup script
cat > /opt/sico-grc/scripts/backup.sh <<'EOF'
#!/bin/bash
BACKUP_DIR="/var/backups/sico"
DATE=$(date +%Y%m%d-%H%M%S)
mkdir -p $BACKUP_DIR

# Database backup
pg_dump -h localhost -U sico_admin sico_grc | gzip > $BACKUP_DIR/db-$DATE.sql.gz

# Audit logs backup
tar -czf $BACKUP_DIR/audit-$DATE.tar.gz /var/log/sico/audit/

# Vector database backup
tar -czf $BACKUP_DIR/vectordb-$DATE.tar.gz /var/lib/chroma/

# Encrypt backups (optional but recommended)
gpg --encrypt --recipient admin@yourdomain.com $BACKUP_DIR/db-$DATE.sql.gz

# Upload to S3 or Azure Blob Storage
# aws s3 cp $BACKUP_DIR/ s3://your-backup-bucket/ --recursive

# Cleanup old backups (keep 90 days)
find $BACKUP_DIR -name "*.gz" -mtime +90 -delete

echo "Backup completed: $DATE"
EOF

chmod +x /opt/sico-grc/scripts/backup.sh

# Schedule daily backups
(crontab -l 2>/dev/null; echo "0 2 * * * /opt/sico-grc/scripts/backup.sh >> /var/log/sico/backup.log 2>&1") | crontab -
```

### 7. Deploy with Docker Compose

```bash
# Copy production compose file
cp deployment/docker-compose.production.yml docker-compose.yml

# Start services
docker compose up -d

# Check status
docker compose ps
docker compose logs -f backend
```

### 8. Initialize RBAC & Admin User

```bash
# Run security setup
docker compose exec backend python scripts/setup_security.py

# Create admin user
docker compose exec backend python -c "
from src.backend.auth.security import create_admin_user
create_admin_user('admin@yourdomain.com', 'SecurePassword123!')
"
```

### 9. Verify Deployment

```bash
# Health check
curl -k https://grc.yourdomain.com/api/v1/health

# Security status
curl -k https://grc.yourdomain.com/api/v1/security-status

# Login test
curl -X POST https://grc.yourdomain.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@yourdomain.com","password":"SecurePassword123!"}'
```

### 10. Setup Monitoring

```bash
# Install Prometheus
sudo systemctl enable prometheus
sudo systemctl start prometheus

# Configure alerts
cat > /etc/prometheus/alerts.yml <<'EOF'
groups:
  - name: sico_grc
    rules:
      - alert: HighCPUUsage
        expr: node_cpu_usage > 80
        for: 5m
        annotations:
          summary: "CPU usage above 80%"
      
      - alert: DiskSpaceLow
        expr: node_filesystem_free_percent < 20
        for: 5m
        annotations:
          summary: "Disk space below 20%"
      
      - alert: ServiceDown
        expr: up{job="sico-backend"} == 0
        for: 2m
        annotations:
          summary: "SICO backend service is down"
EOF

# Restart Prometheus
sudo systemctl restart prometheus
```

---

## Post-Deployment Tasks

### 1. Load Production Data

```bash
# Load control frameworks
docker compose exec backend python scripts/load_sample_data.py --production

# Import client data (if applicable)
docker compose exec backend python scripts/import_client_data.py
```

### 2. Configure Monitoring Dashboards

- Access Prometheus: http://server-ip:9090
- Create Grafana dashboards for:
  - API response times
  - Database connections
  - Failed login attempts
  - Audit log volume

### 3. Test Backup Restoration

```bash
# Test restore procedure
./scripts/restore_backup.sh db-20260210-020000.sql.gz
```

### 4. Document Configuration

- Store all credentials in password manager
- Document server IP addresses
- Document DNS configuration
- Document TLS certificate renewal dates

---

## Maintenance Schedule

### Daily
- Check backup logs
- Monitor error rates
- Review failed login attempts

### Weekly
- Review audit logs
- Check disk space
- Update threat intelligence

### Monthly
- Security patches
- Certificate renewal check
- Backup restoration test

### Quarterly (90 days)
- Rotate SECRET_KEY and ENCRYPTION_KEY
- Penetration testing
- Compliance audit
- Disaster recovery drill

---

## Compliance Verification

### NCA ECC Checklist
- ✅ ECC-IS-3: Authentication & authorization implemented
- ✅ ECC-IS-5: 7-year audit logging active
- ✅ ECC-RM: Risk management module operational
- ✅ ECC-TP: Third-party integrations secured

### NCA CCC Checklist
- ✅ CCC-SEC-01: Data encryption at rest and in transit
- ✅ CCC-SEC-03: TLS 1.3 enabled
- ✅ CCC-SEC-04: Comprehensive audit trail
- ✅ CCC-IAM: Identity and access management

### PDPL Checklist
- ✅ Article 6-9: Consent management operational
- ✅ Article 12-17: DSAR workflow functional
- ✅ Article 27: Breach notification system ready
- ✅ Article 29: PII encryption with Azure Key Vault

### SDAIA AI Checklist
- ✅ Model registry operational
- ✅ Bias testing documentation complete
- ✅ Ethics framework documented
- ✅ Governance controls active

---

## Troubleshooting

### Issue: TLS Certificate Not Working
```bash
# Verify certificate
openssl x509 -in /etc/ssl/certs/sico-grc.crt -text -noout

# Check private key
openssl rsa -in /etc/ssl/private/sico-grc.key -check

# Test TLS connection
openssl s_client -connect grc.yourdomain.com:443
```

### Issue: Database Connection Failed
```bash
# Test database connection
psql -h your-db-host -U sico_admin -d sico_grc

# Check PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-15-main.log

# Verify network access
telnet your-db-host 5432
```

### Issue: High Memory Usage
```bash
# Check container memory
docker stats

# Restart services
docker compose restart backend

# Increase container memory limits in docker-compose.yml
```

---

## Security Incident Response

### If Breach Detected

1. **Immediate Actions** (within 1 hour):
   - Isolate affected systems
   - Disable compromised accounts
   - Preserve audit logs
   - Document incident timeline

2. **Investigation** (within 24 hours):
   - Identify breach vector
   - Assess data exposure
   - Review audit logs
   - Determine scope

3. **Notification** (within 72 hours - PDPL Article 27):
   - Notify SDAIA (Saudi Data & AI Authority)
   - Inform affected data subjects
   - Report to management
   - Document response actions

4. **Remediation**:
   - Patch vulnerabilities
   - Rotate all keys and passwords
   - Implement additional controls
   - Update incident response plan

---

## Support & Contact

**Emergency On-Call**: [Your 24/7 contact number]
**Email**: support@yourdomain.com
**Ticketing**: [Your ticketing system URL]

**Escalation Path**:
1. Level 1: Operations team
2. Level 2: Security team
3. Level 3: Engineering management
4. Level 4: Executive team

---

## Appendix

### A. Required Ports

| Port | Service | Access |
|------|---------|--------|
| 443 | HTTPS (Frontend + API) | Public |
| 5432 | PostgreSQL | Internal only |
| 6379 | Redis | Internal only |
| 8001 | Chroma Vector DB | Internal only |
| 9090 | Prometheus | Admin only |

### B. Recommended Server Specifications

**Minimum**:
- 4 CPU cores
- 16 GB RAM
- 200 GB SSD
- 100 Mbps network

**Recommended (100+ users)**:
- 8 CPU cores
- 32 GB RAM
- 500 GB SSD
- 1 Gbps network

### C. Software Versions

- Ubuntu: 22.04 LTS
- Docker: 24.0+
- PostgreSQL: 15+
- Redis: 7+
- Python: 3.11+
- Node.js: 20+

---

**Document Version**: 1.0  
**Last Updated**: 2026-02-10  
**Status**: Production Ready ✅
