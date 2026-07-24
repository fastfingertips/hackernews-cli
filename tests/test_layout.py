import curses
import unittest
from datetime import datetime, timedelta, timezone
from unittest.mock import Mock, patch

from hackernews_cli.hn import Article
from hackernews_cli.ui.components.article_list import display_article_list
from hackernews_cli.ui.components.footer import draw_feed_footer
from hackernews_cli.ui.components.frame import PageFrame, Region
from hackernews_cli.ui.components.header import draw_feed_header
from hackernews_cli.ui.pages.home import home_story_capacity
from hackernews_cli.ui.terminal.colors import VISITED_COLOR_PAIR
from hackernews_cli.ui.terminal.drawing import truncate_line


class RecordingWindow:
    def __init__(self):
        self.writes = []

    def addstr(self, y, x, text, attr=0):
        self.writes.append((y, x, text, attr))


class LayoutTests(unittest.TestCase):
    STATUS_DATE = (
        datetime.now(timezone.utc) - timedelta(hours=2)
    ).isoformat()

    @patch("hackernews_cli.ui.components.article_list.curses.has_colors", return_value=False)
    def test_story_uses_requested_column_order(self, _has_colors):
        window = RecordingWindow()
        article = Article(
            title="A useful story",
            link="https://example.com/story",
            rank="1.",
            domain="example.com",
            score="42 points",
            author="ada",
            age="2 hours ago",
            comments_count="12 comments",
            fetched_at=self.STATUS_DATE,
        )

        display_article_list(window, [article], 0, 2, 0, 120, 10)

        self.assertEqual(len(window.writes), 2)
        self.assertIn("Points", window.writes[0][2])
        self.assertLess(window.writes[0][2].index("Points"), window.writes[0][2].index("Link"))
        self.assertLess(window.writes[0][2].index("Link"), window.writes[0][2].index("Age"))
        self.assertLess(window.writes[0][2].index("Age"), window.writes[0][2].index("Fetched"))
        self.assertLess(window.writes[0][2].index("Fetched"), window.writes[0][2].index("Replies"))
        self.assertIn(">   1. 42", window.writes[1][2])
        self.assertIn("A useful story (example.com)", window.writes[1][2])
        self.assertIn("2 hours", window.writes[1][2])
        self.assertIn("2h ago", window.writes[1][2])

    @patch("hackernews_cli.ui.components.article_list.curses.has_colors", return_value=False)
    def test_story_without_fetch_timestamp_shows_unknown_value(self, _has_colors):
        window = RecordingWindow()

        display_article_list(
            window,
            [Article("Story", "https://example.com/story")],
            0,
            2,
            0,
            120,
            10,
        )

        fetched_start = window.writes[0][2].index("Fetched")
        fetched_value = window.writes[1][2][fetched_start:fetched_start + 10].strip()
        self.assertEqual(fetched_value, "-")

    @patch("hackernews_cli.ui.components.article_list.curses.has_colors", return_value=False)
    def test_loading_spinner_uses_last_content_row(self, _has_colors):
        window = RecordingWindow()

        display_article_list(
            window,
            [Article("Story", "https://example.com/story")],
            0,
            start_y=2,
            start_x=0,
            pane_width=120,
            pane_height=8,
            loading_frame=1,
        )

        loading_write = next(write for write in window.writes if "Loading" in write[2])
        self.assertEqual(loading_write[0], 9)
        self.assertIn("/ Loading next page...", loading_write[2])

    @patch("hackernews_cli.ui.components.article_list.curses.has_colors", return_value=False)
    def test_visited_story_uses_dedicated_column(self, _has_colors):
        window = RecordingWindow()
        article = Article("Read story", "https://example.com/read")

        display_article_list(
            window,
            [article],
            0,
            2,
            0,
            80,
            10,
            visited_dates={article.link: self.STATUS_DATE},
        )

        header = window.writes[0][2]
        row = window.writes[1][2]
        self.assertIn("Visited", header)
        self.assertNotIn("[visited]", row)
        self.assertIn("2h ago", row)

    @patch("hackernews_cli.ui.components.article_list.curses.has_colors", return_value=False)
    def test_read_story_uses_dedicated_column(self, _has_colors):
        window = RecordingWindow()
        article = Article("Read story", "https://example.com/read")

        display_article_list(
            window,
            [article],
            selected_index=0,
            start_y=2,
            start_x=0,
            pane_width=90,
            pane_height=10,
            read_dates={article.link: self.STATUS_DATE},
        )

        self.assertIn("Read", window.writes[0][2])
        self.assertTrue(window.writes[1][2].rstrip().endswith("2h ago"))

    @patch("hackernews_cli.ui.components.article_list.curses.has_colors", return_value=False)
    def test_favorite_story_uses_dedicated_column(self, _has_colors):
        window = RecordingWindow()
        article = Article("Favorite story", "https://example.com/favorite")

        display_article_list(
            window,
            [article],
            selected_index=0,
            start_y=2,
            start_x=0,
            pane_width=90,
            pane_height=10,
            favorite_dates={article.link: self.STATUS_DATE},
        )

        header = window.writes[0][2]
        row = window.writes[1][2]
        self.assertLess(header.index("Visited"), header.index("Fav"))
        self.assertLess(header.index("Fav"), header.index("Read"))
        self.assertNotIn("[fav]", row)
        self.assertIn("2h ago", row)

    @patch("hackernews_cli.ui.components.article_list.curses.has_colors", return_value=False)
    def test_read_later_story_uses_dedicated_column(self, _has_colors):
        window = RecordingWindow()
        article = Article("Later story", "https://example.com/later")

        display_article_list(
            window,
            [article],
            0,
            2,
            0,
            120,
            10,
            later_dates={article.link: self.STATUS_DATE},
        )

        self.assertIn("Later", window.writes[0][2])
        self.assertIn("2h ago", window.writes[1][2])

    @patch("hackernews_cli.ui.components.article_list.curses.color_pair", return_value=512)
    @patch("hackernews_cli.ui.components.article_list.curses.has_colors", return_value=True)
    def test_visited_story_uses_distinct_color(self, _has_colors, color_pair):
        window = RecordingWindow()
        article = Article("Read story", "https://example.com/read")

        display_article_list(
            window,
            [article],
            selected_index=-1,
            start_y=2,
            start_x=0,
            pane_width=80,
            pane_height=10,
            visited_dates={article.link: self.STATUS_DATE},
        )

        color_pair.assert_any_call(VISITED_COLOR_PAIR)
        self.assertEqual(window.writes[1][3], 512 | curses.A_DIM)

    @patch("hackernews_cli.ui.components.header.curses.has_colors", return_value=False)
    def test_header_has_plain_categories_without_tab_boxes(self, _has_colors):
        window = RecordingWindow()

        draw_feed_header(
            window,
            Region(0, 2, 120),
            1,
            10,
            "",
            "top",
        )

        rendered = "".join(write[2] for write in window.writes)
        self.assertIn("hn", rendered)
        self.assertIn("top", rendered)
        self.assertIn("favorites", rendered)
        self.assertIn("later", rendered)
        self.assertIn("history", rendered)
        self.assertIn("filters", rendered)
        self.assertIn("data", rendered)
        self.assertIn("about", rendered)
        self.assertIn("help", rendered)
        self.assertNotIn("||", rendered)
        self.assertNotIn("[TOP]", rendered)
        favorites_write = next(
            write for write in window.writes
            if write[2] == "favorites"
        )
        help_write = next(
            write for write in window.writes
            if write[2] == "help"
        )
        self.assertGreaterEqual(favorites_write[1], 55)
        self.assertLessEqual(help_write[1] + len(help_write[2]), 118)

    @patch("hackernews_cli.ui.components.header.curses.has_colors", return_value=False)
    def test_header_shows_live_list_stats(self, _has_colors):
        window = RecordingWindow()

        draw_feed_header(
            window,
            Region(0, 2, 120),
            2,
            10,
            "",
            "top",
            listed_count=60,
            visited_count=12,
            favorite_count=4,
            read_count=9,
        )

        rendered = "".join(write[2] for write in window.writes)
        self.assertIn("listed 60", rendered)
        self.assertIn("visited 12", rendered)
        self.assertIn("fav 4", rendered)
        self.assertIn("read 9", rendered)

    @patch("hackernews_cli.ui.components.header.curses.has_colors", return_value=False)
    def test_compact_header_right_aligns_local_tabs(
            self,
            _has_colors):
        window = RecordingWindow()

        draw_feed_header(
            window,
            Region(0, 2, 80),
            1,
            10,
            "",
            "top",
        )

        rendered = "".join(write[2] for write in window.writes)
        self.assertNotIn("||", rendered)
        self.assertIn("help", rendered)
        fav_write = next(
            write for write in window.writes
            if write[2] == "fav"
        )
        help_write = next(
            write for write in window.writes
            if write[2] == "help"
        )
        self.assertGreaterEqual(fav_write[1], 40)
        self.assertLessEqual(help_write[1] + len(help_write[2]), 78)

    @patch("hackernews_cli.ui.components.footer.caps_lock_enabled", return_value=True)
    @patch("hackernews_cli.ui.components.footer.curses.has_colors", return_value=False)
    def test_footer_reflects_caps_lock_actions(self, _has_colors, _caps_lock):
        window = RecordingWindow()

        draw_feed_footer(window, Region(17, 3, 100))

        rendered = "".join(write[2] for write in window.writes)
        self.assertIn("CAPS ON", rendered)
        self.assertIn("T read later", rendered)
        self.assertIn("A load all", rendered)
        self.assertIn("S filters", rendered)
        self.assertIn("G bottom", rendered)
        self.assertIn("F favorites", rendered)
        self.assertIn("H history", rendered)
        self.assertIn("B open10", rendered)
        self.assertIn("Left/Right tabs", rendered)
        self.assertIn("Q quit", rendered)

    @patch("hackernews_cli.ui.components.footer.caps_lock_enabled", return_value=False)
    @patch("hackernews_cli.ui.components.footer.curses.has_colors", return_value=False)
    def test_footer_shows_lowercase_actions_when_caps_lock_is_off(
            self,
            _has_colors,
            _caps_lock):
        window = RecordingWindow()

        draw_feed_footer(window, Region(17, 3, 120))

        rendered = "".join(write[2] for write in window.writes)
        self.assertIn("caps off", rendered)
        self.assertIn("a load all", rendered)
        self.assertIn("t later", rendered)
        self.assertIn("s save", rendered)
        self.assertIn("f fav", rendered)
        self.assertIn("r read", rendered)
        self.assertIn("b open5", rendered)
        self.assertIn("left/right tabs", rendered)
        self.assertIn("q quit", rendered)

    def test_page_frame_regions_cover_screen_without_overlap(self):
        screen = Mock()
        screen.getmaxyx.return_value = (20, 100)

        frame = PageFrame.from_screen(screen)

        self.assertEqual(frame.header, Region(0, 2, 100))
        self.assertEqual(frame.content, Region(2, 15, 100))
        self.assertEqual(frame.footer, Region(17, 3, 100))
        self.assertEqual(frame.header.end_y, frame.content.y)
        self.assertEqual(frame.content.end_y, frame.footer.y)

    def test_page_frame_remains_valid_in_short_terminal(self):
        screen = Mock()
        screen.getmaxyx.return_value = (3, 40)

        frame = PageFrame.from_screen(screen)

        self.assertEqual(frame.header.height, 2)
        self.assertEqual(frame.content.height, 0)
        self.assertEqual(frame.footer.height, 1)
        self.assertEqual(frame.footer.end_y, 3)

    def test_home_capacity_tracks_terminal_height(self):
        screen = Mock()
        screen.getmaxyx.return_value = (56, 120)

        self.assertEqual(home_story_capacity(screen), 49)

    def test_truncation_never_exceeds_available_width(self):
        self.assertEqual(truncate_line("long", 0), "")
        self.assertEqual(truncate_line("long", 2), "..")
        self.assertLessEqual(len(truncate_line("long value", 5)), 5)


if __name__ == "__main__":
    unittest.main()
