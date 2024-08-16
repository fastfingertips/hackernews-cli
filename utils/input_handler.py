import curses
import webbrowser
from utils.fetch_utils import fetch_hacker_news
from pages import show_filter_page, show_help_page


def handle_input(key, stdscr, current_page, page, selected_index, filter_query, filtered_articles):
    """
    Handle user input and update the state accordingly.
    
    :param key: The key pressed by the user
    :param stdscr: The curses window object
    :param current_page: The current page number
    :param page: The current page data
    :param selected_index: The index of the currently selected item
    :param filter_query: The current filter query
    :param filtered_articles: The filtered list of articles
    :return: Updated current_page, page, selected_index, filter_query
    """
    if key == curses.KEY_RIGHT:
        if current_page < page.total_pages:
            current_page += 1
            page = fetch_hacker_news(current_page)
            selected_index = 0
    elif key == curses.KEY_LEFT:
        if current_page > 1:
            current_page -= 1
            page = fetch_hacker_news(current_page)
            selected_index = 0
    elif key == curses.KEY_DOWN:
        selected_index = min(selected_index + 1, len(filtered_articles) - 1)
    elif key == curses.KEY_UP:
        selected_index = max(selected_index - 1, 0)
    elif key == curses.KEY_ENTER or key == 10:
        if 0 <= selected_index < len(filtered_articles):
            webbrowser.open(filtered_articles[selected_index].link)
    elif key == ord(' '):
        current_page = 1
        page = fetch_hacker_news(current_page)
        selected_index = 0
        filter_query = ""
    elif key == ord('r'):
        page = fetch_hacker_news(current_page)
        selected_index = 0
    elif key == ord('q'):
        return None, None, None, None  # Signal to quit
    elif key == ord('f'):
        filter_query = show_filter_page(stdscr, filter_query)
        # Optionally refresh the page after applying the filter
        page = fetch_hacker_news(current_page)
    elif key == ord('h'):
        show_help_page(stdscr)
    
    return current_page, page, selected_index, filter_query
