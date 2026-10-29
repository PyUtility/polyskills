# -*- encoding: utf-8 -*-

"""
Shared Fixtures of the Hook Tests

:class:`HookTestCase` runs every test in a temporary folder with its
own home folder and git configuration, so a test never reads or
writes the real VS Code settings or the git setup of the user. It
also builds a local bare repository, with the settings template of
the working tree, to serve as the ``file://`` remote of the hooks.
"""

import contextlib
import io
import json
import os
import pathlib
import shutil
import subprocess
import tempfile
import unittest

from typing import Optional
from unittest import mock

from repository import TEMPLATE_PATH, remove_tree

ROOT     = pathlib.Path(__file__).resolve().parents[4]
TEMPLATE = ROOT / TEMPLATE_PATH


def git(*args : str) -> str:
    """
    Run a git command for a fixture, failing the test on an error.

    :type  args: str
    :param args: The git command and its arguments.

    :rtype:   str
    :returns: The standard output of the command.
    """

    result = subprocess.run(
        ["git", *args], capture_output = True, encoding = "utf-8",
        check = True,
    )
    return result.stdout


def template_tags() -> list[dict]:
    """
    Read the tags of the settings template of the working tree.

    :rtype:   list[dict]
    :returns: The tags of the template.
    """

    text = TEMPLATE.read_text(encoding = "utf-8")
    return json.loads(text)["better-comments.tags"]


@unittest.skipIf(shutil.which("git") is None, "git is not installed")
class HookTestCase(unittest.TestCase):
    """
    A test with a temporary home folder, an isolated git setup, and a
    settings file path (``self.settings``) that does not exist yet.
    """

    def setUp(self) -> None:
        temp = tempfile.mkdtemp(prefix = "hook-test-")
        self.temp = pathlib.Path(temp)
        self.addCleanup(remove_tree, self.temp)

        home = self.temp / "home"
        home.mkdir()
        gitconfig = self.temp / "gitconfig"
        gitconfig.write_text("", encoding = "utf-8")

        patcher = mock.patch.dict(os.environ, {
            "HOME"                : str(home),
            "USERPROFILE"         : str(home),
            "APPDATA"             : str(home / "AppData"),
            "XDG_CONFIG_HOME"     : str(home / ".config"),
            "GIT_CONFIG_GLOBAL"   : str(gitconfig),
            "GIT_CONFIG_NOSYSTEM" : "1",
            "GIT_AUTHOR_NAME"     : "Hook Test",
            "GIT_AUTHOR_EMAIL"    : "hook@test.invalid",
            "GIT_COMMITTER_NAME"  : "Hook Test",
            "GIT_COMMITTER_EMAIL" : "hook@test.invalid",
        })
        patcher.start()
        self.addCleanup(patcher.stop)

        self.settings = self.temp / "settings.json"


    def remote(self, data : Optional[bytes] = None) -> str:
        """
        Build a bare repository, in a new folder, whose ``master``
        branch holds the settings template, and keep its path in
        ``self.bare``.

        :type  data: Optional[bytes]
        :param data: The content of the template, or ``None`` for the
            template of the working tree.

        :rtype:   str
        :returns: The ``file://`` URL of the bare repository.
        """

        root = pathlib.Path(tempfile.mkdtemp(dir = self.temp))
        bare, seed = root / "remote.git", root / "seed"
        self.bare = bare
        master = "refs/heads/master"
        git("init", "--quiet", "--bare", str(bare))
        git("-C", str(bare), "symbolic-ref", "HEAD", master)
        git("-C", str(bare), "config", "uploadpack.allowFilter", "1")

        git("init", "--quiet", str(seed))
        git("-C", str(seed), "symbolic-ref", "HEAD", master)
        path = seed / TEMPLATE_PATH
        path.parent.mkdir(parents = True)
        if data is None:
            data = TEMPLATE.read_bytes()
        path.write_bytes(data)

        git("-C", str(seed), "add", "--all")
        git("-C", str(seed), "commit", "--quiet", "-m", "seed")
        git("-C", str(seed), "push", "--quiet", str(bare), "master")
        return bare.as_uri()


    def run_hook(self, hook : object, *args : str) -> tuple[int, str]:
        """
        Run a hook in the process, with its output captured.

        :type  hook: object
        :param hook: The hook, such as ``PullHook()``.

        :type  args: str
        :param args: The command-line arguments.

        :rtype:   tuple[int, str]
        :returns: The exit code, and the standard output and error.
        """

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            with contextlib.redirect_stderr(output):
                code = hook.main(list(args))

        return code, output.getvalue()
