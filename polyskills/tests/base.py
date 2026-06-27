# -*- encoding: utf-8 -*-

"""
Shared Fixtures and Constants for the Polyskills Test Suite
-----------------------------------------------------------

Centralizes the live-repository coordinates, the expected payload,
and the bring-up/tear-down lifecycle for every concrete test case so
that individual modules stay focused on the contract they verify and
the suite remains DRY.
"""

import os
import shutil
import logging
import tempfile
import warnings
import unittest

from pathlib import Path
from typing import Set

import urllib3

from polyskills.remote.sources import GithubManager, SourceControl

# silence insecure-request + GitHub redirect noise for opt-in live runs
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

# ? live-network tests are opt-in to keep the default test run hermetic
# ? and offline; set POLYSKILLS_RUN_LIVE=1 to exercise them. Behind a
# ? TLS-intercepting proxy also set POLYSKILLS_NO_VERIFY=1 so the live
# ? fixture can reach GitHub without certificate verification.
_RUN_LIVE : str  = os.environ.get("POLYSKILLS_RUN_LIVE", "")
_VERIFY   : bool = not os.environ.get("POLYSKILLS_NO_VERIFY")

# ? canonical user-level skill installation root (platform-agnostic via Path.home())
USER_SKILL_ROOT  : Path   = Path.home() / ".claude" / "skills"
SKILL_FILENAME   : str    = "SKILL.md"


@unittest.skipUnless(
    _RUN_LIVE, "live-network tests; set POLYSKILLS_RUN_LIVE=1 to run"
)
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
        class to avoid re-creating the HTTP session needlessly.
        """

        cls.logger = logging.getLogger(
            f"polyskills.tests.{cls.__name__}"
        )
        cls.manager = GithubManager(
            control = SourceControl(
                pagination = PAGINATION, verify = _VERIFY
            )
        )


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
