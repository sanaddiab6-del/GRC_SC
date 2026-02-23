# Evidence Master Catalog

## Overview

The Evidence Master Catalog provides a comprehensive inventory of evidence types that demonstrate compliance with regulatory controls (ECC, CCC, PDPL).

## Evidence Categories

### 1. Policies & Procedures
Documented organizational standards and operational procedures.

### 2. Technical Configurations
System settings, baselines, and hardening configurations.

### 3. Logs & Records
Security logs, access logs, audit trails, and system records.

### 4. Assessments & Reports
Risk assessments, vulnerability scans, penetration tests, and audit reports.

### 5. Training & Awareness
Training materials, attendance records, and awareness campaigns.

### 6. Contracts & Agreements
Third-party agreements, SLAs, and vendor contracts.

### 7. Incident Records
Incident reports, breach notifications, and response documentation.

### 8. Business Continuity
BCP/DRP plans, testing results, and recovery procedures.

## Evidence Template Structure

Each evidence template includes:
- **Evidence ID**: Unique identifier
- **Evidence Name**: Descriptive name (bilingual)
- **Category**: Evidence category
- **Related Controls**: Controls this evidence satisfies
- **Template**: Document or data template
- **Collection Method**: How to collect this evidence
- **Retention Period**: How long to retain
- **Review Frequency**: How often to review/update

## File Structure

- `evidence-catalog.yaml` - Master catalog with all evidence types
- `evidence-control-mapping.yaml` - Mapping of evidence to controls
- `templates/` - Actual templates for each evidence type

---

**Last Updated**: February 2026
