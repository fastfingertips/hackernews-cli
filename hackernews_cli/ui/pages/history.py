"""Interactive browsing-history screen."""

import curses
import webbrowser

from ...app.record_filtering import filter_history
from ...data.events import OPEN_HISTORY
from ...services import ActivityService
from ..components.history_table import draw_history
from ..terminal.prompts import show_record_filter
from ..tabs import switch_for_key


def show_history(stdscr, context):
    """Browse the activity log and undo reversible state changes."""
    history_repository = context.history_repository
    read_repository = context.read_repository
    activity_service = ActivityService(context)
    selected_index = 0
    confirm_clear = False
    status = ""
    filter_query = ""
    stdscr.timeout(-1)

    try:
        while True:
            all_entries = history_repository.list_entries()
            entries = filter_history(all_entries, filter_query)
            selected_index = min(
                selected_index,
                max(0, len(entries) - 1),
            )
            draw_history(
                stdscr,
                entries,
                selected_index,
                status,
                filter_query,
                len(all_entries),
                {entry.url for entry in all_entries},
                read_repository.read_urls(),
                history_repository.activity_stats(),
            )
            key = stdscr.getch()

            tab_switch = switch_for_key("history", key)
            if tab_switch:
                return tab_switch
            if key in (27, ord("q"), ord("Q"), ord("H")):
                return
            if key in (curses.KEY_DOWN, ord("j"), ord("J")) and entries:
                selected_index = min(selected_index + 1, len(entries) - 1)
            elif key in (curses.KEY_UP, ord("k"), ord("K")) and entries:
                selected_index = max(selected_index - 1, 0)
            elif key in (curses.KEY_ENTER, 10) and entries:
                entry = entries[selected_index]
                webbrowser.open(entry.url)
                history_repository.add(entry.url, entry.title, OPEN_HISTORY)
                status = "Opened URL"
            elif key in (ord("u"), ord("U")) and entries:
                result = activity_service.undo(entries[selected_index])
                status = result.message
            elif key in (ord("d"), ord("D")) and entries:
                history_repository.delete(entries[selected_index].id)
                status = "Deleted selected entry"
            elif key == ord("c"):
                if confirm_clear:
                    history_repository.clear()
                    selected_index = 0
                    confirm_clear = False
                    status = "History cleared"
                else:
                    confirm_clear = True
                    status = "Press c again to clear all history"
                continue
            elif key == ord("/"):
                filter_query = show_record_filter(
                    stdscr,
                    "filter history",
                    (
                        'Example: action:favorite url:github.com -action:opened',
                        "Fields: title: url: action:",
                        "Dates: after:2026-01-01 before:2027-01-01",
                        "Quoted phrases and -negation are supported",
                    ),
                    filter_query,
                )
                selected_index = 0
                status = ""
            else:
                status = ""
            confirm_clear = False
    finally:
        stdscr.timeout(100)
