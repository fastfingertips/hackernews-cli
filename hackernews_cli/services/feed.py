"""Feed loading and state transitions."""

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
        state.page = self.get_page(1, category)
        state.selected_index = 0
        state.filter_query = ""

    def refresh(self, state):
        state.page = self.context.page_service.refresh_category(
            state.category
        )
        state.selected_index = 0

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
