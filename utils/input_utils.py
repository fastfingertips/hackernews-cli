
import webbrowser
from utils.fetch_utils import fetch_hacker_news
from pages import show_filter_page, show_help_page
from curses import KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN, KEY_ENTER


def handle_navigation(key, current_page, page, selected_index, articles):
    """Handle navigation keys."""
    if key == KEY_RIGHT:
        if current_page < page.total_pages:
            current_page += 1
            page = fetch_hacker_news(current_page)
            selected_index = 0
    elif key == KEY_LEFT:
        if current_page > 1:
            current_page -= 1
            page = fetch_hacker_news(current_page)
            selected_index = 0
    elif key == KEY_DOWN:
        selected_index = min(selected_index + 1, len(articles) - 1)
    elif key == KEY_UP:
        selected_index = max(selected_index - 1, 0)
    return current_page, page, selected_index

def handle_actions(key, stdscr, current_page, page, selected_index, articles, filter_query:str=""):
    """Handle action keys."""
    if key == KEY_ENTER or key == 10:
        if 0 <= selected_index < len(articles):
            webbrowser.open(articles[selected_index].link)
    elif key == ord(' '):
        current_page = 1
        page = fetch_hacker_news(current_page)
        selected_index = 0
        filter_query = "" # reset filter query
    elif key == ord('r'):
        page = fetch_hacker_news(current_page)
        selected_index = 0
    elif key == ord('f'):
        filter_query = show_filter_page(stdscr, filter_query)
        page = fetch_hacker_news(current_page)
    elif key == ord('h'):
        show_help_page(stdscr)
    return current_page, page, selected_index, filter_query
