"""Bottom keybinding hints bar."""

import curses
from ..terminal.drawing import safe_addstr, truncate_line
from ..terminal.colors import MUTED_COLOR_PAIR
from ..terminal.keyboard import caps_lock_enabled


def draw_footer(stdscr, region, left_text, right_text=""):
    """Render navigation hints entirely inside the footer region."""
    if region.height == 0:
        return
    muted_attr = (
        curses.color_pair(MUTED_COLOR_PAIR)
        if curses.has_colors()
        else curses.A_DIM
    )
    safe_addstr(stdscr, region.y, 0, "-" * region.width, muted_attr)
    if region.height == 1:
        return

    lines = (
        list(left_text)
        if isinstance(left_text, (tuple, list))
        else [left_text]
    )
    available_lines = max(0, region.height - 1)
    visible_lines = lines[:available_lines]
    rendered_right = truncate_line(right_text, region.width)
    right_row = max(0, len(visible_lines) - 1)
    for index, line in enumerate(visible_lines):
        reserved = len(rendered_right) if index == right_row else 0
        safe_addstr(
            stdscr,
            region.y + 1 + index,
            0,
            truncate_line(
                line,
                max(0, region.width - reserved),
            ),
            curses.A_DIM,
        )
    if rendered_right:
        safe_addstr(
            stdscr,
            region.y + 1 + right_row,
            max(0, region.width - len(rendered_right)),
            rendered_right,
            curses.A_DIM,
        )


def draw_feed_footer(stdscr, region):
    """Render Caps Lock-aware navigation for the main feed."""
    if caps_lock_enabled():
        lines = (
            "  CAPS ON  T read later  A load all  S filters"
            "  F favorites  H history  B open10",
            "  G bottom  J/K/L move  Enter open  I about  D data  U refresh",
        )
        right = "Q quit  "
    else:
        lines = (
            "  caps off  t later  a load all  / filter  s save"
            "  f fav  r read  b open5",
            "  j/k/l move  enter open  i about  d data  u refresh",
        )
        right = "q quit  "
    draw_footer(stdscr, region, lines, right)
