"""Low-level curses drawing primitives."""

import curses


def safe_addstr(stdscr, y, x, string, attr=0):
    """Write a string to the screen, silently ignoring out-of-bounds errors."""
    try:
        stdscr.addstr(y, x, string, attr)
    except curses.error:
        pass


def truncate_line(text, max_length, count=3, symbol='.'):
    """Truncate text to max_length, appending an ellipsis symbol if needed."""
    if max_length <= 0:
        return ""
    text = text.rstrip()
    if len(text) > max_length:
        if max_length <= count:
            return symbol * max_length
        return text[:max(0, max_length - count)] + symbol * count
    return text


def highlight_selection(stdscr, condition, line, y, x, attr_on=0):
    """Render a line with highlight when selected, plain otherwise."""
    if condition:
        attr = attr_on if attr_on else curses.A_REVERSE
        safe_addstr(stdscr, y, x, line, attr)
    else:
        safe_addstr(stdscr, y, x, line)
