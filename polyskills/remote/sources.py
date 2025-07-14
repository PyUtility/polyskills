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
from dataclasses import dataclass

class ValidSources(Enum):
    GITHUB = "https://www.github.com/"


@dataclass(frozen = True)
class SourceControl:
    """
    Additional parameters for remote source data control. These are
    typically for advanced users.

    :type  pagination: int
    :param pagination: A pagination parameter controls how manye
        results are returned in one page for a ``GET`` request from
        ``https://api.github.com/repos/{owner}/{repo}/tags/`` (same
        can be applicable for other websites). Defaults to 100, which
        is the maximum value allowed.

    Each parameter should be available as a CLI command for dynamic
    control which sets the data class defaults during runtime.
    """

    pagination : int = 100
