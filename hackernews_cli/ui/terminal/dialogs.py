"""Modal dialog windows and help rendering."""

import curses
import time

from .colors import apply_default_background


def show_info(stdscr, message, title="Info", display_time=2):
    """Show a timed informational popup in the center of the screen."""
    height, width = stdscr.getmaxyx()
    padding = 2
    box_width = max(len(message) + 2 * padding, len(title) + 2 * padding)
    box_height = 5
    start_y = height // 2 - box_height // 2
    start_x = width // 2 - box_width // 2

    info_win = curses.newwin(box_height, box_width, start_y, start_x)
    apply_default_background(info_win)
    info_win.box()
    info_win.addstr(1, padding, title, curses.A_BOLD)
    info_win.addstr(3, padding, message)
    info_win.refresh()

    time.sleep(display_time)
    info_win.clear()
    stdscr.refresh()


def show_info_with_cancel(stdscr, message, title, display_time=2):
    """
    Show a timed info window that can be cancelled with Escape.

    Returns True if the user cancelled, False otherwise.
    """
    height, width = stdscr.getmaxyx()
    window_height = 7
    window_width = max(len(title) + 4, len(message) + 4)

    win = curses.newwin(
        window_height, window_width,
        height // 2 - window_height // 2,
        width // 2 - window_width // 2
    )
    apply_default_background(win)
    win.box()
    title_line = f" {title} "
    win.addstr(1, (window_width - len(title_line)) // 2, title_line, curses.A_BOLD)

    for i, line in enumerate(message.split('\n')):
        if i < window_height - 3:
            win.addstr(i + 2, 2, line[:window_width - 4])

    win.refresh()
    start_time = time.time()

    while True:
        key = stdscr.getch()
        if key == 27:  # ESC
            win.clear()
            win.refresh()
            show_info(stdscr, "Cancelled", "Info", 1)
            time.sleep(0.5)
            return True
        if time.time() - start_time > display_time:
            break

    win.clear()
    win.refresh()
    return False


def display_help_text(stdscr, region, help_text):
    """Render help text entirely inside the content region."""
    visible_lines = help_text[:region.height]
    if not visible_lines:
        return
    padding_y = region.y + max(0, (region.height - len(visible_lines)) // 2)
    padding_x = max(
        0,
        (region.width - max(len(line) for line in visible_lines)) // 2,
    )

    for index, line in enumerate(visible_lines):
        stdscr.addstr(
            padding_y + index,
            padding_x,
            line[:max(0, region.width - padding_x - 1)],
        )
