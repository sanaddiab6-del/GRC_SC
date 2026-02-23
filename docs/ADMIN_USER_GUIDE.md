# 📚 SICO GRC Platform - Administrator User Guide

## Table of Contents

1. [Getting Started](#getting-started)
2. [User Management](#user-management)
3. [Control Management](#control-management)
4. [Evidence Management](#evidence-management)
5. [Reporting](#reporting)
6. [Privacy Management](#privacy-management)
7. [Security Operations](#security-operations)
8. [System Administration](#system-administration)
9. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Initial Login

1. Navigate to: `https://your-domain.com`
2. Default admin credentials are provided during setup
3. **IMPORTANT**: Change default password immediately after first login

### User Interface

The platform supports bilingual operation:
- **Arabic (العربية)**: Default, RTL layout
- **English**: LTR layout
- Switch languages using the language toggle in the top navigation bar

### Dashboard Overview

The main dashboard shows:
- Total controls by framework (ECC, CCC, PDPL)
- Compliance status breakdown
- Recent activity timeline
- Control priority distribution
- Risk heatmap

---

## User Management

### Adding Users

1. Navigate to **Settings** → **Users**
2. Click **Add User**
3. Fill in required fields:
   - Email (will be used for login)
   - Full Name
   - Role (see roles below)
4. Click **Create User**
5. User receives email with temporary password

### User Roles

| Role | Permissions | Use Case |
|------|-------------|----------|
| **Admin** | Full system access | IT administrators |
| **Compliance Officer** | Manage controls, evidence, reports | Compliance team leads |
| **Auditor** | Read-only + generate reports | Internal/external auditors |
| **Analyst** | View controls, add evidence | Compliance analysts |
| **Viewer** | Read-only public data | Stakeholders, management |

### Editing Users

1. Navigate to **Settings** → **Users**
2. Click on user email
3. Edit fields:
   - Full Name
   - Roles (can assign multiple)
   - Active status
4. Click **Save Changes**

### Disabling Users

**Do NOT delete users** - this breaks audit trails.

Instead:
1. Edit user
2. Set **Active** to **No**
3. User can no longer log in but audit history is preserved

### Password Reset

**For Users**:
1. Login page → **Forgot Password**
2. Enter email
3. Receive reset link (valid 1 hour)

**For Admins**:
1. Navigate to **Settings** → **Users**
2. Click user → **Reset Password**
3. Generate temporary password
4. Share securely with user

---

## Control Management

### Understanding Controls

Controls are organized by framework:
- **ECC**: Essential Cybersecurity Controls (NCA Saudi)
- **CCC**: Cloud Cybersecurity Controls (NCA Saudi)
- **PDPL**: Personal Data Protection Law (Saudi DGA)

Each control has:
- **Control ID**: Unique identifier (e.g., ECC-GV-1)
- **Title**: Bilingual (Arabic/English)
- **Description**: What the control requires
- **Policy Guidance**: How to write policies
- **Procedure Guidance**: Step-by-step implementation
- **Status**: Compliant, Partial, Non-Compliant, N/A
- **Priority**: Critical, High, Medium, Low
- **Maturity Level**: 1-5 (CMMI scale)

### Viewing Controls

1. Navigate to **Controls**
2. Filter by:
   - Framework (ECC, CCC, PDPL, All)
   - Status
   - Priority
   - Search by ID or title
3. Click control card to view details

### Updating Control Status

1. Open control details
2. Click **Edit Status**
3. Select new status:
   - **Compliant**: Fully implemented
   - **Partial**: Partially implemented
   - **Non-Compliant**: Not implemented
   - **Not Applicable**: Does not apply
4. Add notes explaining status change
5. Click **Save**

### Setting Maturity Level

Maturity levels follow CMMI:
- **1**: Ad-hoc (no formal process)
- **2**: Documented (policy exists)
- **3**: Implemented (procedures followed)
- **4**: Measured (metrics tracked)
- **5**: Optimized (continuous improvement)

### Linking Controls

Controls can be cross-referenced:
1. Edit control
2. **Related Controls** section
3. Add related controls from other frameworks
4. Save changes

---

## Evidence Management

### Understanding Evidence

Evidence proves control implementation. Types include:
- Policies & procedures documents
- Configuration screenshots
- System logs
- Training records
- Audit reports

### Uploading Evidence

1. Navigate to control details
2. Click **Add Evidence**
3. Fill in:
   - Title (bilingual)
   - Description
   - Evidence type
   - File upload
4. Click **Upload**

**Supported Formats**:
- Documents: PDF, DOCX, XLSX
- Images: PNG, JPG
- Logs: TXT, CSV, JSON, LOG

**Size Limits**:
- Maximum file size: 50 MB
- Compressed archives: ZIP, TAR.GZ

### Validating Evidence

**For Auditors**:
1. Navigate to **Evidence** → **Pending Validation**
2. Review evidence:
   - Check completeness
   - Verify authenticity
   - Assess quality
3. Actions:
   - **Validate**: Accept evidence
   - **Reject**: Return with notes
4. Add validation notes
5. Click **Save Decision**

### Evidence Retention

Per NCA requirements:
- Minimum retention: 7 years
- Automatic retention tracking
- Deletion protection until retention expires

### Viewing Evidence

1. Navigate to control → **Evidence** tab
2. See all linked evidence
3. Click to download/view
4. Audit trail shows who uploaded/viewed

---

## Reporting

### Available Reports

1. **Compliance Summary**
   - Overall compliance by framework
   - Status breakdown
   - Trend analysis

2. **Risk Heatmap**
   - Likelihood vs Impact matrix
   - Risk distribution
   - Treatment status

3. **Audit Readiness**
   - Evidence coverage
   - Documentation gaps
   - Maturity assessment

4. **Gap Analysis**
   - Non-compliant controls
   - Required actions
   - Priority recommendations

5. **Executive Dashboard**
   - High-level metrics
   - Compliance trends
   - Key performance indicators

### Generating Reports

1. Navigate to **Reports**
2. Select report type
3. Configure filters:
   - Date range
   - Frameworks
   - Status filters
4. Select format: PDF, HTML, JSON
5. Click **Generate**
6. Download when ready

### Scheduled Reports

1. Navigate to **Reports** → **Scheduled**
2. Click **New Schedule**
3. Configure:
   - Report type
   - Frequency (daily, weekly, monthly)
   - Recipients (email addresses)
   - Format
4. Click **Create Schedule**

### Report Templates

Customize report templates:
1. Navigate to **Settings** → **Report Templates**
2. Select template to edit
3. Customize:
   - Company logo
   - Color scheme
   - Content sections
4. Save changes

---

## Privacy Management

### Consent Management

**Recording Consent**:
1. Navigate to **Privacy** → **Consent**
2. Click **Record Consent**
3. Fill in:
   - Data subject identifier (hashed)
   - Consent type (marketing, analytics, etc.)
   - Consent given: Yes/No
   - Consent method (web, email, in-person)
4. Save

**Withdrawing Consent**:
1. Find consent record
2. Click **Withdraw**
3. Confirm action
4. Consent marked as withdrawn with timestamp

### Data Subject Access Requests (DSAR)

**Processing DSAR**:
1. Navigate to **Privacy** → **DSAR**
2. New request shows as **Pending**
3. Request types:
   - **Access**: Provide personal data copy
   - **Rectification**: Correct inaccurate data
   - **Erasure**: Delete personal data
   - **Portability**: Export data in standard format
   - **Objection**: Stop processing
   - **Restriction**: Limit processing

**Responding to DSAR**:
1. Open DSAR request
2. Review request details
3. Gather required information
4. Respond within 30 days (PDPL requirement)
5. Upload response document
6. Mark as **Completed**

### Data Breach Management

**Reporting Breach**:
1. Navigate to **Privacy** → **Breaches**
2. Click **Report Breach**
3. Fill in:
   - Detection date
   - Breach type
   - Affected records (estimate)
   - Description
   - Containment actions
4. Save

**72-Hour Notification**:
- System automatically tracks deadline
- Alerts sent as deadline approaches
- Notify SDAIA within 72 hours (PDPL Article 27)

---

## Security Operations

### Monitoring Failed Logins

1. Navigate to **Security** → **Audit Logs**
2. Filter by action: "failed_login"
3. Review patterns:
   - Repeated failures from same IP
   - Account lockouts
   - Suspicious timing

**Account Lockout**:
- Automatic after 5 failed attempts
- 30-minute lockout period
- Admin can unlock manually

### Reviewing Audit Logs

1. Navigate to **Security** → **Audit Logs**
2. Filter by:
   - User
   - Action type
   - Date range
   - Resource type
3. Export for analysis: CSV, JSON

**Audit Log Retention**: 7 years (NCA requirement)

### Security Incidents

**Logging Incident**:
1. Navigate to **Security** → **Incidents**
2. Click **Report Incident**
3. Fill in:
   - Severity (Critical, High, Medium, Low)
   - Category (data breach, malware, etc.)
   - Description
   - Affected systems
   - Detection date
4. Assign to responder
5. Save

**Responding to Incident**:
1. Open incident
2. Add response actions
3. Update status (Investigating, Contained, Resolved)
4. Link to affected controls
5. Document lessons learned
6. Close incident

### Risk Management

**Adding Risk**:
1. Navigate to **Risk** → **Risk Register**
2. Click **Add Risk**
3. Fill in:
   - Title (bilingual)
   - Category
   - Likelihood (1-5)
   - Impact (1-5)
   - Risk score (auto-calculated)
4. Assign risk owner
5. Define treatment strategy

**Risk Heatmap**:
- Visual representation of risks
- Color-coded by severity
- Click on cell to see risks

---

## System Administration

### System Configuration

1. Navigate to **Settings** → **System**
2. Configure:
   - Company name
   - Logo
   - Default language
   - Time zone
   - Date format

### Backup Management

**Manual Backup**:
```bash
# SSH to server
ssh admin@your-server

# Run backup script
sudo /opt/sico-grc/scripts/backup.sh
```

**Restore from Backup**:
```bash
# SSH to server
ssh admin@your-server

# Run restore script
sudo /opt/sico-grc/scripts/restore_backup.sh backup-file.sql.gz
```

### Database Maintenance

**View Database Stats**:
1. Navigate to **Settings** → **System Health**
2. View:
   - Database size
   - Connection pool usage
   - Query performance
   - Slow queries

**Optimize Database** (monthly):
```bash
# SSH to server
ssh admin@your-server

# Run optimization
docker compose exec postgres psql -U sico_admin -d sico_grc -c "VACUUM ANALYZE;"
```

### Certificate Renewal

TLS certificates expire annually (Let's Encrypt: 90 days)

**Check Expiry**:
```bash
openssl x509 -in /etc/ssl/certs/sico-grc.crt -noout -dates
```

**Renew Certificate**:
```bash
sudo certbot renew
sudo systemctl restart nginx
```

### Key Rotation (Quarterly)

Per compliance requirements, rotate keys every 90 days:

1. Generate new keys:
```bash
python scripts/production_setup.py --generate
```

2. Update `.env` file with new keys
3. Restart services:
```bash
docker compose restart backend
```

4. Test login functionality
5. Document rotation in change log

---

## Troubleshooting

### Issue: User Cannot Login

**Symptoms**: Login fails with "Invalid credentials"

**Causes**:
1. Account locked (5 failed attempts)
2. Account disabled
3. Incorrect password

**Resolution**:
1. Check audit logs for failed attempts
2. Check user status (Settings → Users)
3. Unlock account if needed
4. Reset password if forgotten

### Issue: Slow Performance

**Symptoms**: Pages load slowly (>5 seconds)

**Causes**:
1. Database connection pool exhausted
2. High query load
3. Insufficient server resources

**Resolution**:
1. Check system health (Settings → System Health)
2. Review slow queries
3. Restart services:
```bash
docker compose restart
```
4. Scale up server if needed

### Issue: Evidence Upload Fails

**Symptoms**: "Upload failed" error

**Causes**:
1. File too large (>50 MB)
2. Unsupported format
3. Storage full

**Resolution**:
1. Check file size and format
2. Check disk space:
```bash
df -h
```
3. Clear old backups if needed
4. Compress large files

### Issue: Missing Audit Logs

**Symptoms**: No logs visible for recent activity

**Causes**:
1. Audit logging middleware disabled
2. Database connection issues
3. Permission issues

**Resolution**:
1. Check backend logs:
```bash
docker compose logs backend | grep audit
```
2. Verify database connection
3. Restart backend service

---

## Support & Resources

### Documentation
- **System Overview**: `SYSTEM_OVERVIEW.md`
- **API Documentation**: https://your-domain.com/api/v1/docs
- **Security Guide**: `docs/SECURITY_README.md`

### Contact Support
- **Email**: support@yourdomain.com
- **Phone**: [Your support number]
- **Emergency**: [Your 24/7 on-call number]

### Training Resources
- **Video Tutorials**: [Your training portal]
- **User Forum**: [Your community forum]
- **Knowledge Base**: [Your KB URL]

---

## Appendix

### A. Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Search controls | Ctrl + K |
| New evidence | Ctrl + E |
| Generate report | Ctrl + R |
| User menu | Ctrl + U |
| Switch language | Ctrl + L |

### B. Default Settings

| Setting | Default Value |
|---------|---------------|
| Session timeout | 30 minutes |
| Password expiry | 90 days |
| Password complexity | 12+ chars, mixed case, digits, special |
| Failed login lockout | 5 attempts, 30 min |
| Audit log retention | 7 years |

### C. Compliance Frameworks

- **NCA ECC**: Essential Cybersecurity Controls
- **NCA CCC**: Cloud Cybersecurity Controls
- **PDPL**: Personal Data Protection Law (Saudi)
- **SDAIA AI**: Saudi Data & AI Authority principles

---

**Document Version**: 1.0  
**Last Updated**: 2026-02-10  
**For**: SICO GRC Platform Administrators
