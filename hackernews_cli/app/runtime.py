"""Top-level loop for the terminal application."""

import curses

from ..services import FeedService
from ..hn.categories import DEFAULT_CATEGORY
from ..ui.pages import draw_home, home_story_capacity, show_home
from ..ui.terminal.animation import selection_frames

from .context import ApplicationContext
from .input import InputController
from .state import FeedState


class ApplicationRuntime:
    def __init__(self, stdscr, context=None):
        self.stdscr = stdscr
        self.context = context or ApplicationContext.create_default()
        self.feed_service = FeedService(self.context)
        first_page = self.feed_service.get_page(1, DEFAULT_CATEGORY)
        self.state = FeedState(first_page)
        self.input_controller = InputController(self.context)
        self.loading_frame = 0

    def run(self):
        try:
            while True:
                self.feed_service.resolve_category(self.state)
                articles = self.context.visible_articles(
                    self.state.page,
                    self.state.filter_query,
                )
                articles = self._fill_viewport(articles)
                capacity = home_story_capacity(self.stdscr)
                is_loading = self.feed_service.is_loading(
                    self.state,
                    len(articles),
                    capacity,
                )
                loading_frame = self.loading_frame if is_loading else None
                key = self._show_home(articles, loading_frame)
                self.loading_frame = (
                    self.loading_frame + 1
                    if is_loading
                    else 0
                )
                if key == -1:
                    continue

                animation_position = self.state.selected_index
                loading_frame = 0

                def animate_selection(
                        target_index,
                        preview_articles,
                        preview_page):
                    nonlocal animation_position
                    for frame_index in selection_frames(
                            animation_position,
                            target_index):
                        self._draw_home(
                            preview_articles,
                            frame_index,
                            preview_page,
                        )
                        curses.napms(35)
                    animation_position = target_index

                def animate_loading():
                    nonlocal loading_frame
                    self._draw_home(
                        articles,
                        self.state.selected_index,
                        self.state.page,
                        loading_frame=loading_frame,
                    )
                    loading_frame += 1

                if not self.input_controller.handle(
                        self.stdscr,
                        key,
                        self.state,
                        articles,
                        animate_selection,
                        animate_loading):
                    break
        finally:
            self.context.close()

    def _show_home(self, articles, loading_frame=None):
        return show_home(
            self.stdscr,
            articles,
            self.state.selected_index,
            self.state.current_page,
            self.state.page.total_pages,
            self.state.filter_query,
            self.state.category,
            self.context.history_repository.visited_dates(),
            self.context.favorite_repository.favorite_dates(),
            self.context.read_repository.read_dates(),
            self.context.reading_list_repository.dates(),
            loading_frame,
        )

    def _fill_viewport(self, articles):
        return self.feed_service.fill_ready_to_count(
            self.state,
            home_story_capacity(self.stdscr),
        )

    def _draw_home(
            self,
            articles,
            selected_index,
            page,
            loading_frame=None):
        draw_home(
            self.stdscr,
            articles,
            selected_index,
            page.current_page,
            page.total_pages,
            self.state.filter_query,
            page.category,
            self.context.history_repository.visited_dates(),
            self.context.favorite_repository.favorite_dates(),
            self.context.read_repository.read_dates(),
            self.context.reading_list_repository.dates(),
            loading_frame=loading_frame,
        )
