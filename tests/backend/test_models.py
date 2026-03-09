"""
Tests for controls/models.py — ControlStatus, FrameworkType, LIFECYCLE_TRANSITIONS.
"""
import pytest


def test_control_status_values():
    from controls.models import ControlStatus

    assert ControlStatus.NOT_STARTED.value == "not_started"
    assert ControlStatus.IN_PROGRESS.value == "in_progress"
    assert ControlStatus.COMPLIANT.value == "compliant"
    assert ControlStatus.NON_COMPLIANT.value == "non_compliant"
    assert ControlStatus.NOT_APPLICABLE.value == "not_applicable"


def test_framework_type_values():
    from controls.models import FrameworkType

    assert FrameworkType.ECC.value == "ECC"
    assert FrameworkType.CCC.value == "CCC"
    assert FrameworkType.PDPL.value == "PDPL"


def test_lifecycle_transitions_keys():
    from controls.models import LIFECYCLE_TRANSITIONS, ControlStatus

    # Every status should have an entry
    for status in ControlStatus:
        assert status in LIFECYCLE_TRANSITIONS, f"{status} missing from LIFECYCLE_TRANSITIONS"


def test_not_started_transitions():
    from controls.models import LIFECYCLE_TRANSITIONS, ControlStatus

    allowed = LIFECYCLE_TRANSITIONS[ControlStatus.NOT_STARTED]
    assert ControlStatus.IN_PROGRESS in allowed
    assert ControlStatus.NOT_APPLICABLE in allowed
    assert ControlStatus.COMPLIANT not in allowed


def test_in_progress_transitions():
    from controls.models import LIFECYCLE_TRANSITIONS, ControlStatus

    allowed = LIFECYCLE_TRANSITIONS[ControlStatus.IN_PROGRESS]
    assert ControlStatus.COMPLIANT in allowed
    assert ControlStatus.NON_COMPLIANT in allowed
    assert ControlStatus.NOT_STARTED not in allowed


def test_non_compliant_transitions():
    from controls.models import LIFECYCLE_TRANSITIONS, ControlStatus

    allowed = LIFECYCLE_TRANSITIONS[ControlStatus.NON_COMPLIANT]
    assert ControlStatus.IN_PROGRESS in allowed
    assert ControlStatus.COMPLIANT not in allowed


def test_compliant_transitions():
    from controls.models import LIFECYCLE_TRANSITIONS, ControlStatus

    allowed = LIFECYCLE_TRANSITIONS[ControlStatus.COMPLIANT]
    assert ControlStatus.IN_PROGRESS in allowed
    assert ControlStatus.NON_COMPLIANT in allowed


def test_not_applicable_transitions():
    from controls.models import LIFECYCLE_TRANSITIONS, ControlStatus

    allowed = LIFECYCLE_TRANSITIONS[ControlStatus.NOT_APPLICABLE]
    assert ControlStatus.NOT_STARTED in allowed
    assert len(allowed) == 1


def test_evidence_status_values():
    from evidence.models import EvidenceStatus

    assert EvidenceStatus.PENDING.value == "pending"
    assert EvidenceStatus.COLLECTED.value == "collected"
    assert EvidenceStatus.VALIDATED.value == "validated"
    assert EvidenceStatus.REJECTED.value == "rejected"
    assert EvidenceStatus.EXPIRED.value == "expired"


def test_evidence_type_values():
    from evidence.models import EvidenceType

    assert EvidenceType.POLICY.value == "policy"
    assert EvidenceType.PROCEDURE.value == "procedure"
    assert EvidenceType.LOG.value == "log"
    assert EvidenceType.SCREENSHOT.value == "screenshot"
    assert EvidenceType.REPORT.value == "report"
    assert EvidenceType.CERTIFICATE.value == "certificate"
    assert EvidenceType.OTHER.value == "other"
