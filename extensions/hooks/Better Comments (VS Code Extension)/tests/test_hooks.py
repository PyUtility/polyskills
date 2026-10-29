# -*- encoding: utf-8 -*-

"""
End-to-End Tests of ``pull.py`` and ``push.py``

The hooks run in the process against a local bare repository (see
:class:`tests.base.HookTestCase`), so the tests need git but never
the network, the real VS Code settings, or a browser.
"""

import datetime as dt
import io
import json
import os
import stat
import unittest

from unittest import mock

from errors import ExitCode, HookError, PushRefusedError
from pull import PullHook
from push import PushHook, _confirm, commit_message
from repository import (
    TEMPLATE_PATH, Repository, _failure, branch_name, check_remote,
    compare_url, github, redact,
)
from tests.base import HookTestCase, git, template_tags
from vscode import TAGS_KEY, Settings

LOCAL_SETTINGS = """{
    // keep this comment
    "editor.tabSize": 4,
}
"""

BRANCH = r"^better-comments/\d{4}-\d{2}-\d{2}-"

MINE = {
    "tag" : "note", "color" : "#00FF00", "strikethrough" : False,
    "underline" : False, "backgroundColor" : "transparent",
    "bold" : True, "italic" : False,
}


class TestPull(HookTestCase):
    """
    ``pull.py`` adds the remote tags, keeps the local-only ones, and
    rejects a conflict unless ``--force`` is given.
    """

    def setUp(self) -> None:
        super().setUp()
        self.url = self.remote()


    def pull(self, *args : str) -> tuple[int, str]:
        """
        Run ``pull.py`` on the test settings and the local remote.

        :type  args: str
        :param args: More command-line arguments.

        :rtype:   tuple[int, str]
        :returns: The exit code and the output.
        """

        return self.run_hook(
            PullHook(), "--settings", str(self.settings),
            "--remote", self.url, *args,
        )


    def write_tags(self, tags : list[dict]) -> None:
        """
        Write the test settings with ``tags``.

        :type  tags: list[dict]
        :param tags: The local tags.
        """

        text = Settings(LOCAL_SETTINGS, "test").render(tags)
        self.settings.write_text(text, encoding = "utf-8")


    def test_adds_tags_and_second_pull_is_a_no_op(self) -> None:
        self.settings.write_text(LOCAL_SETTINGS, encoding = "utf-8")

        code, output = self.pull()
        self.assertEqual(code, ExitCode.OK, output)
        text = self.settings.read_text(encoding = "utf-8")
        self.assertIn("// keep this comment", text)
        self.assertEqual(Settings(text, "test").tags, template_tags())

        backup = self.settings.with_name("settings.json.bak")
        backup.unlink()
        before = self.settings.read_bytes()

        code, output = self.pull()
        self.assertEqual(code, ExitCode.OK, output)
        self.assertIn("Already in sync", output)
        self.assertEqual(self.settings.read_bytes(), before)
        self.assertFalse(backup.exists())


    def test_conflict_is_rejected(self) -> None:
        tags = template_tags()
        tags[0]["color"] = "#000000"
        self.write_tags(tags)
        before = self.settings.read_bytes()

        code, output = self.pull()
        self.assertEqual(code, ExitCode.REJECTED, output)
        self.assertIn("--force", output)
        self.assertIn('"#000000" (local)', output)
        self.assertEqual(self.settings.read_bytes(), before)


    def test_force_overwrites_and_keeps_local_only(self) -> None:
        tags = template_tags()
        tags[0]["color"] = "#000000"
        self.write_tags(tags + [MINE])

        code, output = self.pull("--force")
        self.assertEqual(code, ExitCode.OK, output)

        result = Settings.load(self.settings).tags
        self.assertEqual(result, template_tags() + [MINE])


    def test_dry_run_with_conflict_is_rejected(self) -> None:
        tags = template_tags()
        tags[0]["color"] = "#000000"
        self.write_tags(tags)

        code, output = self.pull("--dry-run")
        self.assertEqual(code, ExitCode.REJECTED, output)


    @unittest.skipIf(
        getattr(os, "geteuid", lambda: 1)() == 0, "root can write"
    )
    def test_read_only_settings(self) -> None:
        self.write_tags([MINE])
        os.chmod(self.settings, stat.S_IREAD)
        self.addCleanup(os.chmod, self.settings, stat.S_IWRITE)
        before = self.settings.read_bytes()

        code, output = self.pull()
        self.assertEqual(code, ExitCode.INVALID, output)
        self.assertIn("read-only", output)
        self.assertEqual(self.settings.read_bytes(), before)
        names = [path.name for path in self.temp.iterdir()]
        self.assertEqual(
            [name for name in names if "settings" in name],
            ["settings.json"],
        )


    def test_template_not_utf8(self) -> None:
        self.url = self.remote(data = b'{"a": "\xff"}')
        code, output = self.pull()
        self.assertEqual(code, ExitCode.INVALID, output)
        self.assertIn("not UTF-8", output)


    def test_dry_run_writes_nothing(self) -> None:
        self.settings.write_text(LOCAL_SETTINGS, encoding = "utf-8")

        code, output = self.pull("--dry-run")
        self.assertEqual(code, ExitCode.OK, output)
        self.assertIn("Dry run", output)
        text = self.settings.read_text(encoding = "utf-8")
        self.assertEqual(text, LOCAL_SETTINGS)


    def test_missing_template_fails(self) -> None:
        code, output = self.run_hook(
            PullHook(), "--settings", str(self.settings),
            "--remote", self.url, "--ref", "missing",
        )
        self.assertEqual(code, ExitCode.GIT, output)


    def test_invalid_remote(self) -> None:
        code, output = self.run_hook(
            PullHook(), "--settings", str(self.settings),
            "--remote", "ext::sh -c touch% /tmp/pwned",
        )
        self.assertEqual(code, ExitCode.INVALID, output)


class TestPush(HookTestCase):
    """
    ``push.py`` proposes the local-only tags on a new branch, only
    after the user confirms.
    """

    def setUp(self) -> None:
        super().setUp()
        self.url = self.remote()

        tags = template_tags() + [MINE]
        self.settings.write_text(
            json.dumps({TAGS_KEY : tags}, indent = 4),
            encoding = "utf-8",
        )


    def push(self, confirm : bool, *args : str) -> tuple[int, str]:
        """
        Run ``push.py`` on the test settings and the local remote,
        with the confirmation answered by ``confirm``.

        :type  confirm: bool
        :param confirm: The answer of the user.

        :type  args: str
        :param args: More command-line arguments.

        :rtype:   tuple[int, str]
        :returns: The exit code and the output.
        """

        with mock.patch("push._confirm", return_value = confirm):
            return self.run_hook(
                PushHook(), "--settings", str(self.settings),
                "--remote", self.url, *args,
            )


    def branches(self) -> list[str]:
        """
        List the branches of the local remote, except ``master``.

        :rtype:   list[str]
        :returns: The branch names, sorted.
        """

        heads = git("-C", str(self.bare), "branch", "--list",
                    "--format=%(refname:short)")
        names = heads.splitlines()
        return sorted(name for name in names if name != "master")


    def test_proposes_local_only_tags(self) -> None:
        code, output = self.push(True)
        self.assertEqual(code, ExitCode.OK, output)
        self.assertIn(f"to {self.url}", output)

        (branch,) = self.branches()
        self.assertRegex(branch, BRANCH + r"note$")

        text = git("-C", str(self.bare), "show",
                   f"{branch}:{TEMPLATE_PATH}")
        self.assertEqual(
            json.loads(text)[TAGS_KEY], template_tags() + [MINE]
        )

        subject = git("-C", str(self.bare), "log", "-1",
                      "--format=%s", branch)
        self.assertEqual(
            subject.strip(),
            "✨ feat(skills): add better comments tag `note`",
        )


    def test_second_push_takes_a_new_branch_name(self) -> None:
        self.push(True)
        code, output = self.push(True)
        self.assertEqual(code, ExitCode.OK, output)

        first, second = self.branches()
        self.assertRegex(first, BRANCH + r"note$")
        self.assertEqual(second, first + "-2")


    def test_invalid_fork_fails_before_asking(self) -> None:
        with mock.patch("push._confirm") as confirm:
            with mock.patch("push.Repository") as repository:
                code, output = self.run_hook(
                    PushHook(), "--settings", str(self.settings),
                    "--remote", self.url, "--fork", "ext::sh -c id",
                )

        self.assertEqual(code, ExitCode.INVALID, output)
        confirm.assert_not_called()
        repository.assert_not_called()


    def test_declined_pushes_nothing(self) -> None:
        code, output = self.push(False)
        self.assertEqual(code, ExitCode.REJECTED, output)
        self.assertEqual(self.branches(), [])


    def test_nothing_to_propose(self) -> None:
        self.settings.write_text(
            json.dumps({TAGS_KEY : template_tags()}),
            encoding = "utf-8",
        )
        code, output = self.push(True)
        self.assertEqual(code, ExitCode.OK, output)
        self.assertIn("Nothing to propose", output)
        self.assertEqual(self.branches(), [])


    def test_include_changed(self) -> None:
        tags = template_tags()
        tags[0]["color"] = "#000000"
        self.settings.write_text(
            json.dumps({TAGS_KEY : tags}), encoding = "utf-8"
        )

        code, output = self.push(True)
        self.assertEqual(code, ExitCode.OK, output)
        self.assertIn("--include-changed", output)
        self.assertEqual(self.branches(), [])

        code, output = self.push(True, "--include-changed")
        self.assertEqual(code, ExitCode.OK, output)
        branch = self.branches()[0]
        text = git("-C", str(self.bare), "show",
                   f"{branch}:{TEMPLATE_PATH}")
        self.assertEqual(json.loads(text)[TAGS_KEY], tags)


class TestConfirm(unittest.TestCase):
    """
    The confirmation never passes without an interactive "yes".
    """

    def test_not_a_terminal(self) -> None:
        with mock.patch("sys.stdin", io.StringIO("y\n")):
            with mock.patch("sys.stderr", io.StringIO()):
                self.assertFalse(_confirm("? "))


    def test_answers(self) -> None:
        stdin = mock.Mock()
        stdin.isatty.return_value = True
        for answer, expected in (
            ("y", True), ("YES", True), ("", False), ("n", False),
            ("yes please", False),
        ):
            with self.subTest(answer = answer):
                with mock.patch("sys.stdin", stdin):
                    with mock.patch("builtins.input",
                                    return_value = answer):
                        self.assertIs(_confirm("? "), expected)


    def test_end_of_input(self) -> None:
        stdin = mock.Mock()
        stdin.isatty.return_value = True
        with mock.patch("sys.stdin", stdin):
            with mock.patch("builtins.input", side_effect = EOFError):
                with mock.patch("sys.stdout", io.StringIO()):
                    self.assertFalse(_confirm("? "))


class TestHelpers(unittest.TestCase):
    """
    The pure helpers of ``repository.py`` and ``push.py``.
    """

    def test_branch_name(self) -> None:
        day = dt.date(2026, 10, 29)
        self.assertEqual(
            branch_name(["..versionadded::", "My Note"], day),
            "better-comments/2026-10-29-versionadded-my-note",
        )
        self.assertRegex(
            branch_name(["!", "?"], day),
            r"^better-comments/2026-10-29-tags-[0-9a-f]{7}$",
        )
        self.assertLessEqual(
            len(branch_name(["a" * 100], day)),
            len("better-comments/2026-10-29-") + 40,
        )


    def test_github(self) -> None:
        for url in (
            "https://github.com/PyUtility/polyskills.git",
            "https://user:token@GitHub.com/PyUtility/polyskills/",
            "git@github.com:PyUtility/polyskills.git",
            "ssh://git@ssh.github.com:443/PyUtility/polyskills.git",
        ):
            with self.subTest(url = url):
                self.assertEqual(
                    github(url), ("PyUtility", "polyskills")
                )

        self.assertIsNone(github("https://gitlab.com/a/b.git"))
        self.assertIsNone(github("file:///tmp/remote.git"))


    def test_compare_url(self) -> None:
        self.assertEqual(
            compare_url(("o", "r"), "master", "me:better-comments/x"),
            "https://github.com/o/r/compare/master..."
            "me:better-comments/x?expand=1",
        )


    def test_failure(self) -> None:
        forbidden = (
            "fatal: unable to access 'https://github.com/o/r.git/':"
            " The requested URL returned error: 403"
        )
        error = _failure("push", forbidden)
        self.assertIsInstance(error, PushRefusedError)
        self.assertIn("--fork", str(error))

        for command in ("clone", "ls-remote"):
            with self.subTest(command = command):
                error = _failure(command, forbidden)
                self.assertNotIsInstance(error, PushRefusedError)
                self.assertEqual(error.code, ExitCode.GIT)

        denied = "remote: Permission to o/r.git denied to me."
        self.assertEqual(
            _failure("push", denied).code, ExitCode.REFUSED
        )

        error = _failure(
            "clone", "fatal: Authentication failed for"
            " 'https://user:ghp_secret@github.com/o/r.git/'",
        )
        self.assertNotIn("ghp_secret", str(error))
        self.assertIn("credentials", str(error))


    def test_redact(self) -> None:
        self.assertEqual(
            redact("fatal: https://user:ghp_secret@github.com/o/r"),
            "fatal: https://github.com/o/r",
        )


    def test_check_remote(self) -> None:
        for remote in (
            "https://github.com/o/r.git", "git@github.com:o/r.git",
            "file:///tmp/r.git", "../r.git", "C:\\repos\\r.git",
        ):
            with self.subTest(remote = remote):
                check_remote(remote, "--remote")

        for remote in (
            "", "-uhack", "ext::sh -c id", "fd::0", "ftp://host/r",
        ):
            with self.subTest(remote = remote):
                with self.assertRaises(HookError):
                    check_remote(remote, "--remote")


    def test_invalid_ref(self) -> None:
        for ref in ("", "--upload-pack=x", "a b"):
            with self.subTest(ref = ref):
                with self.assertRaises(HookError):
                    Repository("https://github.com/o/r.git", ref)


    def test_commit_message(self) -> None:
        old = {"tag" : "!", "color" : "#FF2D00"}
        new = {"tag" : "!", "color" : "#000000"}
        message = commit_message([MINE], [(old, new)])

        subject, _, body = message.partition("\n\n")
        self.assertTrue(subject.startswith("✨🛠️ feat(skills): add"))
        self.assertLessEqual(len(subject), 72)
        self.assertIn(
            '- add `note` - color "#00FF00", bold true', body
        )
        self.assertIn(
            '- update `!` - color "#FF2D00" -> "#000000"', body
        )
        self.assertNotIn("Co-authored-by", message)
        for line in message.splitlines():
            self.assertLessEqual(len(line), 72, line)


    def test_long_subject_counts_the_tags(self) -> None:
        tags = [dict(MINE, tag = f"long-tag-name-{idx}")
                for idx in range(5)]
        subject = commit_message(tags, []).splitlines()[0]
        self.assertEqual(
            subject, "✨ feat(skills): add 5 better comments tags"
        )


if __name__ == "__main__":
    unittest.main()
