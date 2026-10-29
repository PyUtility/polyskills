# -*- encoding: utf-8 -*-

"""
Base Class of the Better Comments Hooks

``pull.py`` and ``push.py`` share the options that select the VS Code
settings and the remote, the report of the difference between the
local and the remote tags, and the handling of errors and exit
codes. :class:`BaseHook` holds them, and each hook adds only its own
options and its :meth:`BaseHook.run` step.

:NOTE: The hooks run only when the user calls them - they are never
    registered to run automatically.
"""

import abc
import argparse
import pathlib
import sys

from typing import Optional

from errors import ExitCode, HookError
from repository import (
    DEFAULT_REF, DEFAULT_REMOTE, TEMPLATE_PATH, Repository, redact
)
from tags import TagDiff, diff, differences, index, show
from vscode import Settings, settings_path


class BaseHook(abc.ABC):
    """
    Base class of a hook: it builds the command line with the shared
    options, runs the hook, and turns every :class:`errors.HookError`
    into its message and exit code. A subclass sets the
    ``description`` of its command line, and implements
    :meth:`_add_arguments` and :meth:`run`.
    """

    description = ""

    def __init__(self) -> None:
        self.parser = argparse.ArgumentParser(
            description = self.description
        )

        target = self.parser.add_mutually_exclusive_group()
        target.add_argument(
            "--settings", type = pathlib.Path, metavar = "PATH",
            help = "the VS Code settings file (default: the user"
            " settings of VS Code)",
        )
        target.add_argument(
            "--workspace", action = "store_true",
            help = "use .vscode/settings.json of the current folder",
        )

        self.parser.add_argument(
            "--remote", default = DEFAULT_REMOTE, metavar = "URL",
            help = "the repository with the settings template"
            " (default: %(default)s)",
        )
        self.parser.add_argument(
            "--ref", default = DEFAULT_REF, metavar = "BRANCH",
            help = "the branch of the remote (default: %(default)s)",
        )

        self._add_arguments(self.parser)


    @abc.abstractmethod
    def _add_arguments(
        self, parser : argparse.ArgumentParser
    ) -> None:
        """
        Add the options of the hook to the command line.

        :type  parser: argparse.ArgumentParser
        :param parser: The command line, with the shared options.
        """


    @abc.abstractmethod
    def run(self, args : argparse.Namespace) -> int:
        """
        Run the hook with the parsed command line.

        :type  args: argparse.Namespace
        :param args: The parsed options.

        :raises HookError: When the hook fails - :meth:`main` prints
            the error and returns its exit code.

        :rtype:   int
        :returns: The exit code, an :class:`errors.ExitCode`.
        """


    def main(self, argv : Optional[list[str]] = None) -> int:
        """
        Parse the options, run the hook, and return its exit code.

        :type  argv: Optional[list[str]]
        :param argv: The arguments, ``sys.argv[1:]`` by default.

        :rtype:   int
        :returns: The exit code, an :class:`errors.ExitCode`.
        """

        _reconfigure()
        args = self.parser.parse_args(argv)
        try:
            return int(self.run(args))
        except HookError as error:
            print(f"error: {error}", file = sys.stderr)
            return int(error.code)
        except KeyboardInterrupt:
            print("\ninterrupted", file = sys.stderr)
            return int(ExitCode.INTERRUPTED)


    @staticmethod
    def _settings(args : argparse.Namespace) -> Settings:
        """
        Load the VS Code settings that the options select.

        :type  args: argparse.Namespace
        :param args: The parsed options.

        :raises SettingsError: When the settings cannot be read.

        :rtype:   Settings
        :returns: The loaded settings.
        """

        path = args.settings or settings_path(args.workspace)
        return Settings.load(path.expanduser())


    @staticmethod
    def _template(
        args : argparse.Namespace, repository : Repository
    ) -> Settings:
        """
        Read the settings template from the clone of the remote.

        :type  args: argparse.Namespace
        :param args: The parsed options.

        :type  repository: Repository
        :param repository: The clone of the remote.

        :raises GitError: When the branch has no settings template.

        :raises SettingsError: When the template is not valid.

        :rtype:   Settings
        :returns: The parsed template.
        """

        source = f"{TEMPLATE_PATH} ({args.ref})"
        return Settings(repository.read(), source)


    @staticmethod
    def _compare(
        args : argparse.Namespace, settings : Settings,
        template : Settings,
    ) -> TagDiff:
        """
        Compare the local tags with the remote ones and print the
        report, with the properties of every tag in conflict.

        :type  args: argparse.Namespace
        :param args: The parsed options.

        :type  settings: Settings
        :param settings: The VS Code settings.

        :type  template: Settings
        :param template: The settings template of the remote.

        :rtype:   TagDiff
        :returns: The difference between the local and remote tags.
        """

        local, remote = settings.tags, template.tags
        change = diff(local, remote)

        print(f"Settings : {settings.path}")
        print(f"Remote   : {redact(args.remote)} ({args.ref})")
        print()
        print(f"  in sync     : {len(change.same)} tag(s)")
        for label, names in (
            ("remote only", change.remote_only),
            ("local only", change.local_only),
        ):
            if names:
                print(f"  {label:<11} : {', '.join(names)}")

        mine, theirs = index(local), index(remote)
        for name in change.conflicts:
            print(f"  conflict    : {name}")
            rows = differences(mine[name], theirs[name])
            for key, old, new in rows:
                print(f"{'':18}{key}: {show(old)} (local),"
                      f" {show(new)} (remote)")

        return change


def _reconfigure() -> None:
    """
    Print the characters that the console cannot encode as escapes
    (for example, an emoji tag on a legacy Windows console) instead of
    failing with an encoding error.
    """

    for stream in (sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            stream.reconfigure(errors = "backslashreplace")
