import curses

def display_help_text(stdscr, help_text):
    """
    Display the help text centered on the terminal screen.
    
    :param stdscr: The curses screen object.
    :param help_text: List of strings containing the help text.
    """
    height, width = stdscr.getmaxyx()
    padding_y = max(0, (height - len(help_text)) // 2)  # Vertical centering
    padding_x = max(0, (width - max(len(line) for line in help_text)) // 2)  # Horizontal centering

    for i, line in enumerate(help_text):
        stdscr.addstr(padding_y + i, padding_x, line[:width - 1])

def wait_for_exit(stdscr):
    """
    Wait for the user to press any key to exit the help page.
    
    :param stdscr: The curses screen object.
    """
    height, width = stdscr.getmaxyx()
    exit_message = "Press any key to return..."
    stdscr.addstr(height - 1, max(0, (width - len(exit_message)) // 2), exit_message, curses.A_REVERSE)
    stdscr.refresh()

    while True:
        key = stdscr.getch()
        if key != -1:
            break