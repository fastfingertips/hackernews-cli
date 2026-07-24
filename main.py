"""Executable entry point for HackerNews CLI."""

import argparse
import curses

from hackernews_cli import __version__
from hackernews_cli.app.runtime import ApplicationRuntime
from hackernews_cli.ui.terminal.colors import (
    apply_default_background,
    init_colors,
)


def run(stdscr):
    """Configure curses and hand control to the application runtime."""
    try:
        curses.curs_set(0)
    except curses.error:
        pass

    stdscr.nodelay(True)
    stdscr.timeout(100)
    init_colors()
    apply_default_background(stdscr)
    ApplicationRuntime(stdscr).run()


def main(argv=None):
    """Start the application in a managed curses session."""
    parser = argparse.ArgumentParser(
        prog="hackernews-cli",
        description="Keyboard-first Hacker News terminal client.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    parser.parse_args(argv)
    curses.wrapper(run)


if __name__ == "__main__":
    main()
