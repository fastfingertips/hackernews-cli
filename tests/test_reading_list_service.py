import unittest
from unittest.mock import Mock, patch

from hackernews_cli.data import ReadingListEntry
from hackernews_cli.services import ReadingListService


class ReadingListServiceTests(unittest.TestCase):
    @patch("hackernews_cli.services.story.webbrowser.open")
    def test_bulk_open_skips_visited_and_read_entries(self, _open_browser):
        entries = [
            ReadingListEntry(
                f"https://example.com/{index}",
                f"Story {index}",
                "2026-07-24T12:00:00+00:00",
            )
            for index in range(4)
        ]
        history = Mock()
        history.visited_urls.return_value = {entries[0].url}
        reads = Mock()
        reads.read_urls.return_value = {entries[1].url}
        context = Mock(
            history_repository=history,
            read_repository=reads,
        )
        selected = []

        result = ReadingListService(context).open_unread(
            entries,
            5,
            selected.append,
        )

        self.assertEqual(result.opened_count, 2)
        self.assertEqual(result.selected_index, 3)
        self.assertEqual(selected, [2, 3])
        self.assertEqual(history.add.call_count, 2)


if __name__ == "__main__":
    unittest.main()
