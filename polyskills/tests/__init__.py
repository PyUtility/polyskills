# -*- encoding: utf-8 -*-

"""
Test Suite for the Polyskills Package
=====================================

A :mod:`unittest` based automated test-suite for the :mod:`polyskills`
package. The default run is hermetic: the CLI, path-resolution, and the
security regression tests (TLS forwarding, archive path-traversal, size
caps, pagination cap) mock the network and synthesise archive fixtures
in memory, so no connection is needed.

Run from the repository root::

    python -m unittest discover -v -s polyskills/tests -t .
    # or, equivalently
    python -m polyskills.tests

:NOTE: The end-to-end tests that hit the live
``https://api.github.com`` REST API and the PyUtility/polyskills
repository are opt-in - set ``POLYSKILLS_RUN_LIVE=1`` to enable them.
Behind a TLS-intercepting proxy also set ``POLYSKILLS_NO_VERIFY=1`` so
the live fixture can reach GitHub, and export ``POLYSKILLS_REMOTE_TOKEN``
(or the workflow's ``GITHUB_TOKEN``) to raise the anonymous rate-limit.
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
