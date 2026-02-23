# Source Code

## SICO GRC Platform - Application Code

This directory contains the application source code for the SICO GRC Platform.

## Structure

```
src/
├── backend/           # FastAPI backend application
├── frontend/          # Next.js frontend application
└── shared/            # Shared utilities and types
```

## Backend (`/backend`)

**Technology**: FastAPI + Python 3.11+

### Directory Structure
```
backend/
├── app/
│   ├── api/              # API routes
│   │   ├── v1/
│   │   │   ├── controls.py
│   │   │   ├── evidence.py
│   │   │   ├── compliance.py
│   │   │   ├── reports.py
│   │   │   └── ai.py
│   ├── core/             # Core functionality
│   │   ├── config.py
│   │   ├── security.py
│   │   └── database.py
│   ├── models/           # Database models
│   │   ├── control.py
│   │   ├── evidence.py
│   │   ├── user.py
│   │   └── audit.py
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   │   ├── control_service.py
│   │   ├── evidence_service.py
│   │   ├── ai_service.py
│   │   └── report_service.py
│   └── utils/            # Utility functions
├── alembic/              # Database migrations
├── tests/                # Test suite
├── requirements.txt      # Python dependencies
└── main.py               # Application entry point
```

### Key Features
- RESTful API endpoints
- Authentication & authorization (JWT)
- Database ORM (SQLAlchemy)
- Background tasks (Celery)
- API documentation (OpenAPI/Swagger)

### Setup
```bash
cd src/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

### Testing
```bash
pytest tests/
```

---

## Frontend (`/frontend`)

**Technology**: Next.js 14 + TypeScript

### Directory Structure
```
frontend/
├── src/
│   ├── app/              # Next.js App Router
│   │   ├── (auth)/       # Authentication pages
│   │   ├── (dashboard)/  # Dashboard pages
│   │   │   ├── controls/
│   │   │   ├── evidence/
│   │   │   ├── compliance/
│   │   │   ├── reports/
│   │   │   └── settings/
│   │   ├── layout.tsx
│   │   └── page.tsx
│   ├── components/       # React components
│   │   ├── ui/           # shadcn/ui components
│   │   ├── controls/     # Control-related components
│   │   ├── evidence/     # Evidence-related components
│   │   ├── charts/       # Chart components
│   │   └── layout/       # Layout components
│   ├── lib/              # Utilities
│   │   ├── api.ts        # API client
│   │   ├── utils.ts      # Helper functions
│   │   └── auth.ts       # Auth utilities
│   ├── hooks/            # Custom React hooks
│   ├── types/            # TypeScript types
│   └── styles/           # Global styles
├── public/               # Static assets
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── next.config.js
```

### Key Features
- Server-side rendering (SSR)
- Client-side routing
- Responsive design (mobile-first)
- Bilingual support (AR/EN)
- Real-time updates
- Interactive dashboards

### Setup
```bash
cd src/frontend
npm install
npm run dev
```

### Build
```bash
npm run build
npm start
```

---

## Shared (`/shared`)

Shared code between backend and frontend.

### Contents
- TypeScript type definitions
- Common utilities
- Validation schemas
- Constants and enums

---

## Development Workflow

### 1. Local Development
```bash
# Terminal 1: Backend
cd src/backend
uvicorn app.main:app --reload

# Terminal 2: Frontend
cd src/frontend
npm run dev

# Terminal 3: Database & Cache (Docker)
docker-compose up postgres redis
```

### 2. Testing
```bash
# Backend tests
cd src/backend && pytest

# Frontend tests
cd src/frontend && npm test
```

### 3. Linting
```bash
# Backend
cd src/backend && pylint app/

# Frontend
cd src/frontend && npm run lint
```

## API Documentation

Once the backend is running, access interactive API docs at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

### Backend
```bash
# Database
DATABASE_URL=postgresql://user:pass@localhost:5432/sico_grc
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI/ML
OPENAI_API_KEY=your_openai_key
VECTOR_DB_PATH=/data/vector_db

# External Integrations
SMTP_HOST=smtp.example.com
SMTP_PORT=587
```

### Frontend
```bash
# API
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_WS_URL=ws://localhost:8000

# Features
NEXT_PUBLIC_ENABLE_AI=true
NEXT_PUBLIC_ENABLE_SOC_BRIDGE=true
```

## Deployment

See `/deployment` directory for Docker and Kubernetes configurations.

---

**Last Updated**: February 2026
