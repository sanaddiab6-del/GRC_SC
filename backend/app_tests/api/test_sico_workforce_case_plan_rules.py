"""Pure business-rule tests, separate from DB-integrated permission tests."""
import pytest
from ai_onboarding.workforce_case_plan_rules import (
    CasePlanInputError, exact_organization_match, normalize_name,
    proposed_case_names, readiness_label, safe_error_codes,
)


def test_normalization():
    assert normalize_name('  Al-Rawasi   Fintech  ') == 'Al-Rawasi Fintech'


def test_exact_organization_ignore_case():
    assert exact_organization_match('Al-Rawasi Fintech', 'al-rawasi fintech')


def test_partial_not_exact():
    assert not exact_organization_match('Al-Rawasi Fintech Division','Al-Rawasi Fintech')


def test_nonmatching_company_not_exact():
    assert not exact_organization_match('Other Company','Al-Rawasi Fintech')


def test_blank_not_exact():
    assert not exact_organization_match('', 'Al-Rawasi Fintech')


def test_generate_case_names():
    out=proposed_case_names('Al-Rawasi Fintech','Banking access management','Essential Cybersecurity Controls')
    assert out['domain']=='Al-Rawasi Fintech'
    assert out['perimeter'].startswith('Al-Rawasi Fintech - Banking access')
    assert out['assessment_version']=='1.0'
    assert 'Essential Cybersecurity Controls' in out['assessment']


def test_name_lengths():
    out=proposed_case_names('T'*100,'S'*200,'F'*100)
    assert len(out['perimeter'])<=160 and len(out['assessment'])<=160


@pytest.mark.parametrize('org,scope,framework',[
    ('','Access management','NCA ECC'), ('AB','Access management','NCA ECC'),
    ('Company','a','NCA ECC'), ('Company','Access management','AB'),
])
def test_incomplete_proposal_blocked(org,scope,framework):
    with pytest.raises(CasePlanInputError):
        proposed_case_names(org,scope,framework)


def test_invalid_text_type_blocked():
    with pytest.raises(CasePlanInputError):
        normalize_name(['Company'])


def test_status_blocked_with_any_blocker():
    assert readiness_label([{'code':'permission_denied'}]) == 'blocked'


def test_status_always_review_when_no_blockers():
    assert readiness_label([]) == 'review_required'


def test_no_object_ids_in_error_codes():
    assert safe_error_codes([{'code':'blocked'},{'code':'blocked'},{'code':'missing'}]) == ['blocked','missing']
