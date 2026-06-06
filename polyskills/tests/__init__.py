# -*- encoding: utf-8 -*-

"""
Test Suite for the Polyskills Package
=====================================

A :mod:`unittest` based automated test-suite for the :mod:`polyskills`
package. The tests exercise the public dispatcher
:meth:`polyskills.remote.sources.GithubManager.get` end-to-end against
a live GitHub repository to validate the contracts surfaced by the
remote source manager.

Run from the repository root::

    python -m unittest discover -v -s polyskills/tests -t .
    # or, equivalently
    python -m polyskills.tests

:NOTE: These tests perform live HTTP requests against
``https://api.github.com``. A network connection is required, and the
GitHub anonymous rate-limit may throttle very frequent runs - export
``POLYSKILLS_REMOTE_TOKEN`` (or set the workflow's ``GITHUB_TOKEN``)
to authenticate the requests.
"""

import os
import tempfile

from pathlib import Path

# ! redirect the polyskills tracking database to a per-process scratch
# ! file *before* importing :mod:`polyskills` so the import-time
# ! bootstrap never touches the real ``~/.polyskills/polyskills.db``.
_TEST_DB_DIR = Path(tempfile.mkdtemp(prefix = "polyskills-suite-"))
_TEST_DB     = _TEST_DB_DIR / "polyskills.db"

from polyskills.db import paths as _db_paths # noqa: E402
from polyskills.db import tracker as _db_tracker # noqa: E402

_db_paths.resolve_db_path = lambda : _TEST_DB # type: ignore[assignment]
_db_tracker.reset_tracker_for_tests()

__version__ = "v1.0.0"

# init-time options registrations, use base.py for shared fixtures
