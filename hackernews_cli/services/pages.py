"""Cache Hacker News pages and prefetch the next batch."""

from concurrent.futures import ThreadPoolExecutor, TimeoutError
from threading import RLock

from ..hn.categories import DEFAULT_CATEGORY
from ..hn.client import fetch_hacker_news
from ..hn.page import Page


class PageService:
    """Load pages and keep the likely next page ready in memory."""

    def __init__(
            self,
            fetcher=fetch_hacker_news,
            total_pages=10,
            story_repository=None):
        self._fetcher = fetcher
        self._total_pages = total_pages
        self._story_repository = story_repository
        self._pages = {}
        self._futures = {}
        self._lock = RLock()
        self._executor = ThreadPoolExecutor(
            max_workers=2,
            thread_name_prefix="hn-prefetch",
        )

    def get_page(
            self,
            page_number,
            category=DEFAULT_CATEGORY,
            refresh=False,
            progress_callback=None):
        key = (category, page_number)

        with self._lock:
            if refresh:
                self._pages.pop(key, None)
                future = self._futures.pop(key, None)
                if future:
                    future.cancel()

            cached = self._pages.get(key)
            future = self._futures.get(key)

        if cached is not None:
            result = cached
        elif future is not None:
            result = self._prepare_page(
                self._await_future(future, progress_callback),
            )
            with self._lock:
                self._futures.pop(key, None)
                self._pages[key] = result
        elif progress_callback is not None:
            future = self._executor.submit(
                self._fetcher,
                page_number,
                category=category,
            )
            result = self._prepare_page(
                self._await_future(future, progress_callback),
            )
            with self._lock:
                self._pages[key] = result
        else:
            result = self._prepare_page(
                self._fetcher(page_number, category=category),
            )
            with self._lock:
                self._pages[key] = result

        self.prefetch(page_number + 1, category)
        return result

    def request_page(
            self,
            page_number,
            category=DEFAULT_CATEGORY):
        """Start loading a page without waiting for the network."""
        if page_number > self._total_pages:
            return

        key = (category, page_number)
        with self._lock:
            if key in self._pages or key in self._futures:
                return
            self._futures[key] = self._executor.submit(
                self._fetcher,
                page_number,
                category=category,
            )

    def get_ready_page(
            self,
            page_number,
            category=DEFAULT_CATEGORY):
        """Return a cached/finished page, or request it and return ``None``."""
        key = (category, page_number)
        self.request_page(page_number, category)

        with self._lock:
            cached = self._pages.get(key)
            future = self._futures.get(key)

        if cached is not None:
            return cached
        if future is None or not future.done():
            return None

        result = self._prepare_page(future.result())
        with self._lock:
            self._futures.pop(key, None)
            self._pages[key] = result
        self.prefetch(page_number + 1, category)
        return result

    def _prepare_page(self, page):
        """Persist a valid response or recover the page from SQLite."""
        if self._story_repository is None:
            return page

        valid_articles = [
            article
            for article in page.articles
            if article.item_id and article.link
        ]
        if not valid_articles:
            cached = self._story_repository.page(
                page.category,
                page.current_page,
            )
            if cached:
                return Page(
                    cached,
                    page.current_page,
                    page.total_pages,
                    page.category,
                )
            return page

        archived = self._story_repository.save_page(page)
        if not archived:
            return page
        return page.append(Page(
            archived,
            page.current_page,
            page.total_pages,
            page.category,
        ))

    @staticmethod
    def _await_future(future, progress_callback):
        if progress_callback is None or future.done():
            return future.result()

        while True:
            progress_callback()
            try:
                return future.result(timeout=0.08)
            except TimeoutError:
                continue

    def prefetch(self, page_number, category=DEFAULT_CATEGORY):
        self.request_page(page_number, category)

    def refresh_category(self, category=DEFAULT_CATEGORY):
        """Discard every cached batch for a feed and load it from page one."""
        with self._lock:
            page_keys = [key for key in self._pages if key[0] == category]
            future_keys = [key for key in self._futures if key[0] == category]
            for key in page_keys:
                self._pages.pop(key, None)
            for key in future_keys:
                future = self._futures.pop(key)
                future.cancel()

        return self.get_page(1, category=category)

    def close(self):
        self._executor.shutdown(wait=False, cancel_futures=True)
