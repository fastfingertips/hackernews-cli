import tempfile
import unittest
from pathlib import Path

from hackernews_cli.data import Database, SavedFilterRepository


class SavedFilterRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        database = Database(
            Path(self.directory.name) / "hackernews-cli-data.sqlite3"
        )
        self.repository = SavedFilterRepository(database)

    def tearDown(self):
        self.directory.cleanup()

    def test_database_starts_with_ready_to_use_filters(self):
        entries = self.repository.list_entries()

        self.assertEqual(len(entries), 6)
        self.assertTrue(all(entry.is_builtin for entry in entries))
        self.assertIn("is:unread", {entry.query for entry in entries})

    def test_custom_filter_can_be_saved_updated_and_removed(self):
        self.assertTrue(
            self.repository.save("My reading list", "is:unread")
        )
        custom = next(
            entry
            for entry in self.repository.list_entries()
            if entry.name == "My reading list"
        )

        self.assertTrue(
            self.repository.save(
                "My reading list",
                "is:unread points:>=100",
            )
        )
        updated = next(
            entry
            for entry in self.repository.list_entries()
            if entry.id == custom.id
        )
        self.assertEqual(updated.query, "is:unread points:>=100")

        self.assertTrue(self.repository.remove(custom.id))
        self.assertNotIn(
            custom.id,
            {entry.id for entry in self.repository.list_entries()},
        )

    def test_builtin_filter_cannot_be_changed_or_deleted(self):
        builtin = self.repository.list_entries()[0]

        self.assertFalse(
            self.repository.update_query(builtin.id, "is:visited")
        )
        self.assertFalse(self.repository.remove(builtin.id))
        self.assertFalse(
            self.repository.save(builtin.name, "is:visited")
        )


if __name__ == "__main__":
    unittest.main()
