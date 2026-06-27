# -*- encoding: utf-8 -*-

"""
Tracking Façade for the Polyskills SQLite Database

Provides a thin, best-effort façade around the SQLite tracking
database materialised by :mod:`polyskills.db.schema`. Every public
method of :class:`Tracker` is engineered to be a no-op on failure -
a corrupt database, a read-only home directory, or a transient lock
must never break the install path of the calling code.

The module also owns a tiny, process-wide invocation-context flag
that downstream remote managers consult to record whether a fetch
was triggered from the CLI ``main()`` or from a direct library API
call. The flag is intentionally process-wide because the CLI is
single-threaded and library callers can build their own
:class:`Tracker` instances when finer granularity is required.
"""

import sqlite3
import warnings

from pathlib import Path
from typing import Optional, Tuple

from polyskills.db import paths as _paths
from polyskills.db.schema import apply_schema

# ? process-wide flag toggled by polyskills.cli.main() before the
# ? remote dispatcher is invoked; defaults to "api" so any direct
# ? library caller is recorded correctly without extra wiring.
_INVOCATION_CONTEXT : str = "api"

_VALID_CONTEXTS : Tuple[str, ...] = ("cli", "api")


def set_invocation_context(context : str) -> None:
    """
    Record the invocation context for subsequent tracker writes.

    The value is persisted into the ``events.invoked_via`` column on
    every recorded fetch so downstream analytics can split CLI usage
    from direct library API usage.

    :type  context: str
    :param context: One of ``"cli"`` or ``"api"``. Any other value is
        silently coerced to ``"api"`` so a typo in a caller never
        breaks the tracker.

    :rtype:   None
    :returns: This function returns nothing - the context is stored
        in a module-level variable consulted by :class:`Tracker`.
    """

    global _INVOCATION_CONTEXT
    _INVOCATION_CONTEXT = (
        context if context in _VALID_CONTEXTS else "api"
    )


def get_invocation_context() -> str:
    """
    Return the current invocation context recorded by
    :func:`set_invocation_context`.

    :rtype:   str
    :returns: Either ``"cli"`` or ``"api"``.
    """

    return _INVOCATION_CONTEXT


class Tracker:
    """
    Best-effort SQLite tracking façade for polyskills extension
    fetches. The class is deliberately small: it owns one connection,
    serialises writes through ``BEGIN IMMEDIATE`` transactions, and
    swallows every exception arising from the database layer so the
    install path of the framework is never broken by a tracker fault.

    :type  database_path: Optional[pathlib.Path]
    :param database_path: Optional explicit database path. When
        omitted the tracker calls :func:`resolve_db_path` so tests can
        monkey-patch the resolver to a temporary file without having
        to touch the :class:`Tracker` constructor.
    """

    def __init__(
        self, database_path : Optional[Path] = None
    ) -> None:
        self._path : Optional[Path] = None
        self._conn : Optional[sqlite3.Connection] = None
        self._healthy : bool = True
        self._warned : bool = False

        try:
            self._path = (
                database_path
                if database_path is not None
                else _paths.resolve_db_path()
            )
            self._conn = sqlite3.connect(
                str(self._path),
                timeout = 5.0,
                isolation_level = None,
                check_same_thread = False
            )
            apply_schema(self._conn)
        except Exception as exc:
            self._healthy = False
            self._warn_once(
                f"polyskills tracker disabled (init failed): {exc!r}"
            )


    def _warn_once(self, message : str) -> None:
        """
        Emit a single :func:`warnings.warn` per process so a broken
        database does not flood stderr on every fetch.

        :type  message: str
        :param message: The human-readable warning text.

        :rtype:   None
        :returns: Nothing - the warning is emitted as a side effect.
        """

        if self._warned:
            return None
        self._warned = True
        warnings.warn(message, RuntimeWarning, stacklevel = 3)


    def is_healthy(self) -> bool:
        """
        Return whether the tracker is currently able to write rows.

        :rtype:   bool
        :returns: ``True`` when the underlying connection is open and
            the schema is in place, ``False`` otherwise.
        """

        return self._healthy and self._conn is not None


    def record_start(
        self,
        source_kind : str,
        remote_url : str,
        owner : Optional[str],
        repository : Optional[str],
        library : str,
        name : str,
        requested_version : str,
        source_dir : str,
        destination_dir : str,
        exists_policy : str
    ) -> Optional[int]:
        """
        Upsert a row into ``extensions`` with ``last_status =
        'in_progress'`` and return the newly assigned (or pre-existing)
        primary key. The id is later passed to :meth:`record_success`
        or :meth:`record_failure` so the matching ``events`` row is
        attributed to the correct extension.

        :type  source_kind: str
        :param source_kind: The :class:`ValidSources` member name, for
            example ``"GITHUB"``.

        :type  remote_url: str
        :param remote_url: Canonical remote URL, used as part of the
            natural key in the ``UNIQUE`` constraint on ``extensions``.

        :type  owner: Optional[str]
        :param owner: Slug owner component, when available. Pure
            informational.

        :type  repository: Optional[str]
        :param repository: Slug repository component, when available.

        :type  library: str
        :param library: Library kind, ``"skills"`` or ``"agents"``.

        :type  name: str
        :param name: Extension leaf name, used as part of the
            natural key on ``extensions``.

        :type  requested_version: str
        :param requested_version: Requested tag, branch, or sha.

        :type  source_dir: str
        :param source_dir: POSIX-style source directory path on the
            remote.

        :type  destination_dir: str
        :param destination_dir: Absolute, normalised destination
            directory path on the local filesystem.

        :type  exists_policy: str
        :param exists_policy: One of ``"fail"``, ``"overwrite"``,
            ``"merge"``.

        :rtype:   Optional[int]
        :returns: The ``extensions.id`` of the upserted row, or
            ``None`` if the tracker is unhealthy or the write failed.
        """

        if not self.is_healthy():
            return None

        invoked_via = get_invocation_context()

        try:
            assert self._conn is not None
            cursor = self._conn.cursor()
            cursor.execute("BEGIN IMMEDIATE")
            cursor.execute(
                """
                INSERT INTO extensions (
                    source_kind, remote_url, owner, repository,
                    library, name, requested_version, source_dir,
                    destination_dir, exists_policy, last_status,
                    invoked_via
                ) VALUES (
                    ?, ?, ?, ?, ?, ?, ?, ?, ?, ?,
                    'in_progress', ?
                )
                ON CONFLICT (remote_url, library, name, destination_dir)
                DO UPDATE SET
                    source_kind        = excluded.source_kind,
                    owner              = excluded.owner,
                    repository         = excluded.repository,
                    requested_version  = excluded.requested_version,
                    source_dir         = excluded.source_dir,
                    exists_policy      = excluded.exists_policy,
                    last_status        = 'in_progress',
                    last_error         = NULL,
                    invoked_via        = excluded.invoked_via,
                    last_installed_at  = CURRENT_TIMESTAMP
                RETURNING id
                """,
                (
                    source_kind, remote_url, owner, repository,
                    library, name, requested_version, source_dir,
                    destination_dir, exists_policy, invoked_via
                )
            )
            row = cursor.fetchone()
            cursor.execute("COMMIT")
            return int(row[0]) if row else None
        except Exception as exc:
            self._safe_rollback()
            self._warn_once(
                f"polyskills tracker record_start failed: {exc!r}"
            )
            return None


    def record_success(
        self,
        extension_id : Optional[int],
        action : str,
        file_count : int,
        byte_count : int,
        duration_ms : int,
        resolved_version : Optional[str] = None
    ) -> None:
        """
        Mark the previously started extension row as successful and
        append a corresponding ``events`` row.

        :type  extension_id: Optional[int]
        :param extension_id: The id returned by :meth:`record_start`.
            ``None`` results in a no-op so callers do not need to
            branch on the start outcome.

        :type  action: str
        :param action: Concrete action taken, for example
            ``"fetch"``, ``"overwrite"``, or ``"merge"``.

        :type  file_count: int
        :param file_count: Number of files that landed in the
            destination directory.

        :type  byte_count: int
        :param byte_count: Total byte count of the files in the
            destination directory.

        :type  duration_ms: int
        :param duration_ms: Wall clock duration of the fetch in
            milliseconds.

        :type  resolved_version: Optional[str]
        :param resolved_version: Resolved tag or commit sha, when
            different from the requested version. Pure informational.

        :rtype:   None
        :returns: Nothing - the rows are written as a side effect.
        """

        if not self.is_healthy() or extension_id is None:
            return None

        invoked_via = get_invocation_context()

        try:
            assert self._conn is not None
            cursor = self._conn.cursor()
            cursor.execute("BEGIN IMMEDIATE")
            cursor.execute(
                """
                UPDATE extensions
                SET resolved_version  = ?,
                    file_count        = ?,
                    byte_count        = ?,
                    last_status       = 'success',
                    last_error        = NULL,
                    last_installed_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (resolved_version, file_count, byte_count, extension_id)
            )
            cursor.execute(
                """
                INSERT INTO events (
                    extension_id, action, resolved_version,
                    file_count, byte_count, duration_ms,
                    status, error, invoked_via
                ) VALUES (?, ?, ?, ?, ?, ?, 'success', NULL, ?)
                """,
                (
                    extension_id, action, resolved_version,
                    file_count, byte_count, duration_ms, invoked_via
                )
            )
            cursor.execute("COMMIT")
        except Exception as exc:
            self._safe_rollback()
            self._warn_once(
                f"polyskills tracker record_success failed: {exc!r}"
            )


    def record_failure(
        self,
        extension_id : Optional[int],
        action : str,
        error : str,
        duration_ms : int
    ) -> None:
        """
        Mark the previously started extension row as failed and
        append a corresponding ``events`` row carrying the error
        message.

        :type  extension_id: Optional[int]
        :param extension_id: The id returned by :meth:`record_start`.
            ``None`` results in a no-op.

        :type  action: str
        :param action: Concrete action attempted, mirroring
            :meth:`record_success`.

        :type  error: str
        :param error: Human-readable error description, typically the
            ``repr`` of the original exception.

        :type  duration_ms: int
        :param duration_ms: Wall clock duration of the failed attempt.

        :rtype:   None
        :returns: Nothing - the rows are written as a side effect.
        """

        if not self.is_healthy() or extension_id is None:
            return None

        invoked_via = get_invocation_context()

        try:
            assert self._conn is not None
            cursor = self._conn.cursor()
            cursor.execute("BEGIN IMMEDIATE")
            cursor.execute(
                """
                UPDATE extensions
                SET last_status       = 'failed',
                    last_error        = ?,
                    last_installed_at = CURRENT_TIMESTAMP
                WHERE id = ?
                """,
                (error, extension_id)
            )
            cursor.execute(
                """
                INSERT INTO events (
                    extension_id, action, duration_ms,
                    status, error, invoked_via
                ) VALUES (?, ?, ?, 'failed', ?, ?)
                """,
                (
                    extension_id, action, duration_ms,
                    error, invoked_via
                )
            )
            cursor.execute("COMMIT")
        except Exception as exc:
            self._safe_rollback()
            self._warn_once(
                f"polyskills tracker record_failure failed: {exc!r}"
            )


    def _safe_rollback(self) -> None:
        """
        Best-effort rollback used by every write helper when an
        exception is raised mid-transaction.

        :rtype:   None
        :returns: Nothing - the rollback is emitted on a best-effort
            basis and any further error is swallowed.
        """

        if self._conn is None:
            return None
        try:
            self._conn.execute("ROLLBACK")
        except Exception:
            pass


    def close(self) -> None:
        """
        Close the underlying SQLite connection. Safe to call multiple
        times and on an already-broken tracker.

        :rtype:   None
        :returns: Nothing - the connection is closed as a side effect.
        """

        if self._conn is None:
            return None
        try:
            self._conn.close()
        except Exception:
            pass
        finally:
            self._conn = None
            self._healthy = False


_TRACKER : Optional[Tracker] = None


def get_tracker() -> Tracker:
    """
    Return the process-wide :class:`Tracker` singleton, creating it
    on the first call. Subsequent calls return the same instance so
    the SQLite connection is opened exactly once per process.

    :rtype:   Tracker
    :returns: The shared :class:`Tracker` instance. The instance may
        report :meth:`Tracker.is_healthy` as ``False`` when the
        database cannot be opened - all public methods of an
        unhealthy tracker are silent no-ops.
    """

    global _TRACKER
    if _TRACKER is None:
        _TRACKER = Tracker()
    return _TRACKER


def reset_tracker_for_tests() -> None:
    """
    Drop the cached singleton so the next :func:`get_tracker` call
    re-runs the bootstrap. Used exclusively by the test suite after a
    monkey-patch of :func:`polyskills.db.paths.resolve_db_path` to
    pick up the new database location.

    :rtype:   None
    :returns: Nothing - the cached singleton is cleared as a side
        effect.
    """

    global _TRACKER
    if _TRACKER is not None:
        _TRACKER.close()
    _TRACKER = None
