import unittest
from unittest.mock import Mock, patch

from hackernews_cli.data import SavedFilter
from hackernews_cli.ui.pages.saved_filters import (
    _search,
    save_active_filter,
    show_saved_filters,
)


class RecordingScreen:
    def __init__(self, keys):
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


class SavedFiltersPageTests(unittest.TestCase):
    def setUp(self):
        self.entry = SavedFilter(
            id=1,
            name="Popular unread",
            query="is:unread points:>=100",
            is_builtin=True,
            created_at="2026-07-24T12:00:00+00:00",
            updated_at="2026-07-24T12:00:00+00:00",
        )

    def test_search_matches_name_query_and_type(self):
        entries = [self.entry]

        self.assertEqual(_search(entries, "popular"), entries)
        self.assertEqual(_search(entries, "points built-in"), entries)
        self.assertEqual(_search(entries, "custom"), [])

    @patch(
        "hackernews_cli.ui.components.saved_filters_table.curses.has_colors",
        return_value=False,
    )
    @patch(
        "hackernews_cli.ui.components.header.curses.has_colors",
        return_value=False,
    )
    @patch(
        "hackernews_cli.ui.components.footer.curses.has_colors",
        return_value=False,
    )
    def test_enter_returns_selected_filter_query(
            self,
            _footer_colors,
            _header_colors,
            _table_colors):
        screen = RecordingScreen([10])
        repository = Mock()
        repository.list_entries.return_value = [self.entry]

        selected = show_saved_filters(screen, repository)

        self.assertEqual(selected, self.entry.query)
        rendered = "".join(write[2] for write in screen.writes)
        self.assertIn("saved filters", rendered)
        self.assertIn("Popular unread", rendered)

    @patch(
        "hackernews_cli.ui.pages.saved_filters.show_filter_name",
        return_value="My filter",
    )
    def test_active_query_can_be_named_and_saved(self, _show_name):
        repository = Mock()
        repository.save.return_value = True

        query, saved = save_active_filter(
            Mock(),
            repository,
            "is:unread",
        )

        self.assertEqual(query, "is:unread")
        self.assertTrue(saved)
        repository.save.assert_called_once_with("My filter", "is:unread")


if __name__ == "__main__":
    unittest.main()
