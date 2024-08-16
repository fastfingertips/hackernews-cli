import curses
from utils.input_handler import handle_input
from utils.fetch_utils import fetch_hacker_news
from utils.filter_utils import apply_filter
from pages import show_home_page

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(1)
    stdscr.timeout(100)

    current_page = 1
    selected_index = 0
    filter_query = ""

    page = fetch_hacker_news(current_page)

    while True:
        # Apply filter to get filtered articles
        filtered_articles = apply_filter(page.articles, filter_query)
        
        # Draw TUI
        show_home_page(stdscr, filtered_articles, selected_index, page.current_page, page.total_pages, filter_query)
        key = stdscr.getch()

        # Handle user input
        result = handle_input(key, stdscr, current_page, page, selected_index, filter_query, filtered_articles)
        
        if result is None:
            break
        
        current_page, page, selected_index, filter_query = result

    curses.endwin()

if __name__ == "__main__":
    curses.wrapper(main)
