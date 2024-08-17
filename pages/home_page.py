from utils.terminal.curses_utils import (
  highlight_selection,
  truncate_line,
  clear_screen
)


@clear_screen
def show_home_page(stdscr, articles, selected_index, current_page, total_pages, filter_query:str=""):
    """Display the home page with articles and additional information."""
    height, width = stdscr.getmaxyx()

    if articles:
        display_articles(stdscr, articles, selected_index, width)
    else:
        display_no_articles_message(stdscr, filter_query)

    show_filter_info(stdscr, filter_query, height, width)
    show_selected_info(stdscr, articles, selected_index, height, width)
    show_footer(stdscr, current_page, total_pages, height, width)

    return stdscr.getch()

def display_articles(stdscr, articles, selected_index, width):
    """Display the articles in a table format with dynamic messages based on the state."""
    title_width, link_width = calculate_column_widths(width)
    draw_table_header(stdscr, title_width, link_width, width)
    display_articles_in_table(stdscr, articles, selected_index, title_width, link_width, width)

def display_no_articles_message(stdscr, filter_query):
    """Display a message if no articles are available."""
    message = (
        "No articles available." if not filter_query
        else f"No articles match the filter: '{filter_query}'"
    )
    stdscr.addstr(0, 0, message)

def calculate_column_widths(total_width):
    """Calculate the column widths for title and link."""
    title_width = max(total_width // 2 - 2, 20)
    link_width = total_width - title_width - 7
    return title_width, link_width

def draw_table_header(stdscr, title_width, link_width, width):
    """Draw the table header with column names."""
    header = f"{'No.':<4} {'Title':<{title_width}} │ {'Link':<{link_width}}"
    stdscr.addstr(0, 0, truncate_line(header, width))
    stdscr.addstr(1, 0, "─" * width)  # horizontal line separator

def display_articles_in_table(stdscr, articles, selected_index, title_width, link_width, width):
    """Display articles in a table format with proper alignment."""
    for i, article in enumerate(articles):
        title = article.title[:title_width].ljust(title_width)
        link = article.link[:link_width].ljust(link_width)
        line = f"{i + 1:<4} {title} │ {link}"
        highlight_selection(stdscr, i == selected_index, truncate_line(line, width), i + 2, 0)

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
    footer_info = f"Page {current_page}/{total_pages} │ Press 'h' for Help"
    stdscr.addstr(height - 1, 0, footer_info[:width])