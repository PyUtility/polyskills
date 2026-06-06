# -*- encoding: utf-8 -*-

"""
Filesystem Path Resolver for the Polyskills Tracking Database

Resolves the canonical on-disk location of the polyskills tracking
SQLite database. The location is fixed by design at
``~/.polyskills/polyskills.db`` so every install of the framework
writes to the same single source of truth and the user never needs
to learn an environment variable to opt in.

Tests redirect the resolver by monkey-patching
:func:`resolve_db_path` to a temporary file so the live user-level
database is never touched by the test suite.
"""

from pathlib import Path

# ? canonical on-disk layout for the polyskills tracking database;
# ? the parent directory is also used by future bookkeeping artefacts
# ? (for example, lock files) so it is exposed as a constant.
POLYSKILLS_HOME : Path = Path.home() / ".polyskills"
DATABASE_FILE   : str  = "polyskills.db"


def resolve_db_path() -> Path:
    """
    Return the absolute path to the polyskills tracking database and
    create its parent directory if it does not yet exist.

    The function is intentionally side-effecting on the parent
    directory so callers can immediately ``sqlite3.connect`` to the
    returned path without an extra ``mkdir`` step. The database file
    itself is created lazily by :mod:`sqlite3` on first connection.

    **Example Usage**

    The resolver is used by :func:`polyskills.db.tracker.get_tracker`
    to open the connection on first use.

    .. code-block:: python

        from polyskills.db.paths import resolve_db_path

        db_path = resolve_db_path()
        print(db_path)
        >> /home/user/.polyskills/polyskills.db

    :raises OSError: If the parent directory cannot be created. The
        caller (typically :class:`Tracker`) is expected to swallow
        the error and degrade to a no-op so the install path is
        never broken by a read-only home directory.

    :rtype:   pathlib.Path
    :returns: Absolute path to ``~/.polyskills/polyskills.db``.
    """

    POLYSKILLS_HOME.mkdir(parents = True, exist_ok = True)
    return POLYSKILLS_HOME / DATABASE_FILE
