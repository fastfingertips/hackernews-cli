from utils.curses_utils import (
  highlight_selection,
  truncate_line,
  clear_screen
)


@clear_screen
def show_home_page(stdscr, articles, selected_index, current_page, total_pages, filter_query):
    """Display the home page with articles and additional information."""
    height, width = stdscr.getmaxyx()

    # Apply filter
    filtered_articles = [s for s in articles if filter_query.lower() in s.title.lower()]

    # Display articles
    display_filtered_articles(stdscr, filtered_articles, selected_index, width)
    
    # Display additional information
    show_filter_info(stdscr, filter_query, height, width)
    show_selected_info(stdscr, filtered_articles, selected_index, height, width)
    show_footer(stdscr, current_page, total_pages, height, width)

    stdscr.refresh()

def display_filtered_articles(stdscr, filtered_articles, selected_index, width):
    """Display the filtered list of articles."""
    for i, article in enumerate(filtered_articles):
        line = f"{i + 1}. {article.title} | ({article.link})"
        line = truncate_line(line, width)
        highlight_selection(stdscr, i == selected_index, line, i, 0)

def show_filter_info(stdscr, filter_query, height, width):
    """Display the current filter information."""
    if filter_query:
        filter_info = f"Filter: {filter_query} (Press Space to clear filter)"
        stdscr.addstr(height - 3, 0, filter_info[:width])

def show_selected_info(stdscr, filtered_articles, selected_index, height, width):
    """Display information about the currently selected article."""
    if filtered_articles:
        info_line = f"Selected: {filtered_articles[selected_index].title}" if selected_index < len(filtered_articles) else "Selected: None"
        stdscr.addstr(height - 2, 0, info_line[:width])

def show_footer(stdscr, current_page, total_pages, height, width):
    """Display the footer information."""
    footer_info = f"Page {current_page}/{total_pages} | Press 'h' for Help"
    stdscr.addstr(height - 1, 0, footer_info[:width])