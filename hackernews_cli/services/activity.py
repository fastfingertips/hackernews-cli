"""Logged favorite/read actions and reversible activity events."""

from dataclasses import dataclass

from ..data.events import (
    FAVORITE_ADDED,
    FAVORITE_REMOVED,
    READ_MARKED,
    READ_UNMARKED,
    READ_LATER_ADDED,
    READ_LATER_REMOVED,
    REVERSIBLE_EVENTS,
)

@dataclass(frozen=True)
class UndoResult:
    success: bool
    message: str


class ActivityService:
    """Change user-managed story state while preserving an audit trail."""

    def __init__(self, context):
        self.history = context.history_repository
        self.favorites = context.favorite_repository
        self.reads = context.read_repository
        self.reading_list = context.reading_list_repository

    def toggle_favorite(self, article):
        if not article:
            return False
        added = self.favorites.toggle(article.link, article.title)
        self.history.add(
            article.link,
            article.title,
            FAVORITE_ADDED if added else FAVORITE_REMOVED,
        )
        return added

    def remove_favorite(self, url, title):
        if url not in self.favorites.favorite_urls():
            return False
        self.favorites.remove(url)
        self.history.add(url, title, FAVORITE_REMOVED)
        return True

    def toggle_read(self, article):
        if not article:
            return False
        return self.toggle_read_url(article.link, article.title)

    def toggle_read_url(self, url, title):
        marked = self.reads.toggle(url, title)
        self.history.add(
            url,
            title,
            READ_MARKED if marked else READ_UNMARKED,
        )
        return marked

    def toggle_read_later(self, article):
        if not article:
            return False
        added = self.reading_list.toggle(article.link, article.title)
        self.history.add(
            article.link,
            article.title,
            READ_LATER_ADDED if added else READ_LATER_REMOVED,
        )
        return added

    def remove_read_later(self, url, title):
        if not self.reading_list.remove(url):
            return False
        self.history.add(url, title, READ_LATER_REMOVED)
        return True

    def undo(self, entry):
        if entry.kind not in REVERSIBLE_EVENTS:
            return UndoResult(False, "Selected event cannot be undone")
        if self.history.is_reverted(entry.id):
            return UndoResult(False, "Selected event was already undone")
        if not self._state_matches(entry):
            return UndoResult(False, "Cannot undo: state changed later")

        inverse_kind = self._apply_inverse(entry)
        self.history.add(
            entry.url,
            entry.title,
            inverse_kind,
            reverted_event_id=entry.id,
        )
        return UndoResult(True, "Change undone")

    def _state_matches(self, entry):
        if entry.kind == FAVORITE_ADDED:
            return entry.url in self.favorites.favorite_urls()
        if entry.kind == FAVORITE_REMOVED:
            return entry.url not in self.favorites.favorite_urls()
        if entry.kind == READ_MARKED:
            return entry.url in self.reads.read_urls()
        if entry.kind == READ_UNMARKED:
            return entry.url not in self.reads.read_urls()
        if entry.kind == READ_LATER_ADDED:
            return entry.url in self.reading_list.urls()
        return entry.url not in self.reading_list.urls()

    def _apply_inverse(self, entry):
        if entry.kind == FAVORITE_ADDED:
            self.favorites.remove(entry.url)
            return FAVORITE_REMOVED
        if entry.kind == FAVORITE_REMOVED:
            self.favorites.add(entry.url, entry.title)
            return FAVORITE_ADDED
        if entry.kind == READ_MARKED:
            self.reads.mark_unread(entry.url)
            return READ_UNMARKED
        if entry.kind == READ_UNMARKED:
            self.reads.mark_read(entry.url, entry.title)
            return READ_MARKED
        if entry.kind == READ_LATER_ADDED:
            self.reading_list.remove(entry.url)
            return READ_LATER_REMOVED
        self.reading_list.add(entry.url, entry.title)
        return READ_LATER_ADDED
