"""Render application identity and runtime information."""

import curses
import platform

from ... import __version__
from ..terminal.drawing import safe_addstr, truncate_line
from .footer import draw_footer
from .header import draw_page_header


REPOSITORY_URL = "https://github.com/fastfingertips/hackernews-cli"


def draw_about(stdscr, frame):
    """Draw About content inside the shared page frame."""
    stdscr.erase()
    draw_page_header(
        stdscr,
        frame.header,
        "about",
        f"version {__version__}",
        "Local-first Hacker News terminal client",
    )

    lines = (
        ("Application", "HackerNews CLI"),
        ("Version", __version__),
        ("Purpose", "Browse and manage Hacker News activity in a terminal"),
        ("Storage", "Local SQLite; cloud sync disabled"),
        ("Python", platform.python_version()),
        ("Platforms", "Windows, Linux, macOS"),
        ("Repository", REPOSITORY_URL),
    )
    start_y = frame.content.y + 1
    label_width = 14
    for index, (label, value) in enumerate(lines):
        y = start_y + index
        if y >= frame.content.end_y:
            break
        safe_addstr(
            stdscr,
            y,
            2,
            truncate_line(
                f"{label:<{label_width}}{value}",
                max(0, frame.content.width - 4),
            ),
            curses.A_NORMAL,
        )

    draw_footer(
        stdscr,
        frame.footer,
        (
            "  g open GitHub repository",
            "  i/q back",
        ),
    )
    stdscr.refresh()
