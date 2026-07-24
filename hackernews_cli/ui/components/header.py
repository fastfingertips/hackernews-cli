"""Shared two-row header with global tab navigation."""

import curses
from ..terminal.colors import HEADER_COLOR_PAIR
from ..terminal.drawing import safe_addstr, truncate_line
from ..tabs import FEED_TAB_COUNT, TABS, normalize_tab_id


def _header_attrs():
    active = (
        curses.color_pair(HEADER_COLOR_PAIR) | curses.A_BOLD
        if curses.has_colors()
        else curses.A_REVERSE
    )
    brand = (
        curses.color_pair(HEADER_COLOR_PAIR) | curses.A_BOLD
        if curses.has_colors()
        else curses.A_BOLD
    )
    return brand, active, curses.A_DIM


def _draw_tabs(stdscr, region, active_tab):
    if region.height == 0:
        return

    brand_attr, active_attr, inactive_attr = _header_attrs()
    brand = "  hn  "
    safe_addstr(stdscr, region.y, 0, brand, brand_attr)

    compact = region.width < 110
    separator = " " if compact else " | "
    active_id = normalize_tab_id(active_tab)
    feed_tabs = TABS[:FEED_TAB_COUNT]
    local_tabs = TABS[FEED_TAB_COUNT:]

    def label_for(tab):
        return tab.compact_label if compact else tab.label

    def draw_group(tabs, x_offset):
        for index, tab in enumerate(tabs):
            label = label_for(tab)
            prefix = separator if index else ""
            if x_offset + len(prefix) + len(label) >= region.width:
                break
            if prefix:
                safe_addstr(
                    stdscr,
                    region.y,
                    x_offset,
                    prefix,
                    inactive_attr,
                )
                x_offset += len(prefix)
            attr = active_attr if tab.id == active_id else inactive_attr
            safe_addstr(stdscr, region.y, x_offset, label, attr)
            x_offset += len(label)
        return x_offset

    feed_end = draw_group(feed_tabs, len(brand))
    local_width = sum(
        len(label_for(tab))
        for tab in local_tabs
    ) + len(separator) * (len(local_tabs) - 1)
    local_x = max(feed_end + 1, region.width - local_width - 2)
    draw_group(local_tabs, local_x)


def draw_feed_header(
        stdscr,
        region,
        current_page,
        total_pages,
        filter_query,
        category,
        listed_count=None,
        visited_count=0,
        favorite_count=0,
        read_count=0,
        later_count=0):
    """Render a quiet, compact feed header."""
    if region.height == 0:
        return
    width = region.width
    inactive_attr = curses.A_DIM
    _draw_tabs(stdscr, region, category)

    stats = f"loaded {current_page}/{total_pages}"
    if listed_count is not None:
        stats = (
            f"{stats}  |  listed {listed_count}  |  visited {visited_count}  |  "
            f"fav {favorite_count}  |  later {later_count}  |  read {read_count}"
        )
    stats_x = max(2, width - len(stats) - 2)
    if stats and region.height > 1:
        safe_addstr(
            stdscr,
            region.y + 1,
            stats_x,
            truncate_line(stats, max(0, width - stats_x)),
            inactive_attr,
        )

    context = f"filter: {filter_query}" if filter_query else ""
    context_width = max(0, stats_x - 4)
    if region.height > 1:
        safe_addstr(
            stdscr,
            region.y + 1,
            2,
            context[:context_width],
            inactive_attr,
        )


def draw_page_header(
        stdscr,
        region,
        title,
        right_text="",
        context=""):
    """Render a consistent two-row header for secondary pages."""
    if region.height == 0:
        return
    active_id = normalize_tab_id(title)
    _draw_tabs(stdscr, region, active_id)
    rendered_right = ""
    right_x = region.width
    if right_text:
        right_limit = max(0, region.width // 2)
        rendered_right = truncate_line(right_text, right_limit)
        right_x = max(2, region.width - len(rendered_right) - 2)
    if region.height > 1:
        detail = f"{title}  |  {context}" if context else title
        safe_addstr(
            stdscr,
            region.y + 1,
            2,
            truncate_line(detail, max(0, right_x - 4)),
            curses.A_DIM,
        )
    if rendered_right:
        safe_addstr(
            stdscr,
            region.y + min(1, region.height - 1),
            right_x,
            rendered_right,
            curses.A_DIM,
        )
