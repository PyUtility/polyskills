# -*- encoding: utf-8 -*-

"""
Hermetic Security Regression Tests for the Remote Pipeline
----------------------------------------------------------

Offline tests that exercise the security-critical behaviour of
:mod:`polyskills.remote.sources` and :func:`polyskills.cli._resolveVerify`
without touching the network. Every remote ``requests.get`` call is
mocked and archive fixtures are synthesised in memory, so the suite runs
deterministically in CI and locally behind a proxy.

The cases lock in the guarantees added by the security hardening pass:
TLS verification is forwarded (never silently disabled), crafted archive
members cannot escape the destination directory, downloads and
extraction are size-bounded, and tag pagination is capped.
"""

import io
import os
import shutil
import tarfile
import tempfile
import unittest

from pathlib import Path
from typing import Dict, Optional
from unittest import mock

from polyskills import cli
from polyskills.remote import sources as sources_mod
from polyskills.remote.sources import GithubManager, SourceControl
from polyskills.error.exceptions import (
    ExtractionError, RemoteError, ValidationError
)

# ? a fixed remote URL that satisfies GithubManager.remotePattern so the
# ? slug extraction succeeds before the mocked download is reached
_REMOTE : str = "https://github.com/owner/repo"

# ? the synthetic archive root mirrors GitHub's `<owner>-<repo>-<sha>`
_ROOT : str = "owner-repo-deadbeef"


def _make_tarball(
    members : Dict[str, bytes], root : str = _ROOT
) -> bytes:
    """
    Build an in-memory ``.tar.gz`` whose every entry is nested under a
    single ``root`` directory, mimicking the layout of a GitHub source
    tarball. Keys are archive-relative POSIX paths and values are the
    raw file contents.

    :type  members: Dict[str, bytes]
    :param members: Mapping of archive-relative path to file bytes; the
        ``root`` prefix is added automatically to each entry.

    :type  root: str
    :param root: Top-level directory name injected ahead of every
        member, defaulting to :data:`_ROOT`.

    :rtype:   bytes
    :returns: The gzip-compressed tar archive as a byte string.
    """

    buffer = io.BytesIO()
    with tarfile.open(fileobj = buffer, mode = "w:gz") as archive:
        for name, content in members.items():
            info = tarfile.TarInfo(f"{root}/{name}")
            info.size = len(content)
            archive.addfile(info, io.BytesIO(content))

    return buffer.getvalue()


class _FakeResponse:
    """
    Minimal stand-in for a non-streaming :class:`requests.Response`
    used by ``_getTags`` and ``_listExtensions``.

    :type  payload: Optional[object]
    :param payload: Value returned by :meth:`json`.

    :type  links: Optional[dict]
    :param links: Value exposed as the ``links`` attribute for
        pagination traversal.
    """

    def __init__(
        self, payload : Optional[object] = None,
        links : Optional[dict] = None
    ) -> None:
        self._payload = payload if payload is not None else []
        self.links = links if links is not None else {}

    def raise_for_status(self) -> None:
        return None

    def json(self) -> object:
        return self._payload


class _FakeStream:
    """
    Streaming :class:`requests.Response` stand-in usable as a context
    manager, yielding a fixed archive payload from :meth:`iter_content`.

    :type  payload: bytes
    :param payload: Raw bytes streamed back to the download loop.
    """

    def __init__(self, payload : bytes) -> None:
        self._payload = payload

    def __enter__(self) -> "_FakeStream":
        return self

    def __exit__(self, *exc : object) -> bool:
        return False

    def raise_for_status(self) -> None:
        return None

    def iter_content(self, chunk_size : int = 1):
        for idx in range(0, len(self._payload), chunk_size):
            yield self._payload[idx : idx + chunk_size]


class TestVerifyResolution(unittest.TestCase):
    """
    Unit tests for :func:`polyskills.cli._resolveVerify`, the single
    point that maps the ``--no-verify`` / ``--request-cert`` flags onto
    the ``verify`` value forwarded to :mod:`requests`.
    """

    def test_default_is_secure(self) -> None:
        """
        With neither flag the resolver must return ``True`` so requests
        verify against the standard trust store.
        """

        self.assertIs(cli._resolveVerify(False, False), True)

    def test_no_verify_disables(self) -> None:
        """``--no-verify`` must resolve to ``False``."""

        self.assertIs(cli._resolveVerify(True, False), False)

    def test_request_cert_pins_certifi_bundle(self) -> None:
        """
        ``--request-cert`` must resolve to the bundled certifi CA path
        for strict verification.
        """

        import certifi

        self.assertEqual(
            cli._resolveVerify(False, True), certifi.where()
        )

    def test_conflicting_flags_raise(self) -> None:
        """
        Requesting both flags together must raise
        :class:`ValidationError` (also a :class:`ValueError`).
        """

        with self.assertRaises(ValidationError):
            cli._resolveVerify(True, True)


class TestVerifyForwarding(unittest.TestCase):
    """
    Guards that the configured ``verify`` value reaches every
    :func:`requests.get` call rather than being silently overridden.
    """

    def test_tags_request_forwards_verify_false(self) -> None:
        """
        A manager built with ``verify=False`` must pass that value to
        the underlying tags request.
        """

        manager = GithubManager(SourceControl(verify = False))
        with mock.patch.object(
            sources_mod.requests, "get",
            return_value = _FakeResponse()
        ) as fake_get:
            manager.get(_REMOTE, mode = "tags")

        self.assertIs(fake_get.call_args.kwargs["verify"], False)

    def test_tags_request_forwards_verify_true(self) -> None:
        """
        The secure default (``verify=True``) must likewise be forwarded
        verbatim to the tags request.
        """

        manager = GithubManager(SourceControl())
        with mock.patch.object(
            sources_mod.requests, "get",
            return_value = _FakeResponse()
        ) as fake_get:
            manager.get(_REMOTE, mode = "tags")

        self.assertIs(fake_get.call_args.kwargs["verify"], True)


class TestPaginationCap(unittest.TestCase):
    """
    Ensures :meth:`GithubManager._getTags` cannot be trapped in an
    endless ``next`` link chain served by a hostile remote.
    """

    def test_endless_pagination_raises_remote_error(self) -> None:
        """
        When every response advertises a ``next`` link, the loop must
        abort with :class:`RemoteError` once ``_MAX_PAGES`` is reached.
        """

        endless = _FakeResponse(
            payload = [], links = {"next": {"url": "https://api/next"}}
        )
        with mock.patch.object(sources_mod, "_MAX_PAGES", 3), \
                mock.patch.object(
                    sources_mod.requests, "get", return_value = endless
                ):
            with self.assertRaises(RemoteError):
                GithubManager().get(_REMOTE, mode = "tags")


class TestArchiveExtractionSafety(unittest.TestCase):
    """
    Offline extraction tests for :meth:`GithubManager._getExtensions`
    covering the happy path and each safety guard, driven by in-memory
    archive fixtures and a mocked streaming download.
    """

    def setUp(self) -> None:
        """Allocate an isolated staging directory per test."""

        self.staging = Path(
            tempfile.mkdtemp(prefix = "polyskills-sec-")
        )
        self.destination = self.staging / "out"

    def tearDown(self) -> None:
        """Remove the staging directory created in :meth:`setUp`."""

        shutil.rmtree(self.staging, ignore_errors = True)

    def _extract(self, payload : bytes, name : str = "skill") -> None:
        """
        Drive :meth:`GithubManager.get` in ``extensions`` mode with the
        download mocked to stream ``payload``.

        :type  payload: bytes
        :param payload: The archive bytes returned by the mocked GET.

        :type  name: str
        :param name: Extension (leaf directory) name to extract.
        """

        with mock.patch.object(
            sources_mod.requests, "get",
            return_value = _FakeStream(payload)
        ):
            GithubManager().get(
                _REMOTE, mode = "extensions", name = name,
                library = "skills", source = "extensions/skills",
                destination = self.destination
            )

    def test_happy_path_extracts_files(self) -> None:
        """
        A well-formed archive must extract every member under the
        target directory into the destination, preserving sub-paths.
        """

        payload = _make_tarball({
            "extensions/skills/skill/SKILL.md": b"---\nname: x\n---\n",
            "extensions/skills/skill/ref/general.md": b"hello",
        })

        self._extract(payload)

        self.assertTrue((self.destination / "SKILL.md").is_file())
        self.assertEqual(
            (self.destination / "ref" / "general.md").read_bytes(),
            b"hello"
        )

    def test_path_traversal_member_is_rejected(self) -> None:
        """
        A crafted member carrying ``..`` segments that escape the
        destination must raise :class:`ExtractionError` and must not
        write the malicious file anywhere outside the destination.
        """

        payload = _make_tarball({
            "extensions/skills/skill/SKILL.md": b"ok",
            "extensions/skills/skill/../../../../escape.txt": b"pwned",
        })

        with self.assertRaises(ExtractionError):
            self._extract(payload)

        leaked = self.staging.parent / "escape.txt"
        self.assertFalse(
            leaked.exists(), f"path traversal leaked file to {leaked}"
        )

    def test_download_exceeding_size_cap_is_rejected(self) -> None:
        """
        A download larger than ``_MAX_ARCHIVE_BYTES`` must abort with
        :class:`ExtractionError` before extraction begins.
        """

        payload = _make_tarball({
            "extensions/skills/skill/SKILL.md": b"x" * 64,
        })

        with mock.patch.object(sources_mod, "_MAX_ARCHIVE_BYTES", 8):
            with self.assertRaises(ExtractionError):
                self._extract(payload)

    def test_extraction_exceeding_size_cap_is_rejected(self) -> None:
        """
        When the cumulative uncompressed size exceeds
        ``_MAX_EXTRACT_BYTES`` the extraction must abort with
        :class:`ExtractionError`.
        """

        payload = _make_tarball({
            "extensions/skills/skill/SKILL.md": b"x" * 256,
        })

        with mock.patch.object(sources_mod, "_MAX_EXTRACT_BYTES", 16):
            with self.assertRaises(ExtractionError):
                self._extract(payload)

    def test_missing_extension_raises_not_found(self) -> None:
        """
        An archive that contains no entry under the requested target
        must raise :class:`FileNotFoundError`.
        """

        payload = _make_tarball({
            "extensions/skills/other/SKILL.md": b"ok",
        })

        with self.assertRaises(FileNotFoundError):
            self._extract(payload, name = "skill")


if __name__ == "__main__":
    unittest.main(verbosity = 2)
