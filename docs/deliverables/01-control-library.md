# Deliverable 1: Control Library

## Overview

The SICO GRC Platform includes a comprehensive control library covering three Saudi regulatory frameworks:

1. **ECC (Essential Cybersecurity Controls)** - NCA
2. **CCC (Cloud Cybersecurity Controls)** - NCA  
3. **PDPL (Personal Data Protection Law)** - SDAIA

## Control Library Structure

Each control in the library includes:

- **Unique Control ID**: Framework-specific identifier (e.g., ECC-GV-1, CCC-AC-01, PDPL-8)
- **Bilingual Content**: All text in both Arabic and English
  - Title (title_en, title_ar)
  - Description (description_en, description_ar)
  - Policy guidance (policy_guidance_en, policy_guidance_ar)
  - Procedure guidance (procedure_guidance_en, procedure_guidance_ar)
- **Metadata**:
  - Framework (ECC, CCC, PDPL)
  - Domain (e.g., Governance, Access Control, Risk Management)
  - Priority level (critical, high, medium, low)
  - Compliance status (compliant, partial, non_compliant)
  - Maturity level (1-5)
- **Evidence Requirements**: List of required evidence types
- **Cross-Framework Mappings**: Related controls in other frameworks

## Control Data Format

### YAML Format
Control data is stored in YAML format for human readability:

```yaml
controls:
  - control_id: "ECC-GV-1"
    framework: "ECC"
    domain: "Governance"
    title_en: "Governance Framework"
    title_ar: "إطار الحوكمة"
    # ... additional fields
```

**Location**: `data/controls/{framework}/{framework}-controls.yaml`

### JSON Format
JSON format is also supported for programmatic access:

```json
{
  "control_id": "ECC-GV-1",
  "framework": "ECC",
  "domain": "Governance",
  "title_en": "Governance Framework",
  "title_ar": "إطار الحوكمة"
}
```

**Location**: `data/controls/ecc_baseline.json`

## Framework Coverage

### ECC (Essential Cybersecurity Controls)

**Domains**:
- Governance (GV)
- Risk Management (RM)
- Access Control (AC)
- Asset Management (AM)
- Cryptography (CR)
- Physical Security (PS)
- Operations Security (OP)
- Communications Security (CS)
- System Acquisition & Development (SA)
- Incident Management (IM)

**Sample Controls**:
- ECC-GV-1: Governance Framework
- ECC-RM-1: Risk Assessment
- ECC-AC-1: Access Control Policy

### CCC (Cloud Cybersecurity Controls)

**Domains**:
- Cloud Governance (GOV)
- Cloud Risk Management (RM)
- Cloud Access Control (AC)
- Data Protection (DATA)
- Cloud Security (SEC)
- Compliance & Audit (COMP)

**Sample Controls**:
- CCC-GOV-01: Cloud Governance Framework
- CCC-RM-01: Cloud Risk Assessment
- CCC-AC-01: Cloud Access Management

### PDPL (Personal Data Protection Law)

**Domains**:
- Governance
- Risk Management
- Access Control
- Data Subject Rights
- Consent Management
- Data Breach Response
- Cross-Border Transfer
- Data Retention

**Sample Controls**:
- PDPL-1: Data Protection Governance
- PDPL-4: Privacy Impact Assessment
- PDPL-8: Data Access Controls
- PDPL-9: Data Subject Rights Management

## Usage

### Loading Controls

```python
# Python example
from src.backend.controls.models import Control
from src.backend.core.database import get_db

# Query controls by framework
controls = await db.execute(
    select(Control).where(Control.framework == "ECC")
)
```

### API Access

```bash
# Get all ECC controls
GET /api/v1/controls?framework=ECC

# Get specific control
GET /api/v1/controls/ECC-GV-1

# Filter by domain
GET /api/v1/controls?framework=ECC&domain=Governance
```

### RAG Queries

The control library is indexed in the vector database for AI-powered queries:

```
Query: "What are the governance requirements for cloud services?"
Response: [Controls CCC-GOV-01, ECC-GV-1 with bilingual content and citations]
```

## Maintenance

### Adding New Controls

1. Add control to appropriate YAML file in `data/controls/{framework}/`
2. Run data loader: `python scripts/load_sample_data.py`
3. Regenerate embeddings: `python ai/scripts/generate_embeddings.py`
4. Verify in API and frontend

### Updating Controls

1. Modify control in YAML file
2. Run database migration if schema changed
3. Reload data: `python scripts/load_sample_data.py`
4. Update embeddings if content changed

## Compliance Mapping

Controls are mapped across frameworks to show relationships:
- See `data/mappings/ecc-ccc-baseline.yaml` for ECC-CCC mappings
- See `data/mappings/ecc_to_ccc.json` for programmatic access

## Related Documents

- [02-ecc-ccc-mapping.md](./02-ecc-ccc-mapping.md) - Cross-framework mapping details
- [Evidence Catalog](../../data/evidence/catalog.yaml) - Evidence types
- [API Documentation](../api/) - Control API endpoints
