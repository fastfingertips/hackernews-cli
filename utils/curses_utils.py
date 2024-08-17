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

def clear_line(stdscr, y, x, length):
    """Clear a line of text at the given coordinates."""
    stdscr.addstr(y, x, ' ' * length)

def get_input(stdscr, prompt):
    """Display a prompt and get user input."""
    stdscr.addstr(0, 0, prompt)
    stdscr.refresh() # Refresh the screen to show the prompt
    curses.echo()
    input_str = ""
    
    while True:
        key = stdscr.getch()
        
        if key == curses.KEY_BACKSPACE or key == 127:
            input_str = input_str[:-1]
            clear_line(stdscr, 0, len(prompt), len(input_str) + 1)
            stdscr.addstr(0, len(prompt), input_str)
        elif key in range(32, 127):
            input_str += chr(key)
            stdscr.addstr(0, len(prompt), input_str)
        elif key == 10:
            break
        elif key == 27:  # ESC key
            input_str = ""
            break

    curses.noecho()
    return input_str
