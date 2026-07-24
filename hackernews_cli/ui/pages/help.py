from ..components.footer import draw_footer
from ..components.frame import PageFrame
from ..components.header import draw_page_header
from ..terminal.decorators import clear_screen
from ..terminal.dialogs import display_help_text


@clear_screen
def show_help(stdscr):
    """
    Display the help page on the terminal screen.
    """
    frame = PageFrame.from_screen(stdscr)
    draw_page_header(
        stdscr,
        frame.header,
        "help",
        context="Keyboard shortcuts and status filters",
    )
    display_help_text(stdscr, frame.content, get_help_text())
    draw_footer(stdscr, frame.footer, "  press any key to return")
    stdscr.getch()


def get_help_text():
    """
    Return a list of help text lines to be displayed.
    """
    return [
        "Navigation (Vim & Standard):",
        "  Up / k         : Move selection up",
        "  Down / j       : Move selection down",
        "  Left / h       : Jump one batch up",
        "  Right / l      : Load the next batch",
        "  End + Down/j   : Load more stories automatically",
        "  g / G          : Jump to Top / Bottom",
        "  PgUp / PgDn    : Jump 5 items up / down",
        "",
        "Categories (1 - 5):",
        "  1 : Top Stories   |  2 : Newest Stories",
        "  3 : Ask HN        |  4 : Show HN",
        "  5 : Jobs",
        "",
        "Actions:",
        "  Enter          : Open article in web browser",
        "  c              : Open HN comment thread in browser",
        "  H              : Open and manage browsing history",
        "  History u / U  : Undo selected favorite/read change",
        "  f              : Add or remove selected favorite",
        "  F              : Open and manage favorites",
        "  r              : Mark selected story read or unread",
        "  t              : Add/remove selected story from read later",
        "  T              : Open and manage the read-later queue",
        "  d / D          : View local database information",
        "  b              : Open top 5 untouched stories by score",
        "  B              : Open top 10 untouched stories by score",
        "  a / A          : Load every available HN batch",
        "  /              : Open email-style filter popup",
        "  s              : Save the active filter",
        "  S              : Open saved and ready-to-use filters",
        "  title:/site:/by: : Filter feed fields",
        "  points:/replies: : Compare numeric fields",
        "  is:visited/fav/read/unread : Filter state",
        "  -term          : Exclude a word or field",
        "  Space          : Reset search filter",
        "  u / U          : Refresh current feed from page one",
        "  q              : Quit application",
        "  ?              : View this help menu",
        "  i / I          : View application information",
    ]
