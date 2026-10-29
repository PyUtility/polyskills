# -*- encoding: utf-8 -*-

"""
Exit Codes, Errors, and Warnings of the Better Comments Hooks

Every failure of a hook is raised as a :class:`HookError` subclass
that carries the exit code of the failure, so :class:`hook.BaseHook`
turns it into one message and one exit code. The codes are shared by
``pull.py`` and ``push.py``:

    * ``0`` - done, or nothing to do.
    * ``1`` - rejected: ``pull.py`` found conflicts, or ``push.py``
      was declined or could not ask for confirmation.
    * ``2`` - invalid usage, settings, or template.
    * ``3`` - git, network, or reference failure.
    * ``4`` - the remote refused the push.
    * ``130`` - interrupted by the user.
"""

import enum
import sys


class ExitCode(enum.IntEnum):
    """
    The exit codes of the hooks, as listed in the module description.
    """

    OK          = 0
    REJECTED    = 1
    INVALID     = 2
    GIT         = 3
    REFUSED     = 4
    INTERRUPTED = 130


class HookError(Exception):
    """
    Base error of the hooks, raised with a message for the user. The
    ``code`` class attribute is the exit code of the failure.
    """

    code : ExitCode = ExitCode.INVALID


class SettingsError(HookError):
    """
    The VS Code settings or the settings template cannot be read,
    parsed, or written.
    """

    code = ExitCode.INVALID


class GitError(HookError):
    """
    A git command failed - ``git`` is missing, the network or the
    authentication failed, or the reference does not exist.
    """

    code = ExitCode.GIT


class PushRefusedError(GitError):
    """
    The remote refused the push, usually for lack of write access.
    """

    code = ExitCode.REFUSED


def warn(message : str) -> None:
    """
    Print a warning for the user on the standard error stream.

    :type  message: str
    :param message: The warning, without the ``warning:`` prefix.
    """

    print(f"warning: {message}", file = sys.stderr)
