"""Feed loading and state transitions."""

from ..hn.page import Page


class FeedService:
    def __init__(self, context):
        self.context = context

    def get_page(
            self,
            page_number,
            category,
            refresh=False,
            progress_callback=None):
        options = {
            "category": category,
            "refresh": refresh,
        }
        if progress_callback is not None:
            options["progress_callback"] = progress_callback
        return self.context.page_service.get_page(page_number, **options)

    def switch_category(self, state, category):
        ready_page = self.context.page_service.get_ready_page(1, category)
        if ready_page is None:
            state.page = Page(
                [],
                current_page=1,
                total_pages=state.page.total_pages,
                category=category,
            )
            state.loading_category = True
        else:
            state.page = ready_page
            state.loading_category = False
        state.selected_index = 0
        state.filter_query = ""

    def resolve_category(self, state):
        """Install a requested category once its first page is ready."""
        if not state.loading_category:
            return False

        ready_page = self.context.page_service.get_ready_page(
            1,
            state.category,
        )
        if ready_page is None:
            return False

        state.page = ready_page
        state.loading_category = False
        state.selected_index = 0
        return True

    def refresh(self, state):
        state.page = self.context.page_service.refresh_category(
            state.category
        )
        state.selected_index = 0
        state.loading_category = False

    def append_next(self, state, progress_callback=None):
        next_page_number = max(state.page.loaded_pages) + 1
        if next_page_number > state.page.total_pages:
            return False

        next_page = self.get_page(
            next_page_number,
            state.category,
            progress_callback=progress_callback,
        )
        state.page = state.page.append(next_page)
        return True

    def append_next_ready(self, state):
        """Append the next batch only when it is already available."""
        if state.loading_category:
            return False

        next_page_number = max(state.page.loaded_pages) + 1
        if next_page_number > state.page.total_pages:
            return False

        next_page = self.context.page_service.get_ready_page(
            next_page_number,
            state.category,
        )
        if next_page is None:
            return False

        state.page = state.page.append(next_page)
        return True

    def fill_ready_to_count(self, state, minimum_count):
        """Use ready prefetched batches without blocking terminal input."""
        articles = self.context.visible_articles(
            state.page,
            state.filter_query,
        )
        while len(articles) < minimum_count:
            if not self.append_next_ready(state):
                break
            articles = self.context.visible_articles(
                state.page,
                state.filter_query,
            )
        return articles

    @staticmethod
    def is_loading(state, visible_count, minimum_count):
        if state.loading_category:
            return True
        next_page_number = max(state.page.loaded_pages) + 1
        return (
            visible_count < minimum_count
            and next_page_number <= state.page.total_pages
        )

    def fill_to_count(
            self,
            state,
            minimum_count,
            progress_callback=None):
        """Append batches until the filtered feed fills the requested rows."""
        articles = self.context.visible_articles(
            state.page,
            state.filter_query,
        )
        while len(articles) < minimum_count:
            def report_progress():
                if progress_callback is not None:
                    progress_callback(articles)

            if not self.append_next(
                    state,
                    progress_callback=(
                        report_progress
                        if progress_callback is not None
                        else None
                    )):
                break
            articles = self.context.visible_articles(
                state.page,
                state.filter_query,
            )
        return articles

    def load_all(self, state, progress_callback=None):
        """Append every available batch and return the filtered result."""
        articles = self.context.visible_articles(
            state.page,
            state.filter_query,
        )
        while True:
            def report_progress():
                if progress_callback is not None:
                    progress_callback(articles)

            if not self.append_next(
                    state,
                    progress_callback=(
                        report_progress
                        if progress_callback is not None
                        else None
                    )):
                return articles
            articles = self.context.visible_articles(
                state.page,
                state.filter_query,
            )
