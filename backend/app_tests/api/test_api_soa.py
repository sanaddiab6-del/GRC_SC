"""
Tests for Statement of Applicability (ISO 27001:2022 §6.1.3):
  - StatementOfApplicability and SoAEntry model creation
  - generate_soa management command
  - soa_export_pdf API action (PDF export, 404 without SoA, 401 unauthenticated)
"""

import pytest
from io import StringIO
from unittest.mock import patch, MagicMock

from django.core.management import call_command
from django.core.management.base import CommandError
from rest_framework.test import APIClient

from core.models import (
    ComplianceAssessment,
    Framework,
    RequirementNode,
    RequirementAssessment,
    StatementOfApplicability,
    SoAEntry,
)
from iam.models import Folder


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _make_ca(name="Test CA") -> tuple:
    """Return (folder, framework, compliance_assessment) for use in tests."""
    folder = Folder.objects.create(name=f"soa-test-folder-{name}")
    framework = Framework.objects.create(
        name="ISO 27001:2022 Test",
        folder=folder,
        min_score=0,
        max_score=100,
    )
    ca = ComplianceAssessment.objects.create(
        name=name,
        folder=folder,
        framework=framework,
        min_score=0,
        max_score=100,
    )
    return folder, framework, ca


# ---------------------------------------------------------------------------
# Model tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_statement_of_applicability_create():
    """StatementOfApplicability can be created and links to a ComplianceAssessment."""
    folder, framework, ca = _make_ca("SoA Model Test")
    soa = StatementOfApplicability.objects.create(
        name="SoA v1",
        folder=folder,
        compliance_assessment=ca,
        version="1.0",
        status=StatementOfApplicability.Status.DRAFT,
    )
    assert soa.pk is not None
    assert str(soa) == "SoA v1 v1.0"
    assert ca.statement_of_applicability == soa


@pytest.mark.django_db
def test_soa_entry_create():
    """SoAEntry can be created and linked to a StatementOfApplicability."""
    folder, framework, ca = _make_ca("SoA Entry Test")
    req_node = RequirementNode.objects.create(
        name="Control A.5.1",
        folder=folder,
        assessable=True,
    )
    ra = RequirementAssessment.objects.create(
        folder=folder,
        compliance_assessment=ca,
        requirement=req_node,
        result=RequirementAssessment.Result.COMPLIANT,
    )
    soa = StatementOfApplicability.objects.create(
        name="SoA for entries",
        folder=folder,
        compliance_assessment=ca,
        version="1.0",
    )
    entry = SoAEntry.objects.create(
        statement=soa,
        requirement_assessment=ra,
        folder=folder,
        applicability=SoAEntry.Applicability.APPLICABLE,
        justification="Required by policy",
    )
    assert entry.pk is not None
    assert entry.applicability == SoAEntry.Applicability.APPLICABLE
    assert soa.entries.count() == 1


@pytest.mark.django_db
def test_soa_entry_unique_together():
    """Creating a duplicate SoAEntry raises IntegrityError."""
    from django.db import IntegrityError

    folder, framework, ca = _make_ca("SoA Unique Test")
    req_node = RequirementNode.objects.create(
        name="Control A.5.2", folder=folder, assessable=True
    )
    ra = RequirementAssessment.objects.create(
        folder=folder,
        compliance_assessment=ca,
        requirement=req_node,
    )
    soa = StatementOfApplicability.objects.create(
        name="SoA unique", folder=folder, compliance_assessment=ca, version="1.0"
    )
    SoAEntry.objects.create(statement=soa, requirement_assessment=ra, folder=folder)
    with pytest.raises(IntegrityError):
        SoAEntry.objects.create(
            statement=soa, requirement_assessment=ra, folder=folder
        )


# ---------------------------------------------------------------------------
# Management command tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_generate_soa_command_creates_soa_and_entries():
    """generate_soa command creates SoA with entries for assessable requirements."""
    folder, framework, ca = _make_ca("generate_soa CA")

    # Create two assessable RequirementNodes and their RequirementAssessments
    for i in range(2):
        node = RequirementNode.objects.create(
            name=f"Req {i}", folder=folder, assessable=True
        )
        RequirementAssessment.objects.create(
            folder=folder, compliance_assessment=ca, requirement=node
        )

    out = StringIO()
    call_command("generate_soa", compliance_assessment_id=str(ca.id), stdout=out)

    soa = StatementOfApplicability.objects.get(compliance_assessment=ca)
    assert soa.version == "1.0"
    assert soa.entries.count() == 2
    assert "Created" in out.getvalue()


@pytest.mark.django_db
def test_generate_soa_command_not_applicable_propagation():
    """generate_soa marks entry as NOT_APPLICABLE when RequirementAssessment is n/a."""
    folder, framework, ca = _make_ca("generate_soa NA CA")
    node = RequirementNode.objects.create(name="NA Req", folder=folder, assessable=True)
    RequirementAssessment.objects.create(
        folder=folder,
        compliance_assessment=ca,
        requirement=node,
        result=RequirementAssessment.Result.NOT_APPLICABLE,
    )

    call_command("generate_soa", compliance_assessment_id=str(ca.id))

    soa = StatementOfApplicability.objects.get(compliance_assessment=ca)
    entry = soa.entries.first()
    assert entry.applicability == SoAEntry.Applicability.NOT_APPLICABLE


@pytest.mark.django_db
def test_generate_soa_command_invalid_id():
    """generate_soa raises CommandError for non-existent ComplianceAssessment."""
    with pytest.raises(CommandError, match="not found"):
        call_command(
            "generate_soa",
            compliance_assessment_id="00000000-0000-0000-0000-000000000000",
        )


@pytest.mark.django_db
def test_generate_soa_command_idempotent():
    """Running generate_soa twice updates rather than duplicates entries."""
    folder, framework, ca = _make_ca("idempotent CA")
    node = RequirementNode.objects.create(name="Req X", folder=folder, assessable=True)
    RequirementAssessment.objects.create(
        folder=folder, compliance_assessment=ca, requirement=node
    )

    call_command("generate_soa", compliance_assessment_id=str(ca.id))
    call_command("generate_soa", compliance_assessment_id=str(ca.id))

    assert StatementOfApplicability.objects.filter(compliance_assessment=ca).count() == 1
    soa = StatementOfApplicability.objects.get(compliance_assessment=ca)
    assert soa.entries.count() == 1


# ---------------------------------------------------------------------------
# API endpoint tests
# ---------------------------------------------------------------------------


@pytest.mark.django_db
def test_soa_export_pdf_no_soa_returns_404(authenticated_client):
    """soa_export_pdf returns 404 when no SoA exists for the assessment."""
    folder, framework, ca = _make_ca("PDF 404 CA")
    url = f"/api/compliance-assessments/{ca.id}/soa_export_pdf/"
    response = authenticated_client.get(url)
    assert response.status_code == 404
    assert "error" in response.json()


@pytest.mark.django_db
@patch("weasyprint.HTML")
def test_soa_export_pdf_returns_pdf(mock_html_cls, authenticated_client):
    """soa_export_pdf returns HTTP 200 with Content-Type application/pdf."""
    # Make WeasyPrint return dummy bytes to avoid rendering overhead
    mock_html_instance = MagicMock()
    mock_html_instance.write_pdf.return_value = b"%PDF-1.4 fake"
    mock_html_cls.return_value = mock_html_instance

    folder, framework, ca = _make_ca("PDF Export CA")
    soa = StatementOfApplicability.objects.create(
        name="SoA PDF", folder=folder, compliance_assessment=ca, version="1.0"
    )

    url = f"/api/compliance-assessments/{ca.id}/soa_export_pdf/"
    response = authenticated_client.get(url)
    assert response.status_code == 200
    assert response["Content-Type"] == "application/pdf"
    assert response["Content-Disposition"].startswith("attachment; filename=")


@pytest.mark.django_db
def test_soa_export_pdf_unauthenticated_returns_401():
    """soa_export_pdf requires authentication."""
    folder, framework, ca = _make_ca("PDF Unauth CA")
    StatementOfApplicability.objects.create(
        name="SoA Unauth", folder=folder, compliance_assessment=ca, version="1.0"
    )

    unauthenticated = APIClient()
    url = f"/api/compliance-assessments/{ca.id}/soa_export_pdf/"
    response = unauthenticated.get(url)
    assert response.status_code in (401, 403)
