# -*- encoding: utf-8 -*-

"""
Schema Definition for the Polyskills Tracking Database

Defines the v1 schema for ``~/.polyskills/polyskills.db`` and the
idempotent :func:`apply_schema` helper that materialises it on a live
:class:`sqlite3.Connection`. The schema is composed of three tables:

  * ``meta`` - one row per bookkeeping key; seeded with the schema
    version and the polyskills package version on first creation.
  * ``extensions`` - latest known state per natural key
    ``(remote_url, library, name, destination_dir)`` so callers can
    answer "what do I currently have installed where?" in one query.
  * ``events`` - append-only audit log; one row per fetch attempt,
    success or failure, so the full history is preserved.

All ``CREATE`` statements use ``IF NOT EXISTS`` so :func:`apply_schema`
can be called on every process start without raising.
"""

import sqlite3

from typing import List

# ? schema version is recorded in ``PRAGMA user_version`` so a future
# ? migration step can detect "v1" databases and upgrade them in
# ? place without inspecting any table contents.
SCHEMA_VERSION : int = 1

_PRAGMAS : List[str] = [
    "PRAGMA journal_mode = WAL",
    "PRAGMA foreign_keys = ON",
    "PRAGMA synchronous = NORMAL",
]

_DDL_META : str = """
CREATE TABLE IF NOT EXISTS meta (
    key            TEXT PRIMARY KEY,
    value          TEXT NOT NULL
)
"""

_DDL_EXTENSIONS : str = """
CREATE TABLE IF NOT EXISTS extensions (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    source_kind        TEXT    NOT NULL,
    remote_url         TEXT    NOT NULL,
    owner              TEXT,
    repository         TEXT,
    library            TEXT    NOT NULL,
    name               TEXT    NOT NULL,
    requested_version  TEXT    NOT NULL,
    resolved_version   TEXT,
    source_dir         TEXT    NOT NULL,
    destination_dir    TEXT    NOT NULL,
    exists_policy      TEXT    NOT NULL,
    file_count         INTEGER,
    byte_count         INTEGER,
    last_status        TEXT    NOT NULL,
    last_error         TEXT,
    invoked_via        TEXT    NOT NULL,
    first_installed_at TEXT    NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    last_installed_at  TEXT    NOT NULL DEFAULT (CURRENT_TIMESTAMP),
    UNIQUE (remote_url, library, name, destination_dir)
)
"""

_DDL_EVENTS : str = """
CREATE TABLE IF NOT EXISTS events (
    id                 INTEGER PRIMARY KEY AUTOINCREMENT,
    extension_id       INTEGER REFERENCES extensions(id) ON DELETE SET NULL,
    action             TEXT    NOT NULL,
    requested_version  TEXT,
    resolved_version   TEXT,
    file_count         INTEGER,
    byte_count         INTEGER,
    duration_ms        INTEGER,
    status             TEXT    NOT NULL,
    error              TEXT,
    invoked_via        TEXT    NOT NULL,
    occurred_at        TEXT    NOT NULL DEFAULT (CURRENT_TIMESTAMP)
)
"""

_DDL_INDEXES : List[str] = [
    "CREATE INDEX IF NOT EXISTS ix_extensions_name "
    "ON extensions(name)",
    "CREATE INDEX IF NOT EXISTS ix_extensions_remote "
    "ON extensions(remote_url)",
    "CREATE INDEX IF NOT EXISTS ix_extensions_status "
    "ON extensions(last_status)",
    "CREATE INDEX IF NOT EXISTS ix_events_extension "
    "ON events(extension_id)",
    "CREATE INDEX IF NOT EXISTS ix_events_time "
    "ON events(occurred_at)",
]


def apply_schema(connection : sqlite3.Connection) -> None:
    """
    Materialise the v1 schema on ``connection`` if it is not already
    present and bump ``PRAGMA user_version`` to :data:`SCHEMA_VERSION`.

    The function is safe to call on every process start - every DDL
    uses ``IF NOT EXISTS`` and the seed rows in ``meta`` use
    ``INSERT OR IGNORE``.

    :type  connection: sqlite3.Connection
    :param connection: An open SQLite connection. The function
        commits its own transaction so the caller does not need to
        wrap the call in a context manager.

    :rtype:   None
    :returns: This function returns nothing - the schema is applied
        as a side effect on ``connection``.
    """

    cursor = connection.cursor()

    for pragma in _PRAGMAS:
        cursor.execute(pragma)

    cursor.execute(_DDL_META)
    cursor.execute(_DDL_EXTENSIONS)
    cursor.execute(_DDL_EVENTS)

    for ddl in _DDL_INDEXES:
        cursor.execute(ddl)

    cursor.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")

    cursor.execute(
        "INSERT OR IGNORE INTO meta (key, value) VALUES (?, ?)",
        ("schema_version", str(SCHEMA_VERSION))
    )
    cursor.execute(
        "INSERT OR IGNORE INTO meta (key, value) VALUES "
        "(?, strftime('%Y-%m-%dT%H:%M:%fZ', 'now'))",
        ("created_at",)
    )

    connection.commit()
