"""Shared page geometry for non-overlapping terminal regions."""

from dataclasses import dataclass


HEADER_HEIGHT = 2
FOOTER_HEIGHT = 3


@dataclass(frozen=True)
class Region:
    y: int
    height: int
    width: int

    @property
    def end_y(self):
        """Return the first row outside this region."""
        return self.y + self.height


@dataclass(frozen=True)
class PageFrame:
    header: Region
    content: Region
    footer: Region

    @classmethod
    def from_screen(cls, stdscr):
        """Split the current terminal into fixed header/footer and fluid content."""
        height, width = stdscr.getmaxyx()
        header_height = min(HEADER_HEIGHT, height)
        footer_height = min(
            FOOTER_HEIGHT,
            max(0, height - header_height),
        )
        content_height = max(0, height - header_height - footer_height)
        return cls(
            header=Region(0, header_height, width),
            content=Region(header_height, content_height, width),
            footer=Region(
                header_height + content_height,
                footer_height,
                width,
            ),
        )
