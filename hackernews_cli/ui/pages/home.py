"""Compose and render the main feed screen."""

from ...hn.categories import DEFAULT_CATEGORY
from ..components import (
    MINIMUM_WIDTH,
    PageFrame,
    display_article_list,
    draw_feed_footer,
    draw_feed_header,
    story_capacity,
)
from ..terminal.decorators import clear_screen
from ..terminal.drawing import safe_addstr


def home_story_capacity(stdscr):
    """Return the number of story rows available in the current frame."""
    frame = PageFrame.from_screen(stdscr)
    return story_capacity(frame.content.height)


@clear_screen
def draw_home(
        stdscr,
        articles,
        selected_index,
        current_page,
        total_pages,
        filter_query: str = "",
        category: str = DEFAULT_CATEGORY,
        visited_dates=None,
        favorite_dates=None,
        read_dates=None,
        later_dates=None,
        loading_frame=None):
    """Draw the home screen without waiting for keyboard input."""
    frame = PageFrame.from_screen(stdscr)
    width = frame.content.width

    if frame.content.height < 6 or width < MINIMUM_WIDTH:
        safe_addstr(stdscr, 0, 0, "Terminal window is too small!")
        return

    visited_dates = visited_dates or {}
    favorite_dates = favorite_dates or {}
    read_dates = read_dates or {}
    later_dates = later_dates or {}
    links = {article.link for article in articles}
    draw_feed_header(
        stdscr,
        frame.header,
        current_page,
        total_pages,
        filter_query,
        category,
        listed_count=len(articles),
        visited_count=len(links.intersection(visited_dates)),
        favorite_count=len(links.intersection(favorite_dates)),
        read_count=len(links.intersection(read_dates)),
        later_count=len(links.intersection(later_dates)),
        cached_count=sum(article.is_cached for article in articles),
    )

    display_article_list(
        stdscr,
        articles,
        selected_index,
        start_y=frame.content.y,
        start_x=0,
        pane_width=width,
        pane_height=frame.content.height,
        visited_dates=visited_dates,
        favorite_dates=favorite_dates,
        read_dates=read_dates,
        later_dates=later_dates,
        loading_frame=loading_frame,
    )

    draw_feed_footer(stdscr, frame.footer)


def show_home(
        stdscr,
        articles,
        selected_index,
        current_page,
        total_pages,
        filter_query: str = "",
        category: str = DEFAULT_CATEGORY,
        visited_dates=None,
        favorite_dates=None,
        read_dates=None,
        later_dates=None,
        loading_frame=None):
    """Draw the home screen and wait for one keyboard event."""
    draw_home(
        stdscr,
        articles,
        selected_index,
        current_page,
        total_pages,
        filter_query,
        category,
        visited_dates,
        favorite_dates,
        read_dates,
        later_dates,
        loading_frame,
    )

    return stdscr.getch()
