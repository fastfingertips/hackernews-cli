import curses

def show_filter_page(stdscr, current_filter):
    stdscr.clear()
    curses.echo()
    height, width = stdscr.getmaxyx()
    stdscr.addstr(0, 0, "Filter: ")
    stdscr.refresh()
    filter_query = ""

    while True:
        key = stdscr.getch()
        
        if key == curses.KEY_BACKSPACE or key == 127:
            filter_query = filter_query[:-1]
            stdscr.addstr(0, 8, " " * (len(filter_query) + 7))
            stdscr.addstr(0, 8, filter_query)
        elif key in range(32, 127):
            filter_query += chr(key)
            stdscr.addstr(0, 8, filter_query)
        elif key == 10:
            break
        elif key == 27:
            filter_query = ""
            break

    curses.noecho()
    return filter_query
