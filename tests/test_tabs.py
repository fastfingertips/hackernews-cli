import curses
import unittest

from hackernews_cli.ui.tabs import (
    FEED_TAB_COUNT,
    TAB_IDS,
    TabSwitch,
    adjacent_tab,
    switch_for_key,
)


class TabNavigationTests(unittest.TestCase):
    def test_all_primary_and_management_tabs_share_one_order(self):
        self.assertEqual(
            TAB_IDS,
            (
                "top",
                "new",
                "ask",
                "show",
                "jobs",
                "favorites",
                "later",
                "history",
                "filters",
                "data",
                "about",
                "help",
            ),
        )
        self.assertEqual(FEED_TAB_COUNT, 5)

    def test_tab_order_wraps_in_both_directions(self):
        self.assertEqual(adjacent_tab("top", -1), "help")
        self.assertEqual(adjacent_tab("help", 1), "top")

    def test_arrow_keys_return_explicit_tab_switches(self):
        self.assertEqual(
            switch_for_key("favorites", curses.KEY_RIGHT),
            TabSwitch("later"),
        )
        self.assertEqual(
            switch_for_key("favorites", curses.KEY_LEFT),
            TabSwitch("jobs"),
        )
        self.assertIsNone(switch_for_key("favorites", ord("j")))


if __name__ == "__main__":
    unittest.main()
