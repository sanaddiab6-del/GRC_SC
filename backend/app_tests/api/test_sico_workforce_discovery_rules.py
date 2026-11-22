"""Pure, DB-free tests for conservative name and identity resolution."""
import pytest

from ai_onboarding.workforce_discovery_rules import (
    DiscoveryInputError, bounded_title, choose_single_exact_domain,
    classify_name_match, clean_hint, framework_terms, prepare_grounded_next_checks,
)


def test_exact_casefolded_whitespace():
    assert classify_name_match(" Al-Rawasi  FINTECH ", "al-rawasi fintech") == "exact"


def test_partial_match_requires_human_confirmation():
    assert classify_name_match("Al-Rawasi Fintech Division", "Al-Rawasi Fintech") == "possible"


def test_unrelated_name_not_matched():
    assert classify_name_match("Company A", "Company B") == "none"


def test_blank_never_matches():
    assert classify_name_match("", "X") == "none"


def test_one_exact_folder_is_selected():
    assert choose_single_exact_domain([{"id": "A", "match": "exact"}]) == "A"


def test_ambiguous_exact_folders_are_not_selected():
    assert choose_single_exact_domain([{"id": "A", "match": "exact"}, {"id": "B", "match": "exact"}]) is None


def test_partial_folder_not_auto_selected():
    assert choose_single_exact_domain([{"id": "A", "match": "possible"}]) is None


def test_terms_include_nca_ecc():
    assert "nca" in framework_terms("NCA ECC-1:2018") and "ecc" in framework_terms("NCA ECC-1:2018")


def test_untrusted_input_is_bounded():
    assert len(clean_hint("x" * 500, 150)) == 150


def test_title_is_bounded():
    assert bounded_title("a" * 200) == "a" * 160


def test_input_type_is_checked():
    with pytest.raises(DiscoveryInputError):
        clean_hint(["anything"])


def test_no_org_candidate_recommends_access_check_not_create():
    checks = prepare_grounded_next_checks("no_readable_domain_match", [], {})
    assert any("Confirm spelling" in x["message"] for x in checks)
    assert not any("Create the domain" in x["message"] for x in checks)

def test_existing_domain_with_missing_records_is_scoped():
    checks = prepare_grounded_next_checks("exact_existing_domain", [{"match": "exact"}], {"assets": []})
    assert any("child domains and permissions" in x["message"] for x in checks)

def test_ambiguous_framework_does_not_auto_approve():
    checks = prepare_grounded_next_checks("exact_existing_domain", [{"match":"possible"}], {"assets":[{"id": "1"}]})
    assert any("regulatory validation" in x["message"] for x in checks)
