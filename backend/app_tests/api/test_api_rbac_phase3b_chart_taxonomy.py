"""
Phase 3B: reproduction and fix-protection tests for the three confirmed Phase 3A findings:

- AppliedControlViewSet.priority_chart_data (core/views.py): built from
  ``AppliedControl.objects.exclude(status="active")`` with no RBAC filter at all.
- AssetClassViewSet.tree (core/views.py / AssetClass.build_tree in core/models.py): built from
  ``AssetClass.objects.all()`` with no RBAC filter.
- AssetViewSet.asset_class (core/views.py): built from
  ``AssetClass.objects.filter(assets__isnull=False)`` with no RBAC filter.

Each class below proves the cross-folder leak against the unmodified endpoint, proves the fix
denies it while preserving the authorized/privileged/empty/RBAC-failure cases, matching the
project's established ``RoleAssignment.get_accessible_object_ids`` pattern used everywhere else.
"""

import uuid
from unittest import mock

import pytest
from django.conf import settings as django_settings
from knox.models import AuthToken
from rest_framework.test import APIClient

from core.models import AppliedControl, Asset, AssetClass
from iam.models import Folder, Permission, RoleAssignment, Role, User, UserGroup


@pytest.fixture(scope="session")
def django_db_modify_db_settings():
    from pathlib import Path

    import ciso_assistant.settings as settings

    settings.DATABASES["default"]["TEST"]["NAME"] = (
        Path(settings.BASE_DIR)
        / "db"
        / f"test_rbac_phase3b_chart_taxonomy_{uuid.uuid4().hex}.sqlite3"
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


def _make_admin_client() -> APIClient:
    admin = User.objects.create_superuser(
        f"admin-{uuid.uuid4().hex[:8]}@tests.com", is_published=True
    )
    admin_group = UserGroup.objects.get(name="BI-UG-ADM")
    admin.folder = admin_group.folder
    admin.save()
    admin_group.user_set.add(admin)

    client = APIClient()
    auth_token = AuthToken.objects.create(user=admin)[1]
    client.credentials(HTTP_AUTHORIZATION=f"Token {auth_token}")
    return client


def _raises(*args, **kwargs):
    raise RuntimeError("simulated RoleAssignment.get_accessible_object_ids failure")


# ---------------------------------------------------------------------------
# V1 — AppliedControlViewSet.priority_chart_data
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestPriorityChartData:
    def test_cross_folder_control_is_excluded(self):
        hidden = _make_domain_folder("prio-hidden")
        visible = _make_domain_folder("prio-visible")
        AppliedControl.objects.create(
            name="SECRETCONTROL", folder=hidden, status="to_do", priority=1
        )
        client = _make_scoped_client(folder=visible, extra_codenames=["view_appliedcontrol"])

        response = client.get("/api/applied-controls/priority_chart_data/")

        assert response.status_code == 200, response.content
        assert b"SECRETCONTROL" not in response.content

    def test_user_without_any_applied_control_permission_sees_nothing(self):
        folder = _make_domain_folder("prio-noperm")
        AppliedControl.objects.create(
            name="NOPERMCONTROL", folder=folder, status="to_do", priority=1
        )
        client = _make_scoped_client(folder=folder, extra_codenames=[])

        response = client.get("/api/applied-controls/priority_chart_data/")

        assert response.status_code == 200, response.content
        assert b"NOPERMCONTROL" not in response.content

    def test_authorized_user_still_sees_own_control(self):
        visible = _make_domain_folder("prio-positive")
        AppliedControl.objects.create(
            name="OWNCONTROL", folder=visible, status="to_do", priority=1
        )
        client = _make_scoped_client(folder=visible, extra_codenames=["view_appliedcontrol"])

        response = client.get("/api/applied-controls/priority_chart_data/")

        assert response.status_code == 200, response.content
        assert b"OWNCONTROL" in response.content

    def test_privileged_superuser_sees_everything(self):
        folder = _make_domain_folder("prio-admin")
        AppliedControl.objects.create(
            name="ADMINVISIBLECONTROL", folder=folder, status="to_do", priority=1
        )
        client = _make_admin_client()

        response = client.get("/api/applied-controls/priority_chart_data/")

        assert response.status_code == 200, response.content
        assert b"ADMINVISIBLECONTROL" in response.content

    def test_no_controls_returns_empty_shape(self):
        folder = _make_domain_folder("prio-empty")
        client = _make_scoped_client(folder=folder, extra_codenames=["view_appliedcontrol"])

        response = client.get("/api/applied-controls/priority_chart_data/")

        assert response.status_code == 200, response.content
        data = response.json()
        assert data["to_do"] == []
        assert data["priority_cnt"] == {"p1": 0, "p2": 0, "p3": 0, "p4": 0}

    def test_rbac_helper_failure_returns_no_data(self):
        folder = _make_domain_folder("prio-rbacfail")
        AppliedControl.objects.create(
            name="RBACFAILCONTROL", folder=folder, status="to_do", priority=1
        )
        client = _make_scoped_client(folder=folder, extra_codenames=["view_appliedcontrol"])
        client.raise_request_exception = False

        with mock.patch.object(
            RoleAssignment, "get_accessible_object_ids", side_effect=_raises
        ):
            response = client.get("/api/applied-controls/priority_chart_data/")

        assert response.status_code == 500, response.status_code
        assert b"RBACFAILCONTROL" not in response.content


# ---------------------------------------------------------------------------
# V2A — AssetClassViewSet.tree
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestAssetClassTree:
    def test_hidden_assetclass_excluded(self):
        hidden = _make_domain_folder("tree-hidden")
        visible = _make_domain_folder("tree-visible")
        AssetClass.objects.create(name="SECRETCLASSTREE", folder=hidden)
        client = _make_scoped_client(folder=visible, extra_codenames=["view_assetclass"])

        response = client.get("/api/asset-class/tree/")

        assert response.status_code == 200, response.content
        assert b"SECRETCLASSTREE" not in response.content

    def test_child_of_hidden_parent_is_not_exposed(self):
        hidden = _make_domain_folder("tree-hidden-parent")
        visible = _make_domain_folder("tree-visible-child")
        parent = AssetClass.objects.create(name="SECRETPARENTTREE", folder=hidden)
        AssetClass.objects.create(name="VISIBLECHILDTREE", parent=parent, folder=visible)
        client = _make_scoped_client(folder=visible, extra_codenames=["view_assetclass"])

        response = client.get("/api/asset-class/tree/")

        assert response.status_code == 200, response.content
        assert b"SECRETPARENTTREE" not in response.content
        # The child's own ancestor chain includes a node the user cannot see; it must not be
        # silently reparented to root either, since that would still disclose that *something*
        # exists above it. Dropping it entirely is the safe behavior.
        assert b"VISIBLECHILDTREE" not in response.content

    def test_authorized_user_sees_own_parent_child_chain(self):
        visible = _make_domain_folder("tree-positive")
        parent = AssetClass.objects.create(name="OWNPARENTTREE", folder=visible)
        AssetClass.objects.create(name="OWNCHILDTREE", parent=parent, folder=visible)
        client = _make_scoped_client(folder=visible, extra_codenames=["view_assetclass"])

        response = client.get("/api/asset-class/tree/")

        assert response.status_code == 200, response.content
        assert b"OWNPARENTTREE" in response.content
        assert b"OWNCHILDTREE" in response.content

    def test_privileged_superuser_sees_everything(self):
        folder = _make_domain_folder("tree-admin")
        AssetClass.objects.create(name="ADMINVISIBLETREE", folder=folder)
        client = _make_admin_client()

        response = client.get("/api/asset-class/tree/")

        assert response.status_code == 200, response.content
        assert b"ADMINVISIBLETREE" in response.content

    def test_rbac_helper_failure_returns_empty_tree(self):
        folder = _make_domain_folder("tree-rbacfail")
        AssetClass.objects.create(name="RBACFAILTREE", folder=folder)
        client = _make_scoped_client(folder=folder, extra_codenames=["view_assetclass"])
        client.raise_request_exception = False

        with mock.patch.object(
            RoleAssignment, "get_accessible_object_ids", side_effect=_raises
        ):
            response = client.get("/api/asset-class/tree/")

        assert response.status_code == 500, response.status_code
        assert b"RBACFAILTREE" not in response.content


# ---------------------------------------------------------------------------
# V2B — AssetViewSet.asset_class
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestAssetAssetClassChoices:
    def _make_class_with_asset(self, *, folder: Folder, marker: str) -> AssetClass:
        asset_class = AssetClass.objects.create(name=marker, folder=folder)
        Asset.objects.create(name=f"{marker}-asset", folder=folder, asset_class=asset_class)
        return asset_class

    def test_hidden_assetclass_excluded(self):
        hidden = _make_domain_folder("ac-choices-hidden")
        visible = _make_domain_folder("ac-choices-visible")
        self._make_class_with_asset(folder=hidden, marker="SECRETCLASSCHOICE")
        client = _make_scoped_client(
            folder=visible, extra_codenames=["view_asset", "view_assetclass"]
        )

        response = client.get("/api/assets/asset_class/")

        assert response.status_code == 200, response.content
        assert b"SECRETCLASSCHOICE" not in response.content

    def test_authorized_user_sees_own_assetclass(self):
        visible = _make_domain_folder("ac-choices-positive")
        self._make_class_with_asset(folder=visible, marker="OWNCLASSCHOICE")
        client = _make_scoped_client(
            folder=visible, extra_codenames=["view_asset", "view_assetclass"]
        )

        response = client.get("/api/assets/asset_class/")

        assert response.status_code == 200, response.content
        assert b"OWNCLASSCHOICE" in response.content

    def test_privileged_superuser_sees_everything(self):
        folder = _make_domain_folder("ac-choices-admin")
        self._make_class_with_asset(folder=folder, marker="ADMINVISIBLECHOICE")
        client = _make_admin_client()

        response = client.get("/api/assets/asset_class/")

        assert response.status_code == 200, response.content
        assert b"ADMINVISIBLECHOICE" in response.content

    def test_no_matching_classes_returns_empty_list(self):
        folder = _make_domain_folder("ac-choices-empty")
        client = _make_scoped_client(
            folder=folder, extra_codenames=["view_asset", "view_assetclass"]
        )

        response = client.get("/api/assets/asset_class/")

        assert response.status_code == 200, response.content
        assert response.json() == []

    def test_rbac_helper_failure_returns_no_data(self):
        folder = _make_domain_folder("ac-choices-rbacfail")
        self._make_class_with_asset(folder=folder, marker="RBACFAILCHOICE")
        client = _make_scoped_client(
            folder=folder, extra_codenames=["view_asset", "view_assetclass"]
        )
        client.raise_request_exception = False

        with mock.patch.object(
            RoleAssignment, "get_accessible_object_ids", side_effect=_raises
        ):
            response = client.get("/api/assets/asset_class/")

        assert response.status_code == 500, response.status_code
        assert b"RBACFAILCHOICE" not in response.content
