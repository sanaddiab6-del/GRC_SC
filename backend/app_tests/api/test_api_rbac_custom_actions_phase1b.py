"""
Phase 1B triage tests for custom DRF actions that resolve protected objects without the
standard RBAC path (``self.get_object()`` / RBAC-filtered ``get_queryset()``) and without an
explicit ``get_accessible_object_ids`` / ``is_access_allowed`` / ``is_object_readable`` check.

Each class targets one candidate that the static triage classified as needing runtime proof.
A negative test is only meaningful against the unmodified code if it fails because the
inaccessible object's data is returned; a positive test proves the authorized path still works.
"""

import datetime
import uuid

import pytest
from django.conf import settings as django_settings
from knox.models import AuthToken
from rest_framework.test import APIClient

from core.models import (
    ComplianceAssessment,
    Framework,
    RequirementNode,
    StoredLibrary,
    Terminology,
)
from core.models import HistoricalMetric, RiskMatrix
from ebios_rm.models import EbiosRMStudy, Stakeholder
from iam.models import Folder, Permission, Role, RoleAssignment, User, UserGroup
from integrations.models import IntegrationProvider
from tprm.models import Entity


@pytest.fixture(scope="session")
def django_db_modify_db_settings():
    from pathlib import Path

    import ciso_assistant.settings as settings

    settings.DATABASES["default"]["TEST"]["NAME"] = (
        Path(settings.BASE_DIR)
        / "db"
        / f"test_rbac_custom_actions_phase1b_{uuid.uuid4().hex}.sqlite3"
    )


@pytest.fixture(autouse=True)
def app_config():
    original_allowed_hosts = list(django_settings.ALLOWED_HOSTS)
    django_settings.ALLOWED_HOSTS = [*original_allowed_hosts, "testserver"]
    try:
        yield
    finally:
        django_settings.ALLOWED_HOSTS = original_allowed_hosts


def _make_domain_folder(name: str) -> Folder:
    return Folder.objects.create(
        name=f"{name}-{uuid.uuid4().hex[:6]}",
        content_type=Folder.ContentType.DOMAIN,
        builtin=False,
        parent_folder=Folder.objects.get(content_type=Folder.ContentType.ROOT),
    )


def _make_scoped_client(*, folder: Folder, extra_codenames: list[str]) -> APIClient:
    """Non-admin user whose only grant is the given codenames inside `folder`."""
    user = User.objects.create_user(
        f"scoped-{uuid.uuid4().hex[:8]}@tests.com", is_published=True
    )
    role = Role.objects.create(name=f"scoped-role-{uuid.uuid4().hex[:8]}")
    role.permissions.set(
        Permission.objects.filter(codename__in=["view_folder", *extra_codenames])
    )
    role.save()
    role_assignment = RoleAssignment.objects.create(
        user=user, role=role, folder=folder, is_recursive=True
    )
    role_assignment.perimeter_folders.add(folder)
    role_assignment.save()

    client = APIClient()
    auth_token = AuthToken.objects.create(user=user)[1]
    client.credentials(HTTP_AUTHORIZATION=f"Token {auth_token}")
    return client


def _make_framework(*, folder: Folder, marker: str) -> tuple[Framework, RequirementNode]:
    framework = Framework.objects.create(
        name=f"{marker}-framework",
        urn=f"urn:phase1b:fw:{uuid.uuid4().hex}",
        ref_id=marker,
        folder=folder,
    )
    node = RequirementNode.objects.create(
        framework=framework,
        urn=f"urn:phase1b:rn:{uuid.uuid4().hex}",
        ref_id=f"{marker}-1",
        name=f"{marker}-requirement",
        assessable=True,
        folder=folder,
    )
    return framework, node


@pytest.mark.django_db
class TestFrameworkTreeAndTemplate:
    """Candidates: FrameworkViewSet.tree, FrameworkViewSet.excel_template."""

    def test_cross_folder_user_cannot_read_framework_tree(self):
        hidden = _make_domain_folder("hidden-fw")
        visible = _make_domain_folder("visible-fw")
        hidden_fw, _ = _make_framework(folder=hidden, marker="SECRETFWTREE")
        client = _make_scoped_client(
            folder=visible, extra_codenames=["view_framework"]
        )

        response = client.get(f"/api/frameworks/{hidden_fw.id}/tree/")

        assert response.status_code in (403, 404), response.content
        assert b"SECRETFWTREE" not in response.content

    def test_inaccessible_and_nonexistent_framework_tree_are_indistinguishable(self):
        hidden = _make_domain_folder("hidden-fw-oracle")
        visible = _make_domain_folder("visible-fw-oracle")
        hidden_fw, _ = _make_framework(folder=hidden, marker="ORACLEFW")
        client = _make_scoped_client(
            folder=visible, extra_codenames=["view_framework"]
        )

        inaccessible = client.get(f"/api/frameworks/{hidden_fw.id}/tree/")
        nonexistent = client.get(f"/api/frameworks/{uuid.uuid4()}/tree/")

        assert inaccessible.status_code == nonexistent.status_code, (
            inaccessible.status_code,
            nonexistent.status_code,
        )

    def test_authorized_user_can_read_framework_tree(self):
        visible = _make_domain_folder("visible-fw-positive")
        fw, _ = _make_framework(folder=visible, marker="PUBLICFWTREE")
        client = _make_scoped_client(
            folder=visible, extra_codenames=["view_framework"]
        )

        response = client.get(f"/api/frameworks/{fw.id}/tree/")

        assert response.status_code == 200, response.content
        assert b"PUBLICFWTREE" in response.content

    def test_cross_folder_user_cannot_export_framework_excel_template(self):
        hidden = _make_domain_folder("hidden-fw-xlsx")
        visible = _make_domain_folder("visible-fw-xlsx")
        hidden_fw, _ = _make_framework(folder=hidden, marker="SECRETFWXLSX")
        client = _make_scoped_client(
            folder=visible, extra_codenames=["view_framework"]
        )

        response = client.get(f"/api/frameworks/{hidden_fw.id}/excel_template/")

        assert response.status_code in (403, 404), response.status_code

    def test_authorized_user_can_export_framework_excel_template(self):
        visible = _make_domain_folder("visible-fw-xlsx-positive")
        fw, _ = _make_framework(folder=visible, marker="PUBLICFWXLSX")
        client = _make_scoped_client(
            folder=visible, extra_codenames=["view_framework"]
        )

        response = client.get(f"/api/frameworks/{fw.id}/excel_template/")

        assert response.status_code == 200, response.status_code


@pytest.mark.django_db
class TestFrameworkMappingStats:
    """Candidate: FrameworkViewSet.mapping_stats — Framework.objects.filter(id=pk) then coverage
    by URN, no RBAC on the framework."""

    def test_cross_folder_user_cannot_read_mapping_stats(self):
        hidden = _make_domain_folder("hidden-fw-mapping")
        visible = _make_domain_folder("visible-fw-mapping")
        hidden_fw, _ = _make_framework(folder=hidden, marker="SECRETFWMAP")
        client = _make_scoped_client(
            folder=visible, extra_codenames=["view_framework"]
        )

        response = client.get(f"/api/frameworks/{hidden_fw.id}/mapping_stats/")

        assert response.status_code in (403, 404), response.status_code

    def test_authorized_user_can_read_mapping_stats(self):
        visible = _make_domain_folder("visible-fw-mapping-positive")
        fw, _ = _make_framework(folder=visible, marker="PUBLICFWMAP")
        client = _make_scoped_client(
            folder=visible, extra_codenames=["view_framework"]
        )

        response = client.get(f"/api/frameworks/{fw.id}/mapping_stats/")

        assert response.status_code == 200, response.status_code


@pytest.mark.django_db
@pytest.mark.xfail(
    reason=(
        "Unrelated defect: core/views.py FrameworkViewSet.names calls "
        "framework.get_name_translated() but it is a property, so every request 500s "
        "before returning data. RBAC exposure cannot be demonstrated until that is fixed."
    ),
    strict=False,
)
class TestFrameworkNames:
    """Candidate: FrameworkViewSet.names — Framework.objects.filter(id__in=...) with no RBAC."""

    def test_cross_folder_user_cannot_resolve_framework_name_by_id(self):
        hidden = _make_domain_folder("hidden-fw-names")
        visible = _make_domain_folder("visible-fw-names")
        hidden_fw, _ = _make_framework(folder=hidden, marker="SECRETFWNAME")
        client = _make_scoped_client(
            folder=visible, extra_codenames=["view_framework"]
        )

        response = client.get(f"/api/frameworks/names/?id[]={hidden_fw.id}")

        assert response.status_code == 200, response.content
        assert str(hidden_fw.id) not in response.json(), response.json()

    def test_authorized_user_can_resolve_framework_name_by_id(self):
        visible = _make_domain_folder("visible-fw-names-positive")
        fw, _ = _make_framework(folder=visible, marker="PUBLICFWNAME")
        client = _make_scoped_client(
            folder=visible, extra_codenames=["view_framework"]
        )

        response = client.get(f"/api/frameworks/names/?id[]={fw.id}")

        assert response.status_code == 200, response.content
        assert str(fw.id) in response.json(), response.json()


@pytest.mark.django_db
class TestComplianceAssessmentProgressTs:
    """Candidate: ComplianceAssessmentViewSet.progress_ts — HistoricalMetric by object_id, no RBAC."""

    def _make_assessment_with_history(self, *, folder: Folder) -> ComplianceAssessment:
        framework = Framework.objects.create(
            name=f"fw-{uuid.uuid4().hex[:6]}", folder=folder
        )
        audit = ComplianceAssessment.objects.create(
            name="Confidential audit", framework=framework, folder=folder
        )
        HistoricalMetric.objects.update_or_create(
            model="ComplianceAssessment",
            object_id=audit.id,
            date=datetime.date.today() - datetime.timedelta(days=1),
            defaults={"data": {"reqs": {"progress_perc": 73}}},
        )
        return audit

    def test_cross_folder_user_cannot_read_progress_history(self):
        hidden = _make_domain_folder("hidden-audit-progress")
        visible = _make_domain_folder("visible-audit-progress")
        audit = self._make_assessment_with_history(folder=hidden)
        client = _make_scoped_client(
            folder=visible, extra_codenames=["view_complianceassessment"]
        )

        response = client.get(f"/api/compliance-assessments/{audit.id}/progress_ts/")

        assert response.status_code in (403, 404) or response.json().get("data") == [], (
            response.json()
        )
        assert b"73" not in response.content

    def test_authorized_user_can_read_progress_history(self):
        visible = _make_domain_folder("visible-audit-progress-positive")
        audit = self._make_assessment_with_history(folder=visible)
        client = _make_scoped_client(
            folder=visible, extra_codenames=["view_complianceassessment"]
        )

        response = client.get(f"/api/compliance-assessments/{audit.id}/progress_ts/")

        assert response.status_code == 200, response.content
        assert response.json()["data"], response.json()


@pytest.mark.django_db
class TestEbiosEcosystemCharts:
    """Candidates: EbiosRMStudyViewSet.ecosystem_chart_data / ecosystem_circular_chart_data —
    Stakeholder.objects.filter(ebios_rm_study=pk), no RBAC on the study."""

    def _make_study_with_stakeholder(self, *, folder: Folder, marker: str) -> EbiosRMStudy:
        matrix = RiskMatrix.objects.create(
            name=f"{marker}-matrix",
            urn=f"urn:phase1b:rm:{uuid.uuid4().hex}",
            ref_id=marker,
            folder=folder,
            json_definition={
                "grid": [[0]],
                "probability": [{"abbreviation": "1", "name": "low", "value": 1}],
                "impact": [{"abbreviation": "1", "name": "low", "value": 1}],
                "risk": [{"abbreviation": "1", "name": "low", "value": 1}],
            },
        )
        study = EbiosRMStudy.objects.create(
            name=f"{marker}-study", folder=folder, risk_matrix=matrix
        )
        entity = Entity.objects.create(name=f"{marker}-entity", folder=folder)
        category = Terminology.objects.get(
            name="supplier", field_path=Terminology.FieldPath.ENTITY_RELATIONSHIP
        )
        Stakeholder.objects.create(
            entity=entity,
            category=category,
            ebios_rm_study=study,
            folder=folder,
        )
        return study

    @pytest.mark.parametrize(
        "suffix", ["ecosystem_chart_data", "ecosystem_circular_chart_data"]
    )
    def test_cross_folder_user_cannot_read_study_stakeholders(self, suffix):
        hidden = _make_domain_folder("hidden-ebios")
        visible = _make_domain_folder("visible-ebios")
        study = self._make_study_with_stakeholder(folder=hidden, marker="SECRETSTAKE")
        client = _make_scoped_client(
            folder=visible, extra_codenames=["view_ebiosrmstudy"]
        )

        response = client.get(f"/api/ebios-rm/studies/{study.id}/{suffix}/")

        assert response.status_code in (403, 404), response.status_code
        assert b"SECRETSTAKE" not in response.content

    @pytest.mark.parametrize(
        "suffix", ["ecosystem_chart_data", "ecosystem_circular_chart_data"]
    )
    def test_authorized_user_can_read_study_stakeholders(self, suffix):
        visible = _make_domain_folder("visible-ebios-positive")
        study = self._make_study_with_stakeholder(folder=visible, marker="PUBLICSTAKE")
        client = _make_scoped_client(
            folder=visible,
            extra_codenames=["view_ebiosrmstudy", "view_stakeholder", "view_entity"],
        )

        response = client.get(f"/api/ebios-rm/studies/{study.id}/{suffix}/")

        assert response.status_code == 200, response.content


@pytest.mark.django_db
class TestGeneralSettingsEnabledIntegrations:
    """Candidate: GeneralSettingsViewSet.object — enabled_integrations is built from every
    active IntegrationProvider, with no folder filtering."""

    def test_cross_folder_user_cannot_see_integration_from_hidden_folder(self):
        hidden = _make_domain_folder("hidden-integration")
        visible = _make_domain_folder("visible-integration")
        IntegrationProvider.objects.create(
            name="SECRETITSMPROVIDER",
            provider_type=IntegrationProvider.ProviderType.ITSM,
            is_active=True,
            folder=hidden,
        )
        client = _make_scoped_client(
            folder=visible, extra_codenames=["view_integrationprovider"]
        )

        response = client.get("/api/settings/general/object/")

        assert response.status_code == 200, response.content
        assert b"SECRETITSMPROVIDER" not in response.content

    def test_authorized_user_sees_integration_from_accessible_folder(self):
        visible = _make_domain_folder("visible-integration-positive")
        IntegrationProvider.objects.create(
            name="PUBLICITSMPROVIDER",
            provider_type=IntegrationProvider.ProviderType.ITSM,
            is_active=True,
            folder=visible,
        )
        client = _make_scoped_client(
            folder=visible, extra_codenames=["view_integrationprovider"]
        )

        response = client.get("/api/settings/general/object/")

        assert response.status_code == 200, response.content
        assert b"PUBLICITSMPROVIDER" in response.content


def _make_mapping_libraries(marker: str) -> StoredLibrary:
    """Source/target framework libraries plus a mapping library, all in the root folder."""
    uid = uuid.uuid4().hex[:8]
    src_fw_urn = f"urn:phase1b:fw:src:{uid}"
    tgt_fw_urn = f"urn:phase1b:fw:tgt:{uid}"

    def _framework_content(fw_urn: str, label: str) -> dict:
        return {
            "framework": {
                "urn": fw_urn,
                "name": f"{marker}-{label}",
                "ref_id": label,
                "requirement_nodes": [
                    {
                        "urn": f"{fw_urn}:1",
                        "ref_id": "1",
                        "name": f"{marker}-{label}-REQ",
                        "assessable": True,
                    }
                ],
            }
        }

    StoredLibrary.objects.create(
        name=f"{marker}-src-lib",
        urn=f"urn:phase1b:lib:src:{uid}",
        version=1,
        content=_framework_content(src_fw_urn, "SRC"),
    )
    StoredLibrary.objects.create(
        name=f"{marker}-tgt-lib",
        urn=f"urn:phase1b:lib:tgt:{uid}",
        version=1,
        content=_framework_content(tgt_fw_urn, "TGT"),
    )
    return StoredLibrary.objects.create(
        name=f"{marker}-mapping-lib",
        urn=f"urn:phase1b:lib:map:{uid}",
        version=1,
        content={
            "requirement_mapping_sets": [
                {
                    "source_framework_urn": src_fw_urn,
                    "target_framework_urn": tgt_fw_urn,
                    "requirement_mappings": [],
                }
            ]
        },
    )


@pytest.mark.django_db
class TestRequirementMappingGraphLibrary:
    """Candidate: RequirementMappingSetViewSet.graph_data — StoredLibrary.objects.get(id=pk) and
    unfiltered framework-library lookups, no RBAC check on the library."""

    def test_standard_library_list_hides_root_library_from_scoped_user(self):
        mapping_lib = _make_mapping_libraries("LISTPROBE")
        visible = _make_domain_folder("visible-lib-list")
        client = _make_scoped_client(
            folder=visible, extra_codenames=["view_storedlibrary"]
        )

        response = client.get("/api/stored-libraries/")

        assert response.status_code == 200, response.content
        assert str(mapping_lib.id) not in str(response.json()), response.json()

    def test_scoped_user_cannot_read_mapping_graph_of_inaccessible_library(self):
        mapping_lib = _make_mapping_libraries("SECRETGRAPH")
        visible = _make_domain_folder("visible-lib-graph")
        client = _make_scoped_client(
            folder=visible, extra_codenames=["view_storedlibrary"]
        )

        response = client.get(
            f"/api/requirement-mapping-sets/{mapping_lib.id}/graph_data/"
        )

        assert response.status_code in (403, 404), response.status_code
        assert b"SECRETGRAPH" not in response.content
