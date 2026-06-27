# -*- encoding: utf-8 -*-

"""
Engine And Schema Bootstrap For The Polyskills Tracking Database
================================================================

Owns the construction of the SQLAlchemy :class:`~sqlalchemy.engine.Engine`
bound to the SQLite tracking database and the idempotent
materialisation of the schema defined in
:mod:`polyskills.database.models`.

The module centralises three SQLite-specific concerns that the rest of
the package should not have to know about:

  * the operating-system independent ``sqlite:///`` URL is built from
    a :class:`pathlib.Path` via its POSIX representation so a Windows
    drive-letter path does not break the URL grammar;
  * the parent directory of the database file is created on demand so
    a first-ever write never fails on a missing ``~/.polyskills``;
  * connection-level ``PRAGMA`` statements (foreign-key enforcement,
    write-ahead logging, a busy timeout) are applied to every pooled
    connection through a ``connect`` event listener.

:NOTE: This module imports SQLAlchemy unconditionally and is therefore
    only imported lazily by :mod:`polyskills.database.tracker` once the
    :data:`polyskills.database.SQLALCHEMY_AVAILABLE` guard has passed.
"""

from pathlib import Path

from typing import Optional, Tuple

from sqlalchemy import create_engine, event
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from polyskills.database.models import Base
from polyskills.database.paths import default_database_path

# ? connection-level pragmas applied to every SQLite connection handed
# ? out of the pool; foreign keys must be enabled explicitly on SQLite
# ? for the ``ON DELETE CASCADE`` on fetch_events to take effect.
_SQLITE_PRAGMAS : Tuple[str, ...] = (
    "PRAGMA foreign_keys = ON",
    "PRAGMA journal_mode = WAL",
    "PRAGMA synchronous = NORMAL",
    "PRAGMA busy_timeout = 5000",
)


def _apply_sqlite_pragmas(dbapi_connection, connection_record) -> None:
    """
    Apply the package :data:`_SQLITE_PRAGMAS` to a freshly opened
    DB-API connection.

    The function is registered as a ``connect`` event listener by
    :func:`create_database_engine` so the pragmas are re-applied to
    every connection the engine pool produces, not merely the first.

    :type  dbapi_connection: sqlite3.Connection
    :param dbapi_connection: The raw DB-API connection SQLAlchemy has
        just opened.

    :type  connection_record: sqlalchemy.pool._ConnectionRecord
    :param connection_record: The pool bookkeeping record for the
        connection; unused but required by the listener signature.

    :rtype:   None
    :returns: Nothing - the pragmas are applied as a side effect on
        ``dbapi_connection``.
    """

    cursor = dbapi_connection.cursor()
    try:
        for pragma in _SQLITE_PRAGMAS:
            cursor.execute(pragma)
    finally:
        cursor.close()


def create_database_engine(
    database_path : Optional[Path] = None
) -> Engine:
    """
    Build a SQLAlchemy :class:`~sqlalchemy.engine.Engine` bound to the
    SQLite tracking database.

    The parent directory of the database file is created on demand so
    the very first write does not fail on a missing ``~/.polyskills``
    directory. A ``connect`` event listener is attached so every
    connection produced by the engine pool has the package pragmas
    (foreign keys, WAL, busy timeout) applied.

    :type  database_path: Optional[pathlib.Path]
    :param database_path: Explicit database location. When omitted the
        canonical :func:`polyskills.database.paths.default_database_path`
        location (``~/.polyskills/records.db``) is used.

    :rtype:   sqlalchemy.engine.Engine
    :returns: A configured engine ready for schema materialisation and
        session binding. The engine is created lazily and opens no
        connection until first use.
    """

    path = database_path if database_path is not None \
        else default_database_path()
    path.parent.mkdir(parents = True, exist_ok = True)

    engine = create_engine(
        f"sqlite:///{path.as_posix()}", future = True
    )
    event.listen(engine, "connect", _apply_sqlite_pragmas)

    return engine


def init_schema(engine : Engine) -> None:
    """
    Materialise every table of the tracking schema on ``engine`` if it
    is not already present.

    The call delegates to :meth:`sqlalchemy.schema.MetaData.create_all`
    which issues ``CREATE TABLE IF NOT EXISTS`` for every model, so the
    function is safe to call on every process start.

    :type  engine: sqlalchemy.engine.Engine
    :param engine: The engine whose bound database should receive the
        schema.

    :rtype:   None
    :returns: Nothing - the schema is created as a side effect on the
        database bound to ``engine``.
    """

    Base.metadata.create_all(engine)


def build_session_factory(
    database_path : Optional[Path] = None
) -> Tuple[Engine, sessionmaker]:
    """
    Construct an engine, materialise the schema, and return both the
    engine and a bound :class:`~sqlalchemy.orm.sessionmaker`.

    This is the single entry point callers need: it composes
    :func:`create_database_engine` and :func:`init_schema` so a caller
    can open a ready-to-use :class:`~sqlalchemy.orm.Session` without
    repeating the bootstrap. The engine is returned alongside the
    factory so the caller may dispose of it explicitly when finished.

    :type  database_path: Optional[pathlib.Path]
    :param database_path: Explicit database location, forwarded to
        :func:`create_database_engine`. Defaults to the canonical
        ``~/.polyskills/records.db`` location when omitted.

    :rtype:   Tuple[sqlalchemy.engine.Engine, sqlalchemy.orm.sessionmaker]
    :returns: A two-tuple ``(engine, session_factory)`` where the
        factory produces :class:`~sqlalchemy.orm.Session` objects bound
        to the engine.
    """

    engine = create_database_engine(database_path)
    init_schema(engine)

    factory = sessionmaker(
        bind = engine, future = True, expire_on_commit = False
    )

    return engine, factory
