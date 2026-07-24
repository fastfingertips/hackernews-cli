import unittest
from threading import Event

from hackernews_cli.hn import Page
from hackernews_cli.services import PageService


class PageServiceTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
