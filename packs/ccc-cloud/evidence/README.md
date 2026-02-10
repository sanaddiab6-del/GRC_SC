
## Overview
Evidence collection templates for NCA Cloud Computing Controls (CCC). Designed for cloud service providers and cloud consumers to demonstrate compliance.

## Cloud-Specific Evidence Categories

### 1. Cloud Governance Evidence
**Domain**: CCC-GOV

**Templates**:
- `cloud_security_policy.docx` - Cloud security governance
- `data_sovereignty_compliance.xlsx` - Saudi data localization tracking
- `cloud_risk_assessment.xlsx` - Cloud-specific risk register
- `shared_responsibility_matrix.xlsx` - CSP vs Customer responsibilities

### 2. Data Security Evidence
**Domain**: CCC-SEC

**Templates**:
- `data_classification_scheme.docx` - Cloud data classification
- `encryption_architecture.vsdx` - Encryption design
- `key_management_plan.docx` - Cloud key management
- `dlp_policy.docx` - Data Loss Prevention procedures
- `data_residency_report.xlsx` - Data location tracking

### 3. Identity & Access Management Evidence
**Domain**: CCC-IAM

**Templates**:
- `identity_federation_guide.docx` - SSO/SAML configuration
- `privileged_access_policy.docx` - PAM procedures
- `mfa_deployment_report.docx` - Multi-factor authentication
- `service_account_inventory.xlsx` - Non-human identities

### 4. Cloud Infrastructure Evidence
**Domain**: CCC-INF

**Templates**:
- `cloud_network_architecture.vsdx` - VPC/VNet design
- `resource_isolation_plan.docx` - Multi-tenancy controls
- `virtual_machine_hardening.xlsx` - VM security baseline
- `container_security_policy.docx` - Docker/Kubernetes security

### 5. Application Security Evidence
**Domain**: CCC-APP

**Templates**:
- `secure_sdlc_policy.docx` - DevSecOps procedures
- `api_security_standard.docx` - API protection requirements
- `web_application_firewall.xlsx` - WAF rules and config
- `code_review_checklist.xlsx` - Security code review

### 6. Cloud Operations Evidence
**Domain**: CCC-OPS

**Templates**:
- `cloud_monitoring_plan.docx` - CloudWatch/Azure Monitor
- `change_management_procedure.docx` - Cloud change control
- `incident_response_playbook.docx` - Cloud IR procedures
- `configuration_management.xlsx` - IaC baseline

### 7. Resilience Evidence
**Domain**: CCC-RES

**Templates**:
- `high_availability_design.vsdx` - Multi-AZ/region architecture
- `disaster_recovery_plan.docx` - Cloud DR procedures
- `backup_strategy.docx` - Cloud backup configuration
- `sla_compliance_report.xlsx` - Availability metrics

### 8. Third-Party Evidence
**Domain**: CCC-TPM

**Templates**:
- `vendor_security_assessment.xlsx` - Cloud vendor evaluation
- `subprocessor_register.xlsx` - Third-party data processors
- `supply_chain_risk.docx` - Vendor risk management
- `sla_monitoring.xlsx` - Service level tracking

## Cloud Service Model Templates

### IaaS Evidence
- Virtual machine configurations
- Network security groups
- Storage encryption settings
- Compute resource allocation

### PaaS Evidence
- Platform security configurations
- Database encryption settings
- Application runtime security
- Platform-level monitoring

### SaaS Evidence
- Tenant isolation verification
- Data segregation controls
- Authentication configurations
- API security settings

## Evidence Collection Tools

### Automated Evidence Collection
```bash
# AWS CLI examples
aws iam get-account-summary > iam_summary.json
aws ec2 describe-security-groups > security_groups.json
aws s3api list-buckets > s3_buckets.json

# Azure CLI examples
az account list > azure_accounts.json
az network nsg list > network_security_groups.json
az storage account list > storage_accounts.json
```

### Cloud Security Posture Management (CSPM)
- AWS Security Hub reports
- Azure Security Center assessments
- Google Cloud Security Command Center
- Third-party tools (Prisma Cloud, CloudGuard)

## Compliance Mapping

Each template includes mappings to:
- ISO 27017 (Cloud Security)
- ISO 27018 (Cloud Privacy)
- CSA Cloud Controls Matrix (CCM)
- NIST SP 800-53 (Cloud extensions)

## Saudi-Specific Requirements

### Data Localization Evidence
- Data residency certificates from CSP
- Data transfer impact assessments
- Cross-border data flow documentation
- SDAIA approval for international transfers

### Cloud Provider Certifications
Required evidence from CSP:
- ISO 27001 certificate
- ISO 27017 certificate
- ISO 27018 certificate (for personal data)
- CSA STAR certification (Level 1 minimum)

## Audit Preparation

### For CSPs (Cloud Service Providers)
- [ ] Infrastructure security evidence
- [ ] Multi-tenancy isolation proof
- [ ] Physical security controls
- [ ] Operational procedures
- [ ] Incident response capabilities

### For Cloud Consumers
- [ ] Shared responsibility documentation
- [ ] Configuration security evidence
- [ ] Access control implementations
- [ ] Data protection measures
- [ ] Vendor oversight records

---
**Last Updated**: February 2024  
**Version**: 1.0  
