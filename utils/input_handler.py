from utils.input_utils import (
  handle_navigation,
  handle_actions
)


def handle_input(stdscr, key, current_page, page, selected_index, articles, filter_query:str = ""):
    """
    Handle user input and update the state accordingly.

    :param stdscr: The curses window object
    :param key: The key pressed by the user
    :param current_page: The current page number
    :param page: The current page data
    :param selected_index: The index of the currently selected item
    :param filter_query: The current filter query
    :param filtered_articles: The filtered list of articles
    :return: Updated current_page, page, selected_index, filter_query
    """
    current_page, page, selected_index = handle_navigation(key, current_page, page, selected_index, articles)
    current_page, page, selected_index, filter_query = handle_actions(key, stdscr, current_page, page, selected_index, articles, filter_query)

    # signal to quit
    if key == ord('q'):
        return None, None, None, None

    return current_page, page, selected_index, filter_query
