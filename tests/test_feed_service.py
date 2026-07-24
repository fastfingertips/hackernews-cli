import unittest
from unittest.mock import Mock

from hackernews_cli.app import FeedState
from hackernews_cli.hn import Article, Page
from hackernews_cli.services import FeedService


class FeedServiceTests(unittest.TestCase):
    def test_fills_available_rows_with_following_batches(self):
        first_articles = [
            Article(f"Story {index}", f"https://example.com/{index}")
            for index in range(30)
        ]
        second_articles = [
            Article(f"Story {index}", f"https://example.com/{index}")
            for index in range(30, 60)
        ]
        first_page = Page(first_articles, 1, 10, "top")
        second_page = Page(second_articles, 2, 10, "top")
        context = Mock()
        context.visible_articles.side_effect = (
            lambda page, _query: page.articles
        )
        preview_sizes = []

        def get_page(_page_number, **options):
            options["progress_callback"]()
            return second_page

        context.page_service.get_page.side_effect = get_page
        state = FeedState(first_page)

        articles = FeedService(context).fill_to_count(
            state,
            50,
            progress_callback=lambda preview: preview_sizes.append(
                len(preview)
            ),
        )

        self.assertEqual(len(articles), 60)
        self.assertEqual(state.current_page, 2)
        self.assertEqual(preview_sizes, [30])

    def test_does_not_fetch_when_visible_rows_already_fit(self):
        articles = [
            Article(f"Story {index}", f"https://example.com/{index}")
            for index in range(60)
        ]
        context = Mock()
        context.visible_articles.return_value = articles
        state = FeedState(Page(articles, 2, 10, "top"))

        result = FeedService(context).fill_to_count(state, 50)

        self.assertEqual(result, articles)
        context.page_service.get_page.assert_not_called()

    def test_load_all_appends_until_total_page_count(self):
        pages = {
            page_number: Page(
                [
                    Article(
                        f"Story {page_number}",
                        f"https://example.com/{page_number}",
                    )
                ],
                page_number,
                3,
                "top",
            )
            for page_number in (2, 3)
        }
        first_page = Page(
            [Article("Story 1", "https://example.com/1")],
            1,
            3,
            "top",
        )
        context = Mock()
        context.visible_articles.side_effect = (
            lambda page, _query: page.articles
        )
        context.page_service.get_page.side_effect = (
            lambda page_number, **_options: pages[page_number]
        )
        state = FeedState(first_page)

        articles = FeedService(context).load_all(state)

        self.assertEqual(len(articles), 3)
        self.assertEqual(state.page.loaded_pages, (1, 2, 3))
        self.assertEqual(context.page_service.get_page.call_count, 2)


if __name__ == "__main__":
    unittest.main()
