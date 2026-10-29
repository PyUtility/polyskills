# -*- encoding: utf-8 -*-

"""
Compare and Merge Lists of Better Comments Tags

A Better Comments tag is a JSON object identified by its ``tag``
string, with the style properties ``color``, ``strikethrough``,
``underline``, ``backgroundColor``, ``bold``, and ``italic``. Two
lists of tags are compared tag by tag: a tag is in sync when every
property is equal, and in conflict when any property differs.

:NOTE: Tags are matched by the exact ``tag`` string, and properties
    by their exact value, so ``#ff2d00`` and ``#FF2D00`` conflict.
"""

import copy
import dataclasses
import json

from typing import Optional

from errors import warn


@dataclasses.dataclass(frozen = True)
class TagDiff:
    """
    The difference between a local and a remote list of tags, as tag
    names. Tags only in one list keep the order of that list, and the
    conflicting tags and the tags in sync keep the local order.

    :type  local_only: tuple[str, ...]
    :param local_only: The tags only in the local list.

    :type  remote_only: tuple[str, ...]
    :param remote_only: The tags only in the remote list.

    :type  conflicts: tuple[str, ...]
    :param conflicts: The tags in both lists with a different style.

    :type  same: tuple[str, ...]
    :param same: The tags in both lists with the same style.
    """

    local_only  : tuple[str, ...]
    remote_only : tuple[str, ...]
    conflicts   : tuple[str, ...]
    same        : tuple[str, ...]


def index(tags : list[dict], source : Optional[str] = None) -> dict:
    """
    Index ``tags`` by their ``tag`` string. Better Comments applies
    the last of duplicate tags, and so does the index.

    :type  tags: list[dict]
    :param tags: The tags to index.

    :type  source: Optional[str]
    :param source: The name of the list, to warn about duplicate tags
        in it, or ``None`` to skip the warning.

    :rtype:   dict
    :returns: The tags by name, in the order of their first use.
    """

    found = {}
    for tag in tags:
        name = tag["tag"]
        if name in found and source is not None:
            warn(f"the {source} have the tag '{name}' more than once"
                 " - the last one is used")
        found[name] = tag

    return found


def diff(local : list[dict], remote : list[dict]) -> TagDiff:
    """
    Compare a local and a remote list of tags.

    :type  local: list[dict]
    :param local: The tags of the VS Code settings.

    :type  remote: list[dict]
    :param remote: The tags of the remote settings template.

    :rtype:   TagDiff
    :returns: The tags only in one list, in conflict, and in sync.
    """

    mine   = index(local, "local settings")
    theirs = index(remote, "remote template")

    return TagDiff(
        local_only  = tuple(cur for cur in mine if cur not in theirs),
        remote_only = tuple(cur for cur in theirs if cur not in mine),
        conflicts   = tuple(
            cur for cur in mine
            if cur in theirs and mine[cur] != theirs[cur]
        ),
        same        = tuple(
            cur for cur in mine if theirs.get(cur) == mine[cur]
        ),
    )


def merge(
    base : list[dict], incoming : list[dict], overwrite : bool
) -> list[dict]:
    """
    Merge ``incoming`` into ``base``: the tags only in ``incoming``
    are appended in their order and, with ``overwrite``, the tags of
    ``base`` that differ take the value of ``incoming``. Every other
    tag of ``base`` is kept as it is, duplicates included.

    ``pull.py`` merges the remote tags into the local ones, and
    ``push.py`` the local tags into the remote ones.

    :type  base: list[dict]
    :param base: The tags to update.

    :type  incoming: list[dict]
    :param incoming: The tags to merge into ``base``.

    :type  overwrite: bool
    :param overwrite: Replace the tags of ``base`` that differ from
        ``incoming`` with the ``incoming`` value.

    :rtype:   list[dict]
    :returns: A new list - the input lists are never changed.
    """

    theirs = index(incoming)
    known  = {cur["tag"] for cur in base}

    merged = [
        theirs.get(cur["tag"], cur) if overwrite else cur
        for cur in base
    ]
    merged.extend(
        tag for name, tag in theirs.items() if name not in known
    )

    return copy.deepcopy(merged)


def differences(old : dict, new : dict) -> list[tuple]:
    """
    List the style properties that differ between two values of the
    same tag. A property missing from one value is ``None`` in it.

    :type  old: dict
    :param old: The first value of the tag.

    :type  new: dict
    :param new: The second value of the tag.

    :rtype:   list[tuple]
    :returns: A ``(property, old value, new value)`` tuple for each
        property that differs, in the order of ``old`` then ``new``.
    """

    keys = list(old) + [key for key in new if key not in old]
    return [
        (key, old.get(key), new.get(key))
        for key in keys if old.get(key) != new.get(key)
    ]


def show(value : object) -> str:
    """
    Format the value of a style property for a message.

    :type  value: object
    :param value: The value, or ``None`` when the property is missing.

    :rtype:   str
    :returns: The value as JSON, or ``unset`` for ``None``.
    """

    if value is None:
        return "unset"

    return json.dumps(value, ensure_ascii = False)
