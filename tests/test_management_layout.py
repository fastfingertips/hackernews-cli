import curses
import unittest
from unittest.mock import patch

from hackernews_cli.data import FavoriteEntry, HistoryActivityStats, HistoryEntry
from hackernews_cli.ui.components.favorites_table import draw_favorites
from hackernews_cli.ui.components.history_table import draw_history


class RecordingScreen:
    def __init__(self):
        self.writes = []

    def erase(self):
        pass

    def getmaxyx(self):
        return 20, 100

    def addstr(self, y, x, text, attr=0):
        self.writes.append((y, x, text, attr))

    def refresh(self):
        pass


class ManagementLayoutTests(unittest.TestCase):
    @patch("hackernews_cli.ui.components.favorites_table.curses.color_pair", side_effect=lambda pair: pair * 100)
    @patch("hackernews_cli.ui.components.favorites_table.curses.has_colors", return_value=True)
    def test_selected_favorite_row_is_yellow_pair(self, _colors, _color_pair):
        screen = RecordingScreen()
        entry = FavoriteEntry(
            "https://example.com/story",
            "Story",
            "2026-07-22T12:00:00+00:00",
        )

        draw_favorites(screen, [entry], 0, "", "", 1)

        selected_row = next(write for write in screen.writes if write[0] == 4)
        self.assertEqual(selected_row[3], 100 | curses.A_BOLD)

    @patch("hackernews_cli.ui.components.history_table.curses.has_colors", return_value=False)
    def test_history_header_shows_event_unique_and_read_stats(self, _colors):
        screen = RecordingScreen()
        entries = [
            HistoryEntry(
                1,
                "https://example.com/story",
                "Story",
                "article",
                "2026-07-22T12:00:00+00:00",
            ),
            HistoryEntry(
                2,
                "https://example.com/story",
                "Story",
                "comments",
                "2026-07-22T12:05:00+00:00",
            ),
        ]

        draw_history(
            screen,
            entries,
            0,
            "",
            "",
            2,
            {entries[0].url},
            {entries[0].url},
            HistoryActivityStats(1, 2, 3, 4),
        )

        rendered = "".join(write[2] for write in screen.writes)
        self.assertIn("events 2", rendered)
        self.assertIn("unique 1", rendered)
        self.assertIn("read 1", rendered)
        self.assertIn("1h 1", rendered)
        self.assertIn("today 2", rendered)
        self.assertIn("week 3", rendered)
        self.assertIn("year 4", rendered)
        self.assertIn("Time (local)", rendered)
        self.assertIn("2026-07-22 ", rendered)
        self.assertIn("ago)", rendered)


if __name__ == "__main__":
    unittest.main()
