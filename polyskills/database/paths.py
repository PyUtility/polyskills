# -*- encoding: utf-8 -*-

"""
Filesystem Path Resolver For The Polyskills Tracking Database
=============================================================

Resolves the canonical on-disk location of the polyskills tracking
database. By design the database lives at a single, predictable path
under the user home directory so every installation of the framework -
regardless of the operating system - writes to the same source of
truth without the user having to learn an environment variable:

    ``~/.polyskills/records.db``

The location is derived from :meth:`pathlib.Path.home` which is fully
operating-system independent (it honours ``%USERPROFILE%`` on Windows
and ``$HOME`` on POSIX systems), so no platform branching is required.

An optional ``POLYSKILLS_DB_PATH`` environment variable overrides the
default location. The override is primarily a testing and power-user
affordance; the value is expanded for both ``$VAR`` / ``%VAR%`` and
``~`` tokens to mirror the path-expansion contract used elsewhere in
the command-line interface.

:NOTE: Path resolution is intentionally side-effect free. The parent
    directory is created by the engine layer at connection time, not
    here, so a read-only query never materialises an empty
    ``~/.polyskills`` directory.
"""

import os

from pathlib import Path

# ? canonical on-disk layout for the polyskills tracking database; the
# ? parent directory may also host future bookkeeping artefacts (for
# ? example lock files) so it is exposed as an importable constant.
POLYSKILLS_HOME   : Path = Path.home() / ".polyskills"
DATABASE_FILENAME : str  = "records.db"

# ? optional override consulted before the default location is used;
# ? primarily exercised by the test-suite to redirect writes onto an
# ? isolated temporary file instead of the real user database.
ENVIRON_DB_PATH : str = "POLYSKILLS_DB_PATH"


def default_database_path() -> Path:
    """
    Return the absolute path to the polyskills tracking database.

    The default location is ``~/.polyskills/records.db`` resolved
    through :meth:`pathlib.Path.home` for operating-system
    independence. When the ``POLYSKILLS_DB_PATH`` environment variable
    is set its value takes precedence and is expanded for environment
    variables and the ``~`` home token before being returned.

    The function performs no filesystem mutation: it neither creates
    the parent directory nor the database file. Materialisation is the
    responsibility of the engine layer so that read-only callers (for
    example the ``polyskills records`` command) can resolve the path
    without creating an empty ``~/.polyskills`` directory as a side
    effect.

    **Example Usage**

    Resolve the default database path on any platform:

    .. code-block:: python

        from polyskills.database.paths import default_database_path

        print(default_database_path())
        >> /home/user/.polyskills/records.db        # POSIX
        >> C:\\Users\\user\\.polyskills\\records.db   # Windows

    :rtype:   pathlib.Path
    :returns: Absolute path to the tracking database, either the
        ``POLYSKILLS_DB_PATH`` override (when set and non-empty) or the
        canonical ``~/.polyskills/records.db`` location.
    """

    override = os.environ.get(ENVIRON_DB_PATH)
    if override:
        expanded = os.path.expandvars(override)
        return Path(expanded).expanduser().resolve()

    return (POLYSKILLS_HOME / DATABASE_FILENAME).resolve()
