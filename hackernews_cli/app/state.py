"""Mutable feed state owned by the application."""

from dataclasses import dataclass


@dataclass
class FeedState:
    page: object
    selected_index: int = 0
    filter_query: str = ""

    @property
    def current_page(self):
        return self.page.current_page

    @property
    def category(self):
        return self.page.category

    def reset_selection(self):
        self.selected_index = 0
