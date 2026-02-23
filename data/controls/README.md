# ECC Control Library

## Essential Cybersecurity Controls (NCA)

This directory contains the Saudi Arabian National Cybersecurity Authority's Essential Cybersecurity Controls (ECC) framework.

## Overview

The ECC framework consists of 114 controls organized into 5 domains:
1. **Cybersecurity Governance** (Controls 1.x)
2. **Cybersecurity Defense** (Controls 2.x)
3. **Cybersecurity Resilience** (Controls 3.x)
4. **Third Party and Cloud Computing Cybersecurity** (Controls 4.x)
5. **Industrial Control Systems Cybersecurity** (Controls 5.x)

## File Structure

- `ecc-controls.yaml` - Complete control library with bilingual descriptions
- `ecc-controls.json` - JSON format for API integration
- `ecc-domains.yaml` - Domain-level structure and metadata
- `ecc-implementation-guide.md` - Implementation guidance per control

## Control Structure

Each control includes:
- **Control ID**: Unique identifier (e.g., 1-1-1)
- **Control Title**: English and Arabic titles
- **Description**: Detailed control description (bilingual)
- **Implementation Guidance**: How to implement the control
- **Evidence Requirements**: What evidence demonstrates compliance
- **Maturity Levels**: Basic, Advanced, Progressive
- **Applicability**: Organization types and sizes
- **References**: Related standards and frameworks

## Sample Control

```yaml
controls:
  - id: "1-1-1"
    domain: "Cybersecurity Governance"
    title_en: "Cybersecurity Policy"
    title_ar: "سياسة الأمن السيبراني"
    description_en: "Develop, document, approve, and communicate a cybersecurity policy"
    description_ar: "تطوير وتوثيق واعتماد ونشر سياسة الأمن السيبراني"
    maturity_level: "Basic"
    evidence_required:
      - "Approved cybersecurity policy document"
      - "Communication records (email, training, acknowledgment)"
      - "Policy review and approval minutes"
    implementation_guide: |
      1. Establish cybersecurity policy objectives aligned with business goals
      2. Define scope, roles, and responsibilities
      3. Obtain management approval
      4. Communicate to all relevant personnel
      5. Review and update annually
```

## Implementation Priority

### Critical (Immediate Implementation)
Controls that address fundamental security requirements.

### High Priority (3-6 months)
Controls that significantly reduce risk.

### Medium Priority (6-12 months)
Controls that enhance security posture.

### Low Priority (12+ months)
Controls for advanced maturity.

---

**Source**: National Cybersecurity Authority (NCA), Saudi Arabia  
**Version**: 2.0 (2023)  
**Last Updated**: February 2026
