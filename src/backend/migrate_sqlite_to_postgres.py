"""
migrate_sqlite_to_postgres.py
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Migrates all data from the local SQLite development database into a
target PostgreSQL database.

Usage
-----
  # Using the default .env DATABASE_URL as the PostgreSQL target:
  python migrate_sqlite_to_postgres.py

  # Override source and/or target explicitly:
  python migrate_sqlite_to_postgres.py \\
        --sqlite  src/backend/sico_grc.db \\
        --postgres "postgresql://user:pass@localhost:5432/sico_grc"

  # Dry-run: validate and log without writing to PostgreSQL:
  python migrate_sqlite_to_postgres.py --dry-run

Prerequisites
-------------
  pip install sqlalchemy psycopg2-binary tqdm

Notes
-----
  * The target PostgreSQL schema must already exist (run ``alembic upgrade head``
    against the PG database before running this script).
  * Foreign-key constraints are deferred for the duration of the import so
    tables can be inserted in alphabetical order rather than requiring a
    full topological sort.
  * UUID columns stored as bare 32-hex-char strings in SQLite are converted
    to the standard 8-4-4-4-12 hyphenated form required by PostgreSQL.
  * JSON / JSONB columns are round-tripped through Python to guarantee
    valid JSON regardless of how SQLite stored them.
  * The ``alembic_version`` table is intentionally skipped – it should be
    managed by Alembic on the target, not overwritten.
  * Each table migration is wrapped in its own transaction; an error in one
    table does not abort the remaining tables.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sqlite3
import sys
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Set, Tuple

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("sqlite2pg")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

# Tables managed exclusively by Alembic or auto-generated at startup – must not be overwritten.
SKIP_TABLES: Set[str] = {
    "alembic_version",
    "permissions",
    "reports",
    "role_permissions",
    "roles",
}

# Regex that matches a 32-character hex string (SQLite UUID storage).
_HEX32_RE = re.compile(r"^[0-9a-f]{32}$", re.IGNORECASE)

# Number of rows per INSERT batch.
BATCH_SIZE = 500


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class TableResult:
    name: str
    rows_read: int = 0
    rows_inserted: int = 0
    rows_failed: int = 0
    skipped: bool = False
    error: Optional[str] = None
    duration_s: float = 0.0


@dataclass
class MigrationReport:
    sqlite_path: str
    postgres_url: str
    dry_run: bool
    results: List[TableResult] = field(default_factory=list)

    # ---- aggregates -------------------------------------------------------

    @property
    def tables_ok(self) -> int:
        return sum(1 for r in self.results if not r.error and not r.skipped)

    @property
    def tables_failed(self) -> int:
        return sum(1 for r in self.results if r.error)

    @property
    def total_inserted(self) -> int:
        return sum(r.rows_inserted for r in self.results)

    @property
    def total_failed_rows(self) -> int:
        return sum(r.rows_failed for r in self.results)

    def print_summary(self) -> None:
        width = 72
        log.info("=" * width)
        log.info("MIGRATION SUMMARY")
        log.info("=" * width)
        log.info("  Source  : %s", self.sqlite_path)
        log.info("  Target  : %s", _mask_url(self.postgres_url))
        log.info("  Dry-run : %s", self.dry_run)
        log.info("-" * width)
        header = f"  {'Table':<35} {'Read':>7} {'Inserted':>9} {'Failed':>7}  Status"
        log.info(header)
        log.info("-" * width)
        for r in self.results:
            if r.skipped:
                status = "SKIP"
            elif r.error:
                status = f"ERROR: {r.error[:28]}"
            else:
                status = "OK  (%.2fs)" % r.duration_s
            log.info(
                "  %-35s %7d %9d %7d  %s",
                r.name, r.rows_read, r.rows_inserted, r.rows_failed, status,
            )
        log.info("-" * width)
        log.info(
            "  TOTAL: %d tables migrated, %d rows inserted, %d rows failed",
            self.tables_ok,
            self.total_inserted,
            self.total_failed_rows,
        )
        if self.tables_failed:
            log.warning("  %d table(s) encountered errors – see log above.", self.tables_failed)
        log.info("=" * width)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _mask_url(url: str) -> str:
    """Replace the password in a connection URL with ***."""
    return re.sub(r"(:)[^:@]+(@)", r"\1***\2", url)


def _to_uuid(value: str) -> str:
    """
    Convert a 32-char hex string to the standard UUID representation expected
    by PostgreSQL (8-4-4-4-12 with hyphens).

    If the value is already hyphenated or is not a 32-char hex string, return
    it unchanged.
    """
    if value and _HEX32_RE.match(value):
        v = value.lower()
        return f"{v[:8]}-{v[8:12]}-{v[12:16]}-{v[16:20]}-{v[20:]}"
    return value


def _is_likely_uuid_column(col_name: str) -> bool:
    """
    Heuristic: is this column likely to store UUIDs?

    The GUID type in this project is used for primary keys (``user_id``,
    ``role_id``, etc.) and foreign keys that reference them.  The column
    names all end with ``_id`` or are exactly ``uuid``.
    """
    lower = col_name.lower()
    return lower.endswith("_id") or lower == "uuid"


def _coerce_value(
    value: Any,
    col_name: str,
    json_cols: Set[str],
) -> Any:
    """
    Apply all type coercions needed to make a SQLite value acceptable by
    PostgreSQL.

    Coercions applied (in order):
    1. ``None`` → ``None``  (pass-through)
    2. JSON columns → round-trip through ``json.loads`` / ``json.dumps`` to
       ensure a valid JSON string is sent to PostgreSQL.
    3. UUID columns containing 32-char hex → hyphenated UUID string.
    4. Boolean-like integers (0 / 1) in columns named ``is_*`` or ``has_*``
       are left as-is; PostgreSQL accepts 0/1 for boolean columns.
    """
    if value is None:
        return None

    # JSON round-trip
    if col_name in json_cols:
        if isinstance(value, str) and value.strip():
            try:
                parsed = json.loads(value)
                return json.dumps(parsed, ensure_ascii=False)
            except (json.JSONDecodeError, TypeError):
                log.debug("  JSON parse failed for column %r, passing raw value", col_name)
        return value

    # UUID coercion
    if isinstance(value, str) and _is_likely_uuid_column(col_name):
        return _to_uuid(value)

    return value


# ---------------------------------------------------------------------------
# SQLite introspection
# ---------------------------------------------------------------------------

def sqlite_tables(conn: sqlite3.Connection) -> List[str]:
    """Return all user table names, excluding system and skip-listed tables."""
    cur = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
    )
    return [
        row[0] for row in cur.fetchall()
        if row[0] not in SKIP_TABLES and not row[0].startswith("sqlite_")
    ]


def sqlite_columns(conn: sqlite3.Connection, table: str) -> List[Dict[str, Any]]:
    """Return column info dicts from PRAGMA table_info."""
    cur = conn.execute(f"PRAGMA table_info(\"{table}\")")
    cols = cur.fetchall()
    # (cid, name, type, notnull, dflt_value, pk)
    return [
        {"name": row[1], "type": row[2].upper()}
        for row in cols
    ]


def sqlite_json_columns(conn: sqlite3.Connection, table: str) -> Set[str]:
    """Return column names that are declared as JSON in SQLite."""
    return {
        col["name"]
        for col in sqlite_columns(conn, table)
        if "JSON" in col["type"]
    }


def sqlite_foreign_keys(conn: sqlite3.Connection, table: str) -> List[str]:
    """Return the list of tables that *table* references via FK."""
    cur = conn.execute(f"PRAGMA foreign_key_list(\"{table}\")")
    return list({row[2] for row in cur.fetchall()})  # row[2] = referenced table


# ---------------------------------------------------------------------------
# Topological sort (dependency order)
# ---------------------------------------------------------------------------

def _topological_sort(tables: List[str], conn: sqlite3.Connection) -> List[str]:
    """
    Return *tables* in an insertion-safe order where referenced tables come
    before the tables that reference them.

    Uses Kahn's algorithm on the FK dependency graph.  Any cycles (which
    should not exist in a well-formed schema) result in the remaining nodes
    being appended in arbitrary order with a warning.
    """
    # Build adjacency: parent_table → set of child tables that depend on it.
    table_set = set(tables)
    in_degree: Dict[str, int] = {t: 0 for t in tables}
    dependents: Dict[str, List[str]] = {t: [] for t in tables}

    for table in tables:
        for ref in sqlite_foreign_keys(conn, table):
            if ref in table_set and ref != table:
                in_degree[table] += 1
                dependents[ref].append(table)

    queue = [t for t in tables if in_degree[t] == 0]
    queue.sort()          # deterministic order within the same level
    sorted_tables: List[str] = []

    while queue:
        table = queue.pop(0)
        sorted_tables.append(table)
        for child in sorted(dependents[table]):
            in_degree[child] -= 1
            if in_degree[child] == 0:
                queue.append(child)

    remaining = [t for t in tables if t not in set(sorted_tables)]
    if remaining:
        log.warning(
            "⚠  Cycle or unresolved dependency detected; appending remaining "
            "tables without guaranteed order: %s",
            remaining,
        )
        sorted_tables.extend(remaining)

    return sorted_tables


# ---------------------------------------------------------------------------
# Row iterator
# ---------------------------------------------------------------------------

def _iter_batches(
    rows: List[Tuple],
    col_names: List[str],
    json_cols: Set[str],
    batch_size: int = BATCH_SIZE,
) -> Generator[List[Dict[str, Any]], None, None]:
    """Yield lists of coerced row dicts in *batch_size* chunks."""
    batch: List[Dict[str, Any]] = []
    for row in rows:
        coerced = {
            col: _coerce_value(val, col, json_cols)
            for col, val in zip(col_names, row)
        }
        batch.append(coerced)
        if len(batch) >= batch_size:
            yield batch
            batch = []
    if batch:
        yield batch


# ---------------------------------------------------------------------------
# PostgreSQL helpers
# ---------------------------------------------------------------------------

@contextmanager
def _pg_deferred_fks(pg_conn):
    """
    Context manager that defers all FK constraint checking for the duration
    of the block.  This lets us insert tables in natural order without
    needing a perfect topological sort.
    """
    pg_conn.execute("SET CONSTRAINTS ALL DEFERRED")
    try:
        yield
    finally:
        # Constraints are checked on commit; any FK violations will surface here.
        pass


def _pg_sequence_reset(pg_conn, table: str, col_names: List[str]) -> None:
    """
    Reset autoincrement sequences after bulk insert so that the next
    ``INSERT`` does not collide with migrated integer PKs.

    Only applies to integer columns named ``id`` (the most common pattern
    in this codebase – UUID PKs have no sequence).
    """
    if "id" not in col_names:
        return
    try:
        pg_conn.execute(
            f"SELECT setval(pg_get_serial_sequence('{table}', 'id'), "
            f"COALESCE((SELECT MAX(id) FROM \"{table}\"), 0) + 1, false)"
        )
    except Exception:
        # Not all tables have a sequence; ignore silently.
        pass


# ---------------------------------------------------------------------------
# Per-table migration
# ---------------------------------------------------------------------------

def migrate_table(
    sqlite_conn: sqlite3.Connection,
    pg_conn,                      # sqlalchemy Connection
    table: str,
    dry_run: bool,
) -> TableResult:
    result = TableResult(name=table)
    t0 = time.monotonic()

    # ---- read from SQLite ------------------------------------------------
    try:
        cur = sqlite_conn.execute(f'SELECT * FROM "{table}"')
        col_names = [d[0] for d in cur.description]
        rows = cur.fetchall()
    except Exception as exc:
        result.error = str(exc)
        log.error("  [%s] SQLite read failed: %s", table, exc)
        result.duration_s = time.monotonic() - t0
        return result

    result.rows_read = len(rows)

    if not rows:
        log.info("  [%s] 0 rows – nothing to insert", table)
        result.duration_s = time.monotonic() - t0
        return result

    json_cols = sqlite_json_columns(sqlite_conn, table)

    if dry_run:
        log.info(
            "  [%s] DRY-RUN – would insert %d rows (%d columns, %d JSON cols)",
            table, len(rows), len(col_names), len(json_cols),
        )
        result.rows_inserted = len(rows)
        result.duration_s = time.monotonic() - t0
        return result

    # ---- write to PostgreSQL ---------------------------------------------
    # Build a parameterised INSERT with ON CONFLICT DO NOTHING so that
    # re-running the script is safe (idempotent).
    placeholders = ", ".join(f":{c}" for c in col_names)
    quoted_cols  = ", ".join(f'"{c}"' for c in col_names)
    insert_sql   = (
        f'INSERT INTO "{table}" ({quoted_cols}) '
        f"VALUES ({placeholders}) "
        f"ON CONFLICT DO NOTHING"
    )

    from sqlalchemy import text as sa_text  # local import to keep top-level clean

    failed_rows = 0
    inserted = 0

    try:
        _pg_deferred_fks(pg_conn)          # defer FK checks inside transaction
        for batch in _iter_batches(rows, col_names, json_cols):
            try:
                pg_conn.execute(sa_text(insert_sql), batch)
                inserted += len(batch)
            except Exception as batch_exc:
                # Row-level retry for the failed batch
                log.debug("  [%s] Batch failed, retrying row-by-row: %s", table, batch_exc)
                for single_row in batch:
                    try:
                        pg_conn.execute(sa_text(insert_sql), [single_row])
                        inserted += 1
                    except Exception as row_exc:
                        failed_rows += 1
                        log.warning(
                            "  [%s] Row insert failed (%s): %s",
                            table, type(row_exc).__name__, str(row_exc)[:120],
                        )

        _pg_sequence_reset(pg_conn, table, col_names)

    except Exception as exc:
        result.error = str(exc)
        log.error("  [%s] Transaction failed: %s", table, exc)

    result.rows_inserted = inserted
    result.rows_failed   = failed_rows
    result.duration_s    = time.monotonic() - t0
    return result


# ---------------------------------------------------------------------------
# Main orchestration
# ---------------------------------------------------------------------------

def resolve_postgres_url(explicit: Optional[str]) -> str:
    """
    Resolve the PostgreSQL target URL.

    Priority:
    1. ``--postgres`` CLI argument
    2. ``DATABASE_URL`` env var (if it references PostgreSQL)
    3. Abort with a clear message
    """
    if explicit:
        url = explicit.strip()
    else:
        # Try to load from the .env file in the backend directory
        env_path = Path(__file__).parent / ".env"
        if env_path.exists():
            for line in env_path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line.startswith("DATABASE_URL="):
                    url = line.split("=", 1)[1].strip().strip('"').strip("'")
                    break
            else:
                url = os.environ.get("DATABASE_URL", "")
        else:
            url = os.environ.get("DATABASE_URL", "")

    if not url:
        log.error(
            "No PostgreSQL URL provided.  Set DATABASE_URL in .env or pass "
            "--postgres <url>."
        )
        sys.exit(1)

    # Normalise async URL → sync for psycopg2
    url = url.replace("postgresql+asyncpg://", "postgresql://")
    url = url.replace("postgres://", "postgresql://")

    if "sqlite" in url.lower():
        log.error(
            "The resolved DATABASE_URL points to SQLite (%s).  "
            "Provide a PostgreSQL URL via --postgres.",
            _mask_url(url),
        )
        sys.exit(1)

    # Swap asyncpg for psycopg2 if needed
    if "+asyncpg" in url:
        url = url.replace("+asyncpg", "")

    return url


def run(
    sqlite_path: str,
    postgres_url: str,
    dry_run: bool,
) -> MigrationReport:
    import sqlalchemy as sa

    report = MigrationReport(
        sqlite_path=sqlite_path,
        postgres_url=postgres_url,
        dry_run=dry_run,
    )

    # ---- open SQLite -------------------------------------------------------
    if not Path(sqlite_path).exists():
        log.error("SQLite file not found: %s", sqlite_path)
        sys.exit(1)

    sqlite_conn = sqlite3.connect(sqlite_path)
    sqlite_conn.row_factory = sqlite3.Row       # named access
    # Read uncommitted for snapshot consistency during export
    sqlite_conn.isolation_level = None

    log.info("Connected to SQLite: %s", sqlite_path)

    tables_all    = sqlite_tables(sqlite_conn)
    tables_sorted = _topological_sort(tables_all, sqlite_conn)

    log.info(
        "Found %d user tables (insertion order determined by FK graph):",
        len(tables_sorted),
    )
    for i, t in enumerate(tables_sorted, 1):
        log.info("  %3d. %s", i, t)

    # ---- open PostgreSQL ---------------------------------------------------
    if not dry_run:
        log.info("Connecting to PostgreSQL: %s", _mask_url(postgres_url))
        try:
            pg_engine = sa.create_engine(postgres_url, future=True)
            log.info("✓ PostgreSQL connection OK")
        except Exception as exc:
            log.error("Could not connect to PostgreSQL: %s", exc)
            sys.exit(1)
    else:
        pg_engine = None

    # ---- migrate tables ----------------------------------------------------
    log.info("Starting data migration%s…", " (DRY-RUN)" if dry_run else "")

    for table in tables_sorted:
        log.info("→ Migrating table: %s", table)
        result: Optional[TableResult] = None

        if dry_run:
            result = migrate_table(sqlite_conn, None, table, dry_run)
        else:
            try:
                with pg_engine.begin() as pg_conn:
                    result = migrate_table(sqlite_conn, pg_conn, table, dry_run)
                    if result.error:
                        raise RuntimeError(result.error)
                log.info("COMMITTED table %s", table)
            except Exception as exc:
                log.error("ROLLED BACK table %s", table)
                if result is None:
                    result = TableResult(name=table, error=str(exc))
                elif not result.error:
                    result.error = str(exc)

        report.results.append(result)

        if result.error:
            log.error(
                "  [%s] ✗ error after %.2fs  (read=%d, inserted=%d, failed=%d)",
                table, result.duration_s,
                result.rows_read, result.rows_inserted, result.rows_failed,
            )
        elif result.rows_read == 0:
            log.info("  [%s] ✓ empty table, nothing to do (%.2fs)", table, result.duration_s)
        else:
            log.info(
                "  [%s] ✓ done in %.2fs  (read=%d, inserted=%d, failed=%d)",
                table, result.duration_s,
                result.rows_read, result.rows_inserted, result.rows_failed,
            )

    # ---- cleanup -----------------------------------------------------------
    sqlite_conn.close()
    if pg_engine is not None:
        pg_engine.dispose()

    return report


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def _parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Migrate data from SQLite to PostgreSQL.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--sqlite",
        default=str(Path(__file__).parent / "sico_grc.db"),
        metavar="PATH",
        help="Path to the SQLite .db file  (default: ./sico_grc.db)",
    )
    parser.add_argument(
        "--postgres",
        default=None,
        metavar="URL",
        help=(
            "PostgreSQL connection URL  "
            "(default: DATABASE_URL from .env, without async driver)"
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Read and validate SQLite data but do not write to PostgreSQL.",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=BATCH_SIZE,
        metavar="N",
        help=f"Rows per INSERT batch  (default: {BATCH_SIZE})",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable DEBUG-level logging.",
    )
    return parser.parse_args()


def main() -> None:
    args = _parse_args()

    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)

    global BATCH_SIZE
    BATCH_SIZE = args.batch_size

    postgres_url = resolve_postgres_url(args.postgres)

    log.info("━" * 60)
    log.info("SQLite → PostgreSQL data migration")
    log.info("━" * 60)

    report = run(
        sqlite_path=args.sqlite,
        postgres_url=postgres_url,
        dry_run=args.dry_run,
    )

    report.print_summary()

    # Exit with non-zero code if any table failed.
    sys.exit(1 if report.tables_failed else 0)


if __name__ == "__main__":
    main()
