import sqlite3
import tempfile
import unittest
from contextlib import closing
from datetime import datetime, timedelta, timezone
from pathlib import Path

from hackernews_cli.data import Database, HistoryRepository


class HistoryRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp_directory = tempfile.TemporaryDirectory()
        database_path = Path(self.temp_directory.name) / "hackernews-cli-data.sqlite3"
        self.repository = HistoryRepository(Database(database_path))

    def tearDown(self):
        self.temp_directory.cleanup()

    def test_each_visit_creates_a_separate_log_entry(self):
        url = "https://example.com/story"
        self.repository.add(url, "Old title", "article")
        self.repository.add(url, "New title", "article")

        entries = self.repository.list_entries()

        self.assertEqual(len(entries), 2)
        self.assertEqual(entries[0].title, "New title")
        self.assertIn(url, self.repository.visited_urls())

    def test_delete_and_clear_manage_history(self):
        first = "https://example.com/first"
        second = "https://example.com/second"
        self.repository.add(first, "First")
        self.repository.add(second, "Second")

        first_entry = next(
            entry for entry in self.repository.list_entries()
            if entry.url == first
        )
        self.repository.delete(first_entry.id)
        self.assertEqual(self.repository.visited_urls(), {second})

        self.repository.clear()
        self.assertEqual(self.repository.list_entries(), [])
        self.assertEqual(self.repository.visited_urls(), set())

    def test_activity_stats_use_hour_day_week_and_year_windows(self):
        now = datetime(2026, 7, 22, 12, 0, tzinfo=timezone.utc)
        timestamps = (
            now - timedelta(minutes=30),
            now - timedelta(hours=3),
            now - timedelta(days=2),
            now - timedelta(days=200),
            now - timedelta(days=500),
        )
        with closing(sqlite3.connect(self.repository.database_path)) as connection:
            with connection:
                connection.executemany(
                    """
                    INSERT INTO history (url, title, kind, visited_at)
                    VALUES (?, ?, 'article', ?)
                    """,
                    [
                        (
                            f"https://example.com/{index}",
                            f"Story {index}",
                            value.isoformat(),
                        )
                        for index, value in enumerate(timestamps)
                    ],
                )

        stats = self.repository.activity_stats(now)

        self.assertEqual(stats.last_hour, 1)
        self.assertEqual(stats.today, 2)
        self.assertEqual(stats.this_week, 3)
        self.assertEqual(stats.this_year, 4)


if __name__ == "__main__":
    unittest.main()
