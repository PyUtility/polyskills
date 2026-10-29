# -*- encoding: utf-8 -*-

"""
Clone the Remote Repository and Propose a Change as a Pull Request

The hooks read the settings template through git, so the proxy,
certificate, and credential setup of the local git client applies to
them as it does to any other git command. :class:`Repository` clones
only the tip of one branch - a shallow, blobless, sparse clone - into
a temporary folder, and removes the clone when it is done.

``push.py`` commits the proposed template on a new branch of the
clone, pushes the branch to the remote (or to a fork of it), and
opens the pull request: with the GitHub CLI (``gh``) when it is
installed, otherwise with the compare page of GitHub in the browser.

:NOTE: Every git command runs with a list of arguments, never through
    a shell, and every printed URL or error is stripped of the
    credentials in it.
"""

import dataclasses
import datetime as dt
import hashlib
import os
import pathlib
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import urllib.parse
import webbrowser

from collections.abc import Callable
from typing import Optional

from errors import (
    GitError, HookError, PushRefusedError, SettingsError, warn
)

DEFAULT_REMOTE = "https://github.com/PyUtility/polyskills.git"
DEFAULT_REF    = "master"
TEMPLATE_DIR   = "extensions/hooks/Better Comments (VS Code Extension)"
TEMPLATE_PATH  = TEMPLATE_DIR + "/settings.json.template"

# ? no line-ending conversion of the template, and no background
# process (gc, maintenance, fsmonitor) holding the temporary clone
_CONFIG = (
    "-c", "core.autocrlf=false", "-c", "core.fsmonitor=false",
    "-c", "gc.auto=0", "-c", "maintenance.auto=false",
)
_NO_PROMPT = {
    "GIT_TERMINAL_PROMPT" : "0", "GCM_INTERACTIVE" : "never"
}

_SCHEMES = {"file", "git", "http", "https", "ssh"}
_SCHEME  = re.compile(r"^([A-Za-z][A-Za-z0-9+.-]*)://")
_HELPER  = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*::")
_USER    = re.compile(r"(?<=://)[^/@\s]+@")

_GITHUB = re.compile(
    r"^(?:https?://(?:[^/@]+@)?github\.com(?::443)?/"
    r"|ssh://(?:[^/@]+@)?(?:ssh\.)?github\.com(?::\d+)?/"
    r"|(?:[^/@:]+@)?github\.com:)"
    r"(?P<owner>[\w.-]+)/(?P<name>[\w.-]+?)(?:\.git)?/?$",
    re.IGNORECASE,
)

_HINTS = tuple(
    (re.compile(pattern, re.IGNORECASE), error, hint)
    for pattern, error, hint in (
        (
            r"permission denied \(publickey\)|authentication failed"
            r"|could not read (username|password)|terminal prompts"
            r"|invalid username or password",
            GitError, "check the git credentials for the remote",
        ),
        (
            r"permission to \S+ denied|denied to |error: 403"
            r"|returned error: 403",
            PushRefusedError,
            "you cannot push to the remote - fork it on GitHub and"
            " run again with --fork <fork-url>",
        ),
        (
            r"shallow update not allowed",
            GitError,
            "the fork is behind the remote - sync the fork on GitHub"
            " and run again",
        ),
        (
            r"not found in upstream|couldn't find remote ref",
            GitError, "the --ref branch does not exist on the remote",
        ),
        (
            r"tell me who you are|empty ident",
            GitError, "set user.name and user.email with git config",
        ),
        (
            r"\bssl\b|certificate",
            GitError,
            "check the proxy and certificate setup of git"
            " (http.proxy, http.sslCAInfo)",
        ),
        (
            r"could not resolve|failed to connect|timed out",
            GitError,
            "check the network connection and the proxy setup of git",
        ),
        (
            r"repository .*not found"
            r"|not appear to be a git repository",
            GitError, "check the --remote (or --fork) URL",
        ),
    )
)


@dataclasses.dataclass(frozen = True)
class Proposal:
    """
    The outcome of :meth:`Repository.publish`.

    :type  branch: str
    :param branch: The new branch with the proposed template.

    :type  target: str
    :param target: The remote the branch was pushed to, without the
        credentials.

    :type  url: Optional[str]
    :param url: The pull request, or the compare page that opens one;
        ``None`` when the remote is not on GitHub.

    :type  created: bool
    :param created: ``True`` when the GitHub CLI created the pull
        request, ``False`` when the compare page still has to be
        submitted.

    :type  browsed: bool
    :param browsed: ``True`` when the compare page was opened in the
        browser.
    """

    branch  : str
    target  : str
    url     : Optional[str]
    created : bool
    browsed : bool


class Repository:
    """
    A temporary clone of the tip of a branch of the remote, used as a
    context manager that clones on entry and removes the clone on
    exit.

    .. code-block:: python

        with Repository(DEFAULT_REMOTE, DEFAULT_REF) as repository:
            text = repository.read()

    :type  remote: str
    :param remote: The URL or the path of the remote repository.

    :type  ref: str
    :param ref: The branch to read, and the base of a pull request.

    :raises HookError: When the remote or the branch is not valid.
    """

    def __init__(self, remote : str, ref : str) -> None:
        check_remote(remote, "--remote")
        if not ref or ref.startswith("-") or any(
            char.isspace() for char in ref
        ):
            raise HookError(f"invalid --ref: {ref!r}")

        self.remote = remote
        self.ref    = ref
        self._root  : Optional[pathlib.Path] = None


    def __enter__(self) -> "Repository":
        self._root = pathlib.Path(
            tempfile.mkdtemp(prefix = "better-comments-")
        )
        try:
            self._clone()
        except BaseException:
            self.close()
            raise

        return self


    def __exit__(self, *exc_info : object) -> None:
        self.close()


    @property
    def path(self) -> pathlib.Path:
        """
        The folder of the clone.

        :rtype:   pathlib.Path
        :returns: The working tree of the temporary clone.
        """

        return self._root / "clone"


    def read(self) -> str:
        """
        Read the settings template from the clone, as it is in git.

        :raises GitError: When the branch has no settings template, or
            it cannot be read.

        :raises SettingsError: When the template is not UTF-8 text.

        :rtype:   str
        :returns: The text of the template, without a byte order mark.
        """

        try:
            data = (self.path / TEMPLATE_PATH).read_bytes()
        except FileNotFoundError:
            raise GitError(
                f"{TEMPLATE_PATH} is not on the {self.ref} branch of"
                f" {redact(self.remote)}"
            ) from None
        except OSError as error:
            raise GitError(
                f"cannot read {TEMPLATE_PATH}: {error.strerror}"
            ) from None

        try:
            return data.decode("utf-8-sig")
        except UnicodeDecodeError:
            message = f"{TEMPLATE_PATH} is not UTF-8 text"
            raise SettingsError(message) from None


    def publish(
        self, text : str, message : str, names : list[str],
        fork : Optional[str] = None,
    ) -> Proposal:
        """
        Commit ``text`` as the settings template on a new branch, push
        the branch, and open the pull request against :attr:`ref`.

        :type  text: str
        :param text: The proposed settings template.

        :type  message: str
        :param message: The commit message - its first line is also
            the title of the pull request, and the rest its body.

        :type  names: list[str]
        :param names: The proposed tags, which name the branch.

        :type  fork: Optional[str]
        :param fork: The URL of a fork to push the branch to, when the
            remote does not accept the push.

        :raises HookError: When :attr:`ref` is not a branch, or the
            fork URL is not valid.

        :raises GitError: When the commit or the push fails.

        :raises PushRefusedError: When the remote refuses the push.

        :rtype:   Proposal
        :returns: The pushed branch and the pull request.
        """

        if fork is not None:
            check_remote(fork, "--fork")

        try:
            _git("symbolic-ref", "--quiet", "HEAD", cwd = self.path)
        except GitError:
            message = f"--ref {self.ref} is not a branch"
            raise HookError(message) from None

        target = fork or "origin"
        branch = self._branch(names, target)
        _git("checkout", "--quiet", "-b", branch, cwd = self.path)

        (self.path / TEMPLATE_PATH).write_bytes(text.encode("utf-8"))
        _git("add", "--", TEMPLATE_PATH, cwd = self.path)

        title, _, body = message.partition("\n")
        message_file = self._root / "COMMIT_EDITMSG"
        message_file.write_bytes(message.encode("utf-8"))
        _git("commit", "--quiet", "--file", str(message_file),
             cwd = self.path)

        _git("push", "--quiet", "--", target,
             f"HEAD:refs/heads/{branch}", cwd = self.path)

        upstream, head = github(self.remote), branch
        if fork is not None:
            owner = github(fork)
            if owner is None:
                upstream = None
            else:
                head = f"{owner[0]}:{branch}"

        url, created, browsed = None, False, False
        if upstream is not None:
            body_file = self._root / "PULL_REQUEST.md"
            body_file.write_bytes(body.strip().encode("utf-8"))
            url = _gh_create(
                upstream, self.ref, head, title, body_file
            )
            created = url is not None
            if not created:
                url     = compare_url(upstream, self.ref, head)
                browsed = _browse(url)

        shown = redact(fork or self.remote)
        return Proposal(branch, shown, url, created, browsed)


    def close(self) -> None:
        """
        Remove the temporary clone. A clone that cannot be removed
        (for example, a file held by an antivirus scan) is reported
        with its path and left behind.
        """

        if self._root is None:
            return

        root, self._root = self._root, None
        remove_tree(root)


    def _clone(self) -> None:
        """
        Clone the tip of :attr:`ref` into :attr:`path`: a sparse,
        blobless clone that checks out only the template folder with
        git 2.25 or later, and a shallow clone with older versions.

        :raises GitError: When git is missing or the clone fails.
        """

        sparse  = _version() >= (2, 25)
        command = [
            "clone", "--quiet", "--depth", "1", "--no-tags",
            f"--branch={self.ref}",
        ]
        if sparse:
            command += ["--filter=blob:none", "--sparse"]

        _git(*command, "--", self.remote, str(self.path),
             prompt = False)
        if sparse:
            _git("sparse-checkout", "set", TEMPLATE_DIR,
                 cwd = self.path)


    def _branch(self, names : list[str], target : str) -> str:
        """
        Return a name from :func:`branch_name` that ``target`` does
        not have yet, adding ``-2``, ``-3``, and so on when it does.

        :type  names: list[str]
        :param names: The proposed tags.

        :type  target: str
        :param target: The remote that the branch is pushed to.

        :raises GitError: When the branches cannot be listed, or every
            name is taken.

        :rtype:   str
        :returns: The free branch name.
        """

        heads = _git("ls-remote", "--heads", "--", target,
                     cwd = self.path)
        taken = {line.split("\t")[-1] for line in heads.splitlines()}

        base = branch_name(names)
        for count in range(1, 100):
            name = base if count == 1 else f"{base}-{count}"
            if f"refs/heads/{name}" not in taken:
                return name

        raise GitError(f"every branch name like {base} is taken")


def remove_tree(path : pathlib.Path) -> None:
    """
    Remove a folder, including the read-only files that git keeps. A
    folder that cannot be removed (for example, a file held by an
    antivirus scan) is reported with its path and left behind.

    :type  path: pathlib.Path
    :param path: The folder to remove.
    """

    option = "onexc" if sys.version_info >= (3, 12) else "onerror"
    try:
        shutil.rmtree(path, **{option : _make_writable})
    except OSError as error:
        warn(f"cannot remove the temporary folder {path}:"
             f" {error.strerror}")


def check_remote(remote : str, option : str) -> None:
    """
    Check that ``remote`` is a URL (``https``, ``http``, ``ssh``,
    ``git``, or ``file``), an scp-like ``user@host:path``, or a local
    path - never an option, or a ``<transport>::`` remote helper that
    could run a command.

    :type  remote: str
    :param remote: The URL or the path to check.

    :type  option: str
    :param option: The option that gave the remote, for the message.

    :raises HookError: When the remote is not allowed.
    """

    scheme = _SCHEME.match(remote)
    if (
        not remote or remote.startswith("-") or _HELPER.match(remote)
        or (scheme and scheme.group(1).lower() not in _SCHEMES)
    ):
        raise HookError(f"invalid {option}: {redact(remote)}")


def redact(text : str) -> str:
    """
    Remove the user and the password or token of every URL in
    ``text``, so no credential is ever printed.

    :type  text: str
    :param text: A URL, or a message that may contain URLs.

    :rtype:   str
    :returns: The text, with ``https://user:token@host`` printed as
        ``https://host``.
    """

    return _USER.sub("", text)


def github(remote : str) -> Optional[tuple[str, str]]:
    """
    Return the owner and the name of a GitHub repository from its
    HTTPS, SSH, or scp-like URL.

    :type  remote: str
    :param remote: The URL of the repository.

    :rtype:   Optional[tuple[str, str]]
    :returns: The ``(owner, name)`` pair, or ``None`` when the URL is
        not a GitHub repository.
    """

    match = _GITHUB.match(remote.strip())
    if match is None:
        return None

    return match.group("owner"), match.group("name")


def compare_url(
    upstream : tuple[str, str], ref : str, head : str
) -> str:
    """
    Return the GitHub page that opens a pull request of ``head`` into
    ``ref``.

    :type  upstream: tuple[str, str]
    :param upstream: The owner and the name of the repository.

    :type  ref: str
    :param ref: The base branch of the pull request.

    :type  head: str
    :param head: The branch to merge, as ``owner:branch`` for a fork.

    :rtype:   str
    :returns: The URL of the compare page.
    """

    owner, name = upstream
    base   = urllib.parse.quote(ref, safe = "/")
    branch = urllib.parse.quote(head, safe = "/:")
    return (
        f"https://github.com/{owner}/{name}/compare/{base}...{branch}"
        "?expand=1"
    )


def branch_name(
    names : list[str], today : Optional[dt.date] = None
) -> str:
    """
    Name the branch of a proposal after the date and its tags, in the
    characters that every git server accepts - for example
    ``better-comments/2026-10-29-versionadded-note``.

    :type  names: list[str]
    :param names: The proposed tags.

    :type  today: Optional[dt.date]
    :param today: The date in the name, today by default.

    :rtype:   str
    :returns: The branch name. Tags without a letter or a digit (such
        as ``!``) are named by a short hash of the tags.
    """

    words = [
        word for name in names
        for word in re.findall(r"[a-z0-9]+", name.lower())
    ]

    slug = ""
    for word in words:
        nxt = f"{slug}-{word}" if slug else word[:40]
        if len(nxt) > 40:
            break
        slug = nxt

    if not slug:
        digest = hashlib.sha256("\n".join(names).encode("utf-8"))
        slug   = f"tags-{digest.hexdigest()[:7]}"

    day = (today or dt.date.today()).isoformat()
    return f"better-comments/{day}-{slug}"


def _git(
    *args : str, cwd : Optional[pathlib.Path] = None,
    prompt : bool = True,
) -> str:
    """
    Run one git command and return its output.

    :type  args: str
    :param args: The git command and its arguments.

    :type  cwd: Optional[pathlib.Path]
    :param cwd: The folder to run the command in.

    :type  prompt: bool
    :param prompt: Let git ask for credentials. Commands that only
        read run without prompts, so they fail fast instead of
        waiting for an answer.

    :raises GitError: When git is missing or the command fails.

    :rtype:   str
    :returns: The standard output of the command.
    """

    env = dict(os.environ)
    if not prompt:
        env.update(_NO_PROMPT)

    try:
        result = subprocess.run(
            ["git", *_CONFIG, *args], cwd = cwd, env = env,
            capture_output = True, encoding = "utf-8",
            errors = "replace", check = False,
        )
    except FileNotFoundError:
        message = "git is not installed or not on the PATH"
        raise GitError(message) from None

    if result.returncode:
        raise _failure(args[0], result.stderr)

    return result.stdout


def _failure(command : str, stderr : str) -> GitError:
    """
    Build the error of a failed git command, with a hint for the
    common causes and without any credentials.

    :type  command: str
    :param command: The git command that failed, such as ``push``.

    :type  stderr: str
    :param stderr: The error output of the command.

    :rtype:   GitError
    :returns: The error (a :class:`PushRefusedError` only when the
        remote refused a ``push``), ready to raise.
    """

    text  = redact(stderr).strip()
    lines = text.splitlines()[-5:] or ["no error output"]
    message = f"git {command} failed:\n  " + "\n  ".join(lines)

    for pattern, error, hint in _HINTS:
        if not pattern.search(text):
            continue

        if error is PushRefusedError and command != "push":
            error, hint = GitError, "check your access to the remote"
        return error(f"{message}\nhint: {hint}")

    return GitError(message)


def _version() -> tuple[int, int]:
    """
    Return the major and the minor version of git.

    :raises GitError: When git is missing.

    :rtype:   tuple[int, int]
    :returns: The version, such as ``(2, 45)``, or ``(0, 0)`` when it
        cannot be read.
    """

    match = re.search(r"(\d+)\.(\d+)", _git("version"))
    if match is None:
        return 0, 0

    return int(match.group(1)), int(match.group(2))


def _gh_create(
    upstream : tuple[str, str], ref : str, head : str, title : str,
    body_file : pathlib.Path,
) -> Optional[str]:
    """
    Create the pull request with the GitHub CLI, when it is installed
    and signed in.

    :type  upstream: tuple[str, str]
    :param upstream: The owner and the name of the repository.

    :type  ref: str
    :param ref: The base branch of the pull request.

    :type  head: str
    :param head: The branch to merge, as ``owner:branch`` for a fork.

    :type  title: str
    :param title: The title of the pull request.

    :type  body_file: pathlib.Path
    :param body_file: The file with the body of the pull request.

    :rtype:   Optional[str]
    :returns: The URL of the pull request, or ``None`` when ``gh`` is
        not installed or fails.
    """

    gh = shutil.which("gh")
    if gh is None:
        return None

    owner, name = upstream
    result = subprocess.run(
        [
            gh, "pr", "create", "--repo", f"{owner}/{name}",
            "--base", ref, "--head", head, "--title", title,
            "--body-file", str(body_file),
        ],
        env = dict(os.environ, GH_PROMPT_DISABLED = "1"),
        capture_output = True, encoding = "utf-8", errors = "replace",
        check = False,
    )

    urls = re.findall(r"https://\S+", result.stdout)
    if result.returncode or not urls:
        lines = redact(result.stderr).strip().splitlines()
        warn("gh pr create failed"
             + (f": {lines[-1]}" if lines else "")
             + " - use the compare page instead")
        return None

    return urls[-1]


def _browse(url : str) -> bool:
    """
    Open ``url`` in a graphical browser. Nothing opens in a session
    without a display, such as over SSH, so a text browser never takes
    over the terminal.

    :type  url: str
    :param url: The page to open.

    :rtype:   bool
    :returns: ``True`` when a browser opened the page.
    """

    env     = os.environ
    desktop = sys.platform in ("win32", "darwin")
    display = env.get("DISPLAY") or env.get("WAYLAND_DISPLAY")
    if not desktop and (not display or "SSH_CONNECTION" in env):
        return False

    try:
        return webbrowser.open(url)
    except webbrowser.Error:
        return False


def _make_writable(
    func : Callable[[str], object], path : str, _error : object
) -> None:
    """
    Clear the read-only flag of ``path`` and run ``func`` on it again;
    git keeps its pack files read-only, which stops their removal on
    Windows.

    :type  func: Callable[[str], object]
    :param func: The removal function that failed.

    :type  path: str
    :param path: The file or folder it failed on.

    :type  _error: object
    :param _error: The error, unused.
    """

    os.chmod(path, stat.S_IWRITE)
    func(path)
