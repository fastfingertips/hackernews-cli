"""Read-later queue behavior independent of terminal rendering."""

from dataclasses import dataclass

from ..data.events import OPEN_READING_LIST
from .story import StoryService


@dataclass(frozen=True)
class ReadingListOpenResult:
    selected_index: int
    opened_count: int


class ReadingListService:
    """Open unread queue entries while skipping completed activity."""

    def __init__(self, context):
        self.context = context
        self.stories = StoryService(context)

    def open_unread(self, entries, limit, selection_callback=None):
        unavailable = (
            self.context.history_repository.visited_urls()
            | self.context.read_repository.read_urls()
        )
        candidates = [
            entry
            for entry in entries
            if entry.url not in unavailable
        ]
        selected_index = 0
        for entry in candidates[:limit]:
            selected_index = entries.index(entry)
            if selection_callback:
                selection_callback(selected_index)
            self.stories.open_url(
                entry.url,
                entry.title,
                OPEN_READING_LIST,
            )
        return ReadingListOpenResult(
            selected_index=selected_index,
            opened_count=min(limit, len(candidates)),
        )
