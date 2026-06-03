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

import tempfile
import requests

from enum import Enum
from pathlib import Path
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Tuple

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

    Each parameter should be available as a CLI command for dynamic
    control which sets the data class defaults during runtime.
    """

    pagination : int = 100

    # ? Token Attribute: Useful only in testing environment
    token : Optional[str] = None


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

        name : Optional[str] = kwargs.get("name", None)
        source : Optional[str] = kwargs.get(
            "source", Path("./skills").as_posix()
        )
        destination : Optional[str] = kwargs.get(
            "destination", Path(f"./skills/{name}")
        )
        version : Optional[str] = kwargs.get("version", "master")

        _m = ["tags", "skills", "agents"] # supported modes
        assert mode.lower() in _m, "Invalid mode, supported: {_m}"

        # ! validate that positional required arguments are available
        assert name is not None and mode == "extensions", \
            "Extension name cannot be null."

        methods = dict(
            tags = self._getTags(remote, prefix = prefix),
            extensions = self._getExtensions(
                remote, name, source = source, destination = destination,
                version = version, formatter = lambda : None
            )
        )

        return methods[mode] # return the underlying assets


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
        self, remote : str, name : str, source : Optional[str],
        destination : Optional[str], version : Optional[str],
        formatter : Optional[Callable] = lambda : None
    ) -> None:
        """
        Get the underlying assets from the "source" directory and
        flush the content to the "destination" directory. In addition,
        if any additional parsing is required by the LLM tool then
        the content should be processed accordingly.
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
                remote_url, verify = False,
                headers = self.headers, timeout = timeout
            )
            response.raise_for_status()

            for item in response.json():
                if prefix and item["name"].starswith(prefix):
                    tags.append(item["name"])
                else:
                    tags.append(item["name"])

            remote_url = response.links.get("next", {}).get("url")
        
        return tags


    def _getExtensions(
        self, remote: str, name : str, source: Optional[str],
        destination: Optional[str], version : Optional[str],
        formatter: Optional[Callable] = lambda : None
    ) -> None:
        """
        Flush the content of the extensions from the source directory
        to the destination directory.
        """

        owner, repository = self.getSlug(remote = remote)
        uri = (
            "https://api.github.com/repos/"
            "{owner}/{repository}/tarball/{tag}"
        ).format(owner = owner, repository = repository, tag = version)

        # co-locate the staging directory with the target, so the
        # final swap-in and atomic same file system rename can be done
        # while flushing the data to destination directory. This would
        # let shutil.move degrade to copy+delte when /tmp is on a
        # different mount, breaking the all-or-nothing promise
        
        return None
