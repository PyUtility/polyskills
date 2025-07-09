# -*- encoding: utf-8 -*-

"""
Control for Valid List of Supported Remote with REST API Services
-----------------------------------------------------------------

The application is designed to be source agnostic - meaning a remote
source which supports ``git`` document hosting and has a REST API to
fetch data using :mod:`requests` is supported.

.. code-block:: python

    print([member.name for member in ValidSources]) # suported sources
    >> ['GITHUB', ...]

    # alternatively, get valid sources using cli::
    polyskills --help
    >> ...
    >> Supported Sources: [('GITHUB', 'https://www.github.com/'), ...]
"""

from enum import Enum

class ValidSources(Enum):
    GITHUB = "https://www.github.com/"
