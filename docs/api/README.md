# SICO GRC Platform API Documentation

## Base URL
```
http://localhost:8000
```

## API Documentation
- **Swagger UI**: http://localhost:8000/api/docs
- **ReDoc**: http://localhost:8000/api/redoc

## Authentication
Currently, the API does not require authentication (in development mode).
Production deployment will use JWT-based authentication.

## Endpoints

### Health & Status

#### GET /
Root endpoint with basic API information.

**Response**:
```json
{
  "name": "SICO GRC Platform API",
  "version": "0.1.0",
  "status": "operational",
  "frameworks": ["ECC", "CCC", "PDPL"]
}
```

#### GET /health
Health check endpoint for monitoring.

**Response**:
```json
{
  "status": "healthy",
  "service": "sico-grc-api"
}
```

### Frameworks

#### GET /api/v1/frameworks
List all supported regulatory frameworks.

**Response**:
```json
{
  "frameworks": [
    {
      "id": "ecc",
      "name": "Essential Cybersecurity Controls",
      "authority": "NCA - National Cybersecurity Authority",
      "version": "2.0",
      "controls_count": 114
    },
    ...
  ]
}
```

### Controls

#### GET /api/v1/controls/
List all controls with optional filters.

**Query Parameters**:
- `framework` (optional): Filter by framework (ecc, ccc, pdpl)
- `domain` (optional): Filter by domain
- `priority` (optional): Filter by priority (Critical, High, Medium, Low)

**Example**:
```bash
curl "http://localhost:8000/api/v1/controls/?framework=ecc&priority=Critical"
```

**Response**:
```json
[
  {
    "id": 1,
    "control_id": "ECC-1.1.1",
    "title": "Information Security Policy",
    "description": "Establish and maintain an information security policy",
    "framework": "ecc",
    "domain": "Cybersecurity Governance",
    "priority": "Critical",
    "implementation_status": "implemented"
  },
  ...
]
```

#### GET /api/v1/controls/{control_id}
Get a specific control by ID.

**Example**:
```bash
curl "http://localhost:8000/api/v1/controls/ECC-1.1.1"
```

**Response**:
```json
{
  "id": 1,
  "control_id": "ECC-1.1.1",
  "title": "Information Security Policy",
  "description": "Establish and maintain an information security policy",
  "framework": "ecc",
  "domain": "Cybersecurity Governance",
  "priority": "Critical",
  "implementation_status": "implemented"
}
```

### Assessments

#### GET /api/v1/assessments/
List all compliance assessments.

**Response**:
```json
[
  {
    "id": 1,
    "name": "Q1 2026 ECC Assessment",
    "framework": "ecc",
    "status": "in_progress",
    "compliance_score": 75.5,
    "created_at": "2026-02-04T13:00:00",
    "updated_at": "2026-02-04T13:00:00"
  },
  ...
]
```

#### GET /api/v1/assessments/dashboard
Get compliance dashboard summary with statistics.

**Response**:
```json
{
  "overall_compliance": 78.5,
  "frameworks": {
    "ecc": {
      "total_controls": 114,
      "implemented": 86,
      "in_progress": 20,
      "not_started": 8,
      "compliance_score": 75.4
    },
    ...
  },
  "recent_activities": [...]
}
```

## Error Responses

All endpoints return standard HTTP status codes:

- `200 OK`: Success
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

Error response format:
```json
{
  "error": "Error type",
  "detail": "Detailed error message"
}
```

## Rate Limiting
Currently not implemented. Will be added in production.

## CORS
CORS is enabled for development origins:
- http://localhost:3000
- http://localhost:8000

## Development

To start the API server:
```bash
cd src/backend
source venv/bin/activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000 with automatic reload on code changes.
