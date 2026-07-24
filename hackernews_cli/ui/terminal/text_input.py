"""Generic centered single-line text editor."""

import curses

from .colors import HEADER_COLOR_PAIR, apply_default_background
from .drawing import safe_addstr, truncate_line


def show_text_popup(
        stdscr,
        title,
        descriptions,
        current_value="",
        prompt_label="Value",
        confirm_label="confirm"):
    """Edit one line of text in a centered popup."""
    screen_height, screen_width = stdscr.getmaxyx()
    popup_height = min(
        max(7, len(descriptions) + 5),
        max(3, screen_height - 2),
    )
    desired_width = max(
        56,
        len(title) + 6,
        *(len(line) + 4 for line in descriptions),
    )
    popup_width = min(desired_width, max(20, screen_width - 4))
    start_y = max(0, (screen_height - popup_height) // 2)
    start_x = max(0, (screen_width - popup_width) // 2)

    window = curses.newwin(
        popup_height,
        popup_width,
        start_y,
        start_x,
    )
    apply_default_background(window)
    window.keypad(True)
    window.timeout(-1)

    value = current_value
    original_value = current_value
    try:
        try:
            curses.curs_set(1)
        except curses.error:
            pass
        curses.noecho()

        while True:
            window.erase()
            window.box()
            _draw_popup(
                window,
                title,
                descriptions,
                value,
                popup_height,
                popup_width,
                prompt_label,
                confirm_label,
            )
            window.refresh()

            key = window.getch()
            if key in (curses.KEY_ENTER, 10, 13):
                return value.strip()
            if key == 27:
                return original_value
            if key in (curses.KEY_BACKSPACE, 8, 127):
                value = value[:-1]
            elif key == 21:
                value = ""
            elif 32 <= key <= 126:
                value += chr(key)
    finally:
        try:
            curses.curs_set(0)
        except curses.error:
            pass
        window.erase()
        window.refresh()
        stdscr.touchwin()
        stdscr.refresh()


def _draw_popup(
        window,
        title,
        descriptions,
        value,
        height,
        width,
        prompt_label,
        confirm_label):
    title_attr = (
        curses.color_pair(HEADER_COLOR_PAIR) | curses.A_BOLD
        if curses.has_colors()
        else curses.A_BOLD
    )
    safe_addstr(window, 0, 2, f" {title} ", title_attr)

    description_limit = max(0, height - 5)
    visible_descriptions = descriptions[:description_limit]
    for index, line in enumerate(visible_descriptions):
        safe_addstr(
            window,
            1 + index,
            2,
            truncate_line(line, max(1, width - 4)),
            curses.A_DIM,
        )

    prompt_y = min(height - 3, 2 + len(visible_descriptions))
    prompt = f"{prompt_label}: "
    input_width = max(1, width - len(prompt) - 4)
    visible_value = value[-input_width:]
    safe_addstr(window, prompt_y, 2, prompt, title_attr)
    safe_addstr(
        window,
        prompt_y,
        2 + len(prompt),
        visible_value.ljust(input_width),
    )
    window.move(prompt_y, 2 + len(prompt) + len(visible_value))
    safe_addstr(
        window,
        height - 2,
        2,
        truncate_line(
            f"Enter {confirm_label} | Esc cancel | Ctrl+U clear",
            max(1, width - 4),
        ),
        curses.A_DIM,
    )
