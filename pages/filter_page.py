from utils.curses_utils import get_input

def show_filter_page(stdscr, current_filter):
    stdscr.clear()
    prompt = "Filter: "
    stdscr.addstr(0, 0, prompt)
    
    # Display the current filter value below the prompt, using quotes for clarity
    if current_filter:
        stdscr.addstr(1, 0, f"Current filter: \"{current_filter}\"")
    
    stdscr.refresh()
    
    # Get new filter query from user input
    filter_query = get_input(stdscr, prompt)
    
    return filter_query