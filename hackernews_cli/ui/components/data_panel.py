"""Render local database information."""

from .footer import draw_footer
from .header import draw_page_header
from .record_table import TableColumn, draw_table_header, draw_table_row


COLUMNS = (
    TableColumn("Database", 14),
    TableColumn("Contains", 44),
    TableColumn("Size", 12, align="right"),
    TableColumn("File"),
)


def draw_data(stdscr, frame, directory, databases, status=""):
    stdscr.erase()
    content = frame.content
    draw_page_header(
        stdscr,
        frame.header,
        "local data",
        "format: SQLite  |  sync: off  |  encryption: no",
        f"directory: {directory or '-'}",
    )
    if content.height:
        draw_table_header(
            stdscr,
            content.y,
            0,
            content.width,
            COLUMNS,
        )

    visible_rows = max(0, content.height - 2)
    for row, database in enumerate(databases[:visible_rows]):
        draw_table_row(
            stdscr,
            content.y + 2 + row,
            0,
            content.width,
            COLUMNS,
            (
                database.name,
                database.purpose,
                _file_size(database.size),
                database.path.name,
            ),
        )

    footer_text = status or "o open folder  q back"
    draw_footer(stdscr, frame.footer, f"  {footer_text}")
    stdscr.refresh()


def _file_size(size):
    value = float(size)
    for unit in ("B", "KB", "MB", "GB"):
        if value < 1024 or unit == "GB":
            return f"{value:.0f} {unit}" if unit == "B" else f"{value:.1f} {unit}"
        value /= 1024
