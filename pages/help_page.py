from utils.curses_utils import display_help_text, wait_for_exit

def show_help_page(stdscr):
    """
    Display the help page on the terminal screen.
    
    :param stdscr: The curses screen object.
    """
    stdscr.clear()

    help_text = get_help_text()

    # Center the help menu on the screen
    display_help_text(stdscr, help_text)

    # Show exit message and wait for key press to return
    wait_for_exit(stdscr)

def get_help_text():
    """
    Return a list of help text lines to be displayed.
    
    :return: List of strings containing the help text.
    """
    return [
        "🔹 Navigation Shortcuts:",
        "  ←: Previous Page  |  Navigate to the previous page.",
        "  →: Next Page      |  Navigate to the next page.",
        "  ↑: Move Up        |  Move the selection upwards in the list.",
        "  ↓: Move Down      |  Move the selection downwards in the list.",
        "",
        "🔹 Action Shortcuts:",
        "  Enter: Open Link  |  Open the selected article in a web browser.",
        "  Space: Home       |  Return to the first page, clearing any filters.",
        "  f: Filter         |  Apply or modify a filter to the list.",
        "  r: Refresh        |  Reload the current page.",
        "  q: Quit           |  Exit the application.",
        "",
        "🔹 Information:",
        "  h: Help Menu      |  Display this help menu.",
        "",
    ]