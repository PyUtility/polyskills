# -*- encoding: utf-8 -*-

"""
Errors and Warnings Handler for the Project
-------------------------------------------

Create a standard documentation with help notes to manager errors and
warnings for the module.
"""

from polyskills.error import warnings
from polyskills.error import exceptions
from polyskills.error.exceptions import (
    PolyskillsError,
    ValidationError,
    RemoteError,
    ExtractionError,
)

__all__ = [
    "exceptions", "warnings",
    "PolyskillsError", "ValidationError",
    "RemoteError", "ExtractionError",
]
