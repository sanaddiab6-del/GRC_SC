# Executive Reporting

## SICO GRC Platform - Reporting Engine

This directory contains templates and generators for executive reporting and compliance dashboards.

## Components

### Templates (`/templates`)
Pre-designed report templates for various stakeholders.

#### PowerPoint Templates
- [ ] `executive-dashboard.pptx` - C-level compliance dashboard
- [ ] `board-report.pptx` - Board of directors report
- [ ] `audit-readiness.pptx` - Audit preparation presentation

#### Excel Templates
- [ ] `compliance-tracker.xlsx` - Compliance status tracker
- [ ] `gap-analysis.xlsx` - Gap analysis workbook
- [ ] `risk-register.xlsx` - Risk register template

#### Word Templates
- [ ] `compliance-report.docx` - Detailed compliance report
- [ ] `audit-report.docx` - Audit findings report
- [ ] `executive-summary.docx` - Executive summary template

### Generators (`/generators`)
Python scripts for automated report generation.

- [ ] `dashboard_generator.py` - Generate dashboard data
- [ ] `report_generator.py` - Generate Word/PDF reports
- [ ] `chart_generator.py` - Generate charts and visualizations
- [ ] `export_generator.py` - Export data in various formats

## Report Types

### Compliance Dashboard
Real-time view of compliance posture across all frameworks.

**Includes**:
- Compliance heatmap (by framework and domain)
- Control implementation status
- Evidence collection progress
- Gap analysis summary
- Trend analysis

### Executive Summary
High-level overview for C-level executives.

**Includes**:
- Overall compliance score
- Key risks and gaps
- Recent achievements
- Upcoming deadlines
- Recommendations

### Audit Readiness Report
Detailed report for audit preparation.

**Includes**:
- Control-by-control status
- Evidence inventory
- Identified gaps
- Remediation plan
- Testing results

### Risk Dashboard
Risk-focused view for CISOs and risk officers.

**Includes**:
- Risk heatmap
- Control effectiveness
- Incident correlation
- Vulnerability trends
- Mitigation status

## Usage

### Generate Reports via CLI
```bash
# Executive dashboard
python reporting/generators/dashboard_generator.py \
  --client-id CLIENT_123 \
  --output reports/dashboard.pdf

# Compliance report
python reporting/generators/report_generator.py \
  --template compliance-report \
  --period monthly \
  --output reports/compliance-jan-2026.pdf
```

### Generate Reports via API
```bash
POST /api/v1/reports/generate
{
  "report_type": "executive_dashboard",
  "client_id": "CLIENT_123",
  "period": "monthly",
  "format": "pdf"
}
```

## Customization

### Custom Templates
1. Copy existing template
2. Modify design and layout
3. Update placeholders
4. Register in template catalog

### Custom Charts
Add new chart types in `chart_generator.py`:
```python
def generate_custom_chart(data, config):
    # Chart generation logic
    pass
```

## Scheduling

Automated report generation can be scheduled:

```yaml
schedules:
  - report_type: "executive_dashboard"
    frequency: "monthly"
    recipients: ["ciso@example.com"]
    format: "pdf"
  
  - report_type: "compliance_tracker"
    frequency: "weekly"
    recipients: ["compliance-team@example.com"]
    format: "excel"
```

---

**Last Updated**: February 2026
