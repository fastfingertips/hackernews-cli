import unittest
from datetime import datetime
from unittest.mock import patch

from hackernews_cli.hn import Article
from hackernews_cli.hn.client import fetch_hacker_news


class HackerNewsClientTests(unittest.TestCase):
    @patch("hackernews_cli.hn.client.parse_html")
    @patch("hackernews_cli.hn.client.fetch_html", return_value="<html></html>")
    def test_fetch_assigns_one_utc_timestamp_to_every_story(
            self,
            _fetch_html,
            parse_html):
        parse_html.return_value = [
            Article("First", "https://example.com/first"),
            Article("Second", "https://example.com/second"),
        ]

        page = fetch_hacker_news()

        fetched_at = {article.fetched_at for article in page.articles}
        self.assertEqual(len(fetched_at), 1)
        parsed = datetime.fromisoformat(fetched_at.pop())
        self.assertIsNotNone(parsed.tzinfo)


if __name__ == "__main__":
    unittest.main()
