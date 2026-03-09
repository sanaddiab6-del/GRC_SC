"""
Tests for the evidence hash computation function (tamper detection).
"""
import hashlib
import pytest


def test_compute_evidence_hash():
    from evidence.router import _compute_evidence_hash
    from evidence.schemas import EvidenceCreate

    data = EvidenceCreate(
        evidence_id="EVD-1",
        control_id="ECC-1",
        evidence_type="policy",
        title_en="Test",
        title_ar="تجريبي",
        file_name="doc.pdf",
        file_size=1024,
    )

    h = _compute_evidence_hash(data)
    assert isinstance(h, str)
    assert len(h) == 64  # SHA-256 hex

    # Verify manually
    payload = "EVD-1|ECC-1|Test|تجريبي|doc.pdf|1024"
    expected = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    assert h == expected


def test_compute_evidence_hash_no_file():
    from evidence.router import _compute_evidence_hash
    from evidence.schemas import EvidenceCreate

    data = EvidenceCreate(
        evidence_id="EVD-2",
        control_id="ECC-2",
        evidence_type="log",
        title_en="Log",
        title_ar="سجل",
    )

    h = _compute_evidence_hash(data)
    # file_name='' file_size=0 in the hash
    payload = "EVD-2|ECC-2|Log|سجل||0"
    expected = hashlib.sha256(payload.encode("utf-8")).hexdigest()
    assert h == expected


def test_compute_evidence_hash_different_inputs():
    from evidence.router import _compute_evidence_hash
    from evidence.schemas import EvidenceCreate

    d1 = EvidenceCreate(
        evidence_id="A",
        control_id="C",
        evidence_type="policy",
        title_en="X",
        title_ar="ي",
    )
    d2 = EvidenceCreate(
        evidence_id="B",
        control_id="C",
        evidence_type="policy",
        title_en="X",
        title_ar="ي",
    )

    assert _compute_evidence_hash(d1) != _compute_evidence_hash(d2)
