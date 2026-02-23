# SICO GRC Platform - API Reference

## Base URL
```
Development: http://localhost:8000
Production: https://api.sico-grc.sa (future)
```

## Authentication
All endpoints except health checks require JWT authentication.

```bash
Authorization: Bearer <token>
```

## Common Headers
```
Content-Type: application/json
Accept-Language: ar | en
```

## Endpoints

### Health Check
```http
GET /api/v1/health
```

**Response:**
```json
{
  "status": "healthy",
  "frameworks": ["ECC", "CCC", "PDPL"],
  "features": {
    "bilingual": true,
    "ai_rag": true,
    "soc_integration": true
  },
  "message_en": "All systems operational",
  "message_ar": "جميع الأنظمة تعمل"
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

#### List Controls
```http
GET /api/v1/controls?framework=ECC&offset=0&limit=50
```

**Query Parameters:**
- `framework` (optional): Filter by ECC, CCC, or PDPL
- `status` (optional): Filter by implementation status
- `domain` (optional): Filter by control domain
- `offset` (default: 0): Pagination offset
- `limit` (default: 50, max: 100): Items per page

**Response:**
```json
{
  "total": 150,
  "offset": 0,
  "limit": 50,
  "items": [
    {
      "id": 1,
      "control_id": "ECC-GV-1",
      "framework": "ECC",
      "domain": "Governance",
      "title_en": "Governance Framework",
      "title_ar": "إطار الحوكمة",
      "status": "compliant",
      "maturity_level": 4,
      "created_at": "2026-02-04T10:00:00Z",
      "updated_at": "2026-02-04T10:00:00Z"
    }
  ]
}
```

#### Get Single Control
```http
GET /api/v1/controls/{control_id}
```

**Response:** Single control object with full details

#### Create Control
```http
POST /api/v1/controls
```

**Request Body:**
```json
{
  "control_id": "ECC-GV-1",
  "framework": "ECC",
  "domain": "Governance",
  "title_en": "Governance Framework",
  "title_ar": "إطار الحوكمة",
  "description_en": "...",
  "description_ar": "...",
  "priority": "critical",
  "status": "not_started"
}
```

#### Update Control
```http
PATCH /api/v1/controls/{control_id}
```

**Request Body:** Partial control object (only changed fields)

#### Delete Control
```http
DELETE /api/v1/controls/{control_id}
```

**Response:** 204 No Content

## Error Responses

All errors return bilingual messages:

```json
{
  "detail": {
    "message_en": "Control ECC-GV-1 not found",
    "message_ar": "لم يتم العثور على الضابط ECC-GV-1"
  }
}
```

## Interactive Documentation
Visit http://localhost:8000/docs for interactive Swagger UI
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
