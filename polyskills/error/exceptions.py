# -*- encoding: utf-8 -*-

"""
Custom Exception Hierarchy for Polyskills
-----------------------------------------

A small, explicit exception hierarchy rooted at :class:`PolyskillsError`
so callers can distinguish the failure modes of the remote pipeline -
input validation, remote transport, and archive extraction - from
unrelated runtime errors, while a single ``except PolyskillsError`` still
catches every domain failure raised by the package.

:NOTE: :class:`ValidationError` also derives from the builtin
    :class:`ValueError` to preserve backward compatibility with callers
    and tests that catch ``ValueError`` for an invalid input.
"""


class PolyskillsError(Exception):
    """
    Base class for every :mod:`polyskills` domain error.

    Catch this to handle any failure raised deliberately by the package
    while letting genuinely unexpected exceptions propagate untouched.
    """


class ValidationError(PolyskillsError, ValueError):
    """
    Raised when a user-supplied argument fails validation - for example
    an unknown ``mode``, a missing required value, an unsupported remote
    URL, or a conflicting TLS option. Subclasses :class:`ValueError` so
    that existing ``except ValueError`` handlers keep working.
    """


class RemoteError(PolyskillsError):
    """
    Raised when a remote source behaves unexpectedly, such as a tag
    pagination chain that exceeds the configured page safety limit.
    """


class ExtractionError(PolyskillsError):
    """
    Raised when a downloaded archive violates a safety constraint - a
    member escaping the destination directory (path traversal), or the
    download / extraction exceeding its configured size limit.
    """
