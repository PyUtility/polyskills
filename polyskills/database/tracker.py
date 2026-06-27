# -*- encoding: utf-8 -*-

"""
Best-Effort Tracking Façade For The Polyskills Database
=======================================================

Provides the high-level, best-effort API the rest of the framework
uses to record extension fetches into and read them back from the
SQLite tracking database. The module is the only public entry point
for tracking; callers never touch :mod:`polyskills.database.models`
or :mod:`polyskills.database.engine` directly.

Two responsibilities live here:

  * **writing** - :func:`record_fetch` upserts the normalised
    ``source`` / ``remote`` / ``extension`` / ``installation`` /
    ``environment`` rows for one fetch attempt and appends a single
    :class:`~polyskills.database.models.FetchEvent`.
  * **reading** - :func:`list_installations` and
    :func:`get_installation` reconstruct the derived facts
    (first-fetched, last-updated, current commit SHA) from the audit
    log so the ``polyskills records`` command can present them.

Every public function is engineered to be a no-op on failure: a
missing SQLAlchemy dependency, a read-only home directory, a locked
database, or any other fault is swallowed and surfaced as a single
per-process :class:`RuntimeWarning`. The install path of the framework
is therefore never broken by a tracking fault.

:NOTE: SQLAlchemy and the sibling :mod:`~polyskills.database.engine`
    and :mod:`~polyskills.database.models` modules are imported lazily
    inside the functions below so that merely importing this module
    (for example from :mod:`polyskills.cli`) never requires the
    dependency to be installed.
"""

import platform as _platform
import socket
import warnings

from pathlib import Path

from typing import Any, Dict, List, Optional, Tuple

from polyskills.database import SQLALCHEMY_AVAILABLE
from polyskills.database.paths import default_database_path

# ? process-wide cache of (engine, session-factory) keyed by the
# ? resolved database path so repeated calls in one process reuse a
# ? single connection pool instead of rebuilding the engine each time.
_FACTORY_CACHE : Dict[str, Tuple[Any, Any]] = {}

# ? single per-process latch so a broken database warns exactly once
# ? rather than flooding stderr on every fetch in a batch run.
_WARNED : bool = False

# ? invocation context persisted into ``fetch_events.invoked_via`` so
# ? downstream analytics can split CLI usage from direct API usage.
_INVOCATION_CONTEXT : str = "api"
_VALID_CONTEXTS : Tuple[str, ...] = ("cli", "api")


def set_invocation_context(context : str) -> None:
    """
    Record the invocation context stamped onto subsequent fetch
    events.

    :type  context: str
    :param context: One of ``"cli"`` or ``"api"``. Any other value is
        silently coerced to ``"api"`` so a caller typo never breaks
        the tracker.

    :rtype:   None
    :returns: Nothing - the context is stored in a module-level
        variable consulted by :func:`record_fetch`.
    """

    global _INVOCATION_CONTEXT
    _INVOCATION_CONTEXT = (
        context if context in _VALID_CONTEXTS else "api"
    )


def get_invocation_context() -> str:
    """
    Return the invocation context recorded by
    :func:`set_invocation_context`.

    :rtype:   str
    :returns: Either ``"cli"`` or ``"api"``.
    """

    return _INVOCATION_CONTEXT


def _warn_once(message : str) -> None:
    """
    Emit a single :func:`warnings.warn` per process.

    :type  message: str
    :param message: The human-readable warning text.

    :rtype:   None
    :returns: Nothing - the warning is emitted as a side effect at
        most once per process lifetime.
    """

    global _WARNED
    if _WARNED:
        return None
    _WARNED = True
    warnings.warn(message, RuntimeWarning, stacklevel = 3)


def _session_factory(database_path : Optional[Path]) -> Optional[Any]:
    """
    Return a cached :class:`~sqlalchemy.orm.sessionmaker` for
    ``database_path``, building and bootstrapping the engine on first
    use.

    The function is the single guarded gateway to the persistence
    layer: it short-circuits when SQLAlchemy is unavailable and
    swallows any engine-construction error, returning ``None`` so
    every caller degrades to a no-op.

    :type  database_path: Optional[pathlib.Path]
    :param database_path: Explicit database location, or ``None`` for
        the canonical ``~/.polyskills/records.db``.

    :rtype:   Optional[sqlalchemy.orm.sessionmaker]
    :returns: A bound session factory, or ``None`` when tracking is
        unavailable or the engine could not be built.
    """

    if not SQLALCHEMY_AVAILABLE:
        _warn_once(
            "polyskills tracking disabled: SQLAlchemy is not installed"
        )
        return None

    resolved = database_path or default_database_path()
    key = str(resolved)

    cached = _FACTORY_CACHE.get(key)
    if cached is not None:
        return cached[1]

    try:
        from polyskills.database.engine import build_session_factory
        engine, factory = build_session_factory(resolved)
    except Exception as exc:  # pragma: no cover - defensive guard
        _warn_once(f"polyskills tracking disabled (init failed): {exc!r}")
        return None

    _FACTORY_CACHE[key] = (engine, factory)
    return factory


def _get_or_create(
    session : Any, model : Any,
    defaults : Optional[Dict[str, Any]] = None, **keys : Any
) -> Any:
    """
    Fetch the row of ``model`` matching ``keys`` or create it.

    The lookup uses only the natural-key columns in ``keys``; any
    ``defaults`` are applied solely on creation so a re-fetch never
    rewrites immutable columns. The new row is flushed so its primary
    key is available to the caller immediately.

    :type  session: sqlalchemy.orm.Session
    :param session: The active session the row is queried and added
        through.

    :type  model: type
    :param model: The mapped model class to query or instantiate.

    :type  defaults: Optional[Dict[str, Any]]
    :param defaults: Extra column values applied only when a new row
        is created.

    :rtype:   object
    :returns: The existing or newly created mapped instance.
    """

    from sqlalchemy.exc import IntegrityError

    instance = session.query(model).filter_by(**keys).one_or_none()
    if instance is not None:
        return instance

    params = dict(keys)
    if defaults:
        params.update(defaults)

    instance = model(**params)
    try:
        with session.begin_nested():
            session.add(instance)
            session.flush()
    except IntegrityError:
        # ? a concurrent writer inserted the same natural key between the
        # ? lookup and the flush; the SAVEPOINT rolls back only this
        # ? insert, leaving the surrounding transaction intact, then the
        # ? now-committed row is re-fetched.
        instance = session.query(model).filter_by(**keys).one()

    return instance


def _resolve_environment(session : Any) -> Any:
    """
    Return the :class:`~polyskills.database.models.Environment` row
    describing the current host, creating it on first encounter.

    The environment identity is the tuple of hostname, platform
    descriptor, Python version, and polyskills version, mirroring the
    unique constraint on the table.

    :type  session: sqlalchemy.orm.Session
    :param session: The active session used for the get-or-create.

    :rtype:   polyskills.database.models.Environment
    :returns: The environment row matching the current host.
    """

    from polyskills.database.models import Environment

    try:
        from polyskills import __version__ as polyskills_version
    except Exception:  # pragma: no cover - defensive guard
        polyskills_version = "unknown"

    return _get_or_create(
        session, Environment,
        hostname = socket.gethostname(),
        platform = _platform.platform(),
        python_version = _platform.python_version(),
        polyskills_version = polyskills_version,
    )


def record_fetch(
    *,
    source_name : str,
    source_base_url : str,
    owner : str,
    repository : str,
    remote_url : str,
    library : str,
    name : str,
    source_dir : str,
    install_path : str,
    requested_version : str,
    action : str,
    status : str,
    resolved_commit_sha : Optional[str] = None,
    file_count : Optional[int] = None,
    total_bytes : Optional[int] = None,
    duration_ms : Optional[int] = None,
    error : Optional[str] = None,
    invoked_via : Optional[str] = None,
    database_path : Optional[Path] = None,
) -> Optional[int]:
    """
    Record one extension fetch attempt - success or failure - into the
    tracking database.

    The call upserts the normalised provider, remote, extension,
    installation, and environment rows and appends one
    :class:`~polyskills.database.models.FetchEvent`. Every argument is
    keyword-only so the long parameter list cannot be supplied
    positionally by mistake. The whole operation is best-effort: any
    failure is swallowed, warned once, and reported as a ``None``
    return so the caller's install path is never disrupted.

    :type  source_name: str
    :param source_name: Provider enumeration name, for example
        ``"GITHUB"``.

    :type  source_base_url: str
    :param source_base_url: Provider base URL stored on first sight of
        the provider.

    :type  owner: str
    :param owner: Repository owner slug.

    :type  repository: str
    :param repository: Repository name slug.

    :type  remote_url: str
    :param remote_url: Canonical remote URL as supplied by the caller.

    :type  library: str
    :param library: Extension kind - ``"skills"``, ``"agents"``, etc.

    :type  name: str
    :param name: Extension leaf name.

    :type  source_dir: str
    :param source_dir: POSIX source directory on the remote.

    :type  install_path: str
    :param install_path: Absolute, resolved destination directory.

    :type  requested_version: str
    :param requested_version: Requested tag, branch, or SHA.

    :type  action: str
    :param action: Concrete action - ``"fetch"``, ``"overwrite"``, or
        ``"merge"``.

    :type  status: str
    :param status: ``"success"`` or ``"failed"``.

    **Keyword Arguments**

    The remaining keyword-only arguments enrich the event row and are
    all optional, defaulting to ``None`` when the caller cannot
    determine them.

        * **resolved_commit_sha** (*Optional[str]*): Concrete commit
            SHA the requested version resolved to.

        * **file_count** (*Optional[int]*): Files written to the
            destination on a successful fetch.

        * **total_bytes** (*Optional[int]*): Total on-disk size of the
            written files.

        * **duration_ms** (*Optional[int]*): Wall-clock duration of
            the attempt in milliseconds.

        * **error** (*Optional[str]*): Error description recorded on a
            failed attempt.

        * **invoked_via** (*Optional[str]*): Override for the recorded
            invocation context; defaults to the process context.

        * **database_path** (*Optional[pathlib.Path]*): Explicit
            database location, primarily for tests.

    :rtype:   Optional[int]
    :returns: The primary key of the inserted ``fetch_events`` row, or
        ``None`` when tracking was unavailable or the write failed.
    """

    factory = _session_factory(database_path)
    if factory is None:
        return None

    from polyskills.database.models import (
        Extension, FetchEvent, Installation, Library, Remote, Source
    )

    context = invoked_via if invoked_via in _VALID_CONTEXTS \
        else get_invocation_context()

    try:
        with factory() as session:
            source = _get_or_create(
                session, Source,
                defaults = {"base_url": source_base_url},
                name = source_name,
            )
            lib = _get_or_create(session, Library, name = library)
            remote = _get_or_create(
                session, Remote, defaults = {"url": remote_url},
                source_id = source.id, owner = owner,
                repository = repository,
            )
            extension = _get_or_create(
                session, Extension,
                remote_id = remote.id, library_id = lib.id,
                name = name, source_dir = source_dir,
            )
            installation = _get_or_create(
                session, Installation,
                extension_id = extension.id, install_path = install_path,
            )

            environment = _resolve_environment(session)

            event = FetchEvent(
                installation_id = installation.id,
                environment_id = environment.id,
                action = action,
                requested_version = requested_version,
                resolved_commit_sha = resolved_commit_sha,
                status = status,
                error = error,
                file_count = file_count,
                total_bytes = total_bytes,
                duration_ms = duration_ms,
                invoked_via = context,
            )
            session.add(event)
            session.commit()
            return int(event.id)
    except Exception as exc:
        _warn_once(f"polyskills tracker record_fetch failed: {exc!r}")
        return None


def _summarise_events(events : List[Any]) -> Dict[str, Any]:
    """
    Reduce an installation's :class:`FetchEvent` rows to the derived
    facts presented by the read API.

    :type  events: List[polyskills.database.models.FetchEvent]
    :param events: All events belonging to one installation, in any
        order.

    :rtype:   Dict[str, Any]
    :returns: A mapping with the first-fetched and last-updated
        timestamps (successful events only), the latest commit SHA and
        requested version, the latest status, and the total attempt
        count.
    """

    ordered = sorted(events, key = lambda event : event.occurred_at)
    successes = [
        event for event in ordered if event.status == "success"
    ]
    latest = ordered[-1] if ordered else None
    latest_success = successes[-1] if successes else None

    return {
        "first_fetched_at": successes[0].occurred_at if successes else None,
        "last_updated_at": latest_success.occurred_at
        if latest_success else None,
        "resolved_commit_sha": latest_success.resolved_commit_sha
        if latest_success else None,
        "requested_version": latest.requested_version if latest else None,
        "last_status": latest.status if latest else None,
        "fetch_count": len(ordered),
    }


def list_installations(
    database_path : Optional[Path] = None
) -> List[Dict[str, Any]]:
    """
    Return one summary row per tracked installation.

    Each summary joins the installation to its extension, remote, and
    library and folds the audit log into the derived first-fetched,
    last-updated, and current-commit facts. The function is read-only
    and best-effort: when tracking is unavailable, the database does
    not yet exist, or a query fails, an empty list is returned.

    :type  database_path: Optional[pathlib.Path]
    :param database_path: Explicit database location, or ``None`` for
        the canonical location.

    :rtype:   List[Dict[str, Any]]
    :returns: A list of summary mappings sorted by extension name then
        install path, each describing one installation.
    """

    factory = _session_factory(database_path)
    if factory is None:
        return []

    from polyskills.database.models import Installation

    try:
        with factory() as session:
            installations = session.query(Installation).all()
            rows : List[Dict[str, Any]] = []
            for installation in installations:
                extension = installation.extension
                remote = extension.remote
                summary = _summarise_events(installation.events)
                summary.update({
                    "name": extension.name,
                    "library": extension.library.name,
                    "owner": remote.owner,
                    "repository": remote.repository,
                    "remote_url": remote.url,
                    "source_dir": extension.source_dir,
                    "install_path": installation.install_path,
                })
                rows.append(summary)
    except Exception as exc:
        _warn_once(f"polyskills tracker list_installations failed: {exc!r}")
        return []

    return sorted(
        rows, key = lambda row : (row["name"], row["install_path"])
    )


def get_installation(
    name : str, database_path : Optional[Path] = None
) -> List[Dict[str, Any]]:
    """
    Return the detailed records for every installation of the
    extension called ``name``.

    The detail extends the :func:`list_installations` summary with the
    full chronological event history of each installation so the
    ``polyskills records --name`` view can show every fetch attempt.

    :type  name: str
    :param name: Extension leaf name to look up.

    :type  database_path: Optional[pathlib.Path]
    :param database_path: Explicit database location, or ``None`` for
        the canonical location.

    :rtype:   List[Dict[str, Any]]
    :returns: A list of detail mappings (one per matching
        installation), each carrying an ``events`` list of per-attempt
        mappings. Empty when no match is found or tracking is
        unavailable.
    """

    factory = _session_factory(database_path)
    if factory is None:
        return []

    from polyskills.database.models import Extension, Installation

    try:
        with factory() as session:
            installations = (
                session.query(Installation)
                .join(Extension)
                .filter(Extension.name == name)
                .all()
            )
            details : List[Dict[str, Any]] = []
            for installation in installations:
                extension = installation.extension
                remote = extension.remote
                summary = _summarise_events(installation.events)
                summary.update({
                    "name": extension.name,
                    "library": extension.library.name,
                    "owner": remote.owner,
                    "repository": remote.repository,
                    "remote_url": remote.url,
                    "source_dir": extension.source_dir,
                    "install_path": installation.install_path,
                    "events": [
                        {
                            "occurred_at": event.occurred_at,
                            "action": event.action,
                            "status": event.status,
                            "requested_version": event.requested_version,
                            "resolved_commit_sha":
                                event.resolved_commit_sha,
                            "file_count": event.file_count,
                            "total_bytes": event.total_bytes,
                            "duration_ms": event.duration_ms,
                            "invoked_via": event.invoked_via,
                            "error": event.error,
                        }
                        for event in sorted(
                            installation.events,
                            key = lambda event : event.occurred_at
                        )
                    ],
                })
                details.append(summary)
    except Exception as exc:
        _warn_once(f"polyskills tracker get_installation failed: {exc!r}")
        return []

    return details


def reset_cache_for_tests() -> None:
    """
    Dispose every cached engine and clear the factory cache.

    Used exclusively by the test-suite between cases that point the
    tracker at different temporary databases so a stale engine is
    never reused across an isolated fixture.

    :rtype:   None
    :returns: Nothing - the module-level cache is emptied as a side
        effect.
    """

    global _WARNED
    for engine, _factory in _FACTORY_CACHE.values():
        try:
            engine.dispose()
        except Exception:  # pragma: no cover - defensive guard
            pass
    _FACTORY_CACHE.clear()
    _WARNED = False
