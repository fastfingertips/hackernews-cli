import curses
import unittest
from unittest.mock import patch

from hackernews_cli.ui.pages.help import show_help
from hackernews_cli.ui.tabs import TabSwitch


class RecordingScreen:
    def __init__(self, keys):
        self.keys = iter(keys)
        self.writes = []
        self.timeouts = []

    def erase(self):
        pass

    def getmaxyx(self):
        return 30, 120

    def addstr(self, y, x, text, attr=0):
        self.writes.append((y, x, text, attr))

    def refresh(self):
        pass

    def timeout(self, value):
        self.timeouts.append(value)

    def getch(self):
        return next(self.keys)


class HelpPageTests(unittest.TestCase):
    @patch(
        "hackernews_cli.ui.components.footer.curses.has_colors",
        return_value=False,
    )
    @patch(
        "hackernews_cli.ui.components.header.curses.has_colors",
        return_value=False,
    )
    def test_unrelated_key_does_not_close_help(
            self,
            _header_colors,
            _footer_colors):
        screen = RecordingScreen((ord("x"), curses.KEY_LEFT))

        result = show_help(screen)

        self.assertEqual(result, TabSwitch("about"))
        self.assertEqual(screen.timeouts, [-1, 100])
        rendered = "".join(write[2] for write in screen.writes)
        self.assertGreaterEqual(rendered.count("Keyboard shortcuts"), 2)

    @patch(
        "hackernews_cli.ui.components.footer.curses.has_colors",
        return_value=False,
    )
    @patch(
        "hackernews_cli.ui.components.header.curses.has_colors",
        return_value=False,
    )
    def test_question_mark_closes_help(
            self,
            _header_colors,
            _footer_colors):
        screen = RecordingScreen((ord("?"),))

        self.assertIsNone(show_help(screen))


if __name__ == "__main__":
    unittest.main()
