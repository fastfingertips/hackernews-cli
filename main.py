import curses
from utils.input_handler import handle_input
from utils.fetch_utils import fetch_hacker_news
from utils.filter_utils import apply_filter
from pages import show_home_page

def main(stdscr):
    """initialize and run the TUI application"""
    curses.curs_set(0)  # hide the cursor
    stdscr.nodelay(1)  # non-blocking input
    stdscr.timeout(100)  # set input timeout

    current_page = 1
    selected_index = 0
    filter_query = ""

    # fetch initial page of articles
    page = fetch_hacker_news(current_page)

    while True:
        # apply filter to get filtered articles
        articles = apply_filter(page.articles, filter_query)

        # draw the home page and get user input
        key = show_home_page(
            stdscr,
            articles,
            selected_index,
            page.current_page,
            page.total_pages,
            filter_query
        )
    
        # handle user input and update state
        result = handle_input(
            stdscr,
            key,
            current_page,
            page,
            selected_index,
            articles, 
            filter_query
        )
        
        # exit if result contains None
        if result is None:
            break

        current_page, page, selected_index, filter_query = result

    curses.endwin()  # end curses mode

if __name__ == "__main__":
    curses.wrapper(main)