#!/usr/bin/env python3
"""
Export Control Libraries in Portable Formats

Exports ECC, CCC, and PDPL control libraries to formats suitable for
migration to an on-premises environment or for offline use.

Output formats:
- JSON (default, structured bilingual library)
- NDJSON (newline-delimited JSON, one record per line – ideal for streaming ingest)
- CSV (flat tabular format for Excel/reporting tools)

Usage:
    python scripts/export_portable.py [--format json|ndjson|csv] [--output ./export]
"""

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from ai.rag.control_loader import load_control_library, CONTROL_LIBRARY_FILES


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Export control libraries to portable formats")
    parser.add_argument(
        "--format",
        choices=["json", "ndjson", "csv"],
        default="json",
        help="Output format (default: json)",
    )
    parser.add_argument(
        "--frameworks",
        nargs="+",
        default=["ECC", "CCC", "PDPL"],
        choices=["ECC", "CCC", "PDPL"],
        help="Frameworks to export (default: all)",
    )
    parser.add_argument(
        "--output",
        default=str(ROOT / "export"),
        help="Output directory (default: ./export)",
    )
    return parser.parse_args()


def export_json(controls: list, output_path: Path, framework: str) -> None:
    """Export as structured JSON."""
    output_path.mkdir(parents=True, exist_ok=True)
    dest = output_path / f"{framework.lower()}_controls_export.json"
    with open(dest, "w", encoding="utf-8") as f:
        json.dump({"framework": framework, "controls": controls}, f, ensure_ascii=False, indent=2)
    print(f"  ✓ JSON  -> {dest}")


def export_ndjson(controls: list, output_path: Path, framework: str) -> None:
    """Export as newline-delimited JSON (one record per line)."""
    output_path.mkdir(parents=True, exist_ok=True)
    dest = output_path / f"{framework.lower()}_controls_export.ndjson"
    with open(dest, "w", encoding="utf-8") as f:
        for ctrl in controls:
            f.write(json.dumps(ctrl, ensure_ascii=False) + "\n")
    print(f"  ✓ NDJSON -> {dest}")


def _flatten_control(ctrl: dict) -> dict:
    """Flatten a control dict for CSV export (handle list fields as semicolon-joined strings)."""
    flat: dict = {}
    for k, v in ctrl.items():
        if isinstance(v, list):
            flat[k] = "; ".join(str(i) for i in v)
        elif isinstance(v, dict):
            for sub_k, sub_v in v.items():
                flat[f"{k}_{sub_k}"] = str(sub_v) if not isinstance(sub_v, (list, dict)) else json.dumps(sub_v, ensure_ascii=False)
        else:
            flat[k] = v
    return flat


def export_csv(controls: list, output_path: Path, framework: str) -> None:
    """Export as flat CSV."""
    if not controls:
        return
    output_path.mkdir(parents=True, exist_ok=True)
    dest = output_path / f"{framework.lower()}_controls_export.csv"
    flat_controls = [_flatten_control(c) for c in controls]
    fieldnames = list(flat_controls[0].keys()) if flat_controls else []
    # Ensure all rows have the same keys
    all_keys: set = set()
    for row in flat_controls:
        all_keys.update(row.keys())
    fieldnames = sorted(all_keys)

    with open(dest, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(flat_controls)
    print(f"  ✓ CSV   -> {dest}")


def main() -> None:
    args = parse_args()
    output_path = Path(args.output)

    print("=" * 60)
    print("SICO GRC Platform - Portable Export")
    print("=" * 60)
    print(f"Format: {args.format.upper()} | Frameworks: {', '.join(args.frameworks)}")
    print(f"Output: {output_path}\n")

    total_exported = 0
    for fw in args.frameworks:
        try:
            library = load_control_library(fw)
            controls = library.get("controls", [])
            print(f"{fw}: {len(controls)} controls")

            if args.format == "json":
                export_json(controls, output_path, fw)
            elif args.format == "ndjson":
                export_ndjson(controls, output_path, fw)
            elif args.format == "csv":
                export_csv(controls, output_path, fw)

            total_exported += len(controls)
        except FileNotFoundError as e:
            print(f"  ⚠️  {fw}: {e}")

    # Export cross-framework mapping
    mapping_src = ROOT / "data" / "mappings" / "cross_framework_mapping.json"
    if mapping_src.exists():
        mapping_dest = output_path / "cross_framework_mapping.json"
        output_path.mkdir(parents=True, exist_ok=True)
        with open(mapping_src, encoding="utf-8") as f:
            mapping = json.load(f)
        with open(mapping_dest, "w", encoding="utf-8") as f:
            json.dump(mapping, f, ensure_ascii=False, indent=2)
        print(f"\nMapping: cross_framework_mapping.json -> {mapping_dest}")

    # Export evidence catalog and policy
    for ev_file in ["evidence_catalog.json", "evidence_policy.json"]:
        ev_src = ROOT / "data" / "evidence" / ev_file
        if ev_src.exists():
            ev_dest = output_path / ev_file
            with open(ev_src, encoding="utf-8") as f:
                ev_data = json.load(f)
            with open(ev_dest, "w", encoding="utf-8") as f:
                json.dump(ev_data, f, ensure_ascii=False, indent=2)
            print(f"Evidence: {ev_file} -> {ev_dest}")

    print(f"\n✅ Export complete: {total_exported} controls exported to {output_path}")


if __name__ == "__main__":
    main()
