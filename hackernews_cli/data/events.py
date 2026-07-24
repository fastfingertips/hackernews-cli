"""Stable activity event names persisted in SQLite."""


OPEN_ARTICLE = "article"
OPEN_COMMENTS = "comments"
OPEN_FAVORITE = "favorite"
OPEN_BULK = "bulk"
OPEN_HISTORY = "history"
OPEN_READING_LIST = "reading_list"

FAVORITE_ADDED = "favorite_added"
FAVORITE_REMOVED = "favorite_removed"
READ_MARKED = "read_marked"
READ_UNMARKED = "read_unmarked"
READ_LATER_ADDED = "read_later_added"
READ_LATER_REMOVED = "read_later_removed"

VISIT_EVENTS = (
    OPEN_ARTICLE,
    OPEN_COMMENTS,
    OPEN_FAVORITE,
    OPEN_BULK,
    OPEN_HISTORY,
    OPEN_READING_LIST,
)
REVERSIBLE_EVENTS = frozenset((
    FAVORITE_ADDED,
    FAVORITE_REMOVED,
    READ_MARKED,
    READ_UNMARKED,
    READ_LATER_ADDED,
    READ_LATER_REMOVED,
))
