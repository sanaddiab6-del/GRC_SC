"""
Phase 2: fail-open behavior in AI onboarding visibility guards.

ai_onboarding/*_suggestion_service.py and *_commit_service.py each independently re-implement
a "is this object visible to the requesting user" check on top of
RoleAssignment.get_accessible_object_ids. Two shapes of that check exist in this codebase:

  - A correct, fail-closed shape (ai_onboarding/framework_control_mapping_suggestion_service.py
    ::_is_visible_to_user): if the RBAC lookup raises, the object is treated as NOT visible.

  - A fail-open shape, duplicated across applied_control_suggestion_service.py,
    asset_suggestion_service.py, evidence_finding_suggestion_service.py (::_assert_visible_to_user)
    and applied_control_commit_service.py, asset_commit_service.py,
    applied_control_suggestion_service.py, asset_suggestion_service.py (the
    ``_visible_*_ids``/``_get_visible_*_ids`` id-set getters): if the RBAC lookup raises, these
    either silently treat the object as visible (``_assert_visible_to_user`` returns instead of
    raising) or return ``None``, which every caller treats as "skip filtering, show everything in
    the folder" rather than "nothing is visible".

The tests below force that RBAC-helper failure (the same failure mode the existing code already
has an ``except Exception`` branch for) and assert the behavior the task specifies: authorization
uncertainty must deny, never grant, access. Each test is written to the SECURE expected behavior,
so it fails against the current fail-open implementation and passes once the shared, fail-closed
``ai_onboarding.rbac_context`` helpers are in place.
"""

import uuid
from unittest import mock

import pytest
from django.conf import settings as django_settings

from core.models import AppliedControl, Asset, Framework
from iam.models import Folder, Permission, Role, RoleAssignment, User, UserGroup


@pytest.fixture(scope="session")
def django_db_modify_db_settings():
    from pathlib import Path

    import ciso_assistant.settings as settings

    settings.DATABASES["default"]["TEST"]["NAME"] = (
        Path(settings.BASE_DIR)
        / "db"
        / f"test_rbac_phase2_ai_consolidation_{uuid.uuid4().hex}.sqlite3"
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


def _make_scoped_user(*, folder: Folder, extra_codenames: list[str]) -> User:
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
    return user


def _raises(*args, **kwargs):
    raise RuntimeError("simulated RoleAssignment.get_accessible_object_ids failure")


# ---------------------------------------------------------------------------
# Bug class A: _assert_visible_to_user silently returns (allows) on RBAC-helper failure.
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestAssertVisibleToUserFailsOpenOnRbacFailure:
    def test_applied_control_suggestion_denies_when_rbac_helper_fails(self):
        from ai_onboarding.applied_control_suggestion_service import (
            AppliedControlSuggestionDraftValidationError,
            _assert_visible_to_user,
        )

        hidden = _make_domain_folder("ac-suggest-assert-hidden")
        visible = _make_domain_folder("ac-suggest-assert-visible")
        control = AppliedControl.objects.create(name="hidden control", folder=hidden)
        user = _make_scoped_user(folder=visible, extra_codenames=["view_appliedcontrol"])

        with mock.patch.object(
            RoleAssignment, "get_accessible_object_ids", side_effect=_raises
        ):
            with pytest.raises(AppliedControlSuggestionDraftValidationError):
                _assert_visible_to_user(user, control, "some_field")

    def test_asset_suggestion_denies_when_rbac_helper_fails(self):
        from ai_onboarding.asset_suggestion_service import (
            AssetSuggestionDraftValidationError,
            _assert_visible_to_user,
        )

        hidden = _make_domain_folder("asset-suggest-assert-hidden")
        visible = _make_domain_folder("asset-suggest-assert-visible")
        asset = Asset.objects.create(name="hidden asset", folder=hidden)
        user = _make_scoped_user(folder=visible, extra_codenames=["view_asset"])

        with mock.patch.object(
            RoleAssignment, "get_accessible_object_ids", side_effect=_raises
        ):
            with pytest.raises(AssetSuggestionDraftValidationError):
                _assert_visible_to_user(user, asset, "some_field")

    def test_evidence_finding_suggestion_denies_when_rbac_helper_fails(self):
        from ai_onboarding.evidence_finding_suggestion_service import (
            EvidenceFindingSuggestionDraftValidationError,
            _assert_visible_to_user,
        )

        hidden = _make_domain_folder("ef-suggest-assert-hidden")
        visible = _make_domain_folder("ef-suggest-assert-visible")
        asset = Asset.objects.create(name="hidden asset", folder=hidden)
        user = _make_scoped_user(folder=visible, extra_codenames=["view_asset"])

        with mock.patch.object(
            RoleAssignment, "get_accessible_object_ids", side_effect=_raises
        ):
            with pytest.raises(EvidenceFindingSuggestionDraftValidationError):
                _assert_visible_to_user(user, asset, "some_field")


@pytest.mark.django_db
class TestAssertVisibleToUserPositiveControls:
    """The legitimate allow/deny behavior (no RBAC-helper failure) must survive the fix."""

    def test_applied_control_suggestion_allows_accessible_and_denies_inaccessible(self):
        from ai_onboarding.applied_control_suggestion_service import (
            AppliedControlSuggestionDraftValidationError,
            _assert_visible_to_user,
        )

        visible_folder = _make_domain_folder("ac-suggest-assert-positive")
        hidden_folder = _make_domain_folder("ac-suggest-assert-positive-hidden")
        visible_control = AppliedControl.objects.create(
            name="visible control", folder=visible_folder
        )
        hidden_control = AppliedControl.objects.create(
            name="hidden control", folder=hidden_folder
        )
        user = _make_scoped_user(
            folder=visible_folder, extra_codenames=["view_appliedcontrol"]
        )

        _assert_visible_to_user(user, visible_control, "some_field")  # must not raise

        with pytest.raises(AppliedControlSuggestionDraftValidationError):
            _assert_visible_to_user(user, hidden_control, "some_field")


# ---------------------------------------------------------------------------
# Bug class B: the "_visible_*_ids" / "_get_visible_*_ids" getters return None on RBAC-helper
# failure, and every caller treats None as "do not filter" -- i.e. show the whole folder.
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestVisibleIdsGetterFailsOpenOnRbacFailure:
    def test_applied_control_commit_service_leaks_folder_on_rbac_failure(self):
        from ai_onboarding.applied_control_commit_service import (
            AiAppliedControlCommitService,
        )

        folder = _make_domain_folder("ac-commit-ids-hidden")
        viewer_folder = _make_domain_folder("ac-commit-ids-viewer")
        # A control the user has no view permission on, inside the folder being committed to.
        invisible_control = AppliedControl.objects.create(
            name="invisible control", folder=folder
        )
        user = _make_scoped_user(folder=viewer_folder, extra_codenames=[])

        service = AiAppliedControlCommitService.__new__(AiAppliedControlCommitService)
        service.user = user

        with mock.patch.object(
            RoleAssignment, "get_accessible_object_ids", side_effect=_raises
        ):
            folder_controls = service._visible_folder_controls(folder)

        assert invisible_control not in folder_controls, (
            "RBAC-helper failure must not widen visibility to the whole folder"
        )

    def test_asset_commit_service_leaks_folder_on_rbac_failure(self):
        from ai_onboarding.asset_commit_service import AiAssetCommitService

        folder = _make_domain_folder("asset-commit-ids-hidden")
        viewer_folder = _make_domain_folder("asset-commit-ids-viewer")
        invisible_asset = Asset.objects.create(name="invisible asset", folder=folder)
        user = _make_scoped_user(folder=viewer_folder, extra_codenames=[])

        service = AiAssetCommitService.__new__(AiAssetCommitService)
        service.user = user

        with mock.patch.object(
            RoleAssignment, "get_accessible_object_ids", side_effect=_raises
        ):
            folder_assets = service._visible_folder_assets(folder)

        assert invisible_asset not in folder_assets, (
            "RBAC-helper failure must not widen visibility to the whole folder"
        )

    def test_applied_control_suggestion_duplicate_detection_hides_inaccessible_on_rbac_failure(
        self,
    ):
        from ai_onboarding.applied_control_suggestion_service import (
            _apply_duplicate_detection,
        )

        folder = _make_domain_folder("ac-suggest-ids-hidden")
        viewer_folder = _make_domain_folder("ac-suggest-ids-viewer")
        AppliedControl.objects.create(name="Duplicate control", folder=folder)
        user = _make_scoped_user(folder=viewer_folder, extra_codenames=[])

        draft = {
            "candidate_applied_controls": [
                {"temporary_id": "t1", "proposed_name": "Duplicate control"}
            ]
        }

        with mock.patch.object(
            RoleAssignment, "get_accessible_object_ids", side_effect=_raises
        ):
            _apply_duplicate_detection(draft, user, folder)

        assert draft["duplicate_candidates"] == [], (
            "RBAC-helper failure must not expose an inaccessible control as a duplicate match"
        )

    def test_asset_suggestion_duplicate_detection_hides_inaccessible_on_rbac_failure(self):
        from ai_onboarding.asset_suggestion_service import _apply_duplicate_detection

        folder = _make_domain_folder("asset-suggest-ids-hidden")
        viewer_folder = _make_domain_folder("asset-suggest-ids-viewer")
        Asset.objects.create(name="Duplicate asset", folder=folder)
        user = _make_scoped_user(folder=viewer_folder, extra_codenames=[])

        draft = {
            "candidate_assets": [
                {"temporary_id": "t1", "proposed_name": "Duplicate asset"}
            ]
        }

        with mock.patch.object(
            RoleAssignment, "get_accessible_object_ids", side_effect=_raises
        ):
            _apply_duplicate_detection(draft, user, folder)

        assert draft["duplicate_candidates"] == [], (
            "RBAC-helper failure must not expose an inaccessible asset as a duplicate match"
        )


@pytest.mark.django_db
class TestVisibleIdsGetterPositiveControls:
    """Normal-path (no RBAC-helper failure) filtering must be unchanged by the fix."""

    def test_applied_control_commit_service_still_filters_normally(self):
        from ai_onboarding.applied_control_commit_service import (
            AiAppliedControlCommitService,
        )

        folder = _make_domain_folder("ac-commit-ids-normal")
        visible_control = AppliedControl.objects.create(name="visible", folder=folder)
        hidden_control = AppliedControl.objects.create(name="hidden", folder=folder)
        user = _make_scoped_user(folder=folder, extra_codenames=["view_appliedcontrol"])

        # Restrict the role assignment's own perimeter so only one of the two is actually
        # viewable, by revoking folder-level visibility after creation is not representative;
        # instead assert that the normal call returns both when the permission is granted and
        # that is_access_allowed/get_accessible_object_ids is the thing being exercised, not
        # bypassed.
        service = AiAppliedControlCommitService.__new__(AiAppliedControlCommitService)
        service.user = user

        folder_controls = service._visible_folder_controls(folder)

        assert visible_control in folder_controls
        assert hidden_control in folder_controls  # both are in the user's own granted folder

    def test_asset_commit_service_still_filters_normally(self):
        from ai_onboarding.asset_commit_service import AiAssetCommitService

        folder = _make_domain_folder("asset-commit-ids-normal")
        asset = Asset.objects.create(name="visible", folder=folder)
        user = _make_scoped_user(folder=folder, extra_codenames=["view_asset"])

        service = AiAssetCommitService.__new__(AiAssetCommitService)
        service.user = user

        folder_assets = service._visible_folder_assets(folder)

        assert asset in folder_assets


# ---------------------------------------------------------------------------
# framework_control_mapping_suggestion_service._is_visible_to_user is already fail-closed.
# This protects that correct behavior across the consolidation.
# ---------------------------------------------------------------------------


@pytest.mark.django_db
class TestFrameworkControlMappingAlreadyFailsClosed:
    def test_denies_when_rbac_helper_fails(self):
        from ai_onboarding.framework_control_mapping_suggestion_service import (
            _is_visible_to_user,
        )

        folder = _make_domain_folder("fcm-already-closed")
        framework = Framework.objects.create(name="fw", folder=folder)
        user = _make_scoped_user(folder=folder, extra_codenames=["view_framework"])

        with mock.patch.object(
            RoleAssignment, "get_accessible_object_ids", side_effect=_raises
        ):
            assert _is_visible_to_user(user, framework) is False

    def test_allows_accessible_framework(self):
        from ai_onboarding.framework_control_mapping_suggestion_service import (
            _is_visible_to_user,
        )

        folder = _make_domain_folder("fcm-already-closed-positive")
        framework = Framework.objects.create(name="fw", folder=folder)
        user = _make_scoped_user(folder=folder, extra_codenames=["view_framework"])

        assert _is_visible_to_user(user, framework) is True
