# -*- encoding: utf-8 -*-

"""
Offline Tests For The Polyskills Tracking Database
==================================================

Hermetic :mod:`unittest` cases for the :mod:`polyskills.database`
sub-package. Every case is fully offline - no network is touched - and
each tracker case writes to its own temporary SQLite file passed
explicitly as ``database_path`` so the real user-level database is
never read or written.

The cases cover four concerns:

  * :class:`TestDatabasePaths` - the OS-independent path resolver and
    its ``POLYSKILLS_DB_PATH`` override.
  * :class:`TestSchemaAndEngine` - schema materialisation, the SQLite
    pragmas, and the ``ON DELETE CASCADE`` behaviour.
  * :class:`TestTracker` - the write and read façade: event recording,
    strict-normalisation of the lookup rows, derived first / last /
    SHA facts, failure capture, and graceful degradation.
  * :class:`TestTrackingCliArguments` - argparse construction of the
    new ``--no-tracking`` flag and the ``records`` subcommand.
"""

import os
import shutil
import tempfile
import unittest

from pathlib import Path
from unittest import mock

from polyskills import cli
from polyskills import database as db
from polyskills.database import engine as db_engine
from polyskills.database import tracker as db_tracker
from polyskills.database.paths import default_database_path

# ? a representative, fully-specified fetch used by the tracker cases;
# ? individual tests override single keys through ``_record`` below.
_FETCH = dict(
    source_name = "GITHUB",
    source_base_url = "https://www.github.com/",
    owner = "PyUtility",
    repository = "polyskills",
    remote_url = "https://github.com/PyUtility/polyskills",
    library = "skills",
    name = "sql-code-format",
    source_dir = "extensions/skills",
    install_path = "/home/user/.claude/skills/sql-code-format",
    requested_version = "master",
    action = "fetch",
    status = "success",
)

_EXPECTED_TABLES = {
    "sources", "libraries", "remotes", "extensions",
    "installations", "environments", "fetch_events",
}


class TestDatabasePaths(unittest.TestCase):
    """
    Path-resolution tests for :func:`default_database_path`.

    These cases make no network request and write nothing to disk; they
    only assert the resolved path string and the override contract.
    """

    def test_default_is_records_db_under_polyskills_home(self) -> None:
        """
        With no override, the path must end in ``.polyskills/records.db``
        and be absolute on every platform.
        """

        with mock.patch.dict(os.environ, {}, clear = False):
            os.environ.pop("POLYSKILLS_DB_PATH", None)
            path = default_database_path()

        self.assertTrue(path.is_absolute())
        self.assertEqual(path.name, "records.db")
        self.assertEqual(path.parent.name, ".polyskills")


    def test_environment_override_is_honoured(self) -> None:
        """
        ``POLYSKILLS_DB_PATH`` must take precedence and be expanded for
        the ``~`` home token.
        """

        with mock.patch.dict(os.environ, {}, clear = False):
            os.environ["POLYSKILLS_DB_PATH"] = os.path.join("~", "x.db")
            path = default_database_path()

        self.assertEqual(path.name, "x.db")
        self.assertNotIn("~", path.as_posix())


    def test_resolution_is_side_effect_free(self) -> None:
        """
        Resolving the default path must not create the parent
        directory; materialisation belongs to the engine layer.
        """

        staging = Path(tempfile.mkdtemp())
        target = staging / "nested" / "records.db"
        try:
            with mock.patch.dict(os.environ, {}, clear = False):
                os.environ["POLYSKILLS_DB_PATH"] = str(target)
                resolved = default_database_path()
            self.assertFalse(resolved.parent.exists())
        finally:
            shutil.rmtree(staging, ignore_errors = True)


class TestSchemaAndEngine(unittest.TestCase):
    """
    Engine and schema tests for :mod:`polyskills.database.engine`.
    """

    def setUp(self) -> None:
        """Allocate an isolated temporary database file per test."""

        self.staging = Path(tempfile.mkdtemp(prefix = "polyskills-db-"))
        self.db = self.staging / "records.db"


    def tearDown(self) -> None:
        """Dispose cached engines and remove the staging directory."""

        db_tracker.reset_cache_for_tests()
        shutil.rmtree(self.staging, ignore_errors = True)


    def test_build_session_factory_creates_every_table(self) -> None:
        """
        :func:`build_session_factory` must materialise all seven
        normalised tables.
        """

        from sqlalchemy import inspect

        engine, _factory = db_engine.build_session_factory(self.db)
        names = set(inspect(engine).get_table_names())
        engine.dispose()

        self.assertEqual(names, _EXPECTED_TABLES)


    def test_sqlite_pragmas_are_applied(self) -> None:
        """
        Every connection must enable foreign keys and use the WAL
        journal so the schema's cascade behaves correctly.
        """

        engine, _factory = db_engine.build_session_factory(self.db)
        try:
            with engine.connect() as connection:
                fk = connection.exec_driver_sql(
                    "PRAGMA foreign_keys"
                ).scalar()
                journal = connection.exec_driver_sql(
                    "PRAGMA journal_mode"
                ).scalar()
        finally:
            engine.dispose()

        self.assertEqual(fk, 1)
        self.assertEqual(str(journal).lower(), "wal")


    def test_deleting_installation_cascades_to_events(self) -> None:
        """
        Removing an installation must cascade-delete its fetch events
        so no orphan audit rows remain.
        """

        from polyskills.database.models import (
            Extension, FetchEvent, Installation, Library, Remote, Source
        )

        engine, factory = db_engine.build_session_factory(self.db)
        try:
            with factory() as session:
                source = Source(
                    name = "GITHUB", base_url = "https://www.github.com/"
                )
                library = Library(name = "skills")
                session.add_all([source, library])
                session.flush()
                remote = Remote(
                    source_id = source.id, owner = "PyUtility",
                    repository = "polyskills",
                    url = "https://github.com/PyUtility/polyskills"
                )
                session.add(remote)
                session.flush()
                extension = Extension(
                    remote_id = remote.id, library_id = library.id,
                    name = "x", source_dir = "extensions/skills"
                )
                session.add(extension)
                session.flush()
                installation = Installation(
                    extension_id = extension.id, install_path = "/tmp/x"
                )
                session.add(installation)
                session.flush()
                session.add(FetchEvent(
                    installation_id = installation.id, action = "fetch",
                    requested_version = "master", status = "success"
                ))
                session.commit()

                session.delete(installation)
                session.commit()
                self.assertEqual(session.query(FetchEvent).count(), 0)
        finally:
            engine.dispose()


class TestTracker(unittest.TestCase):
    """
    Write and read tests for :mod:`polyskills.database.tracker`.

    Each case targets a private temporary database via the explicit
    ``database_path`` argument, so the suite-level redirect is never
    relied upon for correctness.
    """

    def setUp(self) -> None:
        """Allocate a temp database and clear the engine cache."""

        self.staging = Path(tempfile.mkdtemp(prefix = "polyskills-trk-"))
        self.db = self.staging / "records.db"
        db_tracker.reset_cache_for_tests()
        db_tracker.set_invocation_context("api")


    def tearDown(self) -> None:
        """Dispose cached engines and remove the staging directory."""

        db_tracker.reset_cache_for_tests()
        shutil.rmtree(self.staging, ignore_errors = True)


    def _record(self, **overrides) -> object:
        """Record a fetch built from ``_FETCH`` plus ``overrides``."""

        payload = dict(_FETCH)
        payload.update(overrides)
        return db.record_fetch(database_path = self.db, **payload)


    def test_record_fetch_persists_and_returns_event_id(self) -> None:
        """A successful record must return the new event primary key."""

        event_id = self._record(
            resolved_commit_sha = "abc123", file_count = 3,
            total_bytes = 4096, duration_ms = 120
        )
        self.assertIsInstance(event_id, int)


    def test_repeated_fetch_reuses_rows_and_normalises(self) -> None:
        """
        Two fetches of the same extension into the same path must yield
        one installation and two events while the lookup tables stay
        deduplicated - the core normalisation guarantee.
        """

        from polyskills.database.models import (
            Extension, FetchEvent, Installation, Remote, Source
        )

        self._record(resolved_commit_sha = "aaa")
        self._record(resolved_commit_sha = "bbb")

        _engine, factory = db_engine.build_session_factory(self.db)
        try:
            with factory() as session:
                self.assertEqual(session.query(Source).count(), 1)
                self.assertEqual(session.query(Remote).count(), 1)
                self.assertEqual(session.query(Extension).count(), 1)
                self.assertEqual(session.query(Installation).count(), 1)
                self.assertEqual(session.query(FetchEvent).count(), 2)
        finally:
            _engine.dispose()


    def test_distinct_extensions_same_path_not_conflated(self) -> None:
        """
        Two different extensions fetched into the same install path must
        yield two installations with independent histories, never one
        installation silently relabelled to the second extension.
        """

        self._record(
            name = "skill-a", install_path = "/shared/path",
            resolved_commit_sha = "aaa"
        )
        self._record(
            name = "skill-b", install_path = "/shared/path",
            resolved_commit_sha = "bbb"
        )

        rows = db.list_installations(database_path = self.db)
        shared = [r for r in rows if r["install_path"] == "/shared/path"]
        self.assertEqual(
            sorted(r["name"] for r in shared), ["skill-a", "skill-b"]
        )
        for row in shared:
            self.assertEqual(row["fetch_count"], 1)


    def test_derived_first_last_and_latest_sha(self) -> None:
        """
        The read summary must derive first-fetched, last-updated, and
        the latest commit SHA from the success events.
        """

        self._record(resolved_commit_sha = "aaa")
        self._record(resolved_commit_sha = "bbb")

        rows = db.list_installations(database_path = self.db)
        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["fetch_count"], 2)
        self.assertEqual(row["resolved_commit_sha"], "bbb")
        self.assertIsNotNone(row["first_fetched_at"])
        self.assertIsNotNone(row["last_updated_at"])
        self.assertEqual(row["last_status"], "success")


    def test_failure_event_recorded_without_derived_timestamps(self) -> None:
        """
        A failed-only installation must record the error yet expose no
        first-fetched or last-updated timestamp.
        """

        self._record(
            name = "broken", install_path = "/tmp/broken",
            status = "failed", error = "HTTP 404"
        )

        rows = db.list_installations(database_path = self.db)
        match = [r for r in rows if r["name"] == "broken"]
        self.assertEqual(len(match), 1)
        self.assertEqual(match[0]["last_status"], "failed")
        self.assertIsNone(match[0]["first_fetched_at"])
        self.assertIsNone(match[0]["resolved_commit_sha"])


    def test_get_installation_includes_event_history(self) -> None:
        """
        The detailed view must return one entry per matching
        installation and embed its chronological event list.
        """

        self._record(resolved_commit_sha = "aaa")
        self._record(resolved_commit_sha = "bbb")

        details = db.get_installation(
            "sql-code-format", database_path = self.db
        )
        self.assertEqual(len(details), 1)
        self.assertEqual(len(details[0]["events"]), 2)
        self.assertEqual(
            details[0]["events"][0]["resolved_commit_sha"], "aaa"
        )


    def test_invocation_context_persisted_on_event(self) -> None:
        """
        The active invocation context must be stamped onto the event.
        """

        db_tracker.set_invocation_context("cli")
        self._record()

        details = db.get_installation(
            "sql-code-format", database_path = self.db
        )
        self.assertEqual(details[0]["events"][0]["invoked_via"], "cli")


    def test_record_fetch_is_noop_without_sqlalchemy(self) -> None:
        """
        With SQLAlchemy reported absent, recording must degrade to a
        silent no-op returning ``None`` instead of raising.
        """

        with mock.patch.object(
            db_tracker, "SQLALCHEMY_AVAILABLE", False
        ):
            result = self._record()
        self.assertIsNone(result)


class TestTrackingCliArguments(unittest.TestCase):
    """
    Hermetic argparse-construction tests for the tracking-related CLI
    surface. These never invoke :func:`cli.main` and touch no database.
    """

    def test_manager_exposes_no_tracking_flag(self) -> None:
        """``--no-tracking`` must parse to ``True`` on the manager."""

        parser = cli.buildParser()
        args = parser.parse_args([
            "manager", "https://github.com/PyUtility/polyskills",
            "--name", "sql-code-format", "--no-tracking", "skills"
        ])
        self.assertTrue(args.no_tracking)


    def test_no_tracking_defaults_to_false(self) -> None:
        """Omitting the flag must leave tracking enabled."""

        parser = cli.buildParser()
        args = parser.parse_args([
            "manager", "https://github.com/PyUtility/polyskills",
            "--name", "sql-code-format", "skills"
        ])
        self.assertFalse(args.no_tracking)


    def test_records_subcommand_parses_name_and_db(self) -> None:
        """The ``records`` subcommand must accept ``--name`` / ``--db``."""

        parser = cli.buildParser()
        args = parser.parse_args([
            "records", "--name", "sql-code-format", "--db", "/tmp/x.db"
        ])
        self.assertEqual(args.command, "records")
        self.assertEqual(args.name, "sql-code-format")
        self.assertEqual(args.db, "/tmp/x.db")


    def test_records_subcommand_defaults(self) -> None:
        """Bare ``records`` must default ``--name`` and ``--db`` to None."""

        parser = cli.buildParser()
        args = parser.parse_args(["records"])
        self.assertEqual(args.command, "records")
        self.assertIsNone(args.name)
        self.assertIsNone(args.db)


if __name__ == "__main__":
    unittest.main(verbosity = 2)
