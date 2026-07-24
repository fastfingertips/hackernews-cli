"""Color palette initialization for the terminal UI."""

import curses


HEADER_COLOR_PAIR = 1
VISITED_COLOR_PAIR = 2
FAVORITE_COLOR_PAIR = 3
READ_COLOR_PAIR = 4
MUTED_COLOR_PAIR = 5
DEFAULT_COLOR_PAIR = 6
READ_LATER_COLOR_PAIR = 7


def init_colors():
    """Initialize curses color pairs for the application."""
    if curses.has_colors():
        try:
            curses.start_color()
            curses.use_default_colors()
            curses.init_pair(DEFAULT_COLOR_PAIR, -1, -1)
            curses.init_pair(
                HEADER_COLOR_PAIR,
                curses.COLOR_YELLOW,
                -1,
            )
            curses.init_pair(
                VISITED_COLOR_PAIR,
                curses.COLOR_CYAN,
                -1,
            )
            curses.init_pair(
                FAVORITE_COLOR_PAIR,
                curses.COLOR_GREEN,
                -1,
            )
            curses.init_pair(
                READ_COLOR_PAIR,
                curses.COLOR_MAGENTA,
                -1,
            )
            curses.init_pair(
                MUTED_COLOR_PAIR,
                curses.COLOR_WHITE,
                -1,
            )
            curses.init_pair(
                READ_LATER_COLOR_PAIR,
                curses.COLOR_BLUE,
                -1,
            )
        except curses.error:
            pass


def apply_default_background(window):
    """Make blank and unstyled cells use the terminal's own colors."""
    if not curses.has_colors():
        return
    try:
        window.bkgd(" ", curses.color_pair(DEFAULT_COLOR_PAIR))
    except curses.error:
        pass
