import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock

from hackernews_cli.app import ApplicationContext
from hackernews_cli.data import (
    Database,
    FavoriteRepository,
    HistoryRepository,
    ReadRepository,
    ReadingListRepository,
)
from hackernews_cli.hn import Article
from hackernews_cli.services import ActivityService


class ActivityServiceTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        database = Database(
            Path(self.directory.name) / "hackernews-cli-data.sqlite3"
        )
        self.context = ApplicationContext(
            page_service=Mock(),
            history_repository=HistoryRepository(database),
            favorite_repository=FavoriteRepository(database),
            read_repository=ReadRepository(database),
            reading_list_repository=ReadingListRepository(database),
        )
        self.service = ActivityService(self.context)
        self.article = Article("Story", "https://example.com/story")

    def tearDown(self):
        self.directory.cleanup()

    def test_favorite_removal_is_logged_and_can_be_undone(self):
        self.service.toggle_favorite(self.article)
        self.service.toggle_favorite(self.article)
        removed_event = self.context.history_repository.list_entries()[0]

        result = self.service.undo(removed_event)
        entries = self.context.history_repository.list_entries()

        self.assertTrue(result.success)
        self.assertIn(
            self.article.link,
            self.context.favorite_repository.favorite_urls(),
        )
        self.assertEqual(entries[0].kind, "favorite_added")
        self.assertEqual(entries[0].reverted_event_id, removed_event.id)
        self.assertTrue(
            self.context.history_repository.is_reverted(removed_event.id)
        )

    def test_same_event_cannot_be_undone_twice(self):
        self.service.toggle_read(self.article)
        event = self.context.history_repository.list_entries()[0]

        self.assertTrue(self.service.undo(event).success)
        second_result = self.service.undo(event)

        self.assertFalse(second_result.success)
        self.assertEqual(second_result.message, "Selected event was already undone")

    def test_state_events_do_not_mark_story_as_visited(self):
        self.service.toggle_favorite(self.article)
        self.service.toggle_read(self.article)

        self.assertEqual(
            self.context.history_repository.visited_urls(),
            set(),
        )

    def test_read_later_removal_is_logged_and_can_be_undone(self):
        self.service.toggle_read_later(self.article)
        self.service.toggle_read_later(self.article)
        removed = self.context.history_repository.list_entries()[0]

        result = self.service.undo(removed)

        self.assertTrue(result.success)
        self.assertIn(
            self.article.link,
            self.context.reading_list_repository.urls(),
        )
        self.assertEqual(
            self.context.history_repository.list_entries()[0].kind,
            "read_later_added",
        )


if __name__ == "__main__":
    unittest.main()
