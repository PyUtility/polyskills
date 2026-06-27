# -*- encoding: utf-8 -*-

"""
SQLAlchemy ORM Models For The Polyskills Tracking Database
==========================================================

Defines the strictly normalised relational schema that backs the
``~/.polyskills/records.db`` tracking database. The schema is modelled
with the SQLAlchemy 2.0 typed declarative mapping (``Mapped`` /
``mapped_column``) and is decomposed to third normal form so that no
recorded fact is duplicated across rows:

    ``sources`` -> ``remotes`` -> ``extensions`` -> ``installations``
    -> ``fetch_events`` <- ``environments``
    ``libraries`` -> ``extensions``

The seven tables are:

  * :class:`Source`      - lookup of supported remote providers, one
    row per :class:`polyskills.remote.sources.ValidSources` member.
  * :class:`Library`     - lookup of extension kinds (``skills``,
    ``agents``, ``commands``, ``hooks``).
  * :class:`Remote`      - one row per ``(provider, owner, repo)``.
  * :class:`Extension`   - one row per logical extension on a remote,
    keyed by ``(remote, library, name, source_dir)``.
  * :class:`Installation`- one row per physical install location on
    this machine, keyed by the absolute destination path.
  * :class:`Environment` - lookup of the host environment a fetch ran
    in, keyed by ``(hostname, platform, python, polyskills)``.
  * :class:`FetchEvent`  - append-only audit row, one per fetch
    attempt (success or failure), carrying the resolved commit SHA,
    timestamp, and on-disk size of that attempt.

Derived facts are never stored: the "first fetched" and "last
updated" timestamps and the "current commit SHA" of an installation
are computed from :class:`FetchEvent` rows via aggregation, keeping
the schema in third normal form.

:NOTE: This module imports SQLAlchemy unconditionally. It is only
    imported lazily by :mod:`polyskills.database.tracker` after the
    :data:`polyskills.database.SQLALCHEMY_AVAILABLE` guard has
    confirmed the dependency is importable.
"""

from datetime import datetime, timezone

from typing import List, Optional

from sqlalchemy import (
    DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
)
from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, relationship
)


def _utc_now() -> datetime:
    """
    Return the current UTC time as a naive :class:`datetime.datetime`.

    The value is the current instant in UTC with its ``tzinfo`` removed.
    SQLite has no timezone-aware storage, so a stored timestamp always
    reads back naive; producing a naive UTC value here keeps a freshly
    recorded event and a reloaded event directly comparable and
    sortable. Every audit timestamp in the database is therefore naive
    UTC by convention.

    :rtype:   datetime.datetime
    :returns: The current UTC instant as a naive ``datetime``.
    """

    return datetime.now(timezone.utc).replace(tzinfo = None)


class Base(DeclarativeBase):
    """
    Declarative base shared by every model in the tracking schema.

    A dedicated subclass of :class:`sqlalchemy.orm.DeclarativeBase`
    is used (rather than the legacy ``declarative_base()`` factory)
    so the schema participates in SQLAlchemy 2.0 typed mappings and
    its :attr:`metadata` can be materialised in one call by
    :func:`polyskills.database.engine.init_schema`.
    """


class Source(Base):
    """
    Lookup table of supported remote providers.

    Each row corresponds to one
    :class:`polyskills.remote.sources.ValidSources` member (for
    example ``GITHUB``) and exists so that :class:`Remote` rows
    reference a provider by foreign key rather than repeating the
    provider name and base URL on every remote.
    """

    __tablename__ = "sources"

    id       : Mapped[int] = mapped_column(primary_key = True)
    name     : Mapped[str] = mapped_column(
        String(64), unique = True, nullable = False
    )
    base_url : Mapped[str] = mapped_column(String(255), nullable = False)

    remotes : Mapped[List["Remote"]] = relationship(
        back_populates = "source"
    )


class Library(Base):
    """
    Lookup table of extension kinds managed by the framework.

    The supported values mirror the CLI library selector -
    ``skills``, ``agents``, ``commands``, ``hooks`` - and are
    referenced by :class:`Extension` rows through a foreign key so the
    kind is never repeated as a free-text column.
    """

    __tablename__ = "libraries"

    id   : Mapped[int] = mapped_column(primary_key = True)
    name : Mapped[str] = mapped_column(
        String(32), unique = True, nullable = False
    )

    extensions : Mapped[List["Extension"]] = relationship(
        back_populates = "library"
    )


class Remote(Base):
    """
    A single remote repository identified by its provider, owner, and
    repository slug.

    The natural key ``(source_id, owner, repository)`` is enforced by
    a unique constraint so re-fetching from the same repository reuses
    the existing row instead of inserting a duplicate.

    :type  source_id: int
    :param source_id: Foreign key into :class:`Source`.

    :type  owner: str
    :param owner: Repository owner slug, for example ``PyUtility``.

    :type  repository: str
    :param repository: Repository name slug, for example
        ``polyskills``.

    :type  url: str
    :param url: The canonical remote URL exactly as supplied on the
        command line.
    """

    __tablename__ = "remotes"
    __table_args__ = (
        UniqueConstraint(
            "source_id", "owner", "repository",
            name = "uq_remote_provider_slug"
        ),
    )

    id         : Mapped[int] = mapped_column(primary_key = True)
    source_id  : Mapped[int] = mapped_column(
        ForeignKey("sources.id"), nullable = False, index = True
    )
    owner      : Mapped[str] = mapped_column(String(255), nullable = False)
    repository : Mapped[str] = mapped_column(String(255), nullable = False)
    url        : Mapped[str] = mapped_column(Text, nullable = False)

    source : Mapped["Source"] = relationship(back_populates = "remotes")
    extensions : Mapped[List["Extension"]] = relationship(
        back_populates = "remote"
    )


class Extension(Base):
    """
    A logical extension hosted on a remote repository.

    The natural key ``(remote_id, library_id, name, source_dir)``
    uniquely identifies an extension and is enforced by a unique
    constraint. The same extension installed into several destinations
    is represented by one :class:`Extension` row and many
    :class:`Installation` rows.

    :type  remote_id: int
    :param remote_id: Foreign key into :class:`Remote`.

    :type  library_id: int
    :param library_id: Foreign key into :class:`Library`.

    :type  name: str
    :param name: Leaf directory name of the extension on the remote.

    :type  source_dir: str
    :param source_dir: POSIX-style source directory on the remote the
        extension was fetched from.
    """

    __tablename__ = "extensions"
    __table_args__ = (
        UniqueConstraint(
            "remote_id", "library_id", "name", "source_dir",
            name = "uq_extension_natural_key"
        ),
    )

    id         : Mapped[int] = mapped_column(primary_key = True)
    remote_id  : Mapped[int] = mapped_column(
        ForeignKey("remotes.id"), nullable = False, index = True
    )
    library_id : Mapped[int] = mapped_column(
        ForeignKey("libraries.id"), nullable = False, index = True
    )
    name       : Mapped[str] = mapped_column(
        String(255), nullable = False, index = True
    )
    source_dir : Mapped[str] = mapped_column(String(512), nullable = False)

    remote  : Mapped["Remote"] = relationship(
        back_populates = "extensions"
    )
    library : Mapped["Library"] = relationship(
        back_populates = "extensions"
    )
    installations : Mapped[List["Installation"]] = relationship(
        back_populates = "extension"
    )


class Installation(Base):
    """
    A physical installation of an extension at one absolute path on
    the local filesystem.

    The natural key is the pair ``(extension_id, install_path)``: the
    same extension re-fetched into the same directory reuses its
    installation row (appending a new :class:`FetchEvent`), while a
    different extension fetched into the same path gets its own
    installation so the two histories are never conflated.

    :type  extension_id: int
    :param extension_id: Foreign key into :class:`Extension`.

    :type  install_path: str
    :param install_path: Absolute, resolved destination directory on
        the local filesystem.
    """

    __tablename__ = "installations"
    __table_args__ = (
        UniqueConstraint(
            "extension_id", "install_path",
            name = "uq_installation_extension_path"
        ),
    )

    id           : Mapped[int] = mapped_column(primary_key = True)
    extension_id : Mapped[int] = mapped_column(
        ForeignKey("extensions.id"), nullable = False, index = True
    )
    install_path : Mapped[str] = mapped_column(
        Text, nullable = False, index = True
    )

    extension : Mapped["Extension"] = relationship(
        back_populates = "installations"
    )
    events : Mapped[List["FetchEvent"]] = relationship(
        back_populates = "installation",
        cascade = "all, delete-orphan"
    )


class Environment(Base):
    """
    Lookup table of host environments a fetch was executed in.

    Recording the environment in its own table - keyed by
    ``(hostname, platform, python_version, polyskills_version)`` -
    keeps these repeating strings out of the high-cardinality
    :class:`FetchEvent` table while still allowing every event to be
    attributed to the exact environment that produced it.
    """

    __tablename__ = "environments"
    __table_args__ = (
        UniqueConstraint(
            "hostname", "platform", "python_version",
            "polyskills_version", name = "uq_environment_identity"
        ),
    )

    id                 : Mapped[int] = mapped_column(primary_key = True)
    hostname           : Mapped[Optional[str]] = mapped_column(String(255))
    platform           : Mapped[Optional[str]] = mapped_column(String(255))
    python_version     : Mapped[Optional[str]] = mapped_column(String(64))
    polyskills_version : Mapped[Optional[str]] = mapped_column(String(64))

    events : Mapped[List["FetchEvent"]] = relationship(
        back_populates = "environment"
    )


class FetchEvent(Base):
    """
    An append-only audit record of a single extension fetch attempt.

    One row is written per attempt - whether it succeeds or fails - so
    the full history of an installation is preserved. The first-fetched
    timestamp, the last-updated timestamp, and the current commit SHA
    of an installation are all derived from these rows by aggregation
    rather than being cached on :class:`Installation`.

    :type  installation_id: int
    :param installation_id: Foreign key into :class:`Installation`.

    :type  environment_id: Optional[int]
    :param environment_id: Foreign key into :class:`Environment`, or
        ``None`` when the environment could not be captured.

    :type  action: str
    :param action: Concrete action taken - ``fetch``, ``overwrite``,
        or ``merge`` - derived from the ``--exists`` policy.

    :type  requested_version: str
    :param requested_version: Tag, branch, or SHA requested by the
        caller, for example ``master``.

    :type  resolved_commit_sha: Optional[str]
    :param resolved_commit_sha: The concrete commit SHA the requested
        version resolved to, when it could be determined.

    :type  status: str
    :param status: Either ``success`` or ``failed``.
    """

    __tablename__ = "fetch_events"

    id              : Mapped[int] = mapped_column(primary_key = True)
    installation_id : Mapped[int] = mapped_column(
        ForeignKey("installations.id", ondelete = "CASCADE"),
        nullable = False, index = True
    )
    environment_id  : Mapped[Optional[int]] = mapped_column(
        ForeignKey("environments.id"), nullable = True, index = True
    )

    action              : Mapped[str] = mapped_column(
        String(32), nullable = False
    )
    requested_version   : Mapped[str] = mapped_column(
        String(255), nullable = False
    )
    resolved_commit_sha : Mapped[Optional[str]] = mapped_column(String(64))
    status              : Mapped[str] = mapped_column(
        String(16), nullable = False, index = True
    )
    error               : Mapped[Optional[str]] = mapped_column(Text)
    file_count          : Mapped[Optional[int]] = mapped_column(Integer)
    total_bytes         : Mapped[Optional[int]] = mapped_column(Integer)
    duration_ms         : Mapped[Optional[int]] = mapped_column(Integer)
    invoked_via         : Mapped[str] = mapped_column(
        String(16), nullable = False, default = "api"
    )
    occurred_at         : Mapped[datetime] = mapped_column(
        DateTime, nullable = False, default = _utc_now, index = True
    )

    installation : Mapped["Installation"] = relationship(
        back_populates = "events"
    )
    environment : Mapped[Optional["Environment"]] = relationship(
        back_populates = "events"
    )
