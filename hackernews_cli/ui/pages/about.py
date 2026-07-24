"""Interactive About screen."""

import webbrowser

from ..components.about_panel import REPOSITORY_URL, draw_about
from ..components.frame import PageFrame
from ..tabs import switch_for_key


def show_about(stdscr):
    """Show application information until the user returns."""
    stdscr.timeout(-1)
    try:
        while True:
            draw_about(stdscr, PageFrame.from_screen(stdscr))
            key = stdscr.getch()
            tab_switch = switch_for_key("about", key)
            if tab_switch:
                return tab_switch
            if key in (27, ord("q"), ord("Q"), ord("i"), ord("I")):
                return
            if key in (ord("g"), ord("G")):
                webbrowser.open(REPOSITORY_URL)
    finally:
        stdscr.timeout(100)
