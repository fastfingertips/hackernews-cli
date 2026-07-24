"""Navigate the current feed state."""

from curses import (
    KEY_DOWN,
    KEY_LEFT,
    KEY_NPAGE,
    KEY_PPAGE,
    KEY_RIGHT,
    KEY_UP,
)

from ..services import FeedService


PAGE_JUMP_SIZE = 30


class NavigationHandler:
    HANDLED_KEYS = {
        KEY_RIGHT,
        KEY_LEFT,
        KEY_DOWN,
        KEY_UP,
        KEY_NPAGE,
        KEY_PPAGE,
        ord("l"),
        ord("L"),
        ord("h"),
        ord("j"),
        ord("J"),
        ord("k"),
        ord("K"),
        ord("g"),
        ord("G"),
    }

    def __init__(
            self,
            state,
            articles,
            context,
            loading_callback=None):
        self.state = state
        self.articles = articles
        self.context = context
        self.loading_callback = loading_callback
        self.feed_service = FeedService(context)

    def next_page(self):
        self._load_next_batch(select_new_item=True)

    def previous_page(self):
        self.state.selected_index = max(
            0,
            self.state.selected_index - PAGE_JUMP_SIZE,
        )

    def select_next_item(self):
        if not self.articles:
            return
        if self.state.selected_index < len(self.articles) - 1:
            self.state.selected_index += 1
        else:
            self._load_next_batch(select_new_item=True)

    def select_previous_item(self):
        if self.articles:
            self.state.selected_index = max(
                self.state.selected_index - 1,
                0,
            )

    def jump_top(self):
        self.state.selected_index = 0

    def jump_bottom(self):
        if self.articles:
            self.state.selected_index = len(self.articles) - 1

    def page_down(self):
        if not self.articles:
            return
        target = self.state.selected_index + 5
        if target < len(self.articles):
            self.state.selected_index = target
        else:
            self._load_next_batch(select_new_item=True)

    def page_up(self):
        if self.articles:
            self.state.selected_index = max(
                self.state.selected_index - 5,
                0,
            )

    def _load_next_batch(self, select_new_item):
        previous_visible_count = len(self.articles)
        if not self.feed_service.append_next(
                self.state,
                progress_callback=self.loading_callback):
            return

        self.articles = self.context.visible_articles(
            self.state.page,
            self.state.filter_query,
        )
        if select_new_item and len(self.articles) > previous_visible_count:
            self.state.selected_index = previous_visible_count
        elif self.articles:
            self.state.selected_index = min(
                self.state.selected_index,
                len(self.articles) - 1,
            )

    def handle_navigation(self, key):
        actions = {
            KEY_RIGHT: self.next_page,
            ord("l"): self.next_page,
            ord("L"): self.next_page,
            KEY_LEFT: self.previous_page,
            ord("h"): self.previous_page,
            KEY_DOWN: self.select_next_item,
            ord("j"): self.select_next_item,
            ord("J"): self.select_next_item,
            KEY_UP: self.select_previous_item,
            ord("k"): self.select_previous_item,
            ord("K"): self.select_previous_item,
            ord("g"): self.jump_top,
            ord("G"): self.jump_bottom,
            KEY_NPAGE: self.page_down,
            KEY_PPAGE: self.page_up,
        }
        action = actions.get(key)
        if action:
            action()

    @classmethod
    def handles(cls, key):
        return key in cls.HANDLED_KEYS
