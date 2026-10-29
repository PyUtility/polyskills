# -*- encoding: utf-8 -*-

"""
Tests of the Comparison and the Merge of Tags (``tags.py``)
"""

import contextlib
import io
import unittest

from tags import diff, differences, merge, show


def _tag(
    name : str, color : str = "#000000", **style : object
) -> dict:
    """
    Build a tag with the default style of Better Comments.

    :type  name: str
    :param name: The tag string.

    :type  color: str
    :param color: The color of the tag.

    :rtype:   dict
    :returns: The tag.
    """

    return {"tag" : name, "color" : color, "bold" : False, **style}


class TestDiff(unittest.TestCase):
    """
    :func:`tags.diff` sorts every tag into exactly one group.
    """

    def test_groups(self) -> None:
        local  = [_tag("a"), _tag("b", "#111111"), _tag("c")]
        remote = [_tag("b", "#222222"), _tag("c"), _tag("d")]

        change = diff(local, remote)
        self.assertEqual(change.local_only, ("a",))
        self.assertEqual(change.remote_only, ("d",))
        self.assertEqual(change.conflicts, ("b",))
        self.assertEqual(change.same, ("c",))


    def test_duplicate_uses_last_and_warns(self) -> None:
        local  = [_tag("a", "#111111"), _tag("a", "#222222")]
        remote = [_tag("a", "#222222")]

        errors = io.StringIO()
        with contextlib.redirect_stderr(errors):
            change = diff(local, remote)

        self.assertEqual(change.same, ("a",))
        self.assertIn("more than once", errors.getvalue())


class TestMerge(unittest.TestCase):
    """
    :func:`tags.merge` adds the new tags, keeps the local-only ones,
    and replaces the conflicting ones only with ``overwrite``.
    """

    def setUp(self) -> None:
        self.local  = [_tag("mine"), _tag("both", "#111111")]
        self.remote = [_tag("both", "#222222"), _tag("new")]


    def test_without_overwrite(self) -> None:
        merged = merge(self.local, self.remote, overwrite = False)
        self.assertEqual(
            merged,
            [_tag("mine"), _tag("both", "#111111"), _tag("new")],
        )


    def test_with_overwrite(self) -> None:
        merged = merge(self.local, self.remote, overwrite = True)
        self.assertEqual(
            merged,
            [_tag("mine"), _tag("both", "#222222"), _tag("new")],
        )


    def test_returns_copies(self) -> None:
        merged = merge(self.local, self.remote, overwrite = True)
        merged[1]["color"] = "#FFFFFF"
        merged[2]["color"] = "#FFFFFF"

        self.assertEqual(self.remote[0]["color"], "#222222")
        self.assertEqual(self.remote[1]["color"], "#000000")


class TestDifferences(unittest.TestCase):
    """
    :func:`tags.differences` lists every property that differs, and
    :func:`tags.show` formats the values.
    """

    def test_changed_and_missing(self) -> None:
        old = _tag("a", "#111111")
        new = _tag("a", "#222222", italic = True)
        del new["bold"]

        self.assertEqual(
            differences(old, new),
            [
                ("color", "#111111", "#222222"),
                ("bold", False, None),
                ("italic", None, True),
            ],
        )


    def test_show(self) -> None:
        self.assertEqual(show(None), "unset")
        self.assertEqual(show(True), "true")
        self.assertEqual(show("#FF2D00"), '"#FF2D00"')


if __name__ == "__main__":
    unittest.main()
