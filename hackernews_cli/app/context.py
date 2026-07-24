"""Central dependency container for the application."""

from dataclasses import dataclass

from ..data import (
    Database,
    FavoriteRepository,
    HistoryRepository,
    ReadRepository,
    ReadingListRepository,
    SavedFilterRepository,
)
from ..services.pages import PageService
from .filtering import apply_filter


@dataclass
class ApplicationContext:
    """Own services and repositories shared across controllers."""

    page_service: object
    history_repository: object
    favorite_repository: object
    read_repository: object
    saved_filter_repository: object = None
    reading_list_repository: object = None

    @classmethod
    def create_default(cls):
        database = Database()
        return cls(
            page_service=PageService(),
            history_repository=HistoryRepository(database),
            favorite_repository=FavoriteRepository(database),
            read_repository=ReadRepository(database),
            saved_filter_repository=SavedFilterRepository(database),
            reading_list_repository=ReadingListRepository(database),
        )

    def visible_articles(self, page, filter_query=""):
        return apply_filter(
            page.articles,
            filter_query,
            self.history_repository.visited_urls(),
            self.favorite_repository.favorite_urls(),
            self.read_repository.read_urls(),
            (
                self.reading_list_repository.urls()
                if self.reading_list_repository is not None
                else set()
            ),
        )

    def activity_urls(self):
        return (
            self.history_repository.visited_urls()
            | self.favorite_repository.favorite_urls()
            | self.read_repository.read_urls()
            | (
                self.reading_list_repository.urls()
                if self.reading_list_repository is not None
                else set()
            )
        )

    def close(self):
        self.page_service.close()
