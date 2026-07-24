import unittest
from unittest.mock import patch

from hackernews_cli.ui.components.about_panel import (
    REPOSITORY_URL,
    draw_about,
)
from hackernews_cli.ui.components.frame import PageFrame
from hackernews_cli.ui.pages.about import show_about


class RecordingScreen:
    def __init__(self, keys=()):
        self.keys = iter(keys)
        self.writes = []

    def erase(self):
        pass

    def getmaxyx(self):
        return 20, 120

    def addstr(self, y, x, text, attr=0):
        self.writes.append((y, x, text, attr))

    def refresh(self):
        pass

    def timeout(self, _value):
        pass

    def getch(self):
        return next(self.keys)


class AboutTests(unittest.TestCase):
    @patch(
        "hackernews_cli.ui.components.footer.curses.has_colors",
        return_value=False,
    )
    @patch(
        "hackernews_cli.ui.components.header.curses.has_colors",
        return_value=False,
    )
    def test_about_panel_shows_identity_version_and_repository(
            self,
            _header_colors,
            _footer_colors):
        screen = RecordingScreen()

        draw_about(screen, PageFrame.from_screen(screen))

        rendered = "".join(write[2] for write in screen.writes)
        self.assertIn("HackerNews CLI", rendered)
        self.assertIn("1.0.0", rendered)
        self.assertIn("Local SQLite", rendered)
        self.assertIn(REPOSITORY_URL, rendered)
        self.assertNotIn("Inspiration", rendered)

    @patch("hackernews_cli.ui.pages.about.webbrowser.open")
    @patch(
        "hackernews_cli.ui.components.footer.curses.has_colors",
        return_value=False,
    )
    @patch(
        "hackernews_cli.ui.components.header.curses.has_colors",
        return_value=False,
    )
    def test_about_page_can_open_repository(
            self,
            _header_colors,
            _footer_colors,
            open_browser):
        screen = RecordingScreen((ord("g"), ord("q")))

        show_about(screen)

        open_browser.assert_called_once_with(REPOSITORY_URL)


if __name__ == "__main__":
    unittest.main()
