from functools import wraps
import curses

def clear_screen(func):
    """Decorator to clear the screen before calling the function."""
    @wraps(func)
    def wrapper(stdscr, *args, **kwargs):
        stdscr.clear()
        return func(stdscr, *args, **kwargs)
    return wrapper

def truncate_line(line, width):
    """Truncate the line to fit within the given width."""
    return line[:width - 4] + '...' if len(line) > width - 1 else line

def safe_addstr(stdscr, y, x, string):
    """Safely add a string to the screen, handling curses.error."""
    try:
        stdscr.addstr(y, x, string)
    except curses.error:
        # Handle the error (e.g., log it, ignore it, etc.)
        pass

def highlight_selection(stdscr, condition, line, y, x):
    """Apply or remove reverse attribute based on the condition."""
    if condition:
        stdscr.attron(curses.A_REVERSE)
    safe_addstr(stdscr, y, x, line)
    if condition:
        stdscr.attroff(curses.A_REVERSE)

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
