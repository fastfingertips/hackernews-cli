"""Render the favorites management table."""

import curses

from ..terminal.drawing import safe_addstr
from ..terminal.colors import FAVORITE_COLOR_PAIR, HEADER_COLOR_PAIR
from ..terminal.keyboard import caps_lock_enabled
from ..time import relative_time
from .footer import draw_footer
from .frame import PageFrame
from .header import draw_page_header
from .record_table import TableColumn, draw_table_header, draw_table_row


COLUMNS = (TableColumn("Added", 12), TableColumn("Link"))


def draw_favorites(
        stdscr,
        entries,
        selected_index,
        status,
        filter_query,
        total_count,
        visited_urls=None,
        read_urls=None):
    stdscr.erase()
    frame = PageFrame.from_screen(stdscr)
    content = frame.content
    width = content.width
    header_attr = (
        curses.color_pair(FAVORITE_COLOR_PAIR) | curses.A_BOLD
        if curses.has_colors() else curses.A_BOLD
    )
    selected_attr = (
        curses.color_pair(HEADER_COLOR_PAIR) | curses.A_BOLD
        if curses.has_colors() else curses.A_BOLD
    )
    visible_urls = {entry.url for entry in entries}
    visited_count = len(visible_urls.intersection(visited_urls or set()))
    read_count = len(visible_urls.intersection(read_urls or set()))
    prefix = (
        f"shown {len(entries)}/{total_count}"
        if filter_query else f"favorites {total_count}"
    )
    count = f"{prefix}  |  visited {visited_count}  |  read {read_count}"
    context = f"filter: {filter_query}" if filter_query else ""
    draw_page_header(stdscr, frame.header, "favorites", count, context)

    if content.height:
        draw_table_header(stdscr, content.y, 0, width, COLUMNS)
    if not entries and content.height > 2:
        safe_addstr(
            stdscr,
            content.y + 2,
            2,
            "No favorite stories.",
            curses.A_DIM,
        )
    elif entries:
        _draw_rows(stdscr, entries, selected_index, content, selected_attr)

    footer_text = status or (
        "CAPS ON  J/K move  enter open  / filter  D remove  Q back"
        if caps_lock_enabled()
        else "j/k move  enter open  / filter  f/d remove  q back"
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
            (relative_time(entry.added_at), f"{entry.title} ({entry.url})"),
            selected=index == selected_index,
            attr=selected_attr if index == selected_index else curses.A_NORMAL,
        )
