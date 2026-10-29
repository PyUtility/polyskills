# -*- encoding: utf-8 -*-

"""
Pull the Better Comments Tags of the Remote into the VS Code Settings

Run the hook only when the tags are to be synced - it never runs
automatically. It reads ``settings.json.template`` of the hook folder
from the remote through git, compares its tags with the
``better-comments.tags`` of the VS Code settings, and writes the
merged tags back:

    * a tag only in the remote is added,
    * a tag only in the local settings is kept,
    * a tag that differs rejects the pull, unless ``--force`` is given
      to overwrite the local value with the remote one.

Only the ``better-comments.tags`` value of the settings is rewritten,
and the previous file is kept as ``settings.json.bak``.

.. code-block:: shell

    $ python pull.py --dry-run
    $ python pull.py --force

:NOTE: A pull with conflicts and without ``--force`` writes nothing,
    not even the tags that are only in the remote.
"""

import argparse
import sys

from errors import ExitCode
from hook import BaseHook
from repository import Repository
from tags import merge


class PullHook(BaseHook):
    """
    Sync the tags of the remote settings template into the VS Code
    settings, rejecting the pull when a tag differs, unless
    ``--force`` is given.
    """

    description = (
        "Sync the Better Comments tags of the polyskills settings"
        " template into the VS Code settings."
    )

    def _add_arguments(
        self, parser : argparse.ArgumentParser
    ) -> None:
        """
        Add the ``--force`` and ``--dry-run`` options.

        :type  parser: argparse.ArgumentParser
        :param parser: The command line, with the shared options.
        """

        parser.add_argument(
            "--force", action = "store_true",
            help = "overwrite the local tags that differ from the"
            " remote (the tags only in the local settings are kept)",
        )
        parser.add_argument(
            "--dry-run", action = "store_true",
            help = "report the changes and write nothing",
        )


    def run(self, args : argparse.Namespace) -> int:
        """
        Compare the local and the remote tags, and write the merged
        tags to the VS Code settings.

        :type  args: argparse.Namespace
        :param args: The parsed options.

        :raises HookError: When the settings, the template, or git
            fails.

        :rtype:   int
        :returns: ``0`` when the settings are in sync, or would be
            with ``--dry-run``; ``1`` when a conflict rejects it.
        """

        settings = self._settings(args)
        with Repository(args.remote, args.ref) as repository:
            template = self._template(args, repository)

        change = self._compare(args, settings, template)
        if change.conflicts and not args.force:
            print(
                f"\nRejected: {len(change.conflicts)} tag(s) differ"
                " from the remote - nothing was written.\nRun again"
                " with --force to overwrite them with the remote"
                " values (the local-only tags are kept)."
            )
            return ExitCode.REJECTED

        local  = settings.tags
        merged = merge(local, template.tags, overwrite = args.force)
        if merged == local:
            print("\nAlready in sync - nothing to write.")
            return ExitCode.OK

        summary = f"add {len(change.remote_only)} tag(s)"
        if args.force and change.conflicts:
            summary += f", overwrite {len(change.conflicts)}"

        if args.dry_run:
            print(f"\nDry run: would {summary} - nothing written.")
            return ExitCode.OK

        existed = settings.path.exists()
        settings.save(merged)
        print(f"\nUpdated the settings: {summary}.")
        if existed:
            print(f"The previous settings are in {settings.backup}.")

        return ExitCode.OK


if __name__ == "__main__":
    sys.exit(PullHook().main())
