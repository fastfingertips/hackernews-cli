import unittest

from hackernews_cli.app.filtering import apply_filter
from hackernews_cli.app.record_filtering import (
    filter_favorites,
    filter_history,
)
from hackernews_cli.data import FavoriteEntry, HistoryEntry
from hackernews_cli.hn import Article


class FeedFilterTests(unittest.TestCase):
    def setUp(self):
        self.first = Article(
            "Python release",
            "https://python.org/release",
            domain="python.org",
            author="guido",
        )
        self.second = Article(
            "Rust release",
            "https://rust-lang.org/release",
            domain="rust-lang.org",
            author="ferris",
        )
        self.articles = [self.first, self.second]

    def test_text_and_status_filters_can_be_combined(self):
        result = apply_filter(
            self.articles,
            "python is:visited is:read",
            visited_urls={self.first.link},
            read_urls={self.first.link},
        )
        self.assertEqual(result, [self.first])

    def test_unread_filter_excludes_explicitly_read_story(self):
        result = apply_filter(
            self.articles,
            "is:unread",
            read_urls={self.first.link},
        )
        self.assertEqual(result, [self.second])

    def test_email_style_fields_quotes_and_negation(self):
        self.first.score = "150 points"
        self.first.comments_count = "12 comments"

        result = apply_filter(
            self.articles,
            'title:"python release" by:guido -site:rust-lang.org '
            "points:>=100 replies:>10",
        )

        self.assertEqual(result, [self.first])

    def test_read_later_state_filter(self):
        result = apply_filter(
            [self.first, self.second],
            "is:later",
            reading_list_urls={self.second.link},
        )

        self.assertEqual(result, [self.second])

    def test_negative_free_text_excludes_matching_story(self):
        result = apply_filter(self.articles, "release -rust")

        self.assertEqual(result, [self.first])


class RecordFilterTests(unittest.TestCase):
    def test_history_matches_action_and_title(self):
        entries = [
            HistoryEntry(
                1,
                "https://example.com/python",
                "Python story",
                "comments",
                "2026-07-22T12:00:00+00:00",
            ),
        ]
        self.assertEqual(filter_history(entries, "python comments"), entries)

    def test_history_matches_undo_action(self):
        entries = [
            HistoryEntry(
                2,
                "https://example.com/python",
                "Python story",
                "favorite_added",
                "2026-07-22T12:00:00+00:00",
                1,
            ),
        ]
        self.assertEqual(filter_history(entries, "undo favorite"), entries)

    def test_favorites_match_url_and_date(self):
        entries = [
            FavoriteEntry(
                "https://example.com/python",
                "Python story",
                "2026-07-22T12:00:00+00:00",
            ),
        ]
        self.assertEqual(filter_favorites(entries, "example 2026-07-22"), entries)

    def test_history_supports_action_date_and_negation_fields(self):
        entries = [
            HistoryEntry(
                1,
                "https://example.com/python",
                "Python story",
                "favorite_removed",
                "2026-07-22T12:00:00+00:00",
            ),
        ]

        result = filter_history(
            entries,
            "action:favorite after:2026-07-01 "
            "before:2026-08-01 -action:opened",
        )

        self.assertEqual(result, entries)

    def test_favorites_support_quoted_title_and_date_range(self):
        entries = [
            FavoriteEntry(
                "https://example.com/python",
                "Local first Python",
                "2026-07-22T12:00:00+00:00",
            ),
        ]

        result = filter_favorites(
            entries,
            'title:"local first" after:2026-01-01 -url:rust',
        )

        self.assertEqual(result, entries)


if __name__ == "__main__":
    unittest.main()
