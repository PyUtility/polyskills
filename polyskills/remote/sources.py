# -*- encoding: utf-8 -*-

"""
Control for Valid List of Supported Remote with REST API Services
-----------------------------------------------------------------

The application is designed to be source agnostic - meaning a remote
source which supports ``git`` document hosting and has a REST API to
fetch data using :mod:`requests` is supported.

.. code-block:: python

    print([member.name for member in ValidSources]) # suported sources
    >> ['GITHUB', ...]

    # alternatively, get valid sources using cli::
    polyskills --help
    >> ...
    >> Supported Sources: [('GITHUB', 'https://www.github.com/'), ...]
"""

import os
import re
import abc
import shutil
import tarfile

import tempfile
import requests

from enum import Enum
from pathlib import Path
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

# ! security limits guarding the remote download / extraction pipeline
# ? the compressed download is capped to bound disk usage, and the
# ? cumulative uncompressed size is capped to defang gzip / tar bombs
_CHUNK_SIZE : int = 1 << 14
_MAX_ARCHIVE_BYTES : int = 100 * (1 << 20)
_MAX_EXTRACT_BYTES : int = 500 * (1 << 20)


class ValidSources(Enum):
    GITHUB = "https://www.github.com/"


@dataclass(frozen = True)
class SourceControl:
    """
    Additional parameters for remote source data control. These are
    typically for advanced users.

    :type  pagination: int
    :param pagination: A pagination parameter controls how manye
        results are returned in one page for a ``GET`` request from
        ``https://api.github.com/repos/{owner}/{repo}/tags/`` (same
        can be applicable for other websites). Defaults to 100, which
        is the maximum value allowed.

    :type  token: Optional[str]
    :param token: A authorization token to access the remote URL, this
        value is discouraged to be used in a production system.

    :type  verify: Union[bool, str]
    :param verify: TLS verification forwarded verbatim to every
        :func:`requests.get` call. ``True`` (default) uses the standard
        trust store and honours the ``REQUESTS_CA_BUNDLE`` /
        ``SSL_CERT_FILE`` environment overrides, a string pins a CA
        bundle path, and ``False`` disables verification entirely
        (discouraged, exposed via the ``--no-verify`` CLI flag).

    Each parameter should be available as a CLI command for dynamic
    control which sets the data class defaults during runtime.
    """

    pagination : int = 100

    # ? Token Attribute: Useful only in testing environment
    token : Optional[str] = None

    # ? TLS verification policy forwarded to every remote request;
    # ? defaults to secure verification, see the param docstring above
    verify : Union[bool, str] = True


class SourceManager(abc.ABC):
    """
    A source manager, which accepts the remote source and returns all
    the default values along with data checks and other valid values.

    :type  source: ValidSources
    :param source: Any valid data source which is supported by the
        module - this is an enumeration object.

    :type  controller: SourceControl
    :param controller: A data class to control the remote URL (REST
        API) for page content, etc. Check the individual control using
        :class:`SourceControl` documentation.
    """

    def __init__(self, source : ValidSources, control : SourceControl) -> None:
        self.source = source
        self.control = control


    @property
    @abc.abstractmethod
    def remotePattern(self) -> re.Pattern:
        """
        Returns the cached compiled regex for the active source. Used
        by ``detectSource()`` (to recognise a URL) and ``getSlug()``
        (to extract ``owner``/``repository`` named groups).
        """

        pass


    def getSlug(self, remote : str) -> Tuple[str, str]:
        """
        Internally checks the remote URL and returns the slug values
        to form the REST API endpoint - namely the ``owner`` and the
        ``repository`` tag.

        .. code-block:: python

            manager = SourceManager(
                ValidSources = ValidSources.GITHUB,
                ...
            )

            owner, repository = manager.getSlug(
                remote = "https://github.com/PyUtility/polyskills"
            )

            print(owner, repository)
            >> PyUtility, polyskills
            print(manager.remoteAPI.format(
                owner = owner, repository = repository
            ))
            >> ...api.github.com/repos/PyUtility/polyskills/tags?...

        :raises ValueError: If the remote URL does not match the
            regular expression pattern supported by the module.
        """

        matches = self.remotePattern.match(remote)

        if not matches:
            raise ValueError(
                f"Not a Valid URL: {remote}, or Not Supported."
            )

        return (matches.group("owner"), matches.group("repository"))


    @property
    @abc.abstractmethod
    def remoteAPI(self) -> str:
        """
        Return the REST API endpoint formatted with slug values (and
        additional controls) such that concrete methods can directly
        invoke to get the remote content using :func:`requests.get`
        method.
        """

        pass


    @property
    @abc.abstractmethod
    def headers(self) -> Dict[str, str]:
        """
        Returns the valid list of headers which are required by the
        REST API of the version control source.
        """

        pass


    def get(self, remote : str, mode : str = "tags", **kwargs) -> Any:
        """
        Get is a concrete method that fetches data from the remote
        source to fetch underlying extensions (skills, agents, etc.)
        and also get other informations like ``tags``, ``commits``,
        which can be used to get the exact version of the extensions
        from the remote source.

        :type  remote: str
        :param remote: Remote URI where the code is hosted. Based on
            the data source, the REST API endpoints are internally
            generated (if exists) or method is exposed.

        :type  mode: str
        :param mode: Typical endpoint based on which the data is to
            be fetched from the remote source, defaults to ``tags``
            which fetches the ``git tag`` from the system.

        **Keyword Arguments**

        The keyword arguments are defined based on the requirement of
        the ``mode`` attribute. Each mode has a particular set of
        optional control requirements as below.

            * MODE: ``tags`` - Fetches the tags from the remote
                repository. This is particularly useful to fetch the
                extensions for a particular version. Accepted keyword
                arguments are:

                - **prefix** (*str*) - This is created to
                    provide a backward compatibility for the initial
                    version (https://pypi.org/project/polyskills/1.0.0/)
                    of the module. Defaults to ``None`` which returns
                    everything.

            * MODE: ``extensions`` - Method to get the extension from
                the remote repository. An extension for LLM tool can
                be ``skills``, ``agents``, etc. which are available.

                - **name** (*str*) - Name of the extension, this is
                    a required value, raises assertion error if None.

                - **source** (*str*) - Directory from where the
                    extension is available. The default value is the
                    `./skills` directory, and should be controlled
                    by the managers.

                - **destination** (*str*) - Destination directory to
                    flush the extension content, defaults to local.

                - **version** (*str*) - Specify the exact version (tags,
                    commit hash) to fetch the extension details. This
                    defaults to ``master`` that is the latest content
                    from the repository. (TODO)

                - **formatter** (*Callable*) - Formatter method based
                    on the final LLM tool. (TODO)
        """

        prefix : Optional[str] = kwargs.get("prefix", None)

        # positional arguments to fetch extensions from remote
        name : Optional[str] = kwargs.get("name", None)
        library : Optional[str] = kwargs.get("library", "skills")

        # generate the source, destination directory defaults
        source : Optional[Path] = kwargs.get(
            "source", Path(f"./{library}").as_posix()
        )
        destination : Optional[Path] = kwargs.get(
            "destination", Path(f"./{library}/{name}")
        )

        # todo: optional keyword argument to refine further control
        version : Optional[str] = kwargs.get("version", "master")
        formatter : Optional[Callable] = kwargs.get(
            "formatter", lambda : None
        )
        exists : str = kwargs.get("exists", "fail")

        # list of supported modes; keyword arguments control
        # always use lower case naming for modes; in-built control
        mode = mode.lower()
        supported = ["tags", "extensions", "list"]
        if mode not in supported:
            raise ValueError(f"Mode = `{mode}` is not in {supported}.")

        # ! validate that positional required arguments are available
        # only enforced for the ``extensions`` mode where they are used
        # ! raised explicitly (not ``assert``) so the checks survive a
        # ! ``python -O`` optimised run where assertions are stripped
        if mode == "extensions":
            if name is None:
                raise ValueError("Extension name cannot be null.")
            if library is None:
                raise ValueError(
                    f"Library cannot be null, supported are {supported}."
                )

        if mode == "list":
            if library is None:
                raise ValueError(
                    f"Library cannot be null, supported are {supported}."
                )

        # lazy dispatch: only the requested branch is invoked
        methods : Dict[str, Callable[[], Any]] = dict(
            tags = lambda : self._getTags(remote, prefix = prefix),
            extensions = lambda : self._getExtensions(
                remote, name, source, destination, # type: ignore[arg-type]
                version, formatter, exists # type: ignore[arg-type]
            ),
            list = lambda : self._listExtensions(
                remote, source, version # type: ignore[arg-type]
            ),
        )

        return methods[mode]() # return the underlying assets


    @abc.abstractmethod
    def _getTags(
        self, remote : str, prefix : Optional[str] = None
    ) -> List[str]:
        """
        Get the valid list of tags with an optional compatibility for
        the https://pypi.org/project/polyskills/1.0.0/ release.
        """

        pass


    @abc.abstractmethod
    def _getExtensions(
        self, remote : str, name : str, source : Path,
        destination : Path, version : str = "master",
        formatter : Optional[Callable] = lambda : None
    ) -> None:
        """
        Get the underlying assets from the "source" directory and
        flush the content to the "destination" directory. In addition,
        if any additional parsing is required by the LLM tool then
        the content should be processed accordingly.
        """

        pass


    @abc.abstractmethod
    def _listExtensions(
        self, remote : str, source : Path, version : str = "master"
    ) -> List[str]:
        """
        List the immediate child directory names available under the
        ``source`` directory of the remote at the given ``version``.

        Each child directory typically corresponds to one extension
        (a skill, an agent, etc.) packaged per the Agents Skills
        [https://agentskills.io/home] standards.

        :rtype:   List[str]
        :returns: Sorted list of directory names. Files at the
            ``source`` root are intentionally excluded.
        """

        pass


    @property
    def _token(self) -> Optional[str]:
        """
        Get the authorization token (if any) for the remote URI, which
        is typically required for private repository.

        :NOTE: Authorization token can be passed to the module either
        by providing the value from environment variable (please set
        ``POLYSKILLS_REMOTE_TOKEN``) which has the highest priority,
        or by setting the value to :attr:`SourceControl.token` which
        is also available as ``--token`` parameter from CLI (the
        later is discouraged). If both the value is provided then the
        environment value is prioritized without an error.
        """

        return os.environ.get(
            "POLYSKILLS_REMOTE_TOKEN", self.control.token
        )


class GithubManager(SourceManager):
    """
    A concrete method to manage remote repository hosted at the
    https://www.github.com/ that hosts extensions for LLM tools.

    :type  control: SourceControl
    :param control: Source control parameter for remote hosts
        connection and to control the ``GET`` requests for the REST
        API endpoints.
    """

    def __init__(self, control : SourceControl = SourceControl()) -> None:
        super().__init__(source = ValidSources.GITHUB, control = control)


    @property
    def remotePattern(self) -> re.Pattern:
        """
        Returns the cached compiled regex for the active source. Used
        by ``detectSource()`` (to recognise a URL) and ``getSlug()``
        (to extract ``owner``/``repository`` named groups). This is
        an explicit pattern for https://github.com/{owner}/{repository}
        with a defined slug groups to build remote.
        """

        return re.compile(
            r"^(?:https?://)?(?:www\.)?github\.com/"
            r"(?P<owner>[^/]+)/(?P<repository>[^/]+?)(?:\.git)?/?$"
        )


    @property
    def remoteAPI(self) -> str:
        """
        Returns the REST API endpoint for GitHub hosted repositories,
        check https://docs.github.com/en/rest for more details.

        :rtype:   str
        :returns: REST API endpoint for GitHub hosted repository with
            positional format options for ``owner``, ``repository``,
            and ``pagination`` control.
        """

        return (
            "https://api.github.com/repos/"
            "{owner}/{repository}/tags?per_page={pagination}"
        )


    @property
    def headers(self) -> Dict[str, str]:
        """
        Returns the valid list of headers which are required by the
        GitHub REST API endpoints.

        :NOTE: The :mod:`requests` strips the ``authorization`` header
        on cross-host redirect, so it is safe to forward the token to
        the tarball endpoint as well - GitHub redirects archive
        downloads to S3 and the token does not follow.
        """

        headers = {
            "accept" : "application/vnd.github+json",
            "X-GitHub-Api-Version" : "2022-11-28",
        }

        if self._token:
            headers["authorization"] = f"Bearer {self._token}"

        return headers


    def _getTags(
        self, remote : str, prefix : Optional[str] = None, **kwargs
    ) -> List[str]:
        """
        Uses the :mod:`requests` to fetch all the tags from the REST
        API with an option to filter the tags based on a prefix.

        :type  prefix: Optional[str]
        :param prefix: A case-sensitive prefix value which filters
            the list of tags. This is a backward compatiblity mode to
            get tags hosted in ``skillName@vX.Y.Z`` format.
        """

        timeout = kwargs.get("timeout", 30)
        owner, repository = self.getSlug(remote = remote)
        remote_url = self.remoteAPI.format(
            owner = owner, repository = repository,
            pagination = self.control.pagination
        )

        tags : List[str] = []

        while remote_url:
            response = requests.get(
                remote_url, verify = self.control.verify,
                headers = self.headers, timeout = timeout
            )
            response.raise_for_status()

            for item in response.json():
                if prefix and not item["name"].startswith(prefix):
                    continue
                tags.append(item["name"])

            remote_url = response.links.get("next", {}).get("url")
        
        return tags


    def _getExtensions(
        self, remote : str, name : str, source : Path,
        destination : Path, version : str = "master",
        formatter : Optional[Callable] = lambda : None,
        exists : str = "fail"
    ) -> None:
        """
        Flush the content of the extensions from the source directory
        of the remote tarball archive into the destination directory.

        :type  exists: str
        :param exists: Behavior when ``destination`` already exists
            and is non-empty. One of ``fail`` (raises
            :class:`FileExistsError`), ``overwrite`` (removes and
            recreates ``destination``), or ``merge`` (extracts on top
            of the existing tree, overwriting on conflict). Defaults
            to ``fail``.
        """

        if exists not in ("fail", "overwrite", "merge"):
            raise ValueError(
                f"exists = `{exists}` not in "
                "['fail', 'overwrite', 'merge']."
            )

        owner, repository = self.getSlug(remote = remote)
        uri = (
            "https://api.github.com/repos/"
            "{owner}/{repository}/tarball/{tag}"
        ).format(owner = owner, repository = repository, tag = version)

        destination = Path(destination)
        if destination.exists() and destination.is_dir() \
                and any(destination.iterdir()):
            if exists == "fail":
                raise FileExistsError(
                    f"Destination `{destination}` exists and is not empty."
                )
            elif exists == "overwrite":
                shutil.rmtree(destination)

        destination.mkdir(parents = True, exist_ok = True)

        # path of the extension as it appears inside the archive,
        # underneath the auto-generated <owner>-<repo>-<sha> prefix
        sub = Path(str(source)).as_posix().lstrip("./").strip("/")
        target = f"{sub}/{name}".strip("/") if sub else name

        with tempfile.NamedTemporaryFile(
            suffix = ".tar.gz", delete = False
        ) as handle:
            archive_path = Path(handle.name)

            try:
                with requests.get(
                    uri, headers = self.headers, stream = True,
                    verify = self.control.verify, timeout = 60,
                    allow_redirects = True
                ) as response:
                    response.raise_for_status()
                    downloaded = 0
                    for chunk in response.iter_content(
                        chunk_size = _CHUNK_SIZE
                    ):
                        if not chunk:
                            continue
                        downloaded += len(chunk)
                        if downloaded > _MAX_ARCHIVE_BYTES:
                            raise ValueError(
                                "Download exceeds the safety limit of "
                                f"{_MAX_ARCHIVE_BYTES} bytes."
                            )
                        handle.write(chunk)
                handle.flush()
                handle.close()

                with tarfile.open(archive_path, mode = "r:gz") as archive:
                    members = archive.getmembers()
                    if not members:
                        raise FileNotFoundError(
                            f"Empty archive for {remote}@{version}"
                        )

                    root = members[0].name.split("/", 1)[0]
                    prefix = f"{root}/{target}/"

                    # ! resolve the destination once so every member can
                    # ! be verified to stay inside this subtree below
                    safe_root = destination.resolve()

                    found = False
                    extracted_bytes = 0
                    for member in members:
                        if not member.name.startswith(prefix):
                            continue
                        found = True
                        relative = member.name[len(prefix):]
                        if not relative:
                            continue

                        out_path = destination / relative

                        # ! defend against path traversal - a crafted
                        # ! member may carry '..' segments that escape
                        resolved = (safe_root / relative).resolve()
                        if resolved != safe_root \
                                and safe_root not in resolved.parents:
                            raise ValueError(
                                f"Unsafe archive member `{member.name}` "
                                "escapes the destination directory."
                            )

                        if member.isdir():
                            out_path.mkdir(parents = True, exist_ok = True)
                        elif member.isfile():
                            extracted_bytes += max(member.size, 0)
                            if extracted_bytes > _MAX_EXTRACT_BYTES:
                                raise ValueError(
                                    "Extraction exceeds the safety limit "
                                    f"of {_MAX_EXTRACT_BYTES} bytes."
                                )
                            out_path.parent.mkdir(
                                parents = True, exist_ok = True
                            )
                            extracted = archive.extractfile(member)
                            if extracted is None:
                                continue
                            with extracted as src_fp, \
                                    open(out_path, "wb") as dst_fp:
                                shutil.copyfileobj(src_fp, dst_fp)
                        # ? symlink / hardlink / device / fifo members
                        # ? are neither dir nor file - skipped on purpose

                    if not found:
                        raise FileNotFoundError(
                            f"Extension `{name}` not found at "
                            f"`{target}` in {remote}@{version}"
                        )
            finally:
                try:
                    archive_path.unlink()
                except OSError:
                    pass


    def _listExtensions(
        self, remote : str, source : Path, version : str = "master",
        **kwargs
    ) -> List[str]:
        """
        Lists the immediate sub-directories under ``source`` for a
        GitHub-hosted repository using the Contents REST API endpoint
        ``GET /repos/{owner}/{repo}/contents/{path}?ref={version}``.

        Only entries with ``type == "dir"`` are returned (each such
        directory corresponds to a single extension), and the result
        is sorted alphabetically for deterministic CLI output.
        """

        timeout = kwargs.get("timeout", 30)
        owner, repository = self.getSlug(remote = remote)

        sub = Path(str(source)).as_posix().lstrip("./").strip("/")
        uri = (
            "https://api.github.com/repos/"
            "{owner}/{repository}/contents/{path}?ref={ref}"
        ).format(
            owner = owner, repository = repository,
            path = sub, ref = version
        )

        response = requests.get(
            uri, verify = self.control.verify,
            headers = self.headers, timeout = timeout
        )
        response.raise_for_status()

        payload = response.json()
        if not isinstance(payload, list):
            raise NotADirectoryError(
                f"Source `{sub}` at {remote}@{version} is not a directory."
            )

        names = [
            item["name"] for item in payload
            if isinstance(item, dict) and item.get("type") == "dir"
        ]

        return sorted(names)
