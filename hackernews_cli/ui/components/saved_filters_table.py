"""Render reusable filters in the shared management-table layout."""

import curses

from ..terminal.colors import HEADER_COLOR_PAIR
from ..terminal.drawing import safe_addstr
from ..terminal.keyboard import caps_lock_enabled
from ..time import relative_time
from .footer import draw_footer
from .frame import PageFrame
from .header import draw_page_header
from .record_table import TableColumn, draw_table_header, draw_table_row


COLUMNS = (
    TableColumn("Type", 10),
    TableColumn("Name", 24),
    TableColumn("Query"),
    TableColumn("Updated", 12),
)


def draw_saved_filters(
        stdscr,
        entries,
        selected_index,
        status,
        search_query,
        total_count,
        active_query):
    stdscr.erase()
    frame = PageFrame.from_screen(stdscr)
    content = frame.content
    selected_attr = (
        curses.color_pair(HEADER_COLOR_PAIR) | curses.A_BOLD
        if curses.has_colors()
        else curses.A_BOLD
    )
    count = (
        f"shown {len(entries)}/{total_count}"
        if search_query
        else f"filters {total_count}"
    )
    context_parts = []
    if active_query:
        context_parts.append(f"active: {active_query}")
    if search_query:
        context_parts.append(f"search: {search_query}")
    draw_page_header(
        stdscr,
        frame.header,
        "saved filters",
        count,
        "  |  ".join(context_parts),
    )

    if content.height:
        draw_table_header(stdscr, content.y, 0, content.width, COLUMNS)
    if not entries and content.height > 2:
        safe_addstr(
            stdscr,
            content.y + 2,
            2,
            "No saved filters.",
            curses.A_DIM,
        )
    elif entries:
        _draw_rows(stdscr, entries, selected_index, content, selected_attr)

    footer_text = status or (
        "CAPS ON  J/K move  enter apply  N new  E edit  D delete  Q back"
        if caps_lock_enabled()
        else "j/k move  enter apply  n new  e edit  d delete  / search  q back"
    )
    draw_footer(
        stdscr,
        frame.footer,
        ("  left/right tabs", f"  {footer_text}"),
    )
    stdscr.refresh()


def _draw_rows(stdscr, entries, selected_index, region, selected_attr):
    visible_count = max(0, region.height - 2)
    if visible_count == 0:
        return
    offset = max(0, min(
        selected_index - visible_count // 2,
        max(0, len(entries) - visible_count),
    ))
    for row, entry in enumerate(entries[offset:offset + visible_count]):
        index = offset + row
        draw_table_row(
            stdscr,
            region.y + 2 + row,
            0,
            region.width,
            COLUMNS,
            (
                "built-in" if entry.is_builtin else "custom",
                entry.name,
                entry.query,
                relative_time(entry.updated_at),
            ),
            selected=index == selected_index,
            attr=selected_attr if index == selected_index else curses.A_NORMAL,
        )
