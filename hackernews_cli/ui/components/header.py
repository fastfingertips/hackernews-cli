"""Minimal top bar with category navigation and pagination."""

import curses
from ...hn.categories import CATEGORIES
from ..terminal.colors import HEADER_COLOR_PAIR
from ..terminal.drawing import safe_addstr, truncate_line


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
    brand = "  hn  "
    brand_attr = (
        curses.color_pair(HEADER_COLOR_PAIR) | curses.A_BOLD
        if curses.has_colors()
        else curses.A_BOLD
    )
    active_attr = (
        curses.color_pair(HEADER_COLOR_PAIR) | curses.A_BOLD
        if curses.has_colors()
        else curses.A_REVERSE
    )
    inactive_attr = curses.A_DIM

    safe_addstr(stdscr, region.y, 0, brand, brand_attr)

    x_offset = len(brand)
    for index, cat in enumerate(CATEGORIES):
        if index:
            safe_addstr(stdscr, region.y, x_offset, "  |  ", inactive_attr)
            x_offset += 5

        label = cat
        if x_offset + len(label) >= width - 12:
            break

        attr = active_attr if cat == category.lower() else inactive_attr
        safe_addstr(stdscr, region.y, x_offset, label, attr)
        x_offset += len(label)

    page_info = f"loaded {current_page}/{total_pages}"
    page_x = max(x_offset + 2, width - len(page_info) - 2)
    if page_x + len(page_info) < width:
        safe_addstr(stdscr, region.y, page_x, page_info, inactive_attr)

    stats = ""
    if listed_count is not None:
        stats = (
            f"listed {listed_count}  |  visited {visited_count}  |  "
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
    title_attr = (
        curses.color_pair(HEADER_COLOR_PAIR) | curses.A_BOLD
        if curses.has_colors()
        else curses.A_BOLD
    )
    rendered_right = ""
    right_x = region.width
    if right_text:
        right_limit = max(0, region.width - len(title) - 8)
        rendered_right = truncate_line(right_text, right_limit)
        right_x = max(2, region.width - len(rendered_right) - 2)
    safe_addstr(
        stdscr,
        region.y,
        2,
        truncate_line(title, max(0, right_x - 4)),
        title_attr,
    )
    if rendered_right:
        safe_addstr(
            stdscr,
            region.y,
            right_x,
            rendered_right,
            curses.A_DIM,
        )
    if context and region.height > 1:
        safe_addstr(
            stdscr,
            region.y + 1,
            2,
            context[:max(0, region.width - 4)],
            curses.A_DIM,
        )
