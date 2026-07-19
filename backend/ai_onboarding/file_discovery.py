from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Iterable


FRAMEWORK_FILE_HINTS = ("framework", "control", "compliance", "standard")
SCOPE_FILE_HINTS = ("scope", "folder", "perimeter", "tenant", "boundary")
MINIMAL_SCOPE_FALLBACK = (
    "backend/core/base_models.py",
    "backend/core/models.py",
    "backend/iam/models.py",
)


def _resolve_root(base_dir: str | Path) -> Path:
    root = Path(base_dir).resolve()
    if root.name == "backend" and root.parent.exists():
        return root.parent
    return root


def _contains_any(text: str, needles: Iterable[str]) -> bool:
    lowered = text.lower()
    return any(needle in lowered for needle in needles)


@lru_cache(maxsize=32)
def discover_framework_files(base_dir: str | Path) -> tuple[str, ...]:
    root = _resolve_root(base_dir)
    matches: list[str] = []
    for path in root.rglob("*.csv"):
        if _contains_any(path.name, FRAMEWORK_FILE_HINTS):
            matches.append(str(path))
    return tuple(matches)


@lru_cache(maxsize=32)
def discover_scope_files(base_dir: str | Path) -> tuple[str, ...]:
    root = _resolve_root(base_dir)
    backend_root = root / "backend" if (root / "backend").exists() else root
    matches: list[str] = []
    for path in backend_root.rglob("*.py"):
        relative_path = path.as_posix().lower()
        if any(
            excluded in relative_path
            for excluded in ("/app_tests/", "/tests/", "/migrations/", "/ai_onboarding/")
        ):
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        if _contains_any(content, SCOPE_FILE_HINTS):
            matches.append(str(path))
    if matches:
        return tuple(matches)
    return tuple(str(root / fallback) for fallback in MINIMAL_SCOPE_FALLBACK)