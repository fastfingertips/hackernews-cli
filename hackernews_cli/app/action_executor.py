"""Execute feed actions without owning keyboard dispatch."""

from ..data.events import OPEN_COMMENTS
from ..services import (
    ActivityService,
    BulkOpenService,
    FeedService,
    StorageService,
    StoryService,
)
from ..ui.pages import (
    save_active_filter,
    show_about,
    show_data,
    show_favorites,
    show_help,
    show_history,
    show_reading_list,
    show_saved_filters,
)
from ..ui.terminal.prompts import show_feed_filter


class ActionExecutor:
    """Coordinate services and modal pages for one input action."""

    def __init__(
            self,
            stdscr,
            state,
            articles,
            context,
            selection_callback=None,
            loading_callback=None):
        self.stdscr = stdscr
        self.state = state
        self.articles = articles
        self.context = context
        self.selection_callback = selection_callback
        self.loading_callback = loading_callback
        self.feed = FeedService(context)
        self.stories = StoryService(context)
        self.activity = ActivityService(context)
        self.storage = StorageService(context)
        self.bulk = BulkOpenService(context, self.feed, self.stories)

    def open_link(self):
        self.stories.open_article(self._selected_article())

    def open_comments(self):
        self.stories.open_article(
            self._selected_article(),
            kind=OPEN_COMMENTS,
        )

    def switch_category(self, category):
        self.feed.switch_category(self.state, category)

    def reset_filter(self):
        self.state.filter_query = ""
        self.state.reset_selection()

    def refresh_page(self):
        self.feed.refresh(self.state)

    def apply_filter(self):
        self.state.filter_query = show_feed_filter(
            self.stdscr,
            self.state.filter_query,
        )
        self.state.reset_selection()

    def show_help(self):
        show_help(self.stdscr)

    def show_about(self):
        show_about(self.stdscr)

    def show_history(self):
        show_history(self.stdscr, self.context)

    def toggle_favorite(self):
        self.activity.toggle_favorite(self._selected_article())

    def show_favorites(self):
        show_favorites(self.stdscr, self.context)

    def toggle_read(self):
        self.activity.toggle_read(self._selected_article())

    def show_data(self):
        show_data(self.stdscr, self.storage)

    def save_filter(self):
        query, _saved = save_active_filter(
            self.stdscr,
            self.context.saved_filter_repository,
            self.state.filter_query,
        )
        if query != self.state.filter_query:
            self.state.filter_query = query
            self.state.reset_selection()

    def show_filters(self):
        query = show_saved_filters(
            self.stdscr,
            self.context.saved_filter_repository,
            self.state.filter_query,
        )
        if query is not None:
            self.state.filter_query = query
            self.state.reset_selection()

    def toggle_read_later(self):
        self.activity.toggle_read_later(self._selected_article())

    def show_reading_list(self):
        show_reading_list(self.stdscr, self.context)

    def bulk_open(self, limit):
        self.articles = self.bulk.execute(
            self.state,
            self.articles,
            limit,
            self.selection_callback,
        )

    def load_all(self):
        self.articles = self.feed.load_all(
            self.state,
            self.loading_callback,
        )

    def _selected_article(self):
        return self.stories.selected_article(
            self.articles,
            self.state.selected_index,
        )
