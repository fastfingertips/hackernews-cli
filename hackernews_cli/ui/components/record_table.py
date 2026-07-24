"""Reusable single-line table rendering for management screens."""

import curses
from dataclasses import dataclass

from ..terminal.drawing import safe_addstr, truncate_line


MARKER_WIDTH = 2


@dataclass(frozen=True)
class TableColumn:
    title: str
    width: int = None
    align: str = "left"


def draw_table_header(stdscr, y, x, width, columns):
    widths = _column_widths(width, columns)
    cells = [column.title for column in columns]
    line = " " * MARKER_WIDTH + _format_cells(cells, columns, widths)
    safe_addstr(stdscr, y, x, truncate_line(line, width), curses.A_DIM)


def draw_table_row(
        stdscr,
        y,
        x,
        width,
        columns,
        cells,
        selected=False,
        attr=0):
    widths = _column_widths(width, columns)
    marker = "> " if selected else "  "
    line = marker + _format_cells(cells, columns, widths)
    safe_addstr(
        stdscr,
        y,
        x,
        truncate_line(line, width).ljust(width),
        attr,
    )


def _column_widths(total_width, columns):
    available = max(1, total_width - MARKER_WIDTH)
    fixed_width = sum(column.width or 0 for column in columns)
    flexible_count = sum(column.width is None for column in columns)
    flexible_width = max(
        8,
        (available - fixed_width) // max(1, flexible_count),
    )
    return [
        column.width if column.width is not None else flexible_width
        for column in columns
    ]


def _format_cells(cells, columns, widths):
    rendered = []
    for value, column, width in zip(cells, columns, widths):
        value = truncate_line(str(value), width)
        rendered.append(
            value.rjust(width) if column.align == "right" else value.ljust(width)
        )
    return "".join(rendered)
