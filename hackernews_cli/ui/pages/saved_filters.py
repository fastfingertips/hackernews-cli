"""Interactive reusable-filter library."""

import curses

from ..components.saved_filters_table import draw_saved_filters
from ..terminal.prompts import (
    show_feed_filter,
    show_filter_name,
    show_record_filter,
)
from ..tabs import switch_for_key


def show_saved_filters(stdscr, repository, active_query=""):
    """Manage saved filters and return the query selected for application."""
    selected_index = 0
    status = ""
    search_query = ""
    stdscr.timeout(-1)

    try:
        while True:
            all_entries = repository.list_entries()
            entries = _search(all_entries, search_query)
            selected_index = min(
                selected_index,
                max(0, len(entries) - 1),
            )
            draw_saved_filters(
                stdscr,
                entries,
                selected_index,
                status,
                search_query,
                len(all_entries),
                active_query,
            )
            key = stdscr.getch()

            tab_switch = switch_for_key("filters", key)
            if tab_switch:
                return tab_switch
            if key in (27, ord("q"), ord("Q"), ord("S")):
                return None
            if key in (curses.KEY_DOWN, ord("j"), ord("J")) and entries:
                selected_index = min(selected_index + 1, len(entries) - 1)
            elif key in (curses.KEY_UP, ord("k"), ord("K")) and entries:
                selected_index = max(selected_index - 1, 0)
            elif key in (curses.KEY_ENTER, 10) and entries:
                return entries[selected_index].query
            elif key in (ord("n"), ord("N")):
                active_query, status = _save_new(
                    stdscr,
                    repository,
                    active_query,
                )
            elif key in (ord("e"), ord("E")) and entries:
                entry = entries[selected_index]
                if entry.is_builtin:
                    status = "Built-in filters are read-only"
                else:
                    query = show_feed_filter(stdscr, entry.query)
                    if query == entry.query:
                        status = ""
                    elif repository.update_query(entry.id, query):
                        status = "Updated custom filter"
                    else:
                        status = "Filter query cannot be empty"
            elif key in (ord("d"), ord("D")) and entries:
                entry = entries[selected_index]
                status = (
                    "Deleted custom filter"
                    if repository.remove(entry.id)
                    else "Built-in filters cannot be deleted"
                )
            elif key == ord("/"):
                search_query = show_record_filter(
                    stdscr,
                    "Search saved filters",
                    (
                        "Search names, queries, or type.",
                        "Examples: unread, points:>=100, custom",
                    ),
                    search_query,
                )
                selected_index = 0
                status = ""
            else:
                status = ""
    finally:
        stdscr.timeout(100)


def save_active_filter(stdscr, repository, active_query):
    """Save the current feed filter, asking for missing query and name."""
    query = active_query or show_feed_filter(stdscr)
    if not query:
        return active_query, False

    name = show_filter_name(stdscr)
    if not name:
        return query, False
    return query, repository.save(name, query)


def _save_new(stdscr, repository, active_query):
    query, saved = save_active_filter(
        stdscr,
        repository,
        active_query,
    )
    return query, "Saved custom filter" if saved else "Filter was not saved"


def _search(entries, query):
    words = query.casefold().split()
    if not words:
        return entries
    return [
        entry
        for entry in entries
        if all(
            word in " ".join((
                entry.name,
                entry.query,
                "built-in" if entry.is_builtin else "custom",
            )).casefold()
            for word in words
        )
    ]
