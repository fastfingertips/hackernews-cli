import unittest
from unittest.mock import Mock

from hackernews_cli.app import ApplicationContext


class ApplicationContextTests(unittest.TestCase):
    def test_combines_activity_from_each_state_repository(self):
        history = Mock()
        history.visited_urls.return_value = {"visited"}
        favorites = Mock()
        favorites.favorite_urls.return_value = {"favorite"}
        reads = Mock()
        reads.read_urls.return_value = {"read"}
        reading_list = Mock()
        reading_list.urls.return_value = {"later"}
        context = ApplicationContext(
            page_service=Mock(),
            history_repository=history,
            favorite_repository=favorites,
            read_repository=reads,
            reading_list_repository=reading_list,
        )

        self.assertEqual(
            context.activity_urls(),
            {"visited", "favorite", "read", "later"},
        )


if __name__ == "__main__":
    unittest.main()
