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
