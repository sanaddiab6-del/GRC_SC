# Deliverable 2: ECC↔CCC Unified Baseline + Delta

## Overview
Mapping between ECC and CCC to identify overlapping controls and create a unified baseline, eliminating redundancy.

## Status
✅ **Initial Mapping Created**
- Basic baseline mapping structure
- Sample control mappings
- Statistics and recommendations

## Files
- `/data/mappings/ecc-ccc-baseline.yaml` - Baseline mapping

## Key Findings
- 78 overlapping controls (68.5% average overlap)
- 36 ECC-unique controls
- 102 CCC-unique controls

## Next Steps
- [ ] Complete mapping of all 114 ECC controls
- [ ] Map all 180 CCC controls
- [ ] Create detailed delta pack for CCC-specific controls
- [ ] Develop unified implementation roadmap
- [ ] Create compliance calculator based on mappings
# Deliverable 2: ECC-CCC Mapping

## Overview

The ECC-CCC mapping provides a systematic relationship between Saudi NCA's Essential Cybersecurity Controls (ECC) and Cloud Cybersecurity Controls (CCC). This mapping helps organizations:

1. **Eliminate redundancy** when implementing both frameworks
2. **Identify gaps** where CCC extends ECC requirements
3. **Streamline compliance** by understanding control relationships
4. **Plan implementation** based on control alignment

## Mapping Types

### 1. Equivalent Mapping
Controls serve the same purpose with minimal differences. Organizations can implement one control to satisfy both frameworks.

**Example**: ECC-GV-1 ↔ CCC-GOV-01
- Both require comprehensive governance framework
- CCC adds cloud-specific oversight requirements
- Alignment score: 0.95 (95% overlap)

### 2. Partial Mapping
Controls overlap but one provides additional requirements. Organizations must implement base control plus framework-specific extensions.

**Example**: ECC-RM-1 → CCC-RM-01, CCC-RM-02
- ECC focuses on general risk assessment
- CCC extends to cloud-specific risks and vendor management
- Alignment score: 0.80 (80% overlap)

### 3. Related Mapping
Controls address similar risks but with different approaches. Organizations should understand both approaches for comprehensive coverage.

## Mapping Structure

### YAML Format

```yaml
mappings:
  - ecc_control: "ECC-GV-1"
    ccc_controls: ["CCC-GOV-01"]
    mapping_type: "equivalent"
    alignment_score: 0.95
    notes: "Both require governance framework. CCC adds cloud oversight."
```

**Location**: `data/mappings/ecc-ccc-baseline.yaml`

### JSON Format

```json
{
  "mappings": [
    {
      "ecc_control": "ECC-GV-1",
      "ccc_controls": ["CCC-GOV-01"],
      "mapping_type": "equivalent",
      "notes": "Both require comprehensive governance framework"
    }
  ]
}
```

**Location**: `data/mappings/ecc_to_ccc.json`

## Key Mappings

### Governance Domain

| ECC Control | CCC Controls | Type | Alignment | Notes |
|-------------|--------------|------|-----------|-------|
| ECC-GV-1 | CCC-GOV-01 | Equivalent | 95% | Cloud-specific governance extensions |

### Risk Management Domain

| ECC Control | CCC Controls | Type | Alignment | Notes |
|-------------|--------------|------|-----------|-------|
| ECC-RM-1 | CCC-RM-01, CCC-RM-02 | Partial | 80% | CCC adds vendor risk and data sovereignty |

### Access Control Domain

| ECC Control | CCC Controls | Type | Alignment | Notes |
|-------------|--------------|------|-----------|-------|
| ECC-AC-1 | CCC-AC-01, CCC-AC-02 | Equivalent | 90% | CCC specifies IAM and federation |

### Data Lifecycle Domain

| ECC Control | CCC Controls | Type | Alignment | Notes |
|-------------|--------------|------|-----------|-------|
| ECC-DL-1 | CCC-DATA-01, CCC-DATA-02, CCC-DATA-03 | Partial | 85% | CCC adds cloud data classification, encryption, retention |

### Information Security Domain

| ECC Control | CCC Controls | Type | Alignment | Notes |
|-------------|--------------|------|-----------|-------|
| ECC-IS-1 | CCC-SEC-01, CCC-SEC-02 | Partial | 75% | CCC focuses on cloud security architecture |

## Alignment Scores

Alignment scores indicate the degree of overlap between controls:

- **90-100%**: Equivalent controls - implement once for both frameworks
- **70-89%**: Partial overlap - base implementation + framework-specific additions
- **50-69%**: Related controls - understand both approaches
- **<50%**: Distinct controls - implement separately

## Implementation Strategy

### For Organizations with Both Frameworks

1. **Start with ECC**: Implement ECC controls as foundation
2. **Identify CCC Extensions**: Review CCC-specific requirements
3. **Implement Cloud-Specific Controls**: Add CCC extensions
4. **Consolidate Documentation**: Single control implementation satisfying both
5. **Leverage Mappings**: Use mapping to demonstrate dual compliance

### For Cloud-First Organizations

1. **Start with CCC**: Implement cloud-specific controls first
2. **Map to ECC**: Use reverse mapping to cover ECC requirements
3. **Address Gaps**: Implement any ECC controls not covered by CCC
4. **Maintain Dual Compliance**: Update both as frameworks evolve

## Usage

### API Access

```bash
# Get ECC-CCC mappings
GET /api/v1/mappings/ecc-to-ccc

# Get mappings for specific ECC control
GET /api/v1/mappings/ecc-to-ccc/ECC-GV-1
```

### Programmatic Access

```python
# Load mapping
import yaml

with open('data/mappings/ecc-ccc-baseline.yaml') as f:
    mappings = yaml.safe_load(f)

# Find CCC controls for ECC-GV-1
for mapping in mappings['mappings']:
    if mapping['ecc_control'] == 'ECC-GV-1':
        print(mapping['ccc_controls'])
```

## Benefits

1. **Cost Reduction**: Implement shared controls once
2. **Time Savings**: Faster dual compliance
3. **Better Understanding**: Clear relationship between frameworks
4. **Gap Analysis**: Identify what's missing
5. **Audit Efficiency**: Demonstrate control coverage across frameworks

## Maintenance

### When to Update Mappings

- NCA releases new ECC or CCC versions
- Organization identifies additional relationships
- Control implementations reveal new overlaps
- Audit findings suggest mapping refinements

### Update Process

1. Review official NCA documentation
2. Analyze control changes
3. Update mapping files (YAML and JSON)
4. Regenerate database mappings
5. Update documentation
6. Notify stakeholders

## Related Documents

- [01-control-library.md](./01-control-library.md) - Complete control library
- [Architecture Overview](../architecture/overview.md) - System architecture
- [ECC Controls](../../data/controls/ecc/ecc-controls.yaml)
- [CCC Controls](../../data/controls/ccc/ccc-controls.yaml)
