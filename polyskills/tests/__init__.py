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

__version__ = "v1.0.0"

# ? Redirect the tracking database onto an isolated temporary file for
# ? the whole test run so no test ever reads from or writes to the real
# ? user-level ``~/.polyskills/records.db``. ``default_database_path``
# ? consults this variable at call time, so setting it here - before
# ? any test triggers a tracking write - is sufficient. The value is
# ? only a safety net; the dedicated database tests still pass an
# ? explicit path for strict per-test isolation. ``setdefault`` keeps
# ? an externally supplied override (for example in CI) intact.
os.environ.setdefault(
    "POLYSKILLS_DB_PATH",
    os.path.join(tempfile.gettempdir(), "polyskills-test-records.db")
)

# init-time options registrations, use base.py for shared fixtures
