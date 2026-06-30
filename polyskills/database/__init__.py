# -*- encoding: utf-8 -*-

"""
Local Tracking Database For The Polyskills Framework
====================================================

The :mod:`polyskills.database` sub-package owns the local SQLite
tracking database that records every extension (a skill, an agent,
etc.) fetched and flushed into a destination directory by the CLI
tool or a direct Python API caller.

The database lives at a fixed, operating-system independent location
under the user home directory:

    ``~/.polyskills/records.db``

Persistence is implemented with the SQLAlchemy Object Relational
Mapper against a strictly normalised relational schema (see
:mod:`polyskills.database.models`) so the recorded facts - which
remote an extension came from, where it was installed, the resolved
commit SHA, and the first-fetched / last-updated timestamps - can be
queried without duplicated, denormalised columns.

Every write performed through :mod:`polyskills.database.tracker` is
best-effort: a missing dependency, a read-only home directory, a
locked database, or any other fault is swallowed and surfaced as a
single per-process warning so the install path of the framework is
never broken by a tracking failure.

:NOTE: SQLAlchemy is a declared runtime dependency, but its presence
    is still probed at import time and exposed through
    :data:`SQLALCHEMY_AVAILABLE`. When the dependency is absent every
    tracking entry point degrades to a silent no-op instead of
    raising :class:`ImportError`.
"""

try:
    import sqlalchemy as _sqlalchemy  # noqa: F401
except ImportError:  # pragma: no cover - exercised only without the dep
    SQLALCHEMY_AVAILABLE = False
else:
    SQLALCHEMY_AVAILABLE = True

from polyskills.database.paths import (
    DATABASE_FILENAME, ENVIRON_DB_PATH, POLYSKILLS_HOME,
    default_database_path
)
from polyskills.database.tracker import (
    get_installation, get_invocation_context, list_installations,
    record_fetch, reset_cache_for_tests, set_invocation_context
)

__all__ = [
    "SQLALCHEMY_AVAILABLE",
    "DATABASE_FILENAME",
    "ENVIRON_DB_PATH",
    "POLYSKILLS_HOME",
    "default_database_path",
    "get_installation",
    "get_invocation_context",
    "list_installations",
    "record_fetch",
    "reset_cache_for_tests",
    "set_invocation_context",
]
