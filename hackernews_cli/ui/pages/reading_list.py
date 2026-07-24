"""Interactive read-later queue."""

import curses

from ...app.record_filtering import filter_favorites
from ...data.events import OPEN_READING_LIST
from ...services import ActivityService, ReadingListService, StoryService
from ..components.reading_list_table import draw_reading_list
from ..terminal.prompts import show_record_filter


def show_reading_list(stdscr, context):
    repository = context.reading_list_repository
    activity = ActivityService(context)
    stories = StoryService(context)
    queue = ReadingListService(context)
    selected_index = 0
    status = ""
    filter_query = ""
    stdscr.timeout(-1)

    try:
        while True:
            all_entries = repository.list_entries()
            entries = filter_favorites(all_entries, filter_query)
            selected_index = min(selected_index, max(0, len(entries) - 1))
            visited_dates = context.history_repository.visited_dates()
            read_dates = context.read_repository.read_dates()
            draw_reading_list(
                stdscr,
                entries,
                selected_index,
                status,
                filter_query,
                len(all_entries),
                visited_dates,
                read_dates,
            )
            key = stdscr.getch()

            if key in (27, ord("q"), ord("Q"), ord("T")):
                return
            if key in (curses.KEY_DOWN, ord("j"), ord("J")) and entries:
                selected_index = min(selected_index + 1, len(entries) - 1)
            elif key in (curses.KEY_UP, ord("k"), ord("K")) and entries:
                selected_index = max(selected_index - 1, 0)
            elif key in (curses.KEY_ENTER, 10) and entries:
                entry = entries[selected_index]
                stories.open_url(entry.url, entry.title, OPEN_READING_LIST)
                status = "Opened read-later story"
            elif key in (ord("r"), ord("R")) and entries:
                entry = entries[selected_index]
                marked = activity.toggle_read_url(entry.url, entry.title)
                status = "Marked read" if marked else "Marked unread"
            elif key in (ord("t"), ord("d"), ord("D")) and entries:
                entry = entries[selected_index]
                activity.remove_read_later(entry.url, entry.title)
                status = "Removed from read later"
            elif key in (ord("b"), ord("B")) and entries:
                limit = 10 if key == ord("B") else 5
                def animate_selection(index):
                    nonlocal selected_index
                    selected_index = index
                    draw_reading_list(
                        stdscr,
                        entries,
                        selected_index,
                        "Opening unread stories...",
                        filter_query,
                        len(all_entries),
                        context.history_repository.visited_dates(),
                        context.read_repository.read_dates(),
                    )
                    curses.napms(35)

                result = queue.open_unread(
                    entries,
                    limit,
                    animate_selection,
                )
                selected_index = result.selected_index
                status = f"Opened {result.opened_count} unread stories"
            elif key == ord("/"):
                filter_query = show_record_filter(
                    stdscr,
                    "Filter read later",
                    (
                        'Example: title:"local first" -url:example.com',
                        "Fields: title: url:",
                        "Dates: after:2026-01-01 before:2027-01-01",
                    ),
                    filter_query,
                )
                selected_index = 0
                status = ""
            else:
                status = ""
    finally:
        stdscr.timeout(100)
