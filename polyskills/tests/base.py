# -*- encoding: utf-8 -*-

"""
Shared Fixtures and Constants for the Polyskills Test Suite
-----------------------------------------------------------

Centralizes the live-repository coordinates, the expected payload,
and the bring-up/tear-down lifecycle for every concrete test case so
that individual modules stay focused on the contract they verify and
the suite remains DRY.
"""

import shutil
import logging
import tempfile
import warnings
import unittest

from pathlib import Path
from typing import Set

import urllib3

from polyskills.db import paths as _db_paths
from polyskills.db import tracker as _db_tracker
from polyskills.remote.sources import GithubManager, SourceControl

# silence verify=False noise + GitHub redirect warnings during runs
warnings.filterwarnings("ignore")
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

logging.basicConfig(
    level = logging.INFO,
    format = "[%(asctime)s] %(levelname)-7s %(message)s",
    datefmt = "%H:%M:%S"
)

# ? live-repository coordinates shared by every concrete test case
REMOTE         : str      = "https://github.com/PyUtility/polyskills"
NAME           : str      = "sql-code-format"
LIBRARY        : Path     = Path("extensions/skills")
VERSION        : str      = "master"
EXPECTED       : Set[str] = {"SKILL.md"} # minimum file expected after extract
PAGINATION     : int      = 100

# ? canonical user-level skill installation root (platform-agnostic via Path.home())
USER_SKILL_ROOT  : Path   = Path.home() / ".claude" / "skills"
SKILL_FILENAME   : str    = "SKILL.md"


class GithubManagerTestCase(unittest.TestCase):
    """
    A reusable :class:`unittest.TestCase` base that provisions a
    :class:`polyskills.remote.sources.GithubManager` instance plus a
    per-test scratch directory which is torn down automatically.

    Concrete cases simply subclass this and add ``test_*`` methods -
    the manager is reachable via ``self.manager``, the per-test
    temporary root via ``self.staging``, and the conventional
    extraction destination via ``self.destination``.
    """

    @classmethod
    def setUpClass(cls) -> None:
        """
        Class-level fixture that builds a single
        :class:`GithubManager` shared by every test method in the
        class to avoid re-creating the HTTP session needlessly. Also
        redirects the tracker database to a per-class temporary file
        so the live ``~/.polyskills/polyskills.db`` is never touched
        by the test suite.
        """

        cls.logger = logging.getLogger(
            f"polyskills.tests.{cls.__name__}"
        )
        cls.manager = GithubManager(
            control = SourceControl(pagination = PAGINATION)
        )

        # ? redirect the tracker database to an isolated temp file
        # ? and reset the singleton so the new path is picked up.
        cls._db_dir = Path(
            tempfile.mkdtemp(prefix = "polyskills-db-")
        )
        cls._db_file = cls._db_dir / "polyskills.db"
        cls._original_resolver = _db_paths.resolve_db_path
        _db_paths.resolve_db_path = lambda : cls._db_file # type: ignore[assignment]
        _db_tracker.reset_tracker_for_tests()


    @classmethod
    def tearDownClass(cls) -> None:
        """
        Restore the original database path resolver and remove the
        per-class temporary database directory. Ensures the test
        suite leaves no scratch artefacts behind.
        """

        _db_tracker.reset_tracker_for_tests()
        _db_paths.resolve_db_path = cls._original_resolver # type: ignore[assignment]
        shutil.rmtree(cls._db_dir, ignore_errors = True)


    def setUp(self) -> None:
        """
        Per-test fixture that allocates an isolated temporary staging
        directory so concurrent or sequential cases never clash on
        the filesystem.
        """

        self.staging = Path(
            tempfile.mkdtemp(prefix = "polyskills-test-")
        )
        self.destination = self.staging / NAME


    def tearDown(self) -> None:
        """
        Per-test cleanup that removes the staging directory created
        by :meth:`setUp`. ``ignore_errors`` keeps the suite resilient
        on Windows where lingering file handles may briefly block
        deletion.
        """

        shutil.rmtree(self.staging, ignore_errors = True)


    def _extract(self) -> None:
        """
        Shared helper that performs a vanilla extension extraction into
        ``self.destination`` with the default ``exists='fail'`` policy
        so individual tests do not duplicate the dispatch boilerplate.

        The method asserts that the dispatcher returns ``None`` (its
        documented contract) so callers only need to assert post-state.
        """

        result = self.manager.get(
            REMOTE, mode = "extensions",
            name = NAME, library = "skills",
            source = LIBRARY, destination = self.destination,
            version = VERSION
        )
        self.assertIsNone(
            result,
            f"Expected None from extensions dispatch, got {result!r}"
        )
