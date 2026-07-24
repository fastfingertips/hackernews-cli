import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from hackernews_cli.data import Database


class DatabaseTests(unittest.TestCase):
    def test_new_database_contains_only_current_application_tables(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "hackernews-cli-data.sqlite3"
            database = Database(path)

            with closing(sqlite3.connect(database.path)) as connection:
                tables = {
                    row[0]
                    for row in connection.execute(
                        "SELECT name FROM sqlite_master WHERE type = 'table'"
                    )
                }
                history_columns = {
                    row[1]
                    for row in connection.execute(
                        "PRAGMA table_info(history)"
                    )
                }
                schema_version = connection.execute(
                    "PRAGMA user_version"
                ).fetchone()[0]

            self.assertEqual(
                tables,
                {
                    "history",
                    "favorites",
                    "read_stories",
                    "saved_filters",
                    "reading_list",
                    "sqlite_sequence",
                },
            )
            self.assertIn("reverted_event_id", history_columns)
            self.assertEqual(schema_version, 4)

    def test_existing_history_table_gains_event_link_column(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "hackernews-cli-data.sqlite3"
            with closing(sqlite3.connect(path)) as connection:
                connection.execute(
                    """
                    CREATE TABLE history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        url TEXT NOT NULL,
                        title TEXT NOT NULL,
                        kind TEXT NOT NULL,
                        visited_at TEXT NOT NULL
                    )
                    """
                )
                connection.execute(
                    """
                    INSERT INTO history (url, title, kind, visited_at)
                    VALUES ('https://example.com', 'Story', 'article', 'now')
                    """
                )
                connection.commit()

            database = Database(path)
            with closing(sqlite3.connect(database.path)) as connection:
                columns = {
                    row[1]
                    for row in connection.execute(
                        "PRAGMA table_info(history)"
                    )
                }
                saved_count = connection.execute(
                    "SELECT COUNT(*) FROM history"
                ).fetchone()[0]

            self.assertIn("reverted_event_id", columns)
            self.assertEqual(saved_count, 1)


if __name__ == "__main__":
    unittest.main()
