from pathlib import Path
import sys
from types import ModuleType, SimpleNamespace

import pytest

from test_sico_call_accounting import OBJECTIVE, REQUIREMENTS, SYSTEMS


DOMAIN_ID = "aaaaaaaa-aaaa-4aaa-8aaa-aaaaaaaaaaaa"
FOREIGN_DOMAIN_ID = "bbbbbbbb-bbbb-4bbb-8bbb-bbbbbbbbbbbb"
FRAMEWORK_ID = "cccccccc-cccc-4ccc-8ccc-cccccccccccc"
FRAMEWORK_NAME = "NIST CSF version 2.0"
FRAMEWORK_REFERENCE = "urn:intuitem:risk:framework:nist-csf-2.0"
ORGANIZATION = "Meridian Logistics Group"


@pytest.fixture
def case_request(monkeypatch, request):
    monkeypatch.syspath_prepend(str(Path(__file__).resolve().parents[1] / "backend"))
    from django.conf import settings

    if not settings.configured:
        original_settings = settings._wrapped
        settings.configure(SECRET_KEY="unit-test-draft-scope-only")
        request.addfinalizer(lambda: setattr(settings, "_wrapped", original_settings))

    from ai_onboarding import llm_provider, sico_case_coverage_views as views

    def fail_provider(*args, **kwargs):
        pytest.fail("Deterministic scaffolding attempted a model provider call")

    monkeypatch.setattr(llm_provider, "get_advisory_provider_selection", fail_provider)
    monkeypatch.setattr(llm_provider.LocalAiProvider, "generate_structured", fail_provider)

    # Replace only the existing database-backed authorization and catalog reads.
    user = SimpleNamespace(pk="test-authenticated-user", is_active=True, is_authenticated=True)
    domain = SimpleNamespace(pk=DOMAIN_ID, name=ORGANIZATION)
    catalog = SimpleNamespace(
        pk=FRAMEWORK_ID, name=FRAMEWORK_NAME, urn=FRAMEWORK_REFERENCE,
        ref_id="NIST-CSF-2.0", library=SimpleNamespace(version=5),
    )
    memberships_checked = []
    lifecycle = ModuleType("ai_onboarding.sico_ai_lifecycle_views")
    lifecycle._scope_candidates = lambda principal, name: (
        [domain] if principal is user and name == ORGANIZATION else []
    )
    lifecycle._framework_candidates = lambda principal, name: (
        [catalog] if principal is user and name == FRAMEWORK_NAME else []
    )
    workflow = ModuleType("ai_onboarding.sico_ai_workflow_views")

    def verify_principal(principal, folder_id):
        assert principal is user
        assert folder_id == DOMAIN_ID
        memberships_checked.append(folder_id)

    workflow.verify_principal = verify_principal
    monkeypatch.setitem(sys.modules, lifecycle.__name__, lifecycle)
    monkeypatch.setitem(sys.modules, workflow.__name__, workflow)

    source_rows = [
        {
            "id": row["requirement_id"],
            "ref_id": row["reference"],
            "name": row["requirement_name"],
            "description": row["description"],
        }
        for row in REQUIREMENTS
    ]
    _, count, digest = views._page_and_digest(source_rows, start=0, batch_size=0)
    assert count == 106

    def load_requirements(principal, framework):
        assert principal is user
        assert framework == FRAMEWORK_NAME
        return {"status": "matched", "framework_id": FRAMEWORK_ID}, iter(source_rows)

    monkeypatch.setattr(views, "_load_authorized_requirements", load_requirements)
    coverage_request = SimpleNamespace(
        user=user,
        data={
            "organization_name": ORGANIZATION,
            "framework_name": FRAMEWORK_NAME,
            "problem": "\n  " + OBJECTIVE + "  \n",
            "source_digest": digest,
        },
    )
    return views, coverage_request, memberships_checked


def test_drafts_are_built_from_authorized_sources_without_model_calls(case_request):
    views, request, memberships_checked = case_request
    response = views.SicoCaseCoveragePlanView().post(request)
    assert response.status_code == 200, response.data
    assert memberships_checked == [DOMAIN_ID]
    plan = response.data
    drafts = {row["activity_number"]: row for row in plan["deterministic_drafts"]}
    assert set(drafts) == {1, 2, 3, 14, 16}
    assert {
        task["draft_reference"] for task in plan["generation_queue"]
        if task["execution_mode"] == "deterministic"
    } <= {row["draft_reference"] for row in drafts.values()}
    assert drafts[1]["model_fields"] == {
        "framework_id": FRAMEWORK_ID,
        "framework_name": FRAMEWORK_NAME,
        "framework_edition": FRAMEWORK_NAME,
        "library_version": 5,
        "source_reference": FRAMEWORK_REFERENCE,
        "source_digest": request.data["source_digest"],
        "requirement_count": 106,
    }
    assert drafts[2]["model_fields"] == {
        "organization_name": ORGANIZATION,
        "objective": {"label": "user-provided objective", "value": request.data["problem"]},
        "assumptions": [{"system": system, "confirmed": False} for system in SYSTEMS],
    }
    assert drafts[3]["model_fields"]["scope_draft_reference"] == drafts[2]["draft_reference"]
    assert drafts[3]["model_fields"]["assessment_status"] == "proposed"
    assert drafts[3]["model_fields"]["framework_name"] == FRAMEWORK_NAME
    assert drafts[3]["model_fields"]["framework_edition"] == FRAMEWORK_NAME
    assert drafts[3]["model_fields"]["library_version"] == 5

    placeholders = plan["requirement_assessment_proposals"]
    assert len(placeholders) == 106
    assert {row["requirement_id"] for row in placeholders} == {
        requirement["requirement_id"] for requirement in REQUIREMENTS
    }
    for row in placeholders:
        assert row["status"] == row["model_fields"]["result"] == "not_assessed"
        assert row["model_fields"]["requirement"] == row["requirement_id"]
        assert row["model_fields"]["observation"] is None
        assert row["compliance_verdict_made"] is False
        assert {"assessment_justification", "evidence_request", "review_method"}.isdisjoint(row)

    for row in [*drafts.values(), *placeholders]:
        assert row["source"] == "sico_deterministic"
        assert row["tenant_id"] == row["organization_id"] == DOMAIN_ID
        assert row["approval_status"] == "not_approved"
        assert row["business_records_written"] is False
    print("5 scaffold drafts; 106 not_assessed placeholders; 0 provider calls")


def test_cross_tenant_ids_rejected_before_scope_lookup(case_request, monkeypatch):
    views, request, memberships_checked = case_request
    request.data.update(tenant_id=FOREIGN_DOMAIN_ID, organization_id=FOREIGN_DOMAIN_ID)

    def fail_source(*args, **kwargs):
        pytest.fail("A request with supplied tenant IDs reached the source loader")

    monkeypatch.setattr(views, "_load_authorized_requirements", fail_source)
    response = views.SicoCaseCoveragePlanView().post(request)
    assert response.status_code == 403
    assert not memberships_checked
    assert response.data["business_records_written"] is False
    print("cross-tenant IDs rejected with 403 before source lookup")
