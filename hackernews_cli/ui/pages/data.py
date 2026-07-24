"""Local database information and folder access screen."""

from ..components.data_panel import draw_data
from ..components.frame import PageFrame


def show_data(stdscr, storage_service):
    status = ""
    stdscr.timeout(-1)
    try:
        while True:
            draw_data(
                stdscr,
                PageFrame.from_screen(stdscr),
                storage_service.directory(),
                storage_service.databases(),
                status,
            )
            key = stdscr.getch()
            if key in (27, ord("q"), ord("Q"), ord("d"), ord("D")):
                return
            if key in (ord("o"), ord("O")):
                try:
                    storage_service.open_directory()
                    status = "Opened local data folder"
                except (FileNotFoundError, OSError) as error:
                    status = f"Could not open folder: {error}"
            else:
                status = ""
    finally:
        stdscr.timeout(100)
