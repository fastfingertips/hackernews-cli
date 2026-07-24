"""Compact tabular Hacker News story list."""

import curses

from ..terminal.drawing import safe_addstr, truncate_line
from ..terminal.colors import (
    FAVORITE_COLOR_PAIR,
    HEADER_COLOR_PAIR,
    MUTED_COLOR_PAIR,
    READ_COLOR_PAIR,
    READ_LATER_COLOR_PAIR,
    VISITED_COLOR_PAIR,
)
from ..time import relative_time


HEADER_HEIGHT = 2

RANK_WIDTH = 7
POINTS_WIDTH = 8
AGE_WIDTH = 10
FETCHED_WIDTH = 10
REPLIES_WIDTH = 8
VISITED_WIDTH = 9
FAVORITE_WIDTH = 9
READ_WIDTH = 9
READ_LATER_WIDTH = 9
MIN_LINK_WIDTH = 8
MINIMUM_WIDTH = (
    RANK_WIDTH
    + POINTS_WIDTH
    + AGE_WIDTH
    + FETCHED_WIDTH
    + REPLIES_WIDTH
    + VISITED_WIDTH
    + FAVORITE_WIDTH
    + READ_WIDTH
    + READ_LATER_WIDTH
    + MIN_LINK_WIDTH
)


def story_capacity(pane_height):
    """Return the story rows left after the table header."""
    return max(0, pane_height - HEADER_HEIGHT)


def _calc_scroll_offset(selected_index, total_items, pane_height):
    """Keep the selected story visible within the available rows."""
    visible_items = max(1, pane_height - HEADER_HEIGHT)
    return max(
        0,
        min(
            selected_index - visible_items // 2,
            max(0, total_items - visible_items),
        ),
    )


def display_article_list(
        stdscr,
        articles,
        selected_index,
        start_y,
        start_x,
        pane_width,
        pane_height,
        visited_dates=None,
        favorite_dates=None,
        read_dates=None,
        later_dates=None,
        loading_frame=None):
    """Render stories with submission age and local fetch freshness."""
    _draw_column_headers(stdscr, start_y, start_x, pane_width)

    if not articles:
        safe_addstr(
            stdscr,
            start_y + HEADER_HEIGHT,
            start_x + RANK_WIDTH,
            "No stories found.",
            curses.A_DIM,
        )
        return

    visited_dates = visited_dates or {}
    favorite_dates = favorite_dates or {}
    read_dates = read_dates or {}
    later_dates = later_dates or {}
    list_height = pane_height - (1 if loading_frame is not None else 0)
    scroll_offset = _calc_scroll_offset(selected_index, len(articles), list_height)
    visible_items = max(1, list_height - HEADER_HEIGHT)
    visible = articles[scroll_offset:scroll_offset + visible_items]

    for idx, article in enumerate(visible):
        actual_idx = scroll_offset + idx
        y = start_y + HEADER_HEIGHT + idx
        if y >= start_y + pane_height:
            break

        is_selected = (actual_idx == selected_index)
        marker = ">" if is_selected else "~" if article.is_cached else " "
        rank = article.rank or f"{actual_idx + 1}."
        rank_cell = f"{marker} {rank:>4} "
        points_cell = _number_from(article.score)
        age_cell = _short_age(
            relative_time(article.published_at)
            if article.published_at
            else article.age
        )
        fetched_cell = relative_time(article.fetched_at)
        replies_cell = _number_from(article.comments_count)
        visited_cell = relative_time(visited_dates.get(article.link))
        favorite_cell = relative_time(favorite_dates.get(article.link))
        later_cell = relative_time(later_dates.get(article.link))
        read_cell = relative_time(read_dates.get(article.link))

        domain = f" ({article.domain})" if article.domain else ""
        link_width = _link_width(pane_width)
        link_cell = truncate_line(
            f"{article.title}{domain}",
            link_width,
        )

        line = (
            f"{rank_cell:<{RANK_WIDTH}}"
            f"{points_cell:<{POINTS_WIDTH}}"
            f"{link_cell:<{link_width}}"
            f"{age_cell:<{AGE_WIDTH}}"
            f"{fetched_cell:<{FETCHED_WIDTH}}"
            f"{replies_cell:>{REPLIES_WIDTH - 1}} "
            f"{visited_cell:>{VISITED_WIDTH - 1}} "
            f"{favorite_cell:>{FAVORITE_WIDTH - 1}} "
            f"{later_cell:>{READ_LATER_WIDTH - 1}} "
            f"{read_cell:>{READ_WIDTH - 1}} "
        )
        selected_attr = (
            curses.color_pair(HEADER_COLOR_PAIR) | curses.A_BOLD
            if curses.has_colors()
            else curses.A_BOLD
        )
        visited_attr = (
            curses.color_pair(VISITED_COLOR_PAIR) | curses.A_DIM
            if curses.has_colors()
            else curses.A_DIM
        )
        favorite_attr = (
            curses.color_pair(FAVORITE_COLOR_PAIR) | curses.A_BOLD
            if curses.has_colors()
            else curses.A_BOLD
        )
        read_attr = (
            curses.color_pair(READ_COLOR_PAIR) | curses.A_DIM
            if curses.has_colors()
            else curses.A_DIM
        )
        later_attr = (
            curses.color_pair(READ_LATER_COLOR_PAIR) | curses.A_BOLD
            if curses.has_colors()
            else curses.A_BOLD
        )
        cached_attr = (
            curses.color_pair(MUTED_COLOR_PAIR) | curses.A_DIM
            if curses.has_colors()
            else curses.A_DIM
        )
        safe_addstr(
            stdscr,
            y,
            start_x,
            truncate_line(line, pane_width).ljust(pane_width),
            selected_attr
            if is_selected
            else favorite_attr
            if article.link in favorite_dates
            else later_attr
            if article.link in later_dates
            else read_attr
            if article.link in read_dates
            else visited_attr
            if article.link in visited_dates
            else cached_attr
            if article.is_cached
            else curses.A_NORMAL,
        )

    if loading_frame is not None and pane_height > HEADER_HEIGHT:
        spinner = ("|", "/", "-", "\\")[loading_frame % 4]
        loading_line = f"  {spinner} Loading next page..."
        safe_addstr(
            stdscr,
            start_y + pane_height - 1,
            start_x,
            truncate_line(loading_line, pane_width).ljust(pane_width),
            curses.A_DIM,
        )


def _draw_column_headers(stdscr, y, x, width):
    link_width = _link_width(width)
    header = (
        f"{'':<{RANK_WIDTH}}"
        f"{'Points':<{POINTS_WIDTH}}"
        f"{'Link':<{link_width}}"
        f"{'Age':<{AGE_WIDTH}}"
        f"{'Fetched':<{FETCHED_WIDTH}}"
        f"{'Replies':>{REPLIES_WIDTH - 1}} "
        f"{'Visited':>{VISITED_WIDTH - 1}} "
        f"{'Fav':>{FAVORITE_WIDTH - 1}} "
        f"{'Later':>{READ_LATER_WIDTH - 1}} "
        f"{'Read':>{READ_WIDTH - 1}} "
    )
    safe_addstr(stdscr, y, x, truncate_line(header, width), curses.A_DIM)


def _link_width(pane_width):
    reserved = (
        RANK_WIDTH
        + POINTS_WIDTH
        + AGE_WIDTH
        + FETCHED_WIDTH
        + REPLIES_WIDTH
        + VISITED_WIDTH
        + FAVORITE_WIDTH
        + READ_LATER_WIDTH
        + READ_WIDTH
    )
    return max(MIN_LINK_WIDTH, pane_width - reserved)


def _number_from(value):
    if not value:
        return "-"
    first_token = str(value).split(maxsplit=1)[0]
    return first_token if first_token.isdigit() else "-"


def _short_age(value):
    if not value:
        return "-"
    return value.removesuffix(" ago")
