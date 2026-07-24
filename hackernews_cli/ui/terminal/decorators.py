"""Decorators for curses screens."""

from functools import wraps


def clear_screen(func):
    """Erase the screen before the function runs, refresh after it returns."""
    @wraps(func)
    def wrapper(stdscr, *args, **kwargs):
        stdscr.erase()
        result = func(stdscr, *args, **kwargs)
        stdscr.refresh()
        return result
    return wrapper
