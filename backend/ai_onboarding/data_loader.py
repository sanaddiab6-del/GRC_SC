from __future__ import annotations

import csv
from collections import defaultdict
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

from .file_discovery import discover_framework_files


@dataclass(slots=True)
class FrameworkControl:
    ref_id: str
    urn: str
    name: str
    description: str
    assessable: bool
    parent_ref_id: str
    evidence: str


@dataclass(slots=True)
class FrameworkRecord:
    name: str
    ref_id: str
    urn: str
    description: str
    total_controls: int = 0
    assessable_controls: int = 0
    source_files: set[str] = field(default_factory=set)
    controls: list[FrameworkControl] = field(default_factory=list)

    @property
    def searchable_text(self) -> str:
        parts = [self.name, self.ref_id, self.urn, self.description]
        for control in self.controls:
            parts.extend([control.ref_id, control.name, control.description, control.evidence])
        return " ".join(part for part in parts if part)


MINIMAL_FRAMEWORK_FALLBACK = FrameworkRecord(
    name="Generic Security Baseline",
    ref_id="generic-security-baseline",
    urn="urn:intuitem:risk:framework:generic-security-baseline",
    description="Minimal built-in fallback framework used when CSV discovery is unavailable.",
    total_controls=3,
    assessable_controls=3,
    controls=[
        FrameworkControl(
            ref_id="1",
            urn="urn:intuitem:risk:req_node:generic-security-baseline:1",
            name="Establish security ownership",
            description="Assign a responsible owner for the new organization.",
            assessable=True,
            parent_ref_id="",
            evidence="Named owner and onboarding checklist",
        ),
        FrameworkControl(
            ref_id="2",
            urn="urn:intuitem:risk:req_node:generic-security-baseline:2",
            name="Define scope and perimeter",
            description="Document the initial organizational scope and boundaries.",
            assessable=True,
            parent_ref_id="",
            evidence="Scope statement and boundary diagram",
        ),
        FrameworkControl(
            ref_id="3",
            urn="urn:intuitem:risk:req_node:generic-security-baseline:3",
            name="Review applicable compliance obligations",
            description="Identify the first compliance obligations relevant to the organization.",
            assessable=True,
            parent_ref_id="",
            evidence="Initial compliance intake notes",
        ),
    ],
)


def _read_csv_rows(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
        fieldnames = reader.fieldnames or []
    return fieldnames, rows


def _summary_key(row: dict[str, str]) -> str:
    return row.get("Framework URN") or row.get("Framework Ref ID") or row.get("Framework Name") or ""


def _detailed_key(row: dict[str, str]) -> str:
    return row.get("Framework URN") or row.get("Framework Ref ID") or row.get("Framework Name") or ""


@lru_cache(maxsize=8)
def load_framework_catalog(base_dir: str | Path) -> tuple[FrameworkRecord, ...]:
    discovered_files = [Path(path) for path in discover_framework_files(base_dir)]
    summaries: dict[str, dict[str, str]] = {}
    details: dict[str, list[FrameworkControl]] = defaultdict(list)

    for path in discovered_files:
        try:
            fieldnames, rows = _read_csv_rows(path)
        except (OSError, csv.Error):
            continue

        if not fieldnames:
            continue

        if "Control Ref ID" in fieldnames:
            for row in rows:
                key = _detailed_key(row)
                if not key:
                    continue
                details[key].append(
                    FrameworkControl(
                        ref_id=row.get("Control Ref ID", "").strip(),
                        urn=row.get("Control URN", "").strip(),
                        name=row.get("Control Name", "").strip(),
                        description=row.get("Control Description", "").strip(),
                        assessable=row.get("Is Assessable", "").strip().lower() in {"yes", "true", "1"},
                        parent_ref_id=row.get("Parent Ref ID", "").strip(),
                        evidence=row.get("Typical Evidence", "").strip(),
                    )
                )
        if "Framework Ref ID" in fieldnames:
            for row in rows:
                key = _summary_key(row)
                if key:
                    summaries[key] = row

    catalog: list[FrameworkRecord] = []
    ordered_keys = list(summaries.keys()) or list(details.keys())
    for key in ordered_keys:
        summary = summaries.get(key, {})
        control_list = details.get(key, [])
        record = FrameworkRecord(
            name=summary.get("Framework Name")
            or summary.get("Framework Ref ID")
            or key,
            ref_id=summary.get("Framework Ref ID", "").strip() or key,
            urn=summary.get("Framework URN", "").strip() or key,
            description=summary.get("Description", "").strip(),
            total_controls=int(summary.get("Total Controls", "0") or 0),
            assessable_controls=int(summary.get("Assessable Controls", "0") or 0),
            source_files={str(path) for path in discovered_files},
            controls=control_list,
        )
        if not record.total_controls:
            record.total_controls = len(control_list)
        if not record.assessable_controls:
            record.assessable_controls = sum(1 for control in control_list if control.assessable)
        catalog.append(record)

    if not catalog:
        for key, control_list in details.items():
            record = FrameworkRecord(
                name=key,
                ref_id=key,
                urn=key,
                description="",
                total_controls=len(control_list),
                assessable_controls=sum(1 for control in control_list if control.assessable),
                source_files={str(path) for path in discovered_files},
                controls=control_list,
            )
            catalog.append(record)

    if not catalog:
        return (MINIMAL_FRAMEWORK_FALLBACK,)

    return tuple(catalog)


def framework_source_files(base_dir: str | Path) -> tuple[str, ...]:
    return tuple(discover_framework_files(base_dir))