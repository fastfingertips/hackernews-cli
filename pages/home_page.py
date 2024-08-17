from utils.curses_utils import (
  highlight_selection,
  truncate_line,
  clear_screen
)


@clear_screen
def show_home_page(stdscr, articles, selected_index, current_page, total_pages, filter_query:str=""):
    """Display the home page with articles and additional information."""
    height, width = stdscr.getmaxyx()

    display_articles(stdscr, articles, selected_index, width, filter_query)
    show_filter_info(stdscr, filter_query, height, width)
    show_selected_info(stdscr, articles, selected_index, height, width)
    show_footer(stdscr, current_page, total_pages, height, width)

    return stdscr.getch()

def display_articles(stdscr, articles, selected_index, width, filter_query):
    """Display the articles and dynamic messages based on the state."""
    clear_screen(stdscr)  # Clear the screen before displaying articles

    if not articles and not filter_query:
        message = "No articles available."
        stdscr.addstr(0, 0, message)
    elif not articles and filter_query:
        message = f"No articles match the filter: '{filter_query}'"
        stdscr.addstr(0, 0, message)
    else:
        for i, article in enumerate(articles):
            line = f"{i + 1}. {article.title} | ({article.link})"
            line = truncate_line(line, width)
            highlight_selection(stdscr, i == selected_index, line, i, 0)

def show_filter_info(stdscr, filter_query, height, width):
    """Display the current filter information."""
    if filter_query:
        filter_info = f"Filter: {filter_query} (Press Space to clear filter)"
    else:
        filter_info = "No filter applied. Press 'f' to apply a filter."
    stdscr.addstr(height - 3, 0, filter_info[:width])

def show_selected_info(stdscr, articles, selected_index, height, width):
    """Display information about the currently selected article."""
    if articles:
        info_line = f"Selected: {articles[selected_index].title}" if selected_index < len(articles) else "Selected: None"
    else:
        info_line = "No articles available to select."
    stdscr.addstr(height - 2, 0, info_line[:width])

def show_footer(stdscr, current_page, total_pages, height, width):
    """Display the footer information."""
    footer_info = f"Page {current_page}/{total_pages} | Press 'h' for Help"
    stdscr.addstr(height - 1, 0, footer_info[:width])