"""Render the read-later management table."""

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
    TableColumn("Added", 12),
    TableColumn("Link"),
    TableColumn("Visited", 12),
    TableColumn("Read", 12),
)


def draw_reading_list(
        stdscr,
        entries,
        selected_index,
        status,
        filter_query,
        total_count,
        visited_dates,
        read_dates):
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
        if filter_query
        else f"read later {total_count}"
    )
    context = f"filter: {filter_query}" if filter_query else ""
    draw_page_header(stdscr, frame.header, "read later", count, context)

    if content.height:
        draw_table_header(stdscr, content.y, 0, content.width, COLUMNS)
    if not entries and content.height > 2:
        safe_addstr(stdscr, content.y + 2, 2, "Reading list is empty.", curses.A_DIM)
    elif entries:
        visible_count = max(0, content.height - 2)
        offset = max(0, min(
            selected_index - visible_count // 2,
            max(0, len(entries) - visible_count),
        ))
        for row, entry in enumerate(entries[offset:offset + visible_count]):
            index = offset + row
            draw_table_row(
                stdscr,
                content.y + 2 + row,
                0,
                content.width,
                COLUMNS,
                (
                    relative_time(entry.added_at),
                    f"{entry.title} ({entry.url})",
                    relative_time(visited_dates.get(entry.url)),
                    relative_time(read_dates.get(entry.url)),
                ),
                selected=index == selected_index,
                attr=selected_attr if index == selected_index else curses.A_NORMAL,
            )

    footer_text = status or (
        "CAPS ON  J/K move  enter open  R read  B open10  D remove  Q back"
        if caps_lock_enabled()
        else "j/k move  enter open  r read  b open5  t/d remove  / filter  q back"
    )
    draw_footer(
        stdscr,
        frame.footer,
        ("  left/right tabs", f"  {footer_text}"),
    )
    stdscr.refresh()
