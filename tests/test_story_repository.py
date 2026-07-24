import tempfile
import unittest
from pathlib import Path

from hackernews_cli.data import Database, StoryRepository
from hackernews_cli.hn import Article, Page


FETCHED_AT = "2026-07-24T12:00:00+00:00"


def story(item_id, score="10 points"):
    return Article(
        title=f"Story {item_id}",
        link=f"https://example.com/{item_id}",
        rank=f"{item_id}.",
        domain="example.com",
        score=score,
        author="ada",
        age="1 hour ago",
        published_at="2026-07-24T11:00:00+00:00",
        comments_count="2 comments",
        hn_link=f"https://news.ycombinator.com/item?id={item_id}",
        item_id=str(item_id),
        fetched_at=FETCHED_AT,
    )


class StoryRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        database = Database(
            Path(self.directory.name) / "hackernews-cli-data.sqlite3"
        )
        self.repository = StoryRepository(database)

    def tearDown(self):
        self.directory.cleanup()

    def test_missing_story_is_retained_as_cached(self):
        self.repository.save_page(
            Page([story(1), story(2)], 1, 10, "top")
        )

        archived = self.repository.save_page(
            Page([story(2), story(3)], 1, 10, "top")
        )

        self.assertEqual([entry.item_id for entry in archived], ["1"])
        self.assertTrue(archived[0].is_cached)
        self.assertEqual(archived[0].fetched_at, FETCHED_AT)

    def test_latest_story_metadata_replaces_previous_values(self):
        self.repository.save_page(
            Page([story(1, "10 points")], 1, 10, "top")
        )
        self.repository.save_page(
            Page([story(1, "25 points")], 1, 10, "top")
        )

        cached_page = self.repository.page("top", 1)

        self.assertEqual(cached_page[0].score, "25 points")
        self.assertTrue(cached_page[0].is_cached)

    def test_categories_keep_independent_feed_membership(self):
        self.repository.save_page(
            Page([story(1)], 1, 10, "top")
        )
        self.repository.save_page(
            Page([story(1)], 2, 10, "new")
        )

        self.assertEqual(
            [entry.item_id for entry in self.repository.page("top", 1)],
            ["1"],
        )
        self.assertEqual(
            [entry.item_id for entry in self.repository.page("new", 2)],
            ["1"],
        )

    def test_visible_archive_is_bounded_per_page(self):
        self.repository.save_page(
            Page(
                [story(item_id) for item_id in range(1, 32)],
                1,
                10,
                "top",
            )
        )
        self.repository.save_page(
            Page([story(99)], 1, 10, "top")
        )

        archived = self.repository.archived_for_page("top", 1)

        self.assertEqual(len(archived), 30)
        self.assertTrue(all(entry.is_cached for entry in archived))


if __name__ == "__main__":
    unittest.main()
