"""Shared, fail-closed RBAC visibility helpers for AI onboarding context builders.

Every AI suggestion/commit workflow in this package needs the same guarantee: an authenticated
user must never have an inaccessible object's data read into an LLM prompt, matched against as
a duplicate candidate, or accepted as a valid reference -- regardless of whether the underlying
RBAC lookup itself succeeds. Several modules re-implemented this check independently, and some
of those copies treated a failure of ``RoleAssignment.get_accessible_object_ids`` as "nothing is
restricted" rather than "nothing is visible". These helpers are the single place that decision is
made: any failure to positively determine visibility is treated as "not visible", never as
"visible".
"""

from __future__ import annotations

from typing import Any

from iam.models import Folder, RoleAssignment


def get_viewable_ids(user, model: type) -> frozenset[Any]:
    """RBAC-accessible ids of `model` for `user`.

    Fails closed (returns an empty set) when visibility cannot be positively determined: an
    unauthenticated user, or any failure raised by the underlying RBAC lookup itself.
    """
    if not getattr(user, "is_authenticated", False):
        return frozenset()
    try:
        viewable_ids = RoleAssignment.get_accessible_object_ids(
            Folder.get_root_folder(), user, model
        )[0]
    except Exception:
        return frozenset()
    return frozenset(viewable_ids)


def filter_visible(queryset_or_manager, model: type, user):
    """`queryset_or_manager` restricted to the ids of `model` that `user` can view."""
    return queryset_or_manager.filter(id__in=get_viewable_ids(user, model))


def is_visible_to_user(user, instance) -> bool:
    """True only if `instance` is positively confirmed visible to `user`.

    Fails closed (returns False) when `instance` is None or visibility cannot be determined.
    """
    if instance is None:
        return False
    return str(instance.id) in {
        str(item_id) for item_id in get_viewable_ids(user, type(instance))
    }
