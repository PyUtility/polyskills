# -*- encoding: utf-8 -*-

"""
Cross-Platform Skill Installation Tests
----------------------------------------

Validates that the :mod:`polyskills` framework can correctly resolve
the per-platform user skill directory and extract a ``SKILL.md``-based
skill from a remote repository into that directory structure.

Two test classes are provided:

  * :class:`TestUserSkillDirectoryPath` - pure path-resolution tests
    that require no network and no filesystem writes. They use
    :class:`pathlib.PurePosixPath` and :class:`pathlib.PureWindowsPath`
    to assert the directory layout is correct on Linux, macOS, and
    Windows without actually touching any real user home directory.

  * :class:`TestSkillInstallToUserDirectory` - live-network tests that
    extract the ``sql-code-format`` skill into a temporary directory
    whose structure mirrors ``~/.claude/skills/<name>/``, then assert
    that ``SKILL.md`` is present, non-empty, and contains valid YAML
    frontmatter (the ``---`` block required by the Agent-Skills standard).
"""

import unittest

from pathlib import Path, PurePosixPath, PureWindowsPath

from polyskills.tests.base import (
    EXPECTED, LIBRARY, NAME, REMOTE, SKILL_FILENAME,
    USER_SKILL_ROOT, VERSION, GithubManagerTestCase
)

# ? representative home-directory roots per OS used in structural tests
_LINUX_HOME   : str = "/home/testuser"
_MACOS_HOME   : str = "/Users/testuser"
_WINDOWS_HOME : str = r"C:\Users\testuser"

# ? YAML frontmatter delimiter shared between SKILL.md and AGENT.md
_FRONTMATTER_DELIMITER : str = "---"


class TestUserSkillDirectoryPath(unittest.TestCase):
    """
    Pure path-resolution tests for the user skill directory.

    These tests make no network requests and write nothing to disk.
    They verify that the :data:`USER_SKILL_ROOT` constant and the
    path construction convention used throughout the framework produce
    the expected directory structure on every supported platform.
    """

    def test_user_skill_root_is_absolute(self) -> None:
        """
        :data:`USER_SKILL_ROOT` must be an absolute path so callers can
        use it as a ``destination`` argument without ambiguity.
        """

        self.assertTrue(
            USER_SKILL_ROOT.is_absolute(),
            f"USER_SKILL_ROOT is not absolute: {USER_SKILL_ROOT}"
        )


    def test_user_skill_root_ends_with_claude_skills(self) -> None:
        """
        The last two path components must be ``.claude`` and ``skills``
        in that order, which is the conventional location for Claude
        Code global skill installations on every supported platform.
        """

        parts = USER_SKILL_ROOT.parts
        self.assertEqual(parts[-2], ".claude")
        self.assertEqual(parts[-1], "skills")


    def test_skill_destination_is_child_of_user_skill_root(self) -> None:
        """
        Installing a named skill creates a sub-directory directly
        beneath :data:`USER_SKILL_ROOT`; its ``name`` component must
        match the skill directory name.
        """

        destination = USER_SKILL_ROOT / NAME

        self.assertEqual(destination.parent, USER_SKILL_ROOT)
        self.assertEqual(destination.name, NAME)


    def test_path_parts_on_linux(self) -> None:
        """
        On a Linux host (``/home/<user>``), the constructed skill
        destination must follow ``/home/<user>/.claude/skills/<name>``.
        Uses :class:`~pathlib.PurePosixPath` so the assertion is valid
        on any platform.
        """

        home = PurePosixPath(_LINUX_HOME)
        skill_root = home / ".claude" / "skills"
        destination = skill_root / NAME

        self.assertEqual(skill_root.parts[-2:], (".claude", "skills"))
        self.assertEqual(destination.name, NAME)
        self.assertTrue(
            destination.as_posix().startswith(_LINUX_HOME),
            f"Unexpected prefix: {destination.as_posix()}"
        )


    def test_path_parts_on_macos(self) -> None:
        """
        On a macOS host (``/Users/<user>``), the constructed skill
        destination must follow ``/Users/<user>/.claude/skills/<name>``.
        Uses :class:`~pathlib.PurePosixPath` so the assertion is valid
        on any platform.
        """

        home = PurePosixPath(_MACOS_HOME)
        skill_root = home / ".claude" / "skills"
        destination = skill_root / NAME

        self.assertEqual(skill_root.parts[-2:], (".claude", "skills"))
        self.assertEqual(destination.name, NAME)
        self.assertTrue(
            destination.as_posix().startswith(_MACOS_HOME),
            f"Unexpected prefix: {destination.as_posix()}"
        )


    def test_path_parts_on_windows(self) -> None:
        """
        On a Windows host (``C:\\Users\\<user>``), the constructed
        skill destination must follow
        ``C:\\Users\\<user>\\.claude\\skills\\<name>``.
        Uses :class:`~pathlib.PureWindowsPath` so the assertion is
        valid on any platform.
        """

        home = PureWindowsPath(_WINDOWS_HOME)
        skill_root = home / ".claude" / "skills"
        destination = skill_root / NAME

        self.assertEqual(skill_root.parts[-2:], (".claude", "skills"))
        self.assertEqual(destination.name, NAME)
        self.assertTrue(
            str(destination).startswith(_WINDOWS_HOME),
            f"Unexpected prefix: {destination}"
        )


    def test_posix_path_separator_compatibility(self) -> None:
        """
        ``Path.as_posix()`` on the skill destination must produce a
        forward-slash-separated string on every platform, because
        :meth:`polyskills.remote.sources.SourceManager.get` passes
        ``source.as_posix()`` to the archive walker internally.
        """

        destination = USER_SKILL_ROOT / NAME
        posix = destination.as_posix()

        self.assertNotIn("\\", posix)
        self.assertIn("/", posix)


    def test_skill_filename_constant_matches_expected(self) -> None:
        """
        The :data:`SKILL_FILENAME` constant must match the filename
        present in the :data:`EXPECTED` set so the install tests and
        the path tests share a single source of truth.
        """

        self.assertIn(SKILL_FILENAME, EXPECTED)


class TestSkillInstallToUserDirectory(GithubManagerTestCase):
    """
    Live-network tests that validate a skill extracted into a staging
    directory whose structure mirrors the conventional user skill
    directory (``~/.claude/skills/<name>/``).

    The staging directory is managed by the :class:`GithubManagerTestCase`
    base: ``self.destination`` is set to ``self.staging / NAME`` in
    ``setUp`` and torn down automatically in ``tearDown``.
    """

    def test_skill_md_present_after_install(self) -> None:
        """
        ``SKILL.md`` must exist at the root of the destination
        directory immediately after the skill is extracted - this is
        the file Claude Code reads to determine skill capabilities.
        """

        self._extract()

        skill_md = self.destination / SKILL_FILENAME

        self.assertTrue(
            skill_md.exists(),
            f"{SKILL_FILENAME} not found after install at {skill_md}"
        )
        self.logger.info(
            "SKILL.md path (user-dir mirror) : %s", skill_md
        )


    def test_skill_md_is_non_empty(self) -> None:
        """
        ``SKILL.md`` must be a non-empty file after extraction.
        An empty file would indicate a corrupt or incomplete download.
        """

        self._extract()

        skill_md = self.destination / SKILL_FILENAME
        size = skill_md.stat().st_size

        self.assertGreater(
            size, 0,
            f"{SKILL_FILENAME} is empty (0 bytes) after install."
        )
        self.logger.info("SKILL.md size : %d B", size)


    def test_skill_md_has_valid_yaml_frontmatter(self) -> None:
        """
        ``SKILL.md`` must open with the YAML frontmatter delimiter
        ``---`` on the very first line, which is the mandatory format
        required by the Agent-Skills standard for auto-invocation by
        Claude Code and compatible LLM tools.
        """

        self._extract()

        skill_md = self.destination / SKILL_FILENAME
        first_line = skill_md.read_text(
            encoding = "utf-8"
        ).splitlines()[0]

        self.assertEqual(
            first_line, _FRONTMATTER_DELIMITER,
            f"First line of {SKILL_FILENAME} is not '---'; "
            f"got {first_line!r}. File may be corrupt or is not a "
            f"valid Agent-Skills skill."
        )


    def test_installed_skill_destination_name_matches_skill(self) -> None:
        """
        The leaf directory name of the installation path must equal
        the skill name so ``/path/to/.claude/skills/<name>/SKILL.md``
        resolves correctly on every platform.
        """

        self._extract()

        self.assertEqual(
            self.destination.name, NAME,
            f"Destination leaf is {self.destination.name!r}, "
            f"expected {NAME!r}."
        )


    def test_installed_files_use_posix_compatible_relative_paths(self) -> None:
        """
        All relative paths inside the extracted skill directory must
        be expressible as POSIX strings (forward-slash-separated) so
        they are portable between Windows, Linux, and macOS hosts.
        """

        self._extract()

        for path in self.destination.rglob("*"):
            if path.is_file():
                relative = path.relative_to(self.destination).as_posix()
                self.assertNotIn(
                    "\\", relative,
                    f"Non-POSIX path separator in relative path: "
                    f"{relative!r}"
                )
