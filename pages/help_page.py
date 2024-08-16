import curses

def show_help_page(stdscr):
    stdscr.clear()
    
    help_text = [
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

    # Display the help menu centered on the screen
    height, width = stdscr.getmaxyx()
    padding_y = max(0, (height - len(help_text)) // 2)  # Vertical centering
    padding_x = max(0, (width - max(len(line) for line in help_text)) // 2)  # Horizontal centering

    # Print help text
    for i, line in enumerate(help_text):
        stdscr.addstr(padding_y + i, padding_x, line[:width - 1])

    # Show exit message in reverse text style
    exit_message = "Press any key to return..."
    stdscr.addstr(height - 1, max(0, (width - len(exit_message)) // 2), exit_message, curses.A_REVERSE)

    stdscr.refresh()

    # Exit help menu on any key press
    while True:
        key = stdscr.getch()
        if key != -1:
            break
