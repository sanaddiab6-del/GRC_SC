# Sanadcom GRC Platform — Production Deployment Guide

This guide covers everything needed to deploy the Sanadcom GRC Platform on a live server (not localhost). It explains the Python/Django backend structure, required environment variables, Docker-based deployment, and post-deployment configuration.

---

## Table of Contents

1. [Architecture Overview](#1-architecture-overview)
2. [Python Backend Structure](#2-python-backend-structure)
3. [Prerequisites](#3-prerequisites)
4. [Server Setup](#4-server-setup)
5. [Environment Configuration](#5-environment-configuration)
6. [Docker Deployment](#6-docker-deployment)
7. [DNS & TLS Configuration](#7-dns--tls-configuration)
8. [First-Run Initialisation](#8-first-run-initialisation)
9. [Post-Deployment Checklist](#9-post-deployment-checklist)
10. [Maintenance & Upgrades](#10-maintenance--upgrades)

---

## 1. Architecture Overview

```
                  Internet
                     │
             ┌───────▼───────┐
             │   Caddy 2.x   │  TLS termination + reverse proxy
             │  (port 443)   │
             └──────┬────────┘
           ┌────────┴────────┐
           ▼                 ▼
  ┌──────────────┐   ┌──────────────┐
  │   Frontend   │   │   Backend    │
  │  SvelteKit   │   │  Django 6 /  │
  │  (port 3000) │   │  Gunicorn    │
  └──────────────┘   │  (port 8000) │
                     └──────┬───────┘
                            │
                   ┌────────┴────────┐
                   ▼                 ▼
          ┌──────────────┐  ┌──────────────┐
          │  PostgreSQL  │  │     Huey     │
          │  (port 5432) │  │  (task queue)│
          └──────────────┘  └──────────────┘
```

All four services (`backend`, `frontend`, `postgres`, `huey`) plus the Caddy reverse proxy are orchestrated via **Docker Compose**.

---

## 2. Python Backend Structure

```
backend/
├── manage.py                  # Django management entry point
├── pyproject.toml             # Poetry dependencies (Python ≥ 3.14)
├── poetry.lock
├── startup.sh                 # Entrypoint: migrate → load libraries → gunicorn
├── Dockerfile
│
├── ciso_assistant/            # Django project package
│   ├── settings.py            # All runtime config (reads from env vars)
│   ├── urls.py                # Root URL dispatcher
│   ├── wsgi.py                # Gunicorn/WSGI entry point
│   ├── asgi.py                # ASGI entry point (websockets/async)
│   └── meta.py                # Version / schema metadata
│
├── iam/                       # Identity & access management
├── core/                      # Shared base models and utilities
├── library/                   # Compliance framework library loader
├── controls/                  # Control management domain
├── evidence/                  # Evidence collection domain
├── notifications/             # Alerting & notifications
├── integrations/              # Third-party integrations (Jira, S3, …)
├── webhooks/                  # Outbound webhooks
├── serdes/                    # Serialisation / deserialisation helpers
└── scripts/                   # One-off management scripts
```

### Key Python runtime components

| Component | Technology | Purpose |
|-----------|-----------|---------|
| Web framework | Django 6 | ORM, auth, admin, REST |
| API layer | Django REST Framework + drf-spectacular | RESTful JSON API + OpenAPI docs |
| Authentication | django-allauth + knox + simplejwt | Session, token, MFA, SAML |
| Task queue | Huey (Redis-backed) | Async jobs, scheduled tasks |
| Web server | Gunicorn (WSGI) | Production HTTP server |
| Database | PostgreSQL 16 via psycopg2 | Primary data store |
| PDF export | WeasyPrint | Compliance reports |
| Storage | django-storages + boto3 | S3-compatible file storage |
| Dependency manager | Poetry 2.x | Reproducible installs |

---

## 3. Prerequisites

Ensure the target server has:

- **OS**: Ubuntu 22.04 LTS or Debian 12 (recommended)
- **Docker Engine** ≥ 24 — [install guide](https://docs.docker.com/engine/install/)
- **Docker Compose plugin** ≥ 2.20 (`docker compose version`)
- **Git**
- A **domain name** pointed at the server's public IP (e.g. `grc.yourdomain.com`)
- Ports **80** and **443** open in your firewall/security group

```bash
# Verify on the server
docker --version
docker compose version
```

---

## 4. Server Setup

### 4.1 Clone the repository

```bash
git clone https://github.com/your-org/sanadcom.git /opt/sanadcom
cd /opt/sanadcom
```

### 4.2 Create a persistent data directory

```bash
mkdir -p /opt/sanadcom/db
```

The `db/` directory is bind-mounted into the backend container and persists:
- `django_secret_key` — auto-generated on first run
- SQLite fallback (only used if PostgreSQL is not configured)

---

## 5. Environment Configuration

Copy and edit the environment file **before** starting any containers.

```bash
cp .env.example .env   # or create .env from scratch (see below)
nano .env
```

### Minimum required variables for production

```env
# ── Application URL (MUST match your real domain + port) ──────────────────────
CISO_ASSISTANT_URL=https://grc.yourdomain.com

# ── Django ────────────────────────────────────────────────────────────────────
DJANGO_SECRET_KEY=<generate with: python -c "import secrets; print(secrets.token_urlsafe(64))">
DJANGO_DEBUG=False
ALLOWED_HOSTS=grc.yourdomain.com,backend,localhost

# ── Database ──────────────────────────────────────────────────────────────────
POSTGRES_NAME=ciso-assistant
POSTGRES_USER=ciso-assistantuser
POSTGRES_PASSWORD=<strong-random-password>
DB_HOST=postgres
DB_PORT=5432

# ── Initial superuser (created on first run, remove after) ────────────────────
DJANGO_SUPERUSER_EMAIL=admin@yourdomain.com
DJANGO_SUPERUSER_PASSWORD=<strong-initial-password>

# ── Frontend ──────────────────────────────────────────────────────────────────
PUBLIC_BACKEND_API_URL=http://backend:8000/api
PUBLIC_BACKEND_API_EXPOSED_URL=https://grc.yourdomain.com/api
PROTOCOL_HEADER=x-forwarded-proto
HOST_HEADER=x-forwarded-host

# ── Optional: S3-compatible file storage ──────────────────────────────────────
# AWS_ACCESS_KEY_ID=
# AWS_SECRET_ACCESS_KEY=
# AWS_STORAGE_BUCKET_NAME=
# AWS_S3_ENDPOINT_URL=
```

> **Security note**: Never commit `.env` to version control. Add it to `.gitignore`.

---

## 6. Docker Deployment

### 6.1 Update `docker-compose.yml` for production

Open `docker-compose.yml` and change the following service-level environment variables so they reference your `.env` file values instead of hard-coded defaults:

```yaml
backend:
  environment:
    - ALLOWED_HOSTS=${ALLOWED_HOSTS}
    - CISO_ASSISTANT_URL=${CISO_ASSISTANT_URL}
    - DJANGO_SECRET_KEY=${DJANGO_SECRET_KEY}
    - DJANGO_DEBUG=${DJANGO_DEBUG}
    - POSTGRES_NAME=${POSTGRES_NAME}
    - POSTGRES_USER=${POSTGRES_USER}
    - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
    - DB_HOST=${DB_HOST}
    - DB_PORT=${DB_PORT}
    - DJANGO_SUPERUSER_EMAIL=${DJANGO_SUPERUSER_EMAIL}
    - DJANGO_SUPERUSER_PASSWORD=${DJANGO_SUPERUSER_PASSWORD}

postgres:
  environment:
    - POSTGRES_DB=${POSTGRES_NAME}
    - POSTGRES_USER=${POSTGRES_USER}
    - POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
```

### 6.2 Update Caddy for your real domain

Replace the `caddy` service command in `docker-compose.yml` (or create a `Caddyfile`) with your real domain. Caddy will automatically obtain a Let's Encrypt TLS certificate:

```caddyfile
grc.yourdomain.com {
    reverse_proxy /api/* backend:8000
    reverse_proxy /* frontend:3000
}
```

Or pass it through the `CISO_ASSISTANT_URL` environment variable — the Docker Compose `caddy` service reads `$$CISO_ASSISTANT_URL` and builds the Caddyfile dynamically.

```env
# In .env
CISO_ASSISTANT_URL=https://grc.yourdomain.com
```

For automatic TLS, Caddy requires port 80 to be reachable (for the ACME HTTP-01 challenge). Make sure port 80 is open. Update the `caddy` service ports accordingly:

```yaml
caddy:
  ports:
    - "80:80"
    - "443:443"
```

### 6.3 Build and start all services

```bash
cd /opt/sanadcom

# Pull or build images
docker compose pull          # if using pre-built images from a registry
# — OR —
docker compose build         # to build locally from source

# Start all services in detached mode
docker compose up -d
```

### 6.4 Monitor startup

```bash
# Follow logs for all services
docker compose logs -f

# Check health of backend specifically
docker compose ps
```

The backend runs database migrations and loads all compliance libraries automatically on first start (via `startup.sh`). This can take **2–5 minutes** on first boot.

---

## 7. DNS & TLS Configuration

### Public DNS

Create an **A record** in your DNS provider pointing your domain to the server's public IP:

```
grc.yourdomain.com.  A  <server-public-ip>
```

### TLS — Automatic (recommended)

Caddy obtains a free Let's Encrypt certificate automatically when:
1. The domain resolves to the server
2. Port 80 is open (for ACME challenge)
3. Port 443 is open (for HTTPS traffic)

No manual certificate management needed.

### TLS — Custom Certificate

If you have an internally-issued or wildcard certificate, mount it into the Caddy container:

```yaml
caddy:
  volumes:
    - ./caddy_data:/data
    - /path/to/cert.pem:/certs/cert.pem:ro
    - /path/to/key.pem:/certs/key.pem:ro
```

Then reference it in the Caddyfile:

```caddyfile
grc.yourdomain.com {
    reverse_proxy /api/* backend:8000
    reverse_proxy /* frontend:3000
    tls /certs/cert.pem /certs/key.pem
}
```

---

## 8. First-Run Initialisation

Once services are healthy, create the initial superuser:

```bash
docker compose exec backend poetry run python manage.py createsuperuser
```

Or, if you set `DJANGO_SUPERUSER_EMAIL` and `DJANGO_SUPERUSER_PASSWORD` in `.env`, the account is created automatically by `startup.sh`. **Remove those variables from `.env` after the first successful start** to prevent accidental recreation.

Access the platform at `https://grc.yourdomain.com`.

---

## 9. Post-Deployment Checklist

- [ ] `DJANGO_DEBUG=False` is set in production
- [ ] `DJANGO_SECRET_KEY` is a strong, unique random value (≥ 50 chars)
- [ ] `POSTGRES_PASSWORD` is strong and not the default
- [ ] `DJANGO_SUPERUSER_EMAIL` / `DJANGO_SUPERUSER_PASSWORD` removed from `.env` after first run
- [ ] HTTPS is working and the certificate is valid (`curl -I https://grc.yourdomain.com`)
- [ ] Port 8000 is **not** exposed directly to the internet (only Caddy on 80/443)
- [ ] PostgreSQL port 5432 is **not** exposed to the internet (`docker compose ps` — no `0.0.0.0:5432` binding)
- [ ] Firewall allows only ports 80 and 443 inbound
- [ ] Database backups are scheduled (see Maintenance section)
- [ ] Log rotation is configured

---

## 10. Maintenance & Upgrades

### Database backup

```bash
# Dump PostgreSQL database
docker compose exec postgres pg_dump \
  -U ciso-assistantuser ciso-assistant \
  > backup-$(date +%Y%m%d-%H%M%S).sql

# Restore
docker compose exec -T postgres psql \
  -U ciso-assistantuser ciso-assistant < backup-YYYYMMDD-HHMMSS.sql
```

### Upgrade to a new version

```bash
cd /opt/sanadcom
git pull origin main

# Rebuild and restart
docker compose build
docker compose up -d

# Migrations run automatically via startup.sh
# Monitor:
docker compose logs -f backend
```

### Run Django management commands

```bash
# Example: collect static files
docker compose exec backend poetry run python manage.py collectstatic --noinput

# Example: load a library manually
docker compose exec backend poetry run python manage.py storelibraries
```

### View running services

```bash
docker compose ps
docker compose stats
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---------|-------------|-----|
| Backend health check fails | DB not ready yet | Wait 2–5 min; check `docker compose logs postgres` |
| `ALLOWED_HOSTS` error | Domain not in `ALLOWED_HOSTS` | Add domain to `ALLOWED_HOSTS` env var |
| TLS certificate not issued | Port 80 blocked | Open port 80 in firewall/security group |
| 502 Bad Gateway | Backend container down | `docker compose restart backend` |
| Static files 404 | `DJANGO_DEBUG=False` without collectstatic | Run `collectstatic` (see above) |
| Cannot login | Superuser not created | Run `createsuperuser` command above |

---

*For internal architecture details see [TECHNICAL_REPORT.md](TECHNICAL_REPORT.md). For security policies see [SECURITY.md](SECURITY.md).*
