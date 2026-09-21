from __future__ import annotations

from contextlib import contextmanager
from typing import Iterator

from django.db import transaction


@contextmanager
def advisory_rollback_transaction() -> Iterator[None]:
    """Run an advisory (suggestion) step in a transaction that is always rolled back.

    The block wraps a local model call that can take several minutes. On SQLite the platform
    starts transactions as BEGIN IMMEDIATE, which holds the database write lock for the whole
    block: every other request that writes, including the auth token refresh, waited, failed
    with "database is locked", and the frontend then logged the user out. Starting this block as
    DEFERRED lets other requests keep writing under WAL, while anything written inside it is
    still rolled back. Other databases are unchanged.
    """
    connection = transaction.get_connection()
    switch_mode = (
        connection.vendor == "sqlite"
        and not connection.in_atomic_block
        and getattr(connection, "transaction_mode", None) == "IMMEDIATE"
    )
    if switch_mode:
        connection.transaction_mode = "DEFERRED"
    try:
        with transaction.atomic():
            try:
                yield
            finally:
                transaction.set_rollback(True)
    finally:
        if switch_mode:
            connection.transaction_mode = "IMMEDIATE"
