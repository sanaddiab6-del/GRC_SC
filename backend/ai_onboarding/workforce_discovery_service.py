"""Read-only, RBAC-scoped SICO discovery of ACTUAL GRC database records.

No model calls, external uploads, arbitrary SQL, document bytes, cross-folder data,
or writes. This produces source-backed candidate records, NOT an audit verdict.

Tenant boundary: organizational records are fetched only by an explicitly matched,
readable Folder ID, then each record is checked using the platform's object RBAC.
Global framework-library entries are also checked for object-read permission.
Production multi-tenant rollout additionally requires company-isolation regression tests.
"""
from __future__ import annotations

from django.db.models import Q
from django.http import Http404

from core.models import (
    AppliedControl, Asset, ComplianceAssessment, Evidence, Framework,
    Perimeter, RiskAssessment, Vulnerability,
)
from iam.models import Folder, RoleAssignment

from .workforce_discovery_rules import (
    bounded_title, choose_single_exact_domain, classify_name_match, clean_hint,
    framework_terms, prepare_grounded_next_checks,
)

# Operational bound; never scan or return an unbounded organization-wide dataset.
SCAN_LIMIT = 250
RETURN_LIMIT = 12


def _readable(user, model, object_id):
    return bool(RoleAssignment.is_object_readable(user, model, object_id))


def _visible_candidates(user, model, candidates, *, max_items=RETURN_LIMIT):
    result = []
    for obj in candidates:
        if not _readable(user, model, obj.pk):
            continue
        result.append({"id": str(obj.pk), "name": bounded_title(obj.name)})
        if len(result) >= max_items:
            break
    return result


def _find_domains(user, organization):
    # Restrict lookups to the specified organization's name, never all tenant folders.
    queryset = Folder.objects.filter(name__icontains=organization).order_by("name", "id")[:SCAN_LIMIT + 1]
    truncated = len(queryset) > SCAN_LIMIT
    results = []
    for obj in list(queryset)[:SCAN_LIMIT]:
        if not _readable(user, Folder, obj.pk):
            continue
        match = classify_name_match(obj.name, organization)
        if match == "none":
            continue
        results.append({"id": str(obj.pk), "name": bounded_title(obj.name), "match": match})
        if len(results) >= RETURN_LIMIT:
            truncated = True
            break
    return results, truncated


def _find_frameworks(user, hint):
    terms = framework_terms(hint)
    if not terms:
        return [], False
    # Candidate search covers framework name, code and URN. Results are hints, not regulatory advice.
    q = Q()
    for term in terms:
        q |= Q(name__icontains=term) | Q(ref_id__icontains=term) | Q(urn__icontains=term)
    raw = list(Framework.objects.filter(q).order_by("name", "id")[:SCAN_LIMIT + 1])
    truncated = len(raw) > SCAN_LIMIT
    result = []
    for framework in raw[:SCAN_LIMIT]:
        if not _readable(user, Framework, framework.pk):
            continue
        result.append({
            "id": str(framework.pk),
            "name": bounded_title(framework.name),
            "reference": bounded_title(framework.ref_id, 100),
            "urn": bounded_title(framework.urn, 255),
            "match": classify_name_match(framework.name, hint),
            "assessable_requirements": framework.requirement_nodes.filter(assessable=True).count(),
        })
        if len(result) >= RETURN_LIMIT:
            truncated = True
            break
    return result, truncated


def _scoped_category(user, model, folder_id, *, exclude_policy=False):
    # Explicit folder_id prevents mixing different company workspaces.
    queryset = model.objects.filter(folder_id=folder_id).order_by("name", "id")
    if exclude_policy:
        queryset = queryset.exclude(category="policy")
    raw = list(queryset[:SCAN_LIMIT + 1])
    truncated = len(raw) > SCAN_LIMIT
    return _visible_candidates(user, model, raw[:SCAN_LIMIT]), truncated


def discover_existing_grc_records(user, *, organization, framework_hint="", selected_folder_id=None):
    organization = clean_hint(organization)
    framework_hint = clean_hint(framework_hint)
    if len(organization) < 3:
        raise ValueError("Provide an organization name of at least 3 characters.")

    folders, folders_truncated = _find_domains(user, organization)
    frameworks, frameworks_truncated = _find_frameworks(user, framework_hint)
    # Automatic selection is safe only for one EXACT permitted name match.
    auto_folder = choose_single_exact_domain(folders)
    selected = None
    if selected_folder_id:
        selected = next((x for x in folders if x["id"] == str(selected_folder_id)), None)
        if selected is None:
            # Do not reveal if the requested ID exists elsewhere.
            raise Http404("Organization not found or not accessible.")
        if not _readable(user, Folder, selected["id"]):
            raise Http404("Organization not found or not accessible.")
    elif auto_folder and not folders_truncated:
        selected = next(x for x in folders if x["id"] == auto_folder)

    categories = {}
    truncated_categories = []
    if selected:
        for name, model, exclude_policy in (
            ("perimeters", Perimeter, False),
            ("assets", Asset, False),
            ("applied_controls", AppliedControl, True),
            ("policies", AppliedControl, False),
            ("vulnerabilities", Vulnerability, False),
            ("evidences", Evidence, False),
            ("risk_assessments", RiskAssessment, False),
            ("compliance_assessments", ComplianceAssessment, False),
        ):
            if name == "policies":
                raw = list(AppliedControl.objects.filter(folder_id=selected["id"], category="policy").order_by("name", "id")[:SCAN_LIMIT + 1])
                categories[name] = _visible_candidates(user, AppliedControl, raw[:SCAN_LIMIT])
                if len(raw) > SCAN_LIMIT:
                    truncated_categories.append(name)
            else:
                categories[name], truncated = _scoped_category(
                    user, model, selected["id"], exclude_policy=exclude_policy
                )
                if truncated:
                    truncated_categories.append(name)

    status = "exact_existing_domain" if selected and selected["match"] == "exact" else (
        "selected_possible_domain" if selected else (
            "ambiguous_or_partial_match" if folders else "no_readable_domain_match"
        )
    )
    # Root-level parent candidates for explicit NEW-domain preparation.
    # The helper checks both read and add-folder permission, never writes.
    from .workforce_case_plan_service import readable_domain_parents
    create_domain_parents = readable_domain_parents(user)
    warnings = []
    if folders_truncated or frameworks_truncated or truncated_categories:
        warnings.append("Results are limited. Do not conclude an item is absent from a truncated list.")
    if not selected:
        warnings.append("No organizational folder was selected: scoped assets, policies and assessments have NOT been searched.")
    if selected and selected["match"] != "exact":
        warnings.append("The selected organization is only a possible name match. Confirm before any write operation.")
    if framework_hint and not frameworks:
        warnings.append("No readable loaded framework candidates matched the hint. This is NOT proof the standard is unavailable.")
    return {
        "kind": "sico_grounded_grc_discovery_v1",
        "mode": "database_lookup_no_llm",
        "organization_requested": organization,
        "framework_requested": framework_hint,
        "domain_status": status,
        "domain_candidates": folders,
        "new_domain_parent_options": create_domain_parents,
        "selected_domain": selected,
        "framework_candidates": frameworks,
        "records_by_category": categories,
        "scan_limited": folders_truncated or frameworks_truncated or bool(truncated_categories),
        "next_checks": prepare_grounded_next_checks(status, frameworks, categories),
        "warnings": warnings,
        "caveats": [
            "Only records readable by this user are returned.",
            "Organizational data is restricted to the selected exact Folder, not its descendants.",
            "Record names are not evidence of security effectiveness or compliance.",
            "No attachment content or confidential document text was examined.",
            "No AI model inferred findings; this is a verified database inventory.",
        ],
        "writes_performed": False,
    }
