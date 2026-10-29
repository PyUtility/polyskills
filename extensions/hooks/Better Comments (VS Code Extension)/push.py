# -*- encoding: utf-8 -*-

"""
Push the Better Comments Tags Added Locally as a Pull Request

Run the hook only when the local tags are to be shared - it never
runs automatically. It compares the ``better-comments.tags`` of the
VS Code settings with ``settings.json.template`` of the hook folder
on the remote and proposes the tags that are only in the local
settings. With ``--include-changed``, it also proposes the local
values of the tags that differ.

Nobody pushes to the default branch of the remote: after the user
confirms, the hook commits the proposed template on a new
``better-comments/<date>-<tags>`` branch, pushes the branch, and opens
a pull request (with ``gh`` when it is installed, otherwise with the
compare page of GitHub). Without write access to the remote, push the
branch to a fork of it with ``--fork``.

.. code-block:: shell

    $ python push.py
    $ python push.py --fork https://github.com/<user>/polyskills.git

:NOTE: The hook always asks before it pushes, and aborts when it runs
    without an interactive terminal.
"""

import argparse
import sys
import textwrap

from errors import ExitCode
from hook import BaseHook
from repository import TEMPLATE_PATH, Repository, check_remote
from tags import differences, index, merge, show


class PushHook(BaseHook):
    """
    Propose the tags that are only in the VS Code settings (and, with
    ``--include-changed``, the local values of the tags that differ)
    as a pull request to the remote settings template.
    """

    description = (
        "Propose the Better Comments tags added locally to the"
        " polyskills settings template as a pull request."
    )

    def _add_arguments(
        self, parser : argparse.ArgumentParser
    ) -> None:
        """
        Add the ``--include-changed`` and ``--fork`` options.

        :type  parser: argparse.ArgumentParser
        :param parser: The command line, with the shared options.
        """

        parser.add_argument(
            "--include-changed", action = "store_true",
            help = "also propose the local values of the tags that"
            " differ from the remote",
        )
        parser.add_argument(
            "--fork", metavar = "URL",
            help = "push the branch to this fork of the remote, when"
            " you cannot push to the remote itself",
        )


    def run(self, args : argparse.Namespace) -> int:
        """
        Compare the local and the remote tags, ask the user, and
        propose the local tags as a pull request.

        :type  args: argparse.Namespace
        :param args: The parsed options.

        :raises HookError: When the settings, the template, or git
            fails.

        :rtype:   int
        :returns: ``0`` when the pull request is proposed or there is
            nothing to propose, ``1`` when the user declines.
        """

        if args.fork is not None:
            check_remote(args.fork, "--fork")

        settings = self._settings(args)
        with Repository(args.remote, args.ref) as repository:
            template = self._template(args, repository)
            change   = self._compare(args, settings, template)

            added, changed = list(change.local_only), []
            if args.include_changed:
                changed = list(change.conflicts)

            if not added and not changed:
                print("\nNothing to propose - the remote has every"
                      " local tag.")
                if change.conflicts:
                    print("Run again with --include-changed to"
                          " propose the local values of the tags"
                          " that differ.")
                return ExitCode.OK

            print(f"\nProposal for {TEMPLATE_PATH} ({args.ref}):")
            for label, names in (("add", added), ("update", changed)):
                for name in names:
                    print(f"  {label:<6} : {name}")

            count = len(added) + len(changed)
            if not _confirm(
                f"\nCreate a pull request with {count} tag(s)? [y/N] "
            ):
                print("Aborted - nothing was pushed.")
                return ExitCode.REJECTED

            local, remote = index(settings.tags), index(template.tags)
            message = commit_message(
                [local[name] for name in added],
                [(remote[name], local[name]) for name in changed],
            )
            proposal = merge(
                template.tags, settings.tags,
                overwrite = args.include_changed,
            )
            result = repository.publish(
                template.render(proposal), message, added + changed,
                fork = args.fork,
            )

        print(f"\nPushed {result.branch} to {result.target}.")
        if result.created:
            print(f"Created the pull request: {result.url}")
        elif result.url:
            opened = " (opened in the browser)"
            note   = opened if result.browsed else ""
            print(f"Open the pull request{note}: {result.url}")
        else:
            print(f"Open a pull request of {result.branch} into"
                  f" {args.ref} on the remote.")

        return ExitCode.OK


def commit_message(
    added : list[dict], changed : list[tuple[dict, dict]]
) -> str:
    """
    Write the commit message of a proposal in the style of the
    ``git-commiter`` skill: an emoji subject of at most 72 characters,
    one paragraph, and a bullet for each tag. The message has no
    co-author trailer, as the user runs the hook.

    :type  added: list[dict]
    :param added: The local tags that the remote does not have.

    :type  changed: list[tuple[dict, dict]]
    :param changed: The ``(remote, local)`` values of each tag that
        differs.

    :rtype:   str
    :returns: The commit message, also the title and the body of the
        pull request.
    """

    names = [tag["tag"] for tag in added]
    names += [new["tag"] for _, new in changed]

    if added and changed:
        prefix, verb = "✨🛠️ feat(skills)", "add and update"
    elif added:
        prefix, verb = "✨ feat(skills)", "add"
    else:
        prefix, verb = "🛠️ refactor(skills)", "update"

    noun    = "tags" if len(names) > 1 else "tag"
    quoted  = ", ".join(f"`{name}`" for name in names)
    subject = f"{prefix}: {verb} better comments {noun} {quoted}"
    if len(subject) > 72:
        count   = len(names)
        subject = f"{prefix}: {verb} {count} better comments {noun}"

    paragraph = textwrap.fill(
        "Propose the Better Comments tags below, taken from the local"
        " VS Code settings by the push.py hook, for the settings"
        " template of the Better Comments hooks.", 72,
    )

    bullets = [f"add `{tag['tag']}` - {_style(tag)}" for tag in added]
    bullets += [
        f"update `{new['tag']}` - " + ", ".join(
            f"{key} {show(before)} -> {show(after)}"
            for key, before, after in differences(old, new)
        )
        for old, new in changed
    ]
    bullets = [
        textwrap.fill(
            bullet, 72,
            initial_indent = "- ", subsequent_indent = "  ",
        )
        for bullet in bullets
    ]

    blocks = [subject, paragraph, "\n".join(bullets)]
    return "\n\n".join(blocks) + "\n"


def _style(tag : dict) -> str:
    """
    Describe the style of a tag by its properties that are not off
    (``false`` or a ``transparent`` background).

    :type  tag: dict
    :param tag: The tag.

    :rtype:   str
    :returns: The style, such as ``color "#D19184", bold true``.
    """

    style = [
        f"{key} {show(value)}" for key, value in tag.items()
        if key != "tag" and value not in (False, None, "transparent")
    ]
    return ", ".join(style) or "default style"


def _confirm(question : str) -> bool:
    """
    Ask the user a yes or no question on the terminal. Only ``y`` or
    ``yes`` confirms; an empty answer or the end of input declines.

    :type  question: str
    :param question: The question, with its ``[y/N]`` hint.

    :rtype:   bool
    :returns: ``True`` when the user confirms, ``False`` otherwise and
        when the standard input is not an interactive terminal.
    """

    if sys.stdin is None or not sys.stdin.isatty():
        print("\nNo interactive terminal to confirm the pull request"
              " - run push.py from a terminal.", file = sys.stderr)
        return False

    try:
        answer = input(question)
    except EOFError:
        print()
        return False

    return answer.strip().lower() in {"y", "yes"}


if __name__ == "__main__":
    sys.exit(PushHook().main())
