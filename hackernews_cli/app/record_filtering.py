"""Filter history and favorite records."""

from datetime import date, datetime

from ..data.events import (
    FAVORITE_ADDED,
    FAVORITE_REMOVED,
    OPEN_ARTICLE,
    OPEN_BULK,
    OPEN_COMMENTS,
    OPEN_FAVORITE,
    OPEN_HISTORY,
    READ_MARKED,
    READ_UNMARKED,
    READ_LATER_ADDED,
    READ_LATER_REMOVED,
    OPEN_READING_LIST,
)
from .filter_query import parse_query

def action_label(kind, reverted_event_id=None):
    labels = {
        OPEN_ARTICLE: "Opened article",
        OPEN_COMMENTS: "Opened comments",
        OPEN_FAVORITE: "Opened from favorites",
        OPEN_BULK: "Opened in bulk",
        OPEN_HISTORY: "Opened from history",
        FAVORITE_ADDED: "Added favorite",
        FAVORITE_REMOVED: "Removed favorite",
        READ_MARKED: "Marked read",
        READ_UNMARKED: "Marked unread",
        READ_LATER_ADDED: "Added to read later",
        READ_LATER_REMOVED: "Removed from read later",
        OPEN_READING_LIST: "Opened from read later",
    }
    label = labels.get(kind, kind.replace("_", " ").title())
    return f"Undo: {label}" if reverted_event_id else label


def filter_history(entries, query):
    if not query:
        return entries
    return [
        entry for entry in entries
        if all(
            _matches_history_term(entry, term)
            for term in parse_query(query)
        )
    ]


def filter_favorites(entries, query):
    if not query:
        return entries
    return [
        entry for entry in entries
        if all(
            _matches_favorite_term(entry, term)
            for term in parse_query(query)
        )
    ]


def _matches_history_term(entry, term):
    action = action_label(entry.kind, entry.reverted_event_id)
    fields = {
        None: lambda: _contains(
            term.value,
            entry.title,
            entry.url,
            action,
            entry.visited_at,
            _local_time(entry.visited_at),
        ),
        "title": lambda: term.value in entry.title.lower(),
        "url": lambda: term.value in entry.url.lower(),
        "action": lambda: term.value in action.lower(),
        "after": lambda: _matches_date(
            entry.visited_at,
            term.value,
            after=True,
        ),
        "before": lambda: _matches_date(
            entry.visited_at,
            term.value,
            after=False,
        ),
    }
    return _apply_negation(term, fields)


def _matches_favorite_term(entry, term):
    fields = {
        None: lambda: _contains(
            term.value,
            entry.title,
            entry.url,
            entry.added_at,
            _local_time(entry.added_at),
        ),
        "title": lambda: term.value in entry.title.lower(),
        "url": lambda: term.value in entry.url.lower(),
        "after": lambda: _matches_date(
            entry.added_at,
            term.value,
            after=True,
        ),
        "before": lambda: _matches_date(
            entry.added_at,
            term.value,
            after=False,
        ),
    }
    return _apply_negation(term, fields)


def _apply_negation(term, fields):
    matcher = fields.get(term.field)
    matched = matcher() if matcher else False
    return not matched if term.negated else matched


def _contains(query, *values):
    return any(query in (value or "").lower() for value in values)


def _matches_date(timestamp, value, after):
    try:
        event_date = datetime.fromisoformat(timestamp).date()
        boundary = date.fromisoformat(value)
    except ValueError:
        return False
    return event_date >= boundary if after else event_date < boundary


def _local_time(value):
    try:
        return datetime.fromisoformat(value).astimezone().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    except ValueError:
        return value
