import tempfile
import unittest
from pathlib import Path

from hackernews_cli.data import Database, ReadRepository


class ReadRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        self.database_path = (
            Path(self.temp_directory.name) / "hackernews-cli-data.sqlite3"
        )

    def tearDown(self):
        self.temp_directory.cleanup()

    def test_toggle_persists_read_and_unread_state(self):
        url = "https://example.com/story"
        database = Database(self.database_path)
        repository = ReadRepository(database)

        self.assertTrue(repository.toggle(url, "Story"))
        self.assertEqual(repository.read_urls(), {url})

        reopened_repository = ReadRepository(Database(self.database_path))
        self.assertEqual(reopened_repository.read_urls(), {url})

        self.assertFalse(reopened_repository.toggle(url, "Story"))
        self.assertEqual(reopened_repository.read_urls(), set())


if __name__ == "__main__":
    unittest.main()
