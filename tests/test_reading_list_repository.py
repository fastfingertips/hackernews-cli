import tempfile
import unittest
from pathlib import Path

from hackernews_cli.data import Database, ReadingListRepository


class ReadingListRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        database = Database(Path(self.directory.name) / "test.sqlite3")
        self.repository = ReadingListRepository(database)

    def tearDown(self):
        self.directory.cleanup()

    def test_toggle_adds_and_removes_deferred_story(self):
        url = "https://example.com/story"

        self.assertTrue(self.repository.toggle(url, "Story"))
        self.assertIn(url, self.repository.urls())
        self.assertEqual(self.repository.list_entries()[0].title, "Story")

        self.assertFalse(self.repository.toggle(url, "Story"))
        self.assertNotIn(url, self.repository.urls())


if __name__ == "__main__":
    unittest.main()
