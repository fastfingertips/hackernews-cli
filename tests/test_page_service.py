import unittest
import tempfile
from pathlib import Path
from threading import Event

from hackernews_cli.data import Database, StoryRepository
from hackernews_cli.hn import Article, Page
from hackernews_cli.services import PageService


class PageServiceTests(unittest.TestCase):
    @staticmethod
    def story(item_id):
        return Article(
            title=f"Story {item_id}",
            link=f"https://example.com/{item_id}",
            item_id=str(item_id),
            fetched_at="2026-07-24T12:00:00+00:00",
        )

    def test_next_page_is_prefetched_and_not_fetched_twice(self):
        calls = []

        def fetcher(page_number, category="top"):
            calls.append((category, page_number))
            return Page([], page_number, 10, category)

        service = PageService(fetcher=fetcher)
        try:
            first = service.get_page(1, "top")
            second = service.get_page(2, "top")

            self.assertEqual(first.current_page, 1)
            self.assertEqual(second.current_page, 2)
            self.assertEqual(calls.count(("top", 2)), 1)
        finally:
            service.close()

    def test_refresh_replaces_cached_page(self):
        calls = []

        def fetcher(page_number, category="top"):
            calls.append((category, page_number))
            return Page([], page_number, 10, category)

        service = PageService(fetcher=fetcher)
        try:
            service.get_page(1, "top")
            service.get_page(1, "top", refresh=True)
            self.assertEqual(calls.count(("top", 1)), 2)
        finally:
            service.close()

    def test_slow_next_page_reports_loading_progress(self):
        next_page_started = Event()
        release_next_page = Event()
        progress_frames = []

        def fetcher(page_number, category="top"):
            if page_number == 2:
                next_page_started.set()
                release_next_page.wait(timeout=2)
            return Page([], page_number, 10, category)

        service = PageService(fetcher=fetcher)
        try:
            service.get_page(1, "top")
            self.assertTrue(next_page_started.wait(timeout=1))

            def report_progress():
                progress_frames.append(len(progress_frames))
                release_next_page.set()

            page = service.get_page(
                2,
                "top",
                progress_callback=report_progress,
            )

            self.assertEqual(page.current_page, 2)
            self.assertGreaterEqual(len(progress_frames), 1)
        finally:
            release_next_page.set()
            service.close()

    def test_ready_prefetched_page_does_not_report_loading(self):
        second_page_ready = Event()

        def fetcher(page_number, category="top"):
            page = Page([], page_number, 10, category)
            if page_number == 2:
                second_page_ready.set()
            return page

        service = PageService(fetcher=fetcher)
        try:
            service.get_page(1, "top")
            self.assertTrue(second_page_ready.wait(timeout=1))
            progress_frames = []

            page = service.get_page(
                2,
                "top",
                progress_callback=lambda: progress_frames.append(1),
            )

            self.assertEqual(page.current_page, 2)
            self.assertEqual(progress_frames, [])
        finally:
            service.close()

    def test_get_ready_page_never_waits_for_slow_fetch(self):
        page_started = Event()
        release_page = Event()
        page_finished = Event()

        def fetcher(page_number, category="top"):
            page_started.set()
            release_page.wait(timeout=2)
            page = Page([], page_number, 10, category)
            page_finished.set()
            return page

        service = PageService(fetcher=fetcher)
        try:
            self.assertIsNone(service.get_ready_page(1, "new"))
            self.assertTrue(page_started.wait(timeout=1))
            self.assertIsNone(service.get_ready_page(1, "new"))

            release_page.set()
            self.assertTrue(page_finished.wait(timeout=1))
            ready = service.get_ready_page(1, "new")

            self.assertIsNotNone(ready)
            self.assertEqual(ready.category, "new")
        finally:
            release_page.set()
            service.close()

    def test_category_refresh_discards_all_loaded_batches(self):
        calls = []

        def fetcher(page_number, category="top"):
            calls.append((category, page_number))
            return Page([], page_number, 10, category)

        service = PageService(fetcher=fetcher)
        try:
            service.get_page(1, "top")
            service.get_page(2, "top")
            refreshed = service.refresh_category("top")
            service.get_page(2, "top")

            self.assertEqual(refreshed.current_page, 1)
            self.assertEqual(calls.count(("top", 1)), 2)
            self.assertEqual(calls.count(("top", 2)), 2)
        finally:
            service.close()

    def test_refresh_appends_story_missing_from_latest_fetch(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = StoryRepository(Database(
                Path(directory) / "data.sqlite3"
            ))
            page_one_calls = 0

            def fetcher(page_number, category="top"):
                nonlocal page_one_calls
                if page_number != 1:
                    return Page([], page_number, 10, category)
                page_one_calls += 1
                articles = (
                    [self.story(1), self.story(2)]
                    if page_one_calls == 1
                    else [self.story(2), self.story(3)]
                )
                return Page(articles, page_number, 10, category)

            service = PageService(
                fetcher=fetcher,
                story_repository=repository,
            )
            try:
                service.get_page(1, "top")
                refreshed = service.get_page(1, "top", refresh=True)
            finally:
                service.close()

        self.assertEqual(
            [article.item_id for article in refreshed.articles],
            ["2", "3", "1"],
        )
        self.assertFalse(refreshed.articles[0].is_cached)
        self.assertTrue(refreshed.articles[-1].is_cached)

    def test_failed_fetch_recovers_last_saved_page(self):
        with tempfile.TemporaryDirectory() as directory:
            repository = StoryRepository(Database(
                Path(directory) / "data.sqlite3"
            ))
            repository.save_page(Page(
                [self.story(1)],
                1,
                10,
                "top",
            ))
            service = PageService(
                fetcher=lambda page_number, category="top": Page(
                    [Article("Network error", "")],
                    page_number,
                    10,
                    category,
                ),
                story_repository=repository,
            )
            try:
                recovered = service.get_page(1, "top")
            finally:
                service.close()

        self.assertEqual(
            [article.item_id for article in recovered.articles],
            ["1"],
        )
        self.assertTrue(recovered.articles[0].is_cached)


if __name__ == "__main__":
    unittest.main()
