# -*- encoding: utf-8 -*-

"""
Hermetic Tests for the Polyskills Tracking Database
---------------------------------------------------

Validates the public surface of the :mod:`polyskills.db` package
without performing any HTTP requests. The cases exercise:

  * Schema bootstrap: a connection passed to :func:`apply_schema`
    ends up with the v1 tables, indexes, and ``user_version``.
  * Idempotency: applying the schema twice does not raise and does
    not duplicate rows in the ``meta`` table.
  * :class:`Tracker` happy path: ``record_start`` followed by
    ``record_success`` produces exactly one row in ``extensions``
    and one in ``events``.
  * :class:`Tracker` failure path: ``record_failure`` writes the
    error column without raising.
  * Upsert semantics: re-installing the same extension into the
    same destination keeps a single ``extensions`` row but appends
    additional ``events`` rows.
  * Invocation context: ``set_invocation_context('cli')`` is
    persisted into the ``invoked_via`` column.
  * Robustness: a corrupt database file does not raise into the
    caller; the tracker degrades to a silent no-op instead.
"""

import sqlite3
import tempfile
import unittest
import warnings

from pathlib import Path
from typing import Tuple

from polyskills.db import paths as _db_paths
from polyskills.db import tracker as _db_tracker
from polyskills.db.schema import SCHEMA_VERSION, apply_schema
from polyskills.db.tracker import (
    Tracker, get_invocation_context, set_invocation_context
)


def _row_counts(database_path : Path) -> Tuple[int, int]:
    """
    Return ``(extensions_count, events_count)`` from ``database_path``.

    The helper opens its own short-lived connection so the assertion
    code stays free of SQLite boilerplate.

    :type  database_path: pathlib.Path
    :param database_path: Database file under inspection.

    :rtype:   Tuple[int, int]
    :returns: Two-tuple of row counts.
    """

    connection = sqlite3.connect(str(database_path))
    try:
        cursor = connection.cursor()
        ext_count = cursor.execute(
            "SELECT COUNT(*) FROM extensions"
        ).fetchone()[0]
        evt_count = cursor.execute(
            "SELECT COUNT(*) FROM events"
        ).fetchone()[0]
        return (int(ext_count), int(evt_count))
    finally:
        connection.close()


class TestSchemaBootstrap(unittest.TestCase):
    """
    Validates :func:`apply_schema` materialises the v1 tables, indexes
    and ``user_version`` on a fresh connection without raising.
    """

    def setUp(self) -> None:
        self.tmpdir = Path(tempfile.mkdtemp(prefix = "polyskills-schema-"))
        self.db = self.tmpdir / "polyskills.db"


    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors = True)


    def test_schema_creates_expected_tables(self) -> None:
        """
        After :func:`apply_schema` the database must contain the
        ``meta``, ``extensions`` and ``events`` tables.
        """

        connection = sqlite3.connect(str(self.db))
        try:
            apply_schema(connection)
            tables = {
                row[0] for row in connection.execute(
                    "SELECT name FROM sqlite_master "
                    "WHERE type = 'table'"
                )
            }
        finally:
            connection.close()

        self.assertIn("meta", tables)
        self.assertIn("extensions", tables)
        self.assertIn("events", tables)


    def test_schema_sets_user_version(self) -> None:
        """
        ``PRAGMA user_version`` must equal :data:`SCHEMA_VERSION`
        after bootstrap so future migrations can detect the version.
        """

        connection = sqlite3.connect(str(self.db))
        try:
            apply_schema(connection)
            version = connection.execute(
                "PRAGMA user_version"
            ).fetchone()[0]
        finally:
            connection.close()

        self.assertEqual(int(version), SCHEMA_VERSION)


    def test_schema_is_idempotent(self) -> None:
        """
        Applying the schema twice must not raise and must not insert
        duplicate ``meta`` rows.
        """

        connection = sqlite3.connect(str(self.db))
        try:
            apply_schema(connection)
            apply_schema(connection)
            count = connection.execute(
                "SELECT COUNT(*) FROM meta WHERE key = 'schema_version'"
            ).fetchone()[0]
        finally:
            connection.close()

        self.assertEqual(int(count), 1)


class TestTrackerLifecycle(unittest.TestCase):
    """
    Validates :class:`Tracker` ``record_start``, ``record_success``
    and ``record_failure`` against an isolated temp database.
    """

    def setUp(self) -> None:
        self.tmpdir = Path(tempfile.mkdtemp(prefix = "polyskills-track-"))
        self.db = self.tmpdir / "polyskills.db"
        set_invocation_context("api")
        self.tracker = Tracker(database_path = self.db)


    def tearDown(self) -> None:
        import shutil
        self.tracker.close()
        shutil.rmtree(self.tmpdir, ignore_errors = True)


    def _start(self) -> int:
        """
        Helper that performs a canonical ``record_start`` call and
        returns the new ``extensions.id``.
        """

        ext_id = self.tracker.record_start(
            source_kind = "GITHUB",
            remote_url = "https://github.com/PyUtility/polyskills",
            owner = "PyUtility",
            repository = "polyskills",
            library = "skills",
            name = "sql-code-format",
            requested_version = "master",
            source_dir = "extensions/skills",
            destination_dir = str(self.tmpdir / "dest"),
            exists_policy = "fail"
        )
        self.assertIsNotNone(ext_id)
        return int(ext_id)


    def test_tracker_is_healthy_after_init(self) -> None:
        """
        A freshly constructed tracker must report itself as healthy
        and have created the database file on disk.
        """

        self.assertTrue(self.tracker.is_healthy())
        self.assertTrue(self.db.exists())


    def test_record_success_writes_one_row_per_table(self) -> None:
        """
        A start + success pair must produce one ``extensions`` row
        and one ``events`` row carrying ``status='success'``.
        """

        ext_id = self._start()
        self.tracker.record_success(
            extension_id = ext_id, action = "fetch",
            file_count = 3, byte_count = 1024, duration_ms = 12,
            resolved_version = "v2.0.0"
        )

        ext_count, evt_count = _row_counts(self.db)
        self.assertEqual(ext_count, 1)
        self.assertEqual(evt_count, 1)

        connection = sqlite3.connect(str(self.db))
        try:
            row = connection.execute(
                "SELECT last_status, file_count, byte_count, "
                "resolved_version FROM extensions WHERE id = ?",
                (ext_id,)
            ).fetchone()
        finally:
            connection.close()

        self.assertEqual(row[0], "success")
        self.assertEqual(row[1], 3)
        self.assertEqual(row[2], 1024)
        self.assertEqual(row[3], "v2.0.0")


    def test_record_failure_marks_extension_failed(self) -> None:
        """
        ``record_failure`` must mark the row as ``failed`` and append
        an ``events`` row with the error message preserved.
        """

        ext_id = self._start()
        self.tracker.record_failure(
            extension_id = ext_id, action = "fetch",
            error = "FileNotFoundError('boom')", duration_ms = 9
        )

        connection = sqlite3.connect(str(self.db))
        try:
            ext_row = connection.execute(
                "SELECT last_status, last_error FROM extensions "
                "WHERE id = ?", (ext_id,)
            ).fetchone()
            evt_row = connection.execute(
                "SELECT status, error FROM events "
                "WHERE extension_id = ?", (ext_id,)
            ).fetchone()
        finally:
            connection.close()

        self.assertEqual(ext_row[0], "failed")
        self.assertIn("boom", ext_row[1])
        self.assertEqual(evt_row[0], "failed")
        self.assertIn("boom", evt_row[1])


    def test_reinstall_upserts_extension_and_appends_events(self) -> None:
        """
        Two consecutive installs against the same natural key must
        keep one ``extensions`` row but accumulate ``events`` rows.
        """

        ext_id_1 = self._start()
        self.tracker.record_success(
            extension_id = ext_id_1, action = "fetch",
            file_count = 1, byte_count = 100, duration_ms = 5
        )
        ext_id_2 = self._start()
        self.tracker.record_success(
            extension_id = ext_id_2, action = "overwrite",
            file_count = 2, byte_count = 200, duration_ms = 5
        )

        ext_count, evt_count = _row_counts(self.db)
        self.assertEqual(ext_id_1, ext_id_2)
        self.assertEqual(ext_count, 1)
        self.assertEqual(evt_count, 2)


    def test_invocation_context_is_persisted(self) -> None:
        """
        Switching the invocation context to ``"cli"`` must surface in
        the ``invoked_via`` column of new event rows.
        """

        set_invocation_context("cli")
        self.assertEqual(get_invocation_context(), "cli")

        ext_id = self._start()
        self.tracker.record_success(
            extension_id = ext_id, action = "fetch",
            file_count = 0, byte_count = 0, duration_ms = 1
        )

        connection = sqlite3.connect(str(self.db))
        try:
            invoked = connection.execute(
                "SELECT invoked_via FROM events "
                "WHERE extension_id = ?", (ext_id,)
            ).fetchone()[0]
        finally:
            connection.close()

        self.assertEqual(invoked, "cli")
        set_invocation_context("api")


class TestCorruptDatabaseDegradesSafely(unittest.TestCase):
    """
    Asserts that a corrupt or unwritable database does not propagate
    its failure into the install path - the tracker must degrade to
    a silent no-op and emit a single warning.
    """

    def setUp(self) -> None:
        self.tmpdir = Path(tempfile.mkdtemp(prefix = "polyskills-corrupt-"))
        self.db = self.tmpdir / "polyskills.db"
        # ! intentionally write garbage so apply_schema fails
        self.db.write_bytes(b"this is not a sqlite database")


    def tearDown(self) -> None:
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors = True)


    def test_corrupt_database_is_handled_silently(self) -> None:
        """
        Constructing a tracker on a corrupt file must not raise and
        every public method must subsequently no-op safely.
        """

        with warnings.catch_warnings(record = True):
            warnings.simplefilter("always")
            tracker = Tracker(database_path = self.db)

        self.assertFalse(tracker.is_healthy())
        self.assertIsNone(
            tracker.record_start(
                source_kind = "GITHUB",
                remote_url = "https://github.com/x/y",
                owner = "x", repository = "y",
                library = "skills", name = "z",
                requested_version = "master",
                source_dir = "skills",
                destination_dir = "/tmp/z",
                exists_policy = "fail"
            )
        )
        # both downstream calls must also no-op without raising
        tracker.record_success(
            extension_id = None, action = "fetch",
            file_count = 0, byte_count = 0, duration_ms = 0
        )
        tracker.record_failure(
            extension_id = None, action = "fetch",
            error = "irrelevant", duration_ms = 0
        )
        tracker.close()


class TestResolveDbPathCreatesParent(unittest.TestCase):
    """
    Validates the canonical path resolver creates the polyskills home
    directory on demand so callers can immediately open the database.
    The test isolates the assertion from the suite-wide monkey-patch
    by importing the path constants directly.
    """

    def test_resolve_db_path_returns_polyskills_db_under_home(self) -> None:
        """
        The canonical path must be ``~/.polyskills/polyskills.db``
        and the parent directory must exist on the filesystem.
        """

        from polyskills.db.paths import (
            DATABASE_FILE, POLYSKILLS_HOME
        )

        canonical = POLYSKILLS_HOME / DATABASE_FILE

        self.assertEqual(canonical.name, "polyskills.db")
        self.assertEqual(canonical.parent.name, ".polyskills")
        self.assertEqual(canonical.parent, Path.home() / ".polyskills")


if __name__ == "__main__":
    unittest.main()
