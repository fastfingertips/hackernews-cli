"""Interactive favorites management screen."""

import curses
import webbrowser

from ...app.record_filtering import filter_favorites
from ...data.events import OPEN_FAVORITE
from ...services import ActivityService
from ..components.favorites_table import draw_favorites
from ..terminal.prompts import show_record_filter


def show_favorites(
        stdscr,
        context):
    """Browse, open, and remove favorite stories."""
    favorite_repository = context.favorite_repository
    history_repository = context.history_repository
    read_repository = context.read_repository
    activity_service = ActivityService(context)
    selected_index = 0
    status = ""
    filter_query = ""
    stdscr.timeout(-1)

    try:
        while True:
            all_entries = favorite_repository.list_entries()
            entries = filter_favorites(all_entries, filter_query)
            selected_index = min(
                selected_index,
                max(0, len(entries) - 1),
            )
            draw_favorites(
                stdscr,
                entries,
                selected_index,
                status,
                filter_query,
                len(all_entries),
                history_repository.visited_urls(),
                read_repository.read_urls(),
            )
            key = stdscr.getch()

            if key in (27, ord("q"), ord("Q"), ord("F")):
                return
            if key in (curses.KEY_DOWN, ord("j"), ord("J")) and entries:
                selected_index = min(selected_index + 1, len(entries) - 1)
            elif key in (curses.KEY_UP, ord("k"), ord("K")) and entries:
                selected_index = max(selected_index - 1, 0)
            elif key in (curses.KEY_ENTER, 10) and entries:
                entry = entries[selected_index]
                webbrowser.open(entry.url)
                history_repository.add(entry.url, entry.title, OPEN_FAVORITE)
                status = "Opened favorite"
            elif key in (ord("d"), ord("D"), ord("f")) and entries:
                entry = entries[selected_index]
                activity_service.remove_favorite(entry.url, entry.title)
                status = "Removed favorite"
            elif key == ord("/"):
                filter_query = show_record_filter(
                    stdscr,
                    "filter favorites",
                    (
                        'Example: title:"local first" -url:example.com',
                        "Fields: title: url:",
                        "Dates: after:2026-01-01 before:2027-01-01",
                        "Free text, quoted phrases, and -negation are supported",
                    ),
                    filter_query,
                )
                selected_index = 0
                status = ""
            else:
                status = ""
    finally:
        stdscr.timeout(100)
