# 📊 Regulatory Core Assets

This directory contains the regulatory frameworks, control libraries, evidence templates, and compliance data that form the foundation of the SICO GRC Platform.

## Directory Structure

### `/controls`
Operational control libraries for ECC, CCC, and PDPL frameworks.

### `/mappings`
Cross-framework mappings and baseline definitions.

### `/evidence`
Evidence catalog and audit-ready templates.

### `/audit`
Test procedures and audit methodologies.

### `/pdpl`
PDPL-specific registers and privacy management tools.

## Data Files Overview

### Control Libraries
- **ECC Controls**: Essential Cybersecurity Controls (114 controls)
- **CCC Controls**: Cloud Cybersecurity Controls (137 controls)
- **PDPL Controls**: Personal Data Protection Law operational controls (40 controls)

### Mapping Files
- ECC↔CCC baseline mapping
- Control inheritance matrix
- Framework crosswalks (ISO 27001, NIST, etc.)

### Evidence Templates
- Policy templates
- Procedure templates
- Log samples
- Configuration baselines
- Assessment reports

### Audit Materials
- Test procedure templates
- Sampling methodologies
- Evidence collection checklists

### PDPL Registers
- Record of Processing Activities (RoPA)
- Data Subject Access Request (DSAR) log
- Breach notification log
- Retention schedule

## Data Formats

All data files use structured formats for easy integration:
- **YAML**: Control definitions, mappings
- **JSON**: API-ready data structures
- **Markdown**: Human-readable documentation
- **Excel**: Templates for business users

## Usage

These assets are consumed by:
1. **Backend API**: Control and evidence management
2. **Frontend**: User interfaces for compliance management
3. **AI Engine**: Knowledge base and RAG pipeline
4. **Reporting**: Dashboard and report generation
5. **SICO Packs**: Pre-packaged compliance bundles

---

**Last Updated**: February 2026
