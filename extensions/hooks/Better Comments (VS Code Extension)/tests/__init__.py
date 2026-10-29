# -*- encoding: utf-8 -*-

"""
Tests of the Better Comments Hooks
==================================

The hook folder is not a package (its name has spaces), so the tests
add it to ``sys.path`` and import the hook modules the way the
scripts import each other. Run the tests from the hook folder:

.. code-block:: shell

    $ python -m unittest discover -s tests -t .
"""

import pathlib
import sys

HOOK_DIR = str(pathlib.Path(__file__).resolve().parent.parent)
if HOOK_DIR not in sys.path:
    sys.path.insert(0, HOOK_DIR)
