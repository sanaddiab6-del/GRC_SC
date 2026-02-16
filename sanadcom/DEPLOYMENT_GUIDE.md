# SICO GRC Platform: Production Deployment and Operations Guide

## Executive Summary

The SICO GRC Platform is a production-grade, fully on-premises, AI-powered Saudi regulatory compliance engine designed to standardize and automate compliance across the Essential Cybersecurity Controls (ECC), Cloud Computing Framework (CCC), and Personal Data Protection Law (PDPL) mandates issued by the National Cybersecurity Authority (NCA) of Saudi Arabia. This guide provides comprehensive instructions for deploying, configuring, and operating the platform in air-gapped, high-security environments such as banking, financial institutions, and government agencies.

## 1. System Architecture

The SICO GRC Platform consists of the following components:

| Component                  | Technology Stack                  | Purpose                                                                                                                                                                   |
| -------------------------- | --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Backend API**            | FastAPI (Python 3.11)             | RESTful API server providing compliance management, evidence collection, reporting, and AI-powered regulatory query capabilities.                                         |
| **Frontend Application**   | Next.js 14 (React, TypeScript)    | Bilingual (Arabic/English) web interface for compliance officers, auditors, and executives to interact with the platform.                                                 |
| **Database**               | PostgreSQL 15                     | Primary relational database storing control libraries, evidence records, audit logs, risk registers, and incident data.                                                   |
| **Cache Layer**            | Redis 7                           | High-performance caching layer for session management, rate limiting, and API response optimization.                                                                      |
| **Vector Database**        | ChromaDB                          | Specialized vector store for the on-premises RAG (Retrieval-Augmented Generation) system, enabling semantic search across regulatory frameworks in both Arabic and English. |
| **AI/RAG Engine**          | LangChain, Sentence Transformers  | On-premises AI system using the `intfloat/multilingual-e5-large` embedding model for bilingual compliance queries without external API dependencies.                      |

## 2. Pre-Deployment Requirements

### Hardware Requirements (Minimum)

For a production deployment supporting up to 100 concurrent users:

*   **CPU**: 8 cores (16 vCPUs recommended)
*   **RAM**: 32 GB (64 GB recommended for AI model loading)
*   **Storage**: 500 GB SSD (1 TB recommended for audit logs and evidence storage)
*   **Network**: 1 Gbps internal network, isolated from the public internet (air-gapped)

### Software Requirements

*   **Operating System**: Ubuntu 22.04 LTS or Red Hat Enterprise Linux 8+
*   **Container Runtime**: Docker 24.0+ and Docker Compose 2.20+
*   **Python**: 3.11 (for backend development and maintenance)
*   **Node.js**: 18.0+ (for frontend development and maintenance)

### Security Requirements (NCA ECC Compliance)

*   **TLS/HTTPS**: Valid TLS 1.3 certificates for all external-facing services (NCA ECC-IS-3)
*   **Encryption at Rest**: Full-disk encryption for all data volumes (PDPL Article 29)
*   **Encryption in Transit**: TLS 1.3 for all inter-service communication
*   **Access Control**: Role-Based Access Control (RBAC) with multi-factor authentication (MFA)
*   **Audit Logging**: Centralized audit logging with 7-year retention (NCA ECC-IS-5)
*   **Network Segmentation**: Isolated network segments for database, application, and presentation tiers

## 3. Deployment Steps

### Step 1: Clone the Repository

```bash
git clone <repository-url> /opt/sico-grc
cd /opt/sico-grc
```

### Step 2: Configure Environment Variables

Create a `.env` file in the root directory with the following production settings:

```bash
# Security (CRITICAL: Generate unique keys for production)
SECRET_KEY=$(openssl rand -hex 32)
ENCRYPTION_KEY=$(python3 -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())")

# Database
DATABASE_URL=postgresql://sico_user:STRONG_PASSWORD@postgres:5432/sico_grc
REDIS_URL=redis://redis:6379/0

# AI/RAG Configuration
EMBEDDING_MODEL=intfloat/multilingual-e5-large
VECTOR_DB_HOST=chroma
VECTOR_DB_PORT=8000

# Security Controls (NCA ECC-IS-3)
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
RATE_LIMIT_PER_HOUR=1000
TLS_ENABLED=true
TLS_CERT_PATH=/etc/ssl/certs/sico-grc.crt
TLS_KEY_PATH=/etc/ssl/private/sico-grc.key

# Audit Logging (NCA ECC-IS-5)
AUDIT_LOG_RETENTION_YEARS=7
AUDIT_LOG_STORAGE_PATH=/var/log/sico/audit
LOG_LEVEL=INFO

# Azure Key Vault (Optional, for centralized secrets management)
AZURE_KEY_VAULT_URL=https://your-keyvault.vault.azure.net/
AZURE_CLIENT_ID=your-client-id
AZURE_CLIENT_SECRET=your-client-secret
AZURE_TENANT_ID=your-tenant-id
```

### Step 3: Deploy with Docker Compose

```bash
# Start all services
docker compose -f deployment/docker-compose.yml up -d

# Verify all services are running
docker compose -f deployment/docker-compose.yml ps

# Check backend logs
docker compose -f deployment/docker-compose.yml logs -f backend

# Check frontend logs
docker compose -f deployment/docker-compose.yml logs -f frontend
```

### Step 4: Initialize the Database

```bash
# Run database migrations
docker compose -f deployment/docker-compose.yml exec backend alembic upgrade head

# Load initial control library data (ECC, CCC, PDPL)
docker compose -f deployment/docker-compose.yml exec backend python3 launch_init.py

# Load enterprise sample data (optional, for demonstration)
docker compose -f deployment/docker-compose.yml exec backend python3 load_enterprise_sample_data.py
```

### Step 5: Initialize the AI/RAG System

```bash
# Build the vector database index
docker compose -f deployment/docker-compose.yml exec backend python3 -c "
from ai.rag.bilingual_retriever import BilingualRetriever
retriever = BilingualRetriever()
print('Vector database initialized successfully')
"
```

### Step 6: Verify Deployment

Access the following URLs to verify the deployment:

*   **Frontend**: `https://your-domain:3000`
*   **Backend API Documentation**: `https://your-domain:8000/docs`
*   **Health Check**: `https://your-domain:8000/api/v1/health`

## 4. Post-Deployment Configuration

### User Management and RBAC

The platform supports five predefined roles:

| Role                  | Permissions                                                                                                                                                                   |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Admin**             | Full system access, including user management, system configuration, and all compliance operations.                                                                           |
| **Compliance Officer**| Create and update controls, upload evidence, manage findings, and generate reports.                                                                                           |
| **Auditor**           | Read-only access to all compliance data, with the ability to validate evidence and approve findings.                                                                          |
| **Analyst**           | Read-only access to dashboards, reports, and analytics.                                                                                                                       |
| **Viewer**            | Read-only access to public dashboards and reports.                                                                                                                            |

To create the first admin user:

```bash
docker compose -f deployment/docker-compose.yml exec backend python3 -c "
from auth.rbac_setup import initialize_rbac
from core.database import AsyncSessionLocal
import asyncio

async def create_admin():
    async with AsyncSessionLocal() as db:
        await initialize_rbac(db)
        print('Admin user created: admin@sico-grc.local')

asyncio.run(create_admin())
"
```

### TLS Certificate Configuration

For production deployments, replace the self-signed certificates with valid certificates from a trusted Certificate Authority (CA):

```bash
# Copy certificates to the backend container
docker cp /path/to/your/certificate.crt sico-backend:/etc/ssl/certs/sico-grc.crt
docker cp /path/to/your/private-key.key sico-backend:/etc/ssl/private/sico-grc.key

# Restart the backend service
docker compose -f deployment/docker-compose.yml restart backend
```

### Backup and Recovery

Implement a daily backup strategy for all critical data:

```bash
# Backup PostgreSQL database
docker compose -f deployment/docker-compose.yml exec postgres pg_dump -U postgres sico_grc > backup_$(date +%Y%m%d).sql

# Backup vector database
docker compose -f deployment/docker-compose.yml exec backend tar -czf /tmp/vectordb_backup.tar.gz /app/vectordb
docker cp sico-backend:/tmp/vectordb_backup.tar.gz ./vectordb_backup_$(date +%Y%m%d).tar.gz

# Backup audit logs
docker compose -f deployment/docker-compose.yml exec backend tar -czf /tmp/audit_logs_backup.tar.gz /var/log/sico/audit
docker cp sico-backend:/tmp/audit_logs_backup.tar.gz ./audit_logs_backup_$(date +%Y%m%d).tar.gz
```

## 5. Operational Monitoring

### Health Checks

The platform exposes health check endpoints for monitoring:

*   **Overall Health**: `GET /api/v1/health`
*   **Database Health**: Checked automatically by the health endpoint
*   **Redis Health**: Checked automatically by the health endpoint
*   **AI/RAG Health**: Checked automatically by the health endpoint

### Logging

All services log to `stdout` and `stderr`, which are captured by Docker. To access logs:

```bash
# View all logs
docker compose -f deployment/docker-compose.yml logs

# View backend logs only
docker compose -f deployment/docker-compose.yml logs backend

# Follow logs in real-time
docker compose -f deployment/docker-compose.yml logs -f
```

### Performance Metrics

Monitor the following metrics for optimal performance:

*   **API Response Time**: Should be < 200ms for 95% of requests
*   **Database Query Time**: Should be < 50ms for 95% of queries
*   **AI Query Time**: Should be < 2 seconds for 95% of RAG queries
*   **Memory Usage**: Backend should use < 8 GB, Frontend should use < 2 GB
*   **CPU Usage**: Should be < 70% under normal load

## 6. Troubleshooting

### Common Issues

| Issue                                      | Cause                                                                                           | Solution                                                                                                                                                                   |
| ------------------------------------------ | ----------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Backend fails to start                     | Missing or invalid `SECRET_KEY` or `ENCRYPTION_KEY`                                             | Verify that the `.env` file contains valid keys. Regenerate keys using the commands provided in Step 2.                                                                   |
| Frontend cannot connect to backend         | Incorrect `NEXT_PUBLIC_API_URL` environment variable                                            | Ensure `NEXT_PUBLIC_API_URL` is set to the correct backend URL (e.g., `https://your-domain:8000`).                                                                        |
| AI queries return 503 errors               | AI model not loaded or vector database not initialized                                          | Run the AI/RAG initialization command from Step 5. This may take several minutes on the first run as the embedding model is downloaded.                                   |
| Database migration fails                   | Database schema is out of sync or corrupted                                                     | Reset the database by running `docker compose down -v` (WARNING: This will delete all data) and then re-run the deployment steps.                                         |
| High memory usage                          | AI embedding model loaded into memory                                                           | This is expected behavior. The `intfloat/multilingual-e5-large` model requires approximately 4-6 GB of RAM. Ensure the host has sufficient memory.                        |

## 7. Security Hardening

### Network Security

*   **Firewall Rules**: Restrict access to ports 3000 (frontend), 8000 (backend), 5432 (database), 6379 (Redis), and 8001 (ChromaDB) to authorized IP ranges only.
*   **Reverse Proxy**: Deploy a reverse proxy (e.g., Nginx, HAProxy) in front of the frontend and backend to handle TLS termination and load balancing.
*   **Intrusion Detection**: Deploy an intrusion detection system (IDS) to monitor network traffic for suspicious activity.

### Application Security

*   **Rate Limiting**: The platform includes built-in rate limiting (60 requests/minute, 1000 requests/hour). Adjust these values in the `.env` file as needed.
*   **Input Validation**: All API endpoints perform strict input validation using Pydantic schemas.
*   **SQL Injection Protection**: The platform uses SQLAlchemy ORM with parameterized queries to prevent SQL injection attacks.
*   **XSS Protection**: The frontend uses React's built-in XSS protection and Content Security Policy (CSP) headers.

### Data Protection

*   **Field-Level Encryption**: Sensitive fields (e.g., PII) are encrypted at rest using AES-256 encryption (PDPL Article 29 compliance).
*   **Audit Logging**: All user actions are logged with timestamps, user IDs, and IP addresses for 7-year retention (NCA ECC-IS-5 compliance).
*   **Data Retention**: Implement automated data retention policies to delete or archive old evidence and audit logs according to organizational policies.

## 8. Compliance Alignment

The SICO GRC Platform is designed to meet the following regulatory requirements:

### NCA Essential Cybersecurity Controls (ECC)

*   **ECC-GV**: Governance controls for cybersecurity policies and procedures
*   **ECC-IS**: Information security controls, including access control (IS-3), incident response (IS-5), and audit logging
*   **ECC-RM**: Risk management framework for identifying, assessing, and mitigating cybersecurity risks
*   **ECC-BC**: Business continuity and disaster recovery planning

### NCA Cloud Computing Framework (CCC)

*   **CCC-SEC**: Cloud security controls for data protection, encryption, and access management
*   **CCC-GOV**: Cloud governance controls for vendor management and service level agreements
*   **CCC-COM**: Cloud compliance controls for regulatory reporting and audit readiness

### Personal Data Protection Law (PDPL)

*   **Article 6-8**: Consent management and lawful processing of personal data
*   **Article 27**: Data breach notification within 72 hours
*   **Article 29**: Technical and organizational measures for data protection, including encryption and pseudonymization

## 9. Support and Maintenance

### Regular Maintenance Tasks

*   **Weekly**: Review audit logs for suspicious activity
*   **Monthly**: Update Docker images to the latest versions
*   **Quarterly**: Conduct a full backup and disaster recovery test
*   **Annually**: Conduct a comprehensive security audit and penetration test

### Updating the Platform

To update the platform to a new version:

```bash
# Pull the latest code
cd /opt/sico-grc
git pull origin main

# Rebuild Docker images
docker compose -f deployment/docker-compose.yml build

# Run database migrations
docker compose -f deployment/docker-compose.yml exec backend alembic upgrade head

# Restart services
docker compose -f deployment/docker-compose.yml restart
```

## 10. Contact and Support

For technical support, please contact your internal IT support team or the platform development team. For regulatory compliance questions, consult with your organization's compliance officer or legal counsel.

---

**Document Version**: 1.0  
**Last Updated**: February 2026  
**Prepared by**: Manus AI
