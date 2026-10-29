# -*- encoding: utf-8 -*-

"""
Tests of the VS Code Settings Reader and Writer (``vscode.py``)
"""

import codecs
import json
import os
import pathlib
import unittest

from unittest import mock

from errors import SettingsError
from tests.base import TEMPLATE, HookTestCase, template_tags
from vscode import TAGS_KEY, Settings, settings_path

TAGS = [{"tag" : "x", "color" : "#123456"}]

SETTINGS = """{
    // the editor
    "editor.tabSize": 4, /* four */
    "url": "http://example.com // not a comment",
    "[python]": {"better-comments.tags": []},
    "better-comments.tags": [
        {"tag": "!", "color": "#FF2D00",},  // trailing comma
    ],
    "files.eol": "\\n",
}
"""


def _tags(text : str) -> list[dict]:
    """
    Read the tags of rendered settings through a fresh reader, which
    also proves that the rendered text is valid JSONC.

    :type  text: str
    :param text: The settings text.

    :rtype:   list[dict]
    :returns: The ``better-comments.tags`` value.
    """

    return Settings(text, "test").tags


class TestRead(unittest.TestCase):
    """
    The reader finds only the top-level ``better-comments.tags``,
    through comments, trailing commas, and comment-like strings.
    """

    def test_jsonc(self) -> None:
        settings = Settings(SETTINGS, "test")
        self.assertTrue(settings.has_tags)
        self.assertEqual(
            settings.tags, [{"tag" : "!", "color" : "#FF2D00"}]
        )


    def test_nested_key_is_not_matched(self) -> None:
        text = '{"[python]": {"better-comments.tags": []}}'
        self.assertFalse(Settings(text, "test").has_tags)


    def test_empty_and_comment_only(self) -> None:
        for text in ("", "  \n", "// only a comment\n"):
            settings = Settings(text, "test")
            self.assertFalse(settings.has_tags)
            self.assertEqual(settings.tags, [])


    def test_invalid(self) -> None:
        for text in (
            "[]",
            '{"a": 1} x',
            '{"a" 1}',
            '{"better-comments.tags": {}}',
            '{"better-comments.tags": [{"color": "#000000"}]}',
            '{"better-comments.tags": [1]}',
            '{"a": "unterminated}',
            '{"a": 1 /* unterminated }',
        ):
            with self.subTest(text = text):
                with self.assertRaises(SettingsError):
                    Settings(text, "test")


    def test_error_points_to_line(self) -> None:
        with self.assertRaises(SettingsError) as context:
            Settings('{\n  // c\n  "a": x\n}', "test")
        self.assertIn("line 3", str(context.exception))


class TestRender(unittest.TestCase):
    """
    Rendering replaces only the tags value, or inserts the key, and
    keeps every other character of the text.
    """

    def test_template_round_trip(self) -> None:
        text = TEMPLATE.read_text(encoding = "utf-8")
        settings = Settings(text, "template")
        self.assertEqual(settings.render(settings.tags), text)


    def test_replace_keeps_the_rest(self) -> None:
        settings = Settings(SETTINGS, "test")
        text = settings.render(TAGS)

        self.assertEqual(_tags(text), TAGS)
        for kept in (
            "// the editor", "/* four */", "// not a comment",
            '"[python]": {"better-comments.tags": []}',
            '"files.eol": "\\n",\n}',
        ):
            self.assertIn(kept, text)
        self.assertNotIn("trailing comma", text)


    def test_insert(self) -> None:
        key   = '"better-comments.tags": ['
        cases = [
            ("", "{\n    " + key),
            ("{}", "{\n    " + key),
            ("{\n}\n", "{\n    " + key),
            ('{"a": 1}', '{"a": 1,\n    ' + key),
            (
                '{\n\t"a": 1 // one\n}',
                '{\n\t"a": 1, // one\n\t' + key,
            ),
            (
                '{\n  "a": 1,\n  // last\n}',
                '{\n  "a": 1,\n  // last\n  ' + key,
            ),
        ]
        for before, start in cases:
            with self.subTest(text = before):
                text = Settings(before, "test").render(TAGS)
                self.assertTrue(text.startswith(start), text)
                self.assertEqual(_tags(text), TAGS)


    def test_insert_after_comment_only_text(self) -> None:
        text = Settings("// note", "test").render(TAGS)
        self.assertTrue(text.startswith("// note\n{\n"))
        self.assertEqual(_tags(text), TAGS)


    def test_crlf_is_kept(self) -> None:
        before = '{\r\n    "a": 1\r\n}\r\n'
        text = Settings(before, "test").render(TAGS)

        self.assertNotIn("\n", text.replace("\r\n", ""))
        self.assertEqual(_tags(text), TAGS)


class TestFile(HookTestCase):
    """
    Loading and saving a settings file, with its backup.
    """

    def test_missing_file(self) -> None:
        settings = Settings.load(self.settings)
        self.assertEqual(settings.tags, [])

        self.assertTrue(settings.save(TAGS))
        self.assertEqual(Settings.load(self.settings).tags, TAGS)
        self.assertFalse(settings.backup.exists())


    def test_save_twice(self) -> None:
        self.settings.write_text('{"a": 1}', encoding = "utf-8")
        settings = Settings.load(self.settings)

        self.assertTrue(settings.save(TAGS))
        self.assertTrue(settings.has_tags)
        self.assertEqual(settings.tags, TAGS)

        other = [{"tag" : "y", "color" : "#654321"}]
        self.assertTrue(settings.save(other))
        self.assertFalse(settings.save(other))
        self.assertEqual(Settings.load(self.settings).tags, other)


    def test_missing_folder(self) -> None:
        path = self.temp / "missing" / "settings.json"
        with self.assertRaises(SettingsError):
            Settings.load(path)


    def test_save_keeps_bom_and_backup(self) -> None:
        data = codecs.BOM_UTF8 + b'{\n    "a": 1\n}\n'
        self.settings.write_bytes(data)

        settings = Settings.load(self.settings)
        self.assertTrue(settings.save(TAGS))

        self.assertTrue(self.settings.read_bytes().startswith(
            codecs.BOM_UTF8
        ))
        self.assertEqual(settings.backup.read_bytes(), data)


    def test_no_write_without_change(self) -> None:
        tags = template_tags()
        self.settings.write_text(
            json.dumps({TAGS_KEY : tags}, indent = 4),
            encoding = "utf-8",
        )

        settings = Settings.load(self.settings)
        self.assertFalse(settings.save(tags))
        self.assertFalse(settings.backup.exists())


    def test_not_utf8(self) -> None:
        self.settings.write_bytes(b'{"a": "\xff"}')
        with self.assertRaises(SettingsError):
            Settings.load(self.settings)


class TestSettingsPath(unittest.TestCase):
    """
    :func:`vscode.settings_path` follows the platform conventions.
    """

    def test_windows(self) -> None:
        with mock.patch("sys.platform", "win32"), \
                mock.patch.dict(os.environ, {"APPDATA" : "C:\\AD"}):
            path = settings_path()
        self.assertEqual(
            path, pathlib.Path("C:\\AD") / "Code" / "User"
            / "settings.json"
        )


    def test_macos(self) -> None:
        with mock.patch("sys.platform", "darwin"):
            path = settings_path()
        self.assertEqual(
            path.parts[-5:],
            ("Library", "Application Support", "Code", "User",
             "settings.json"),
        )


    def test_linux_relative_xdg_is_ignored(self) -> None:
        env = {"XDG_CONFIG_HOME" : "relative"}
        with mock.patch("sys.platform", "linux"), \
                mock.patch.dict(os.environ, env):
            path = settings_path()
        self.assertEqual(path.parts[-4], ".config")


    def test_workspace(self) -> None:
        self.assertEqual(
            settings_path(workspace = True),
            pathlib.Path.cwd() / ".vscode" / "settings.json",
        )


if __name__ == "__main__":
    unittest.main()
