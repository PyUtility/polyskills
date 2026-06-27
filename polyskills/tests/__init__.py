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

__version__ = "v1.0.0"

# init-time options registrations, use base.py for shared fixtures
