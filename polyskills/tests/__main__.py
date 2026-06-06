# -*- encoding: utf-8 -*-

"""
Entry-point for ``python -m polyskills.tests``
----------------------------------------------

Discovers and runs every ``test_*.py`` module that lives under the
:mod:`polyskills.tests` package and exits with a shell-friendly
status code so the entry-point can be wired straight into a CI step
without an additional shim.
"""

import os

# ! suppress the import-time tracker bootstrap so the live user-level
# ! ``~/.polyskills/polyskills.db`` is never touched by the suite.
# ! the variable must be set before any ``polyskills`` import below.
os.environ.setdefault("POLYSKILLS_DISABLE_BOOTSTRAP", "1")

import sys
import unittest

import polyskills.tests as suite_pkg


def main() -> int:
    """
    Discover and run every test case in the :mod:`polyskills.tests`
    package using the package's own filesystem location, so that the
    command works irrespective of the current working directory.

    :rtype:   int
    :returns: ``0`` when every test passed, ``1`` otherwise.
    """

    start_dir = os.path.dirname(os.path.abspath(suite_pkg.__file__))

    loader = unittest.TestLoader()
    suite = loader.discover(start_dir = start_dir, top_level_dir = None)
    runner = unittest.TextTestRunner(verbosity = 2)
    result = runner.run(suite)

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
