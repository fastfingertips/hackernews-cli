from utils.curses_utils import (
  clear_screen,
  safe_addstr,
  get_input
)

@clear_screen
def show_filter_page(stdscr, current_filter: str = ""):
    prompt = "filter: "
    safe_addstr(stdscr, 0, 0, prompt)
    
    # display the current filter value below the prompt, using quotes for clarity
    if current_filter:
        safe_addstr(stdscr, 1, 0, f"current filter: \"{current_filter}\"")
    
    # get new filter query from user input
    filter_query = get_input(stdscr, prompt)
    
    return filter_query
