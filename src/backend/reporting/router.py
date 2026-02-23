"""
Reporting API Router
Executive dashboards and compliance reports
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import List
from datetime import datetime
import uuid

from core.database import get_db
from controls.models import Control, ControlStatus, FrameworkType
from evidence.models import Evidence, EvidenceStatus
from reporting.models import Report, ReportType, ReportStatus
from reporting.schemas import (
    ReportRequest,
    ReportResponse,
    ComplianceSummary,
    ControlPosture,
    DashboardData,
)
Reporting Router
API endpoints for compliance reporting
"""

from fastapi import APIRouter

router = APIRouter()


def _str_value(v) -> str:
    """Return the string value of an enum or plain string."""
    return v if isinstance(v, str) else v.value


@router.get("/dashboard", response_model=DashboardData)
async def get_executive_dashboard(
    db: AsyncSession = Depends(get_db),
):
    """
    Get executive dashboard with real-time compliance data
    """
    # Get total count and status breakdown using SQL aggregation
    total_count_query = select(func.count()).select_from(Control)
    total_result = await db.execute(total_count_query)
    total_controls = total_result.scalar() or 0
    
    # Get status counts with single query
    status_query = select(
        Control.status,
        func.count(Control.id)
    ).group_by(Control.status)
    status_result = await db.execute(status_query)
    
    status_counts = {
        "compliant": 0,
        "non_compliant": 0,
        "in_progress": 0,
        "not_started": 0,
        "not_applicable": 0,
    }
    
    for status, count in status_result:
        status_counts[status.value] = count
    
    for control in all_controls:
        status = _str_value(control.status)
        status_counts[status] = status_counts.get(status, 0) + 1
        
        # By framework
        framework = _str_value(control.framework)
        if framework not in by_framework:
            by_framework[framework] = {
    # Get framework breakdown with single query
    framework_query = select(
        Control.framework,
        Control.status,
        func.count(Control.id)
    ).group_by(Control.framework, Control.status)
    framework_result = await db.execute(framework_query)
    
    by_framework = {}
    for framework, status, count in framework_result:
        fw_key = framework.value
        if fw_key not in by_framework:
            by_framework[fw_key] = {
                "compliant": 0,
                "non_compliant": 0,
                "in_progress": 0,
                "not_started": 0,
                "not_applicable": 0,
                "total": 0,
            }
        by_framework[fw_key][status.value] = count
        by_framework[fw_key]["total"] += count
    
    # Get domain breakdown with single query
    domain_query = select(
        Control.domain,
        Control.status,
        func.count(Control.id)
    ).group_by(Control.domain, Control.status)
    domain_result = await db.execute(domain_query)
    
    by_domain = {}
    for domain, status, count in domain_result:
        if domain not in by_domain:
            by_domain[domain] = {
                "statuses": {
                    "compliant": 0,
                    "non_compliant": 0,
                    "in_progress": 0,
                    "not_started": 0,
                    "not_applicable": 0,
                }
            }
        by_domain[domain]["statuses"][status.value] = count
    
    compliance_rate = (status_counts["compliant"] / total_controls * 100) if total_controls > 0 else 0
    
    compliance_summary = ComplianceSummary(
        total_controls=total_controls,
        compliant=status_counts["compliant"],
        non_compliant=status_counts["non_compliant"],
        in_progress=status_counts["in_progress"],
        not_started=status_counts["not_started"],
        not_applicable=status_counts["not_applicable"],
        compliance_rate=round(compliance_rate, 2),
        by_framework=by_framework,
    )
    
    # Control posture by domain
    control_posture = []
    for domain, data in by_domain.items():
        avg_maturity = sum(c.maturity_level for c in data["controls"]) / len(data["controls"]) if data["controls"] else 0
        control_posture.append(ControlPosture(
            domain=domain,
            total_controls=len(data["controls"]),
            maturity_average=round(avg_maturity, 2),
            status_breakdown=data["statuses"],
        ))
    
    # Get evidence statistics
    evidence_query = select(func.count()).select_from(Evidence)
    total_evidence = await db.scalar(evidence_query) or 0
    
    pending_validations_query = select(func.count()).select_from(Evidence).where(
        Evidence.status == EvidenceStatus.COLLECTED
    )
    pending_validations = await db.scalar(pending_validations_query) or 0
    
    # Get high priority gaps (non-compliant critical controls)
    gaps_query = select(Control).where(
        Control.status == ControlStatus.NON_COMPLIANT,
        Control.priority == "critical"
    ).limit(5)
    gaps_result = await db.execute(gaps_query)
    gaps_controls = gaps_result.scalars().all()
    
    high_priority_gaps = [
        {
            "control_id": c.control_id,
            "title_en": c.title_en,
            "title_ar": c.title_ar,
            "framework": _str_value(c.framework),
        }
        for c in gaps_controls
    ]
    
    return DashboardData(
        compliance_summary=compliance_summary,
        control_posture=control_posture,
        recent_evidence=total_evidence,
        pending_validations=pending_validations,
        high_priority_gaps=high_priority_gaps,
        frameworks=list(by_framework.keys()),
    )


@router.post("/reports", response_model=ReportResponse, status_code=201)
async def generate_report(
    report_request: ReportRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Generate a compliance report
    """
    report_id = f"RPT-{uuid.uuid4().hex[:8].upper()}"
    
    # Determine report title based on type
    report_titles = {
        "compliance_summary": {
            "en": "Compliance Summary Report",
            "ar": "تقرير ملخص الامتثال"
        },
        "control_posture": {
            "en": "Control Posture Report",
            "ar": "تقرير وضع الضوابط"
        },
        "evidence_status": {
            "en": "Evidence Status Report",
            "ar": "تقرير حالة الأدلة"
        },
        "risk_heatmap": {
            "en": "Risk Heatmap",
            "ar": "خريطة المخاطر الحرارية"
        },
        "audit_readiness": {
            "en": "Audit Readiness Report",
            "ar": "تقرير جاهزية التدقيق"
        },
        "executive_dashboard": {
            "en": "Executive Dashboard Report",
            "ar": "تقرير لوحة القيادة التنفيذية"
        },
    }
    
    titles = report_titles.get(report_request.report_type, {"en": "Report", "ar": "تقرير"})
    
    # Generate report data based on type
    if report_request.report_type == "compliance_summary":
        # Get dashboard data as report content
        dashboard_data = await get_executive_dashboard(db)
        report_data = dashboard_data.model_dump()
    else:
        report_data = {"message": "Report generation in progress"}
    
    report = Report(
        report_id=report_id,
        report_type=report_request.report_type,
        status=ReportStatus.COMPLETED,
        title_en=titles["en"],
        title_ar=titles["ar"],
        framework_filter=report_request.framework_filter,
        date_range_start=report_request.date_range_start,
        date_range_end=report_request.date_range_end,
        report_data=report_data,
        file_format=report_request.file_format,
        generated_by=report_request.generated_by,
        generated_at=datetime.utcnow(),
    )
    
    db.add(report)
    await db.commit()
    await db.refresh(report)
    
    return report


@router.get("/reports/{report_id}", response_model=ReportResponse)
async def get_report(
    report_id: str,
    db: AsyncSession = Depends(get_db),
):
    """Get a specific report"""
    query = select(Report).where(Report.report_id == report_id)
    result = await db.execute(query)
    report = result.scalar_one_or_none()
    
    if not report:
        raise HTTPException(
            status_code=404,
            detail={
                "message_en": f"Report {report_id} not found",
                "message_ar": f"لم يتم العثور على التقرير {report_id}",
            },
        )
    
    return report


@router.get("/reports", response_model=List[ReportResponse])
async def list_reports(
    db: AsyncSession = Depends(get_db),
):
    """List all generated reports"""
    query = select(Report).order_by(Report.created_at.desc()).limit(50)
    result = await db.execute(query)
    reports = result.scalars().all()
    
    return reports

@router.get("/")
async def list_reports():
    """List all reports"""
    return {"reports": []}


@router.post("/generate")
async def generate_report():
    """Generate new report"""
    return {"status": "generating"}
