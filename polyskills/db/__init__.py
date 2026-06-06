# -*- encoding: utf-8 -*-

"""
Local Tracking Database for the Polyskills Framework
=====================================================

The :mod:`polyskills.db` sub-package owns the local SQLite tracking
database used by the framework to record every extension that is
fetched, downloaded, and flushed into a destination directory by
either the CLI tool or a direct Python API caller.

The database lives at a fixed location under the user home directory:

    ``~/.polyskills/polyskills.db``

The database file is created lazily on the very first import of the
:mod:`polyskills` package and is then re-used by every subsequent
import - the schema bootstrap is idempotent and uses
``CREATE TABLE IF NOT EXISTS`` for every table.

Public Surface
--------------

The sub-package exposes a small, deliberately narrow API so the rest
of the framework only ever has to learn three names:

  * :func:`get_tracker` - returns a process-wide :class:`Tracker`
    singleton; the first call also runs :func:`apply_schema`.
  * :func:`set_invocation_context` - records whether the calling
    frame is the CLI ``main()`` or a direct library API caller; the
    value is persisted into ``events.invoked_via`` so downstream
    analytics can split CLI from API usage.
  * :class:`Tracker` - the concrete object returned by
    :func:`get_tracker`; offers ``record_start``, ``record_success``,
    and ``record_failure``.

:NOTE: Every public method of :class:`Tracker` is engineered to be a
best-effort no-op on failure - a broken database, a read-only home
directory, or a permission error never raises into the caller. The
install path is therefore guaranteed to succeed (or fail for its own
reasons) regardless of the database health.
"""

from polyskills.db.paths import resolve_db_path
from polyskills.db.schema import apply_schema
from polyskills.db.tracker import (
    Tracker, get_tracker, set_invocation_context
)

__all__ = [
    "Tracker",
    "apply_schema",
    "get_tracker",
    "resolve_db_path",
    "set_invocation_context",
]
