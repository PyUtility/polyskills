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

__version__ = "v1.0.0"

# init-time options registrations, use base.py for shared fixtures
