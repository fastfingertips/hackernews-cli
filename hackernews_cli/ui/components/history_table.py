"""Render the history management table."""

import curses

from ...app.record_filtering import action_label
from .footer import draw_footer
from .frame import PageFrame
from .header import draw_page_header
from ..terminal.drawing import safe_addstr
from ..terminal.colors import HEADER_COLOR_PAIR
from ..terminal.keyboard import caps_lock_enabled
from ..time import full_relative_time
from .record_table import TableColumn, draw_table_header, draw_table_row


COLUMNS = (
    TableColumn("Time (local)", 34),
    TableColumn("Action", 24),
    TableColumn("Link"),
)


def draw_history(
        stdscr,
        entries,
        selected_index,
        status,
        filter_query,
        total_count,
        all_urls=None,
        read_urls=None,
        activity_stats=None):
    stdscr.erase()
    frame = PageFrame.from_screen(stdscr)
    content = frame.content
    width = content.width
    header_attr = (
        curses.color_pair(HEADER_COLOR_PAIR) | curses.A_BOLD
        if curses.has_colors() else curses.A_BOLD
    )
    all_urls = all_urls or set()
    read_urls = read_urls or set()
    visible_urls = {entry.url for entry in entries}
    visible_read = len(visible_urls.intersection(read_urls))
    count = _count_text(
        entries,
        total_count,
        filter_query,
        visible_urls,
        all_urls,
        visible_read,
    )
    context = _activity_text(activity_stats)
    if filter_query:
        context = f"filter: {filter_query}  |  {context}" if context else (
            f"filter: {filter_query}"
        )
    draw_page_header(stdscr, frame.header, "history", count, context)

    if content.height:
        draw_table_header(stdscr, content.y, 0, width, COLUMNS)
    if not entries and content.height > 2:
        safe_addstr(
            stdscr,
            content.y + 2,
            2,
            "No activity events.",
            curses.A_DIM,
        )
    elif entries:
        _draw_rows(stdscr, entries, selected_index, content, header_attr)

    footer_text = status or (
        "CAPS ON  J/K move  enter open  U undo  / filter  D delete  Q back"
        if caps_lock_enabled()
        else "j/k move  enter open  u undo  / filter  d delete  c clear  q back"
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
                full_relative_time(entry.visited_at),
                action_label(entry.kind, entry.reverted_event_id),
                f"{entry.title} ({entry.url})",
            ),
            selected=index == selected_index,
            attr=selected_attr if index == selected_index else curses.A_NORMAL,
        )


def _count_text(entries, total, query, visible_urls, all_urls, read_count):
    if query:
        return (
            f"shown {len(entries)}/{total}  |  "
            f"unique {len(visible_urls)}/{len(all_urls)}  |  read {read_count}"
        )
    return f"events {total}  |  unique {len(all_urls)}  |  read {read_count}"


def _activity_text(stats):
    if not stats:
        return ""
    return (
        f"reads  1h {stats.last_hour}  |  today {stats.today}  |  "
        f"week {stats.this_week}  |  year {stats.this_year}"
    )
