# -*- encoding: utf-8 -*-

"""
Hermetic Tests for the Polyskills Command-Line Interface
--------------------------------------------------------

Validates the public surface of :mod:`polyskills.cli` without touching
the network. The cases are split into focused
:class:`unittest.TestCase` subclasses so each failure points straight
at the broken contract:

  * :class:`TestBuildParser` - argparse construction, flag presence,
    defaults, choices, and required arguments.
  * :class:`TestResolveManager` - the source-detection registry:
    correct concrete manager for a GitHub URL, ``ValueError`` for
    unsupported remotes, and ``SourceControl`` propagation.
  * :class:`TestGetWrapper` - the CLI-side :func:`polyskills.cli.get`
    wrapper delegates to :meth:`SourceManager.get` with the documented
    ``mode='extensions'`` keyword payload.
  * :class:`TestMainDispatch` - the :func:`polyskills.cli.main` entry
    point: terminal sub-commands print and exit early, the
    ``manager`` sub-command applies the documented source/destination
    defaults, builds :class:`SourceControl` from
    ``--pagination``/``--token``, and delegates to :func:`get`.

:NOTE: Every test in this module is hermetic - no HTTP requests, no
filesystem writes outside :mod:`tempfile` scratch space. Live network
contracts for the underlying :class:`GithubManager` are exercised by
:mod:`polyskills.tests.test_remote_sources` and
:mod:`polyskills.tests.test_skill_install`.
"""

import io
import os
import sys
import argparse
import contextlib
import unittest

from pathlib import Path
from typing import List, Tuple
from unittest import mock

from polyskills import cli
from polyskills.remote.sources import (
    GithubManager, SourceControl, SourceManager, ValidSources
)

# ? canonical fixture values reused across every dispatch-style case
_REMOTE      : str = "https://github.com/PyUtility/polyskills"
_NAME        : str = "sql-code-format"
_LIBRARY     : str = "skills"
_VERSION     : str = "master"
_PAGINATION  : int = 100


def _parse(argv : List[str]) -> argparse.Namespace:
    """
    Convenience wrapper that builds the production parser and parses
    ``argv`` with stderr redirected so argparse error output never
    leaks into the test runner display.

    :type  argv: List[str]
    :param argv: Argument vector excluding the program name.

    :rtype:   argparse.Namespace
    :returns: The parsed namespace produced by :func:`cli.buildParser`.
    """

    parser = cli.buildParser()

    with contextlib.redirect_stderr(io.StringIO()):
        return parser.parse_args(argv)


def _run_main(argv : List[str]) -> Tuple[int, str, str]:
    """
    Invoke :func:`cli.main` with a synthetic ``sys.argv`` and capture
    stdout, stderr, and the resolved exit code so tests can assert on
    the CLI behavior without spawning a subprocess.

    :type  argv: List[str]
    :param argv: Argument vector excluding the program name; the
        leading ``polyskills`` token is injected automatically.

    :rtype:   Tuple[int, str, str]
    :returns: Tuple of ``(exit_code, stdout, stderr)`` where
        ``exit_code`` is ``0`` when :func:`cli.main` returns normally
        and the value passed to :class:`SystemExit` otherwise.
    """

    out = io.StringIO()
    err = io.StringIO()
    code = 0

    with mock.patch.object(sys, "argv", ["polyskills"] + argv):
        try:
            with contextlib.redirect_stdout(out), \
                    contextlib.redirect_stderr(err):
                cli.main()
        except SystemExit as exc:
            code = int(exc.code) if exc.code is not None else 0

    return (code, out.getvalue(), err.getvalue())


class TestBuildParser(unittest.TestCase):
    """
    Argparse-construction tests for :func:`cli.buildParser`. These
    cases never call :func:`cli.main` and therefore never reach the
    remote-dispatch code path.
    """

    def test_returns_argument_parser(self) -> None:
        """
        :func:`cli.buildParser` must return a configured
        :class:`argparse.ArgumentParser` whose ``prog`` is the public
        CLI entry-point name.
        """

        parser = cli.buildParser()

        self.assertIsInstance(parser, argparse.ArgumentParser)
        self.assertEqual(parser.prog, "polyskills")


    def test_command_is_required(self) -> None:
        """
        Calling the parser with no sub-command must exit with a
        non-zero status because ``COMMAND`` is declared as required.
        """

        with self.assertRaises(SystemExit) as ctx:
            _parse([])

        self.assertNotEqual(ctx.exception.code, 0)


    def test_sources_subcommand_attaches_func_default(self) -> None:
        """
        The ``sources`` sub-command attaches a callable ``func``
        default that yields a string enumerating every member of
        :class:`ValidSources`.
        """

        args = _parse(["sources"])

        self.assertTrue(hasattr(args, "func"))
        self.assertTrue(callable(args.func))

        rendered = args.func()
        self.assertIsInstance(rendered, str)
        for member in ValidSources:
            self.assertIn(member.name, rendered)


    def test_tools_subcommand_attaches_func_default(self) -> None:
        """
        The ``tools`` sub-command attaches a callable ``func`` default
        that yields a string enumerating every member of
        :class:`SupportedTools`, mirroring the ``sources`` sub-command.
        """

        from polyskills.apps.tools import SupportedTools

        args = _parse(["tools"])

        self.assertTrue(hasattr(args, "func"))
        self.assertTrue(callable(args.func))

        rendered = args.func()
        self.assertIsInstance(rendered, str)
        for member in SupportedTools:
            self.assertIn(member.name, rendered)


    def test_manager_requires_remote_and_library(self) -> None:
        """
        The ``manager`` sub-command must reject invocations missing
        either the positional ``remote`` URL or the ``LIBRARY``
        sub-parser selector.
        """

        with self.assertRaises(SystemExit):
            _parse(["manager"])

        with self.assertRaises(SystemExit):
            _parse(["manager", _REMOTE, "--name", _NAME])


    def test_manager_requires_name_flag(self) -> None:
        """
        The ``-n/--name`` flag must be required at the ``manager``
        level so the dispatcher can build the default destination
        directory deterministically.
        """

        with self.assertRaises(SystemExit):
            _parse(["manager", _REMOTE, "skills"])


    def test_manager_defaults_match_source_manager_contract(self) -> None:
        """
        Successful parsing must populate ``--version`` with
        ``'master'`` and ``--exists`` with ``'fail'`` so the namespace
        mirrors the defaults documented on
        :meth:`SourceManager._getExtensions`.
        """

        args = _parse([
            "manager", _REMOTE, "--name", _NAME, "skills"
        ])

        self.assertEqual(args.command, "manager")
        self.assertEqual(args.library, "skills")
        self.assertEqual(args.remote, _REMOTE)
        self.assertEqual(args.name, _NAME)
        self.assertEqual(args.version, "master")
        self.assertEqual(args.exists, "fail")
        self.assertEqual(args.pagination, _PAGINATION)
        self.assertIsNone(args.source)
        self.assertIsNone(args.destination)
        self.assertIsNone(args.token)


    def test_exists_choices_are_enforced(self) -> None:
        """
        ``--exists`` must only accept the documented tri-state
        ``{fail, overwrite, merge}`` and reject anything else with a
        non-zero exit.
        """

        for value in ("fail", "overwrite", "merge"):
            args = _parse([
                "manager", _REMOTE, "--name", _NAME,
                "--exists", value, "skills"
            ])
            self.assertEqual(args.exists, value)

        with self.assertRaises(SystemExit):
            _parse([
                "manager", _REMOTE, "--name", _NAME,
                "--exists", "purge", "skills"
            ])


    def test_library_subparser_accepts_skills_and_agents(self) -> None:
        """
        Both registered library sub-parsers must be selectable and
        must surface their own name via ``args.library``.
        """

        for library in ("skills", "agents"):
            args = _parse([
                "manager", _REMOTE, "--name", _NAME, library
            ])
            self.assertEqual(args.library, library)


    def test_pagination_and_token_are_parsed(self) -> None:
        """
        ``--pagination`` must be coerced to :class:`int` and
        ``--token`` must be retained verbatim so the dispatcher can
        forward both into :class:`SourceControl`.
        """

        args = _parse([
            "manager", _REMOTE, "--name", _NAME,
            "--pagination", "25", "--token", "ghp_test",
            "skills"
        ])

        self.assertEqual(args.pagination, 25)
        self.assertIsInstance(args.pagination, int)
        self.assertEqual(args.token, "ghp_test")


class TestResolveManager(unittest.TestCase):
    """
    Tests the private :func:`cli._resolveManager` registry helper
    that maps a remote URL to the matching concrete
    :class:`SourceManager` factory.
    """

    def test_github_url_resolves_to_github_manager(self) -> None:
        """
        A canonical ``https://github.com/<owner>/<repo>`` URL must
        resolve to a :class:`GithubManager` instance whose
        :attr:`source` is :attr:`ValidSources.GITHUB`.
        """

        control = SourceControl()
        manager = cli._resolveManager(remote = _REMOTE, control = control)

        self.assertIsInstance(manager, GithubManager)
        self.assertIsInstance(manager, SourceManager)
        self.assertIs(manager.source, ValidSources.GITHUB)


    def test_control_is_propagated_into_manager(self) -> None:
        """
        The ``control`` argument must be forwarded verbatim to the
        concrete factory so ``--pagination`` and ``--token`` reach
        the underlying HTTP layer.
        """

        control = SourceControl(pagination = 17, token = "secret")
        manager = cli._resolveManager(remote = _REMOTE, control = control)

        self.assertIs(manager.control, control)
        self.assertEqual(manager.control.pagination, 17)
        self.assertEqual(manager.control.token, "secret")


    def test_unsupported_remote_raises_value_error(self) -> None:
        """
        A remote URL that no registered ``remotePattern`` matches
        must raise :class:`ValueError` with a message that lists the
        supported source roots so the user can self-correct.
        """

        with self.assertRaises(ValueError) as ctx:
            cli._resolveManager(
                remote = "https://gitlab.com/foo/bar",
                control = SourceControl()
            )

        self.assertIn("not supported", str(ctx.exception))
        self.assertIn(ValidSources.GITHUB.value, str(ctx.exception))


class TestGetWrapper(unittest.TestCase):
    """
    Tests the public :func:`cli.get` wrapper, which mirrors the
    signature of :meth:`SourceManager._getExtensions` and dispatches
    via :meth:`SourceManager.get` with ``mode='extensions'``.
    """

    def test_dispatches_to_source_manager_with_extensions_mode(self) -> None:
        """
        :func:`cli.get` must call :meth:`SourceManager.get` exactly
        once with ``mode='extensions'`` and forward every documented
        keyword (``name``, ``source``, ``destination``, ``version``,
        ``formatter``, ``exists``).
        """

        source = Path("./skills").as_posix()
        destination = Path("./skills/sql-code-format")
        formatter = lambda : None

        fake_manager = mock.MagicMock(spec = SourceManager)
        fake_manager.get.return_value = None

        with mock.patch.object(
            cli, "_resolveManager", return_value = fake_manager
        ) as resolver:
            result = cli.get(
                remote = _REMOTE, name = _NAME,
                source = source, destination = destination,
                version = _VERSION, formatter = formatter,
                exists = "overwrite",
                control = SourceControl(pagination = 50)
            )

        self.assertIsNone(result)
        resolver.assert_called_once()
        fake_manager.get.assert_called_once_with(
            remote = _REMOTE, mode = "extensions",
            name = _NAME, source = source, destination = destination,
            version = _VERSION, formatter = formatter,
            exists = "overwrite",
        )


    def test_default_control_is_built_when_omitted(self) -> None:
        """
        Omitting ``control`` must trigger construction of a default
        :class:`SourceControl` so callers can use the wrapper with a
        minimal positional signature.
        """

        captured = {}

        def fake_resolver(remote, control):
            captured["control"] = control
            return mock.MagicMock(spec = SourceManager)

        with mock.patch.object(cli, "_resolveManager", new = fake_resolver):
            cli.get(
                remote = _REMOTE, name = _NAME,
                source = Path("./skills"),
                destination = Path("./skills/sql-code-format")
            )

        self.assertIsInstance(captured["control"], SourceControl)
        self.assertEqual(captured["control"].pagination, 100)
        self.assertIsNone(captured["control"].token)


class TestMainDispatch(unittest.TestCase):
    """
    Tests :func:`cli.main` end-to-end with the network layer mocked
    out via :func:`cli.get`. These cases verify that argparse output
    is wired into the dispatcher correctly and that defaults align
    with the contract of :meth:`SourceManager._getExtensions`.
    """

    def test_sources_command_prints_listing_and_exits(self) -> None:
        """
        ``polyskills sources`` must print the rendered listing to
        stdout and return without invoking the manager dispatcher.
        """

        with mock.patch.object(cli, "get") as fake_get:
            code, stdout, _ = _run_main(["sources"])

        self.assertEqual(code, 0)
        self.assertIn("Available Sources", stdout)
        self.assertIn(ValidSources.GITHUB.name, stdout)
        fake_get.assert_not_called()


    def test_tools_command_prints_listing_and_exits(self) -> None:
        """
        ``polyskills tools`` must print the rendered listing of
        supported LLM tools to stdout and return without invoking the
        manager dispatcher, mirroring ``polyskills sources``.
        """

        from polyskills.apps.tools import SupportedTools

        with mock.patch.object(cli, "get") as fake_get:
            code, stdout, _ = _run_main(["tools"])

        self.assertEqual(code, 0)
        self.assertIn("Available LLM Tools", stdout)
        for member in SupportedTools:
            self.assertIn(member.name, stdout)
        fake_get.assert_not_called()


    def test_manager_dispatches_with_documented_defaults(self) -> None:
        """
        When neither ``--source`` nor ``--destination`` is supplied,
        :func:`cli.main` must compute ``./{library}`` and
        ``./{library}/{name}`` and forward every documented keyword
        to :func:`cli.get`.
        """

        with mock.patch.object(cli, "get") as fake_get:
            code, _, _ = _run_main([
                "manager", _REMOTE, "--name", _NAME, "skills"
            ])

        self.assertEqual(code, 0)
        fake_get.assert_called_once()

        kwargs = fake_get.call_args.kwargs
        self.assertEqual(kwargs["remote"], _REMOTE)
        self.assertEqual(kwargs["name"], _NAME)
        self.assertEqual(kwargs["version"], "master")
        self.assertEqual(kwargs["exists"], "fail")
        self.assertEqual(
            Path(kwargs["source"]).as_posix(),
            Path(f"./{_LIBRARY}").as_posix()
        )
        self.assertEqual(
            Path(kwargs["destination"]).as_posix(),
            Path(f"./{_LIBRARY}/{_NAME}").as_posix()
        )

        control = kwargs["control"]
        self.assertIsInstance(control, SourceControl)
        self.assertEqual(control.pagination, _PAGINATION)
        self.assertIsNone(control.token)


    def test_manager_forwards_explicit_source_and_destination(self) -> None:
        """
        Explicit ``--source`` and ``--destination`` values must be
        forwarded verbatim (modulo POSIX normalization) and must
        override the library-derived defaults.
        """

        custom_source = "extensions/skills"
        custom_destination = "build/skills/sql-code-format"

        with mock.patch.object(cli, "get") as fake_get:
            code, _, _ = _run_main([
                "manager", _REMOTE,
                "--name", _NAME,
                "--source", custom_source,
                "--destination", custom_destination,
                "skills"
            ])

        self.assertEqual(code, 0)
        kwargs = fake_get.call_args.kwargs
        self.assertEqual(
            Path(kwargs["source"]).as_posix(),
            Path(custom_source).as_posix()
        )
        self.assertEqual(
            Path(kwargs["destination"]).as_posix(),
            Path(custom_destination).as_posix()
        )


    def test_manager_forwards_pagination_and_token_to_control(self) -> None:
        """
        ``--pagination`` and ``--token`` must populate the
        :class:`SourceControl` instance handed to :func:`cli.get` so
        the HTTP layer sees the user-supplied values.
        """

        with mock.patch.object(cli, "get") as fake_get:
            code, _, _ = _run_main([
                "manager", _REMOTE,
                "--name", _NAME,
                "--pagination", "42",
                "--token", "ghp_token",
                "--version", "v1.2.3",
                "--exists", "overwrite",
                "skills"
            ])

        self.assertEqual(code, 0)
        kwargs = fake_get.call_args.kwargs
        self.assertEqual(kwargs["version"], "v1.2.3")
        self.assertEqual(kwargs["exists"], "overwrite")

        control = kwargs["control"]
        self.assertEqual(control.pagination, 42)
        self.assertEqual(control.token, "ghp_token")


    def test_manager_supports_agents_library(self) -> None:
        """
        ``polyskills manager <remote> --name <name> agents`` must
        derive ``./agents/<name>`` as the default destination, so the
        wiring is symmetric for every registered library sub-parser.
        """

        with mock.patch.object(cli, "get") as fake_get:
            code, _, _ = _run_main([
                "manager", _REMOTE,
                "--name", "python-code-reviewer",
                "agents"
            ])

        self.assertEqual(code, 0)
        kwargs = fake_get.call_args.kwargs
        self.assertEqual(
            Path(kwargs["source"]).as_posix(),
            Path("./agents").as_posix()
        )
        self.assertEqual(
            Path(kwargs["destination"]).as_posix(),
            Path("./agents/python-code-reviewer").as_posix()
        )


    def test_unsupported_remote_exits_with_clean_error(self) -> None:
        """
        :func:`cli.main` must render the :class:`ValueError` raised by
        :func:`cli._resolveManager` for an unknown remote as a concise
        ``[ERROR]`` message on stderr and exit non-zero, instead of
        leaking a raw traceback to the user.
        """

        code, _, err = _run_main([
            "manager", "https://gitlab.com/foo/bar",
            "--name", _NAME, "skills"
        ])

        self.assertEqual(code, 1)
        self.assertIn("[ERROR]", err)
        self.assertIn("not supported", err)
        self.assertNotIn("Traceback", err)


class TestDestinationExpansion(unittest.TestCase):
    """
    Regression tests for the ``--destination`` (and mirror
    ``--source``) path-expansion contract. The CLI must expand the
    user-home shorthand ``~`` and any environment variable references
    (``$VAR`` / ``${VAR}`` / ``%VAR%``) *before* the value is handed
    off to :func:`cli.get`, otherwise a literal ``~`` directory is
    silently created next to the current working directory instead
    of the documented user-skills location (e.g.,
    ``~/.claude/skills/<name>``).

    These cases are kept hermetic: :func:`cli.get` is mocked so no
    HTTP requests are made and no files are written - the tests only
    inspect the keyword payload that the dispatcher would forward.
    """

    def _assert_expanded(self, raw: str, kw: str, kwargs: dict) -> Path:
        """
        Shared assertion helper: the keyword ``kw`` in ``kwargs`` must
        be a path that no longer contains a leading ``~`` segment and
        no unresolved ``$VAR`` / ``%VAR%`` tokens.

        :returns: The forwarded path, normalised to a :class:`Path`.
        """

        forwarded = Path(kwargs[kw])
        rendered = forwarded.as_posix()

        self.assertFalse(
            rendered.startswith("~"),
            f"`{kw}` retained a literal '~' prefix: {rendered!r} "
            f"(input was {raw!r})"
        )
        self.assertNotIn("$", rendered)
        self.assertNotIn("%", rendered)

        # ? expanding ``~`` must yield an absolute path; a leftover
        # ? relative path is the canonical signature of the bug.
        self.assertTrue(
            forwarded.is_absolute(),
            f"`{kw}` was not expanded to an absolute path: "
            f"{rendered!r} (input was {raw!r})"
        )
        return forwarded


    def test_destination_tilde_is_expanded(self) -> None:
        """
        ``--destination ~/.claude/skills/<name>`` must be expanded to
        the user's home directory before being forwarded to
        :func:`cli.get`. This is the exact bug report: a literal
        ``~`` was being treated as a relative directory.
        """

        raw = f"~/.claude/skills/{_NAME}"

        with mock.patch.object(cli, "get") as fake_get:
            code, _, _ = _run_main([
                "manager", _REMOTE,
                "--name", _NAME,
                "--destination", raw,
                "skills"
            ])

        self.assertEqual(code, 0)
        fake_get.assert_called_once()
        forwarded = self._assert_expanded(
            raw, "destination", fake_get.call_args.kwargs
        )

        expected = Path(raw).expanduser().resolve(strict = False)
        self.assertEqual(
            forwarded.resolve(strict = False).as_posix(),
            expected.as_posix()
        )

        parts = forwarded.as_posix().split("/")
        self.assertIn(".claude", parts)
        self.assertIn("skills", parts)
        self.assertEqual(parts[-1], _NAME)


    def test_source_tilde_is_expanded(self) -> None:
        """
        ``--source`` must follow the same expansion rule as
        ``--destination`` so users can mirror a remote layout rooted
        at their home directory without breaking the dispatch.
        """

        raw = "~/remote-skills"

        with mock.patch.object(cli, "get") as fake_get:
            code, _, _ = _run_main([
                "manager", _REMOTE,
                "--name", _NAME,
                "--source", raw,
                "skills"
            ])

        self.assertEqual(code, 0)
        self._assert_expanded(raw, "source", fake_get.call_args.kwargs)


    def test_destination_envvar_is_expanded(self) -> None:
        """
        An environment-variable reference in ``--destination`` (using
        the platform-native syntax) must also be resolved before
        dispatch so shell-style values from CI configs work.
        """

        marker = "POLYSKILLS_TEST_HOME"
        target = Path.home().as_posix()
        raw_unix    = f"${marker}/.claude/skills/{_NAME}"
        raw_windows = f"%{marker}%\\.claude\\skills\\{_NAME}"

        # ? exercise both syntaxes so the test is meaningful on every
        # ? supported platform; ``os.path.expandvars`` understands
        # ? ``$VAR`` everywhere and ``%VAR%`` on Windows.
        with mock.patch.dict(os.environ, {marker: target}, clear = False):
            for raw in (raw_unix, raw_windows):
                with mock.patch.object(cli, "get") as fake_get:
                    code, _, _ = _run_main([
                        "manager", _REMOTE,
                        "--name", _NAME,
                        "--destination", raw,
                        "skills"
                    ])

                self.assertEqual(code, 0, msg = f"input: {raw!r}")
                kwargs = fake_get.call_args.kwargs
                rendered = Path(kwargs["destination"]).as_posix()

                # ? on POSIX hosts ``%VAR%`` is *not* an env-var
                # ? syntax, so just guarantee no token leaked through;
                # ? for ``$VAR`` we additionally assert the resolved
                # ? prefix is correct.
                self.assertNotIn(f"${marker}", rendered)
                if raw is raw_unix:
                    self.assertTrue(
                        rendered.startswith(target),
                        f"$VAR not resolved: {rendered!r}"
                    )


    def test_absolute_destination_is_passed_through(self) -> None:
        """
        An already-absolute ``--destination`` must be forwarded
        verbatim (modulo POSIX normalisation) - the expansion logic
        must not alter paths that have nothing to expand.
        """

        raw = Path.home().joinpath(
            ".claude", "skills", _NAME
        ).as_posix()

        with mock.patch.object(cli, "get") as fake_get:
            code, _, _ = _run_main([
                "manager", _REMOTE,
                "--name", _NAME,
                "--destination", raw,
                "skills"
            ])

        self.assertEqual(code, 0)
        kwargs = fake_get.call_args.kwargs
        self.assertEqual(
            Path(kwargs["destination"]).as_posix(),
            Path(raw).as_posix()
        )


    def test_default_destination_unchanged_when_flag_omitted(self) -> None:
        """
        When ``--destination`` is omitted the dispatcher must continue
        to derive ``./<library>/<name>`` exactly as before; the
        expansion fix must not regress the default-derivation path.
        """

        with mock.patch.object(cli, "get") as fake_get:
            code, _, _ = _run_main([
                "manager", _REMOTE, "--name", _NAME, "skills"
            ])

        self.assertEqual(code, 0)
        kwargs = fake_get.call_args.kwargs
        self.assertEqual(
            Path(kwargs["destination"]).as_posix(),
            Path(f"./{_LIBRARY}/{_NAME}").as_posix()
        )


if __name__ == "__main__":
    unittest.main()
