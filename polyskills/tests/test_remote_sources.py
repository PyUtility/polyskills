# -*- encoding: utf-8 -*-

"""
End-to-End Tests for the GitHub Remote Source Manager
-----------------------------------------------------

Exercises :meth:`polyskills.remote.sources.GithubManager.get` for
both ``mode='tags'`` and ``mode='extensions'`` against the live
https://github.com/PyUtility/polyskills repository to assert the
public contracts surfaced by the dispatcher.

The cases mirror the legacy ``tests.py`` smoke script but are split
into focused :class:`unittest.TestCase` subclasses so failures point
straight at the broken contract and so the suite is discoverable by
``unittest discover``.
"""

from polyskills.tests.base import (
    EXPECTED, LIBRARY, NAME, REMOTE, VERSION, GithubManagerTestCase
)


class TestGithubManagerTags(GithubManagerTestCase):
    """
    Validates the ``mode='tags'`` branch of
    :meth:`GithubManager.get` - both the un-filtered listing and the
    case-sensitive ``prefix`` filter that exists for backward
    compatibility with the ``skillName@vX.Y.Z`` tag scheme.
    """

    def test_returns_list_of_tags(self) -> None:
        """
        ``manager.get(remote, mode='tags')`` must return a ``list``
        (possibly empty) without raising for a public repository.
        """

        tags = self.manager.get(REMOTE, mode = "tags")

        self.assertIsInstance(
            tags, list,
            f"Expected list of tags, got {type(tags).__name__}"
        )
        self.logger.info("Total tags fetched : %d", len(tags))
        if tags:
            self.logger.info("Sample (up to 5)   : %s", tags[:5])


    def test_prefix_filter_returns_only_matching_tags(self) -> None:
        """
        The ``prefix`` keyword must filter case-sensitively and the
        post-condition holds whether or not any tag actually starts
        with the prefix.
        """

        filtered = self.manager.get(REMOTE, mode = "tags", prefix = "v")

        self.assertIsInstance(filtered, list)
        self.assertTrue(
            all(tag.startswith("v") for tag in filtered),
            f"Prefix filter returned non-matching tags: {filtered}"
        )
        self.logger.info(
            "Prefix='v' filter  : %d tag(s)", len(filtered)
        )


class TestGithubManagerExtensions(GithubManagerTestCase):
    """
    Validates the ``mode='extensions'`` branch of
    :meth:`GithubManager.get` - the happy-path extraction, the
    ``exists='fail'`` guard, and the ``exists='overwrite'`` cleanup
    semantics.
    """

    def _extract(self) -> None:
        """
        Helper that performs a vanilla extension extraction into
        ``self.destination`` with the default ``exists='fail'``
        policy so individual tests do not duplicate the dispatch
        boilerplate.
        """

        result = self.manager.get(
            REMOTE, mode = "extensions",
            name = NAME, library = "skills",
            source = LIBRARY, destination = self.destination,
            version = VERSION
        )
        self.assertIsNone(
            result,
            f"Expected None from extensions dispatch, got {result!r}"
        )


    def test_extracts_expected_files_into_destination(self) -> None:
        """
        After a successful dispatch the destination must contain at
        least every file enumerated in :data:`EXPECTED`.
        """

        self._extract()

        files = sorted(
            path.relative_to(self.destination).as_posix()
            for path in self.destination.rglob("*") if path.is_file()
        )

        self.assertTrue(
            files, "No files were extracted into destination."
        )
        missing = EXPECTED - set(files)
        self.assertFalse(
            missing,
            f"Expected files missing after extraction: {missing}"
        )
        self.logger.info("Extracted %d file(s).", len(files))


    def test_exists_fail_guards_non_empty_destination(self) -> None:
        """
        Re-running the dispatcher against a non-empty destination
        with the default ``exists='fail'`` policy must raise
        :class:`FileExistsError`.
        """

        self._extract()

        with self.assertRaises(FileExistsError):
            self.manager.get(
                REMOTE, mode = "extensions",
                name = NAME, source = LIBRARY,
                destination = self.destination, version = VERSION
            )


    def test_exists_overwrite_replaces_stale_content(self) -> None:
        """
        ``exists='overwrite'`` must wipe pre-existing destination
        contents before re-extracting the extension payload.
        """

        self._extract()

        stale = self.destination / "stale.txt"
        stale.write_text("old content", encoding = "utf-8")

        self.manager.get(
            REMOTE, mode = "extensions",
            name = NAME, source = LIBRARY,
            destination = self.destination, version = VERSION,
            exists = "overwrite"
        )

        self.assertFalse(
            stale.exists(),
            "exists='overwrite' did not clear pre-existing files."
        )
