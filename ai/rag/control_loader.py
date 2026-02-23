"""
Control Library Loader for RAG (Repo Mode)
Loads controls from the structured JSON library files and prepares them for vector indexing.
Supports ECC, CCC, and PDPL frameworks with bilingual content.
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass


# Gracefully import Document - fall back to dataclass if langchain unavailable
try:
    from langchain.schema import Document  # type: ignore[import-not-found]
    _LANGCHAIN_AVAILABLE = True
except ImportError:
    @dataclass
    class Document:  # type: ignore[no-redef]
        page_content: str
        metadata: Dict[str, Any]
    _LANGCHAIN_AVAILABLE = False


# Default path to control libraries relative to repo root
_REPO_ROOT = Path(__file__).resolve().parents[2]
_DATA_DIR = _REPO_ROOT / "data"
_CONTROLS_DIR = _DATA_DIR / "controls"

CONTROL_LIBRARY_FILES: Dict[str, str] = {
    "ECC": str(_CONTROLS_DIR / "ecc_controls.json"),
    "CCC": str(_CONTROLS_DIR / "ccc_controls.json"),
    "PDPL": str(_CONTROLS_DIR / "pdpl_controls.json"),
}


def load_control_library(framework: str, path: Optional[str] = None) -> Dict[str, Any]:
    """
    Load a control library JSON file for the given framework.

    Args:
        framework: One of 'ECC', 'CCC', 'PDPL'
        path: Optional override path to the JSON file

    Returns:
        Parsed library dict with 'controls' list
    """
    file_path = path or CONTROL_LIBRARY_FILES.get(framework.upper())
    if not file_path:
        raise ValueError(f"Unknown framework: {framework}. Supported: ECC, CCC, PDPL")

    if not os.path.exists(file_path):
        raise FileNotFoundError(
            f"Control library file not found: {file_path}. "
            "Run scripts/build_rag_index.py to initialize the index."
        )

    with open(file_path, encoding="utf-8") as f:
        return json.load(f)


def controls_to_documents(
    controls: List[Dict[str, Any]],
    language: str = "both",
) -> List[Document]:
    """
    Convert control dicts to RAG Document objects with bilingual content.

    Each control produces up to 3 documents:
    - description chunk (always)
    - policy guidance chunk (if present)
    - procedure guidance chunk (if present)

    Args:
        controls: List of control dicts from the JSON library
        language: 'en', 'ar', or 'both' (default) - determines chunk content

    Returns:
        List of Document objects ready for vector store indexing
    """
    docs: List[Document] = []

    for ctrl in controls:
        control_id = ctrl.get("control_id", "")
        framework = ctrl.get("framework", "")
        base_meta = {
            "control_id": control_id,
            "framework": framework,
            "domain": ctrl.get("domain", ""),
            "title_en": ctrl.get("title_en", ""),
            "title_ar": ctrl.get("title_ar", ""),
        }

        desc_en = ctrl.get("description_en", "")
        desc_ar = ctrl.get("description_ar", "")

        # Description chunk
        if language == "en":
            content = desc_en
        elif language == "ar":
            content = desc_ar
        else:
            content = f"{desc_en}\n\n{desc_ar}" if desc_ar else desc_en

        if content.strip():
            docs.append(Document(
                page_content=content,
                metadata={**base_meta, "section": "description"},
            ))

        # Policy guidance chunk (ECC uses policy_guidance_en/ar)
        pol_en = ctrl.get("policy_guidance_en", "")
        pol_ar = ctrl.get("policy_guidance_ar", "")
        if pol_en or pol_ar:
            if language == "en":
                pol_content = pol_en
            elif language == "ar":
                pol_content = pol_ar
            else:
                pol_content = f"{pol_en}\n\n{pol_ar}" if pol_ar else pol_en
            if pol_content.strip():
                docs.append(Document(
                    page_content=pol_content,
                    metadata={**base_meta, "section": "policy"},
                ))

        # Procedure guidance chunk
        proc_en = ctrl.get("procedure_guidance_en", "")
        proc_ar = ctrl.get("procedure_guidance_ar", "")
        if proc_en or proc_ar:
            if language == "en":
                proc_content = proc_en
            elif language == "ar":
                proc_content = proc_ar
            else:
                proc_content = f"{proc_en}\n\n{proc_ar}" if proc_ar else proc_en
            if proc_content.strip():
                docs.append(Document(
                    page_content=proc_content,
                    metadata={**base_meta, "section": "procedure"},
                ))

    return docs


def load_all_frameworks_as_documents(
    frameworks: Optional[List[str]] = None,
    language: str = "both",
) -> List[Document]:
    """
    Load controls from all (or specified) frameworks and return as Documents.

    Args:
        frameworks: List of framework names to load. Defaults to ['ECC', 'CCC', 'PDPL'].
        language: 'en', 'ar', or 'both'

    Returns:
        Combined list of Documents from all frameworks
    """
    if frameworks is None:
        frameworks = ["ECC", "CCC", "PDPL"]

    all_docs: List[Document] = []
    for fw in frameworks:
        try:
            library = load_control_library(fw)
            controls = library.get("controls", [])
            docs = controls_to_documents(controls, language=language)
            all_docs.extend(docs)
        except FileNotFoundError:
            pass  # Framework library not yet available; skip gracefully

    return all_docs


def get_library_stats() -> Dict[str, Any]:
    """Return statistics about available control libraries."""
    stats: Dict[str, Any] = {}
    for fw, path in CONTROL_LIBRARY_FILES.items():
        if os.path.exists(path):
            with open(path, encoding="utf-8") as f:
                lib = json.load(f)
            stats[fw] = {
                "total_controls": lib.get("total_controls", len(lib.get("controls", []))),
                "version": lib.get("version", ""),
                "last_updated": lib.get("last_updated", ""),
            }
        else:
            stats[fw] = {"available": False}
    return stats
