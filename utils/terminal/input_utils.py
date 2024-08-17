from .handlers import (
    NavigationHandler,
    ActionHandler
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

    navigation_handler = NavigationHandler(current_page, page, selected_index, articles)
    action_handler = ActionHandler(stdscr, current_page, page, selected_index, articles, filter_query)

    current_page, page, selected_index = navigation_handler.handle_navigation(key)
    filter_query = action_handler.handle_action(key)

    # signal to quit
    if key == ord('q'):
        return None, None, None, None

    return current_page, page, selected_index, filter_query