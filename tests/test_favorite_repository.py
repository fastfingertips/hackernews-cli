import tempfile
import unittest
from pathlib import Path

from hackernews_cli.data import Database, FavoriteRepository


class FavoriteRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        database_path = Path(self.temp_directory.name) / "hackernews-cli-data.sqlite3"
        self.repository = FavoriteRepository(Database(database_path))

    def tearDown(self):
        self.temp_directory.cleanup()

    def test_toggle_adds_and_then_removes_favorite(self):
        url = "https://example.com/story"

        self.assertTrue(self.repository.toggle(url, "Story"))
        self.assertEqual(self.repository.favorite_urls(), {url})
        self.assertEqual(self.repository.list_entries()[0].title, "Story")

        self.assertFalse(self.repository.toggle(url, "Story"))
        self.assertEqual(self.repository.favorite_urls(), set())
        self.assertEqual(self.repository.list_entries(), [])


if __name__ == "__main__":
    unittest.main()
