# -*- encoding: utf-8 -*-

"""
Read and Write the Better Comments Tags of a VS Code Settings File

VS Code keeps its settings in a JSON with comments (JSONC) file, so
the module never rewrites the whole file: it locates the value of the
``better-comments.tags`` key in the original text and splices only
that value, which keeps every comment, every other setting, the byte
order mark, and the line endings as they are. The key is added after
the last setting when it is missing.

The settings template of the repository is plain JSON, so the same
:class:`Settings` class reads it and renders the template that
``push.py`` proposes.

:NOTE: A comment inside the old ``better-comments.tags`` value is
    lost when the value is replaced, as the whole value is rendered
    again.
"""

import codecs
import collections
import contextlib
import copy
import json
import os
import pathlib
import re
import shutil
import sys
import tempfile

from typing import Optional

from errors import SettingsError, warn

TAGS_KEY = "better-comments.tags"

_DECODER  = json.JSONDecoder(strict = False)
_SPACE    = re.compile(r"[ \t\r\n]*")
_STRING   = r'"(?:\\.|[^"\\])*"'
_COMMENT  = re.compile(_STRING + r"|//[^\r\n]*|/\*.*?\*/", re.DOTALL)
_TRAILING = re.compile(_STRING + r"|,(?=[ \t\r\n]*[\]}])", re.DOTALL)

_Member = collections.namedtuple(
    "_Member", ["key", "key_start", "start", "end", "value"]
)


def settings_path(workspace : bool = False) -> pathlib.Path:
    """
    Return the path of the VS Code user settings of the platform, or
    of the workspace settings in the current directory.

    Insiders, VSCodium, Flatpak, and portable installs keep their
    settings elsewhere - pass that path with ``--settings``.

    :type  workspace: bool
    :param workspace: Return ``.vscode/settings.json`` of the current
        directory in place of the user settings.

    :rtype:   pathlib.Path
    :returns: The path of the settings file, which may not exist.
    """

    if workspace:
        return pathlib.Path.cwd() / ".vscode" / "settings.json"

    home = pathlib.Path.home()
    if sys.platform == "win32":
        roaming = home / "AppData" / "Roaming"
        root    = os.environ.get("APPDATA") or roaming
    elif sys.platform == "darwin":
        root = home / "Library" / "Application Support"
    else:
        xdg  = os.environ.get("XDG_CONFIG_HOME", "")
        root = xdg if os.path.isabs(xdg) else home / ".config"

    return pathlib.Path(root) / "Code" / "User" / "settings.json"


def _blank(match : re.Match) -> str:
    """
    Keep a JSON string as it is, and replace a comment or a trailing
    comma with spaces of the same length (line breaks are kept), so
    every offset of the blanked text points into the original text.

    :type  match: re.Match
    :param match: A string, comment, or trailing comma.

    :rtype:   str
    :returns: The string, or the blanked comment or comma.
    """

    token = match.group(0)
    if token.startswith('"'):
        return token

    return re.sub(r"[^\r\n]", " ", token)


class Settings:
    """
    The text of a VS Code settings file, or of the settings template,
    with the location of its ``better-comments.tags`` value. The text
    is parsed once; :meth:`render` returns the text with new tags,
    and :meth:`save` writes it back to the file it was loaded from.

    :type  text: str
    :param text: The text of the file, without a byte order mark. An
        empty text, or one with only comments, is an empty object.

    :type  source: str
    :param source: The name of the file in the messages, usually its
        path.

    :raises SettingsError: When the text is not a JSON object, or the
        ``better-comments.tags`` value is not a list of tags.
    """

    def __init__(self, text : str, source : str) -> None:
        self.source = source

        self.path : Optional[pathlib.Path] = None
        self.bom  = False

        self._load(text)
        count = sum(cur.key == TAGS_KEY for cur in self._members)
        if count > 1:
            warn(f"{source}: '{TAGS_KEY}' is set {count} times"
                 " - the last one is used")


    @classmethod
    def load(cls, path : pathlib.Path) -> "Settings":
        """
        Read the settings file at ``path``. A missing file reads as an
        empty object, and is created by :meth:`save`, when its folder
        exists.

        :type  path: pathlib.Path
        :param path: The path of the settings file.

        :raises SettingsError: When the folder of the file is missing,
            or the file cannot be read, is not UTF-8, or is invalid.

        :rtype:   Settings
        :returns: The parsed settings, bound to ``path``.
        """

        if path.exists():
            try:
                data = path.read_bytes()
            except OSError as error:
                raise SettingsError(
                    f"cannot read {path}: {error.strerror}"
                ) from None
        elif path.parent.is_dir():
            data = b""
        else:
            raise SettingsError(
                f"VS Code settings not found: {path} - pass the"
                " settings file with --settings"
            )

        try:
            text = data.decode("utf-8-sig")
        except UnicodeDecodeError:
            raise SettingsError(f"{path} is not UTF-8 text") from None

        settings = cls(text, str(path))
        settings.path = path
        settings.bom  = data.startswith(codecs.BOM_UTF8)
        return settings


    @property
    def has_tags(self) -> bool:
        """
        Whether the settings have a ``better-comments.tags`` value.

        :rtype:   bool
        :returns: ``True`` when the key is present.
        """

        return self._tags is not None


    @property
    def tags(self) -> list[dict]:
        """
        A copy of the ``better-comments.tags`` value.

        :rtype:   list[dict]
        :returns: The tags, or an empty list when the key is missing.
        """

        return copy.deepcopy(self._tags.value) if self._tags else []


    @property
    def backup(self) -> pathlib.Path:
        """
        The path of the copy that :meth:`save` keeps of the previous
        file, next to the real file when the path is a symbolic link.

        :rtype:   pathlib.Path
        :returns: The path of ``<settings file>.bak``.
        """

        target = self.path.resolve()
        return target.with_name(target.name + ".bak")


    def render(self, tags : list[dict]) -> str:
        """
        Return the text with ``tags`` as the ``better-comments.tags``
        value. Only that value changes - every other character of the
        text is kept. The key is added after the last setting when it
        is missing.

        :type  tags: list[dict]
        :param tags: The new tags.

        :rtype:   str
        :returns: The new text of the file.
        """

        if self._tags is None:
            return self._insert(tags)

        member = self._tags
        indent = self._indent(member.key_start)
        if indent is None:
            indent = self._unit()

        text, value = self.text, self._dump(tags, indent)
        return text[:member.start] + value + text[member.end:]


    def save(self, tags : list[dict]) -> bool:
        """
        Write the text with ``tags`` to the file it was loaded from.
        The previous file is copied to :attr:`backup`, and the new
        text is written to a temporary file that replaces the old one,
        so an interrupted write never leaves half a file.

        :type  tags: list[dict]
        :param tags: The new tags.

        :raises SettingsError: When the file is read-only or cannot be
            written.

        :rtype:   bool
        :returns: ``True`` when the file was written, ``False`` when
            it already had these tags.
        """

        text = self.render(tags)
        if text == self.text and self.path.exists():
            return False

        target = self.path.resolve()
        if target.exists() and not os.access(target, os.W_OK):
            raise SettingsError(f"{target} is read-only")

        data = text.encode("utf-8")
        if self.bom:
            data = codecs.BOM_UTF8 + data

        temp = None
        try:
            if target.exists():
                shutil.copy2(target, self.backup)

            handle, temp = tempfile.mkstemp(
                prefix = f".{target.name}.", dir = target.parent
            )
            with os.fdopen(handle, "wb") as stream:
                stream.write(data)

            if target.exists():
                shutil.copymode(target, temp)
            os.replace(temp, target)
        except OSError as error:
            if temp is not None:
                with contextlib.suppress(OSError):
                    os.remove(temp)
            raise SettingsError(
                f"cannot write {target}: {error.strerror}"
            ) from None

        self._load(text)
        return True


    @property
    def _newline(self) -> str:
        """
        The line break that most lines of the text end with.

        :rtype:   str
        :returns: ``"\\r\\n"`` or ``"\\n"``.
        """

        crlf = self.text.count("\r\n")
        return "\r\n" if crlf * 2 > self.text.count("\n") else "\n"


    def _load(self, text : str) -> None:
        """
        Parse ``text`` as the text of the settings, and locate its
        members and its ``better-comments.tags`` value.

        :type  text: str
        :param text: The text of the settings.

        :raises SettingsError: When the text is not a JSON object, or
            the ``better-comments.tags`` value is not a list of tags.
        """

        self.text = text
        self._uncommented = _COMMENT.sub(_blank, text)
        self._code = _TRAILING.sub(_blank, self._uncommented)

        self._open  : Optional[int] = None
        self._close : Optional[int] = None

        self._members = self._parse()
        self._tags    = self._find()


    def _parse(self) -> list[_Member]:
        """
        Parse the top-level members of the blanked text, and record
        the offsets of the braces of the root object.

        :raises SettingsError: When the text is not a JSON object.

        :rtype:   list[_Member]
        :returns: The members, in the order of the text.
        """

        code, members = self._code, []

        idx = self._skip(0)
        if idx == len(code):
            return members

        if code[idx] != "{":
            raise self._error("the root is not a JSON object", idx)

        self._open = idx
        idx = self._skip(idx + 1)
        while not code.startswith("}", idx):
            if not code.startswith('"', idx):
                raise self._error("expected a property name", idx)

            key_start = idx
            key, idx  = self._decode(key_start)
            idx = self._skip(idx)
            if not code.startswith(":", idx):
                raise self._error("expected ':'", idx)

            start = self._skip(idx + 1)
            value, end = self._decode(start)
            members.append(_Member(key, key_start, start, end, value))

            idx = self._skip(end)
            if code.startswith(",", idx):
                idx = self._skip(idx + 1)
            elif not code.startswith("}", idx):
                raise self._error("expected ',' or '}'", idx)

        self._close = idx
        if self._skip(idx + 1) != len(code):
            raise self._error("text after the root object", idx)

        return members


    def _find(self) -> Optional[_Member]:
        """
        Find the ``better-comments.tags`` member and check its value.
        VS Code uses the last of duplicate keys, and so does the hook.

        :raises SettingsError: When the value is not a list of tags.

        :rtype:   Optional[_Member]
        :returns: The member, or ``None`` when the key is missing.
        """

        found = [cur for cur in self._members if cur.key == TAGS_KEY]
        if not found:
            return None

        member = found[-1]
        if not isinstance(member.value, list):
            message = f"'{TAGS_KEY}' is not a list"
            raise self._error(message, member.start)

        for idx, tag in enumerate(member.value, start = 1):
            name = tag.get("tag") if isinstance(tag, dict) else None
            if not isinstance(name, str):
                message = f"entry {idx} of '{TAGS_KEY}' has no 'tag'"
                raise self._error(message, member.start)

        return member


    def _insert(self, tags : list[dict]) -> str:
        """
        Return the text with a new ``better-comments.tags`` member
        after the last member. A comma is added after the last value
        when there is none, and comments stay where they are.

        :type  tags: list[dict]
        :param tags: The new tags.

        :rtype:   str
        :returns: The new text of the file.
        """

        text, newline, unit = self.text, self._newline, self._unit()
        member = json.dumps(TAGS_KEY) + ": " + self._dump(tags, unit)

        if self._open is None:
            if text and not text.endswith(("\n", "\r")):
                text += newline
            lines = ["{", unit + member, "}", ""]
            return text + newline.join(lines)

        close = self._close
        start = self._line_start(close)
        if text[start:close].strip(" \t"):
            start, member = close, newline + unit + member + newline
        else:
            member = unit + member + newline

        end, comma = start, ""
        if self._members:
            end = self._members[-1].end
            if "," not in self._uncommented[end:close]:
                comma = ","

        parts = [text[:end], comma, text[end:start], member]
        return "".join(parts) + text[start:]


    def _dump(self, tags : list[dict], indent : str) -> str:
        """
        Render ``tags`` as indented JSON whose continuation lines
        start with ``indent``, in the line break of the text.

        :type  tags: list[dict]
        :param tags: The tags to render.

        :type  indent: str
        :param indent: The indentation of the line of the key.

        :rtype:   str
        :returns: The JSON text of the value.
        """

        value = json.dumps(
            tags, indent = self._unit(), ensure_ascii = False
        )
        return value.replace("\n", self._newline + indent)


    def _unit(self) -> str:
        """
        The indentation of one level, taken from the first top-level
        member that starts its own line, or four spaces.

        :rtype:   str
        :returns: The indentation unit of the text.
        """

        for member in self._members:
            indent = self._indent(member.key_start)
            if indent:
                return indent

        return "    "


    def _indent(self, offset : int) -> Optional[str]:
        """
        Return the white space before ``offset`` on its line.

        :type  offset: int
        :param offset: An offset in the text.

        :rtype:   Optional[str]
        :returns: The indentation, or ``None`` when other text comes
            before ``offset`` on its line.
        """

        prefix = self.text[self._line_start(offset):offset]
        return None if prefix.strip(" \t") else prefix


    def _line_start(self, offset : int) -> int:
        """
        Return the offset of the start of the line of ``offset``.

        :type  offset: int
        :param offset: An offset in the text.

        :rtype:   int
        :returns: The offset just after the previous line break.
        """

        text = self.text[:offset]
        return max(text.rfind("\n"), text.rfind("\r")) + 1


    def _skip(self, offset : int) -> int:
        """
        Return the offset of the first character after the white space
        (and the blanked comments) at ``offset``.

        :type  offset: int
        :param offset: An offset in the text.

        :rtype:   int
        :returns: The offset of the next character that is not blank.
        """

        return _SPACE.match(self._code, offset).end()


    def _decode(self, offset : int) -> tuple[object, int]:
        """
        Decode the JSON value at ``offset`` of the blanked text.

        :type  offset: int
        :param offset: The offset of the first character of the value.

        :raises SettingsError: When the text is not valid JSON.

        :rtype:   tuple[object, int]
        :returns: The value and the offset just after it.
        """

        try:
            return _DECODER.raw_decode(self._code, offset)
        except json.JSONDecodeError as error:
            raise self._error(error.msg, error.pos) from None


    def _error(self, message : str, offset : int) -> SettingsError:
        """
        Build the error for ``message`` at ``offset``, with the line
        and the column in the original text.

        :type  message: str
        :param message: What is wrong.

        :type  offset: int
        :param offset: Where it is wrong.

        :rtype:   SettingsError
        :returns: The error, ready to raise.
        """

        line   = self.text.count("\n", 0, offset) + 1
        column = offset - self.text.rfind("\n", 0, offset)
        return SettingsError(
            f"{self.source}: {message} (line {line}, column {column})"
        )
