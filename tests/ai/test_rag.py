# AI/RAG Tests - Retriever, Chunker, Control Loader
import json
import os
import pytest
from pathlib import Path

from ai.rag.bilingual_retriever import BilingualRetriever
from ai.rag.chunker import ControlChunker
from ai.rag.control_loader import (
    controls_to_documents,
    load_all_frameworks_as_documents,
    load_control_library,
    get_library_stats,
)

# Repo root for locating data files in tests
REPO_ROOT = Path(__file__).resolve().parents[2]


def test_control_chunker():
    """Test control chunking for RAG"""
    chunker = ControlChunker(chunk_size=512, chunk_overlap=128)

    control_data = {
        "control_id": "ECC-GV-1",
        "framework": "ECC",
        "domain": "Governance",
        "title_en": "Governance Framework",
        "title_ar": "إطار الحوكمة",
        "description_en": "Test description in English",
        "description_ar": "وصف الاختبار بالعربية",
        "policy_guidance_en": "Policy guidance text",
        "policy_guidance_ar": "نص توجيهات السياسة",
    }

    chunks = chunker.chunk_control(control_data)

    assert len(chunks) >= 2  # At least description and policy chunks
    assert all(hasattr(chunk, "page_content") for chunk in chunks)
    assert all(hasattr(chunk, "metadata") for chunk in chunks)

    # Check metadata
    first_chunk = chunks[0]
    assert first_chunk.metadata["control_id"] == "ECC-GV-1"
    assert first_chunk.metadata["framework"] == "ECC"
    assert "section" in first_chunk.metadata


def test_chunker_batch_processing():
    """Test batch chunking of multiple controls"""
    chunker = ControlChunker()

    controls = [
        {
            "control_id": f"ECC-GV-{i}",
            "framework": "ECC",
            "domain": "Governance",
            "title_en": f"Control {i}",
            "title_ar": f"ضابط {i}",
            "description_en": f"Description {i}",
            "description_ar": f"وصف {i}",
        }
        for i in range(1, 6)
    ]

    all_chunks = chunker.chunk_batch(controls)

    assert len(all_chunks) >= 5  # At least one chunk per control

    # Check that all control IDs are present
    control_ids = {chunk.metadata["control_id"] for chunk in all_chunks}
    assert len(control_ids) == 5


# --- Control Library Loader tests ---

def test_load_ecc_control_library():
    """Test loading the ECC JSON control library from the repo."""
    library = load_control_library("ECC")
    assert library["framework"] == "ECC"
    assert len(library["controls"]) > 0
    # Verify bilingual fields on first control
    first = library["controls"][0]
    assert "title_en" in first
    assert "title_ar" in first
    assert "description_en" in first
    assert "control_id" in first


def test_load_ccc_control_library():
    """Test loading the CCC JSON control library from the repo."""
    library = load_control_library("CCC")
    assert library["framework"] == "CCC"
    assert len(library["controls"]) > 0


def test_load_pdpl_control_library():
    """Test loading the PDPL JSON control library from the repo."""
    library = load_control_library("PDPL")
    assert library["framework"] == "PDPL"
    assert len(library["controls"]) > 0


def test_controls_to_documents_bilingual():
    """Test converting controls to Documents with both languages."""
    controls = [
        {
            "control_id": "ECC-1-1-1",
            "framework": "ECC",
            "domain": "Cybersecurity Governance",
            "title_en": "Cybersecurity Strategy",
            "title_ar": "استراتيجية الأمن السيبراني",
            "description_en": "A cybersecurity strategy must be defined.",
            "description_ar": "يجب تحديد استراتيجية للأمن السيبراني.",
        }
    ]
    docs = controls_to_documents(controls, language="both")
    assert len(docs) == 1
    assert "cybersecurity strategy" in docs[0].page_content.lower()
    assert "استراتيجية" in docs[0].page_content
    assert docs[0].metadata["section"] == "description"
    assert docs[0].metadata["framework"] == "ECC"


def test_controls_to_documents_language_en():
    """Test that English-only mode returns only English content."""
    controls = [
        {
            "control_id": "ECC-1-1-1",
            "framework": "ECC",
            "domain": "Cybersecurity Governance",
            "title_en": "Cybersecurity Strategy",
            "title_ar": "استراتيجية الأمن السيبراني",
            "description_en": "A cybersecurity strategy must be defined.",
            "description_ar": "يجب تحديد استراتيجية للأمن السيبراني.",
        }
    ]
    docs = controls_to_documents(controls, language="en")
    assert "cybersecurity strategy" in docs[0].page_content.lower()
    assert "استراتيجية" not in docs[0].page_content


def test_load_all_frameworks_as_documents():
    """Test loading all frameworks into Document objects (Repo Mode)."""
    docs = load_all_frameworks_as_documents(frameworks=["ECC", "CCC", "PDPL"])
    assert len(docs) > 0
    frameworks_in_docs = {doc.metadata["framework"] for doc in docs}
    assert "ECC" in frameworks_in_docs
    assert "CCC" in frameworks_in_docs
    assert "PDPL" in frameworks_in_docs


def test_get_library_stats():
    """Test that library stats returns info for all three frameworks."""
    stats = get_library_stats()
    for fw in ("ECC", "CCC", "PDPL"):
        assert fw in stats
        assert stats[fw].get("available") is not False  # library files should exist
        assert stats[fw].get("total_controls", 0) > 0


# --- Data file integrity tests ---

def test_ecc_controls_json_structure():
    """Validate ECC controls JSON has required fields on each control."""
    library = load_control_library("ECC")
    for ctrl in library["controls"]:
        assert "control_id" in ctrl, f"Missing control_id: {ctrl}"
        assert "framework" in ctrl
        assert ctrl["framework"] == "ECC"
        assert "description_en" in ctrl


def test_ccc_controls_json_structure():
    """Validate CCC controls JSON has required fields."""
    library = load_control_library("CCC")
    for ctrl in library["controls"]:
        assert "control_id" in ctrl
        assert ctrl["framework"] == "CCC"
        assert "description_en" in ctrl


def test_pdpl_controls_json_structure():
    """Validate PDPL controls JSON has required fields."""
    library = load_control_library("PDPL")
    for ctrl in library["controls"]:
        assert "control_id" in ctrl
        assert ctrl["framework"] == "PDPL"
        assert "description_en" in ctrl


def test_evidence_catalog_structure():
    """Validate the evidence catalog has all required evidence types."""
    catalog_path = REPO_ROOT / "data" / "evidence" / "evidence_catalog.json"
    assert catalog_path.exists(), "evidence_catalog.json not found"
    with open(catalog_path, encoding="utf-8") as f:
        catalog = json.load(f)
    assert "evidence_types" in catalog
    assert len(catalog["evidence_types"]) > 5
    for ev in catalog["evidence_types"]:
        assert "evidence_id" in ev
        assert "name_en" in ev
        assert "name_ar" in ev
        assert "applicable_frameworks" in ev


def test_evidence_policy_structure():
    """Validate evidence_policy.json has the expected structure."""
    policy_path = REPO_ROOT / "data" / "evidence" / "evidence_policy.json"
    assert policy_path.exists(), "evidence_policy.json not found"
    with open(policy_path, encoding="utf-8") as f:
        policy = json.load(f)
    assert "policy_name" in policy
    assert "policy_name_ar" in policy
    assert "principles" in policy
    assert len(policy["principles"]) > 0
    assert "retention_schedule" in policy


def test_cross_framework_mapping_structure():
    """Validate cross_framework_mapping.json has baseline and delta sections."""
    mapping_path = REPO_ROOT / "data" / "mappings" / "cross_framework_mapping.json"
    assert mapping_path.exists(), "cross_framework_mapping.json not found"
    with open(mapping_path, encoding="utf-8") as f:
        mapping = json.load(f)
    assert "baseline_mappings" in mapping
    assert len(mapping["baseline_mappings"]) > 0
    assert "delta_controls" in mapping
    assert "ECC_only" in mapping["delta_controls"]
    assert "CCC_only" in mapping["delta_controls"]
    assert "PDPL_only" in mapping["delta_controls"]
    # Each baseline mapping has primary + mapped_to
    for m in mapping["baseline_mappings"]:
        assert "primary" in m
        assert "mapped_to" in m
        assert len(m["mapped_to"]) > 0


@pytest.mark.skip(reason="Requires vector database and embedding model setup")
def test_bilingual_retriever():
    """Test bilingual retriever (requires Chroma setup)"""
    retriever = BilingualRetriever()
    # This would require actual vector database setup
    # Skipped in unit tests, would run in integration tests
    pass
