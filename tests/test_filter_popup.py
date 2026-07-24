import unittest
from unittest.mock import patch

from hackernews_cli.ui.terminal.prompts import (
    show_feed_filter,
    show_filter_popup,
)


class FakeScreen:
    def getmaxyx(self):
        return 24, 100

    def touchwin(self):
        pass

    def refresh(self):
        pass


class FakeWindow:
    def __init__(self, keys):
        self.keys = iter(keys)
        self.writes = []

    def keypad(self, _enabled):
        pass

    def bkgd(self, *_args):
        pass

    def timeout(self, _value):
        pass

    def erase(self):
        pass

    def box(self):
        pass

    def addstr(self, *_args):
        self.writes.append(_args)

    def refresh(self):
        pass

    def move(self, *_args):
        pass

    def getch(self):
        return next(self.keys)


class FilterPopupTests(unittest.TestCase):
    @patch("hackernews_cli.ui.terminal.text_input.curses.noecho")
    @patch("hackernews_cli.ui.terminal.text_input.curses.curs_set")
    @patch("hackernews_cli.ui.terminal.text_input.curses.has_colors", return_value=False)
    def test_enter_applies_edited_filter(self, _colors, _cursor, _noecho):
        window = FakeWindow([ord("x"), 10])
        with patch("hackernews_cli.ui.terminal.text_input.curses.newwin", return_value=window):
            result = show_filter_popup(
                FakeScreen(),
                "Filter",
                ("Description",),
                "old",
            )
        self.assertEqual(result, "oldx")

    @patch("hackernews_cli.ui.terminal.text_input.curses.noecho")
    @patch("hackernews_cli.ui.terminal.text_input.curses.curs_set")
    @patch("hackernews_cli.ui.terminal.text_input.curses.has_colors", return_value=False)
    def test_escape_keeps_original_filter(self, _colors, _cursor, _noecho):
        window = FakeWindow([8, 27])
        with patch("hackernews_cli.ui.terminal.text_input.curses.newwin", return_value=window):
            result = show_filter_popup(
                FakeScreen(),
                "Filter",
                ("Description",),
                "old",
            )
        self.assertEqual(result, "old")

    @patch("hackernews_cli.ui.terminal.text_input.curses.noecho")
    @patch("hackernews_cli.ui.terminal.text_input.curses.curs_set")
    @patch("hackernews_cli.ui.terminal.text_input.curses.has_colors", return_value=False)
    def test_feed_popup_explains_fields_states_and_negation(
            self,
            _colors,
            _cursor,
            _noecho):
        window = FakeWindow([10])
        with patch(
                "hackernews_cli.ui.terminal.text_input.curses.newwin",
                return_value=window):
            show_feed_filter(FakeScreen())

        rendered = " ".join(
            str(argument)
            for write in window.writes
            for argument in write
        )
        self.assertIn("title:", rendered)
        self.assertIn("points:>=100", rendered)
        self.assertIn("is:unread", rendered)
        self.assertIn("- to exclude", rendered)


if __name__ == "__main__":
    unittest.main()
