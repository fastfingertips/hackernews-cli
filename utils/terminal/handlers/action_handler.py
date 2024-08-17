import webbrowser
from utils.terminal.curses_utils import show_info_with_cancel
from utils.html.fetch_utils import fetch_hacker_news
from pages import show_filter_page, show_help_page
from curses import KEY_ENTER


class ActionHandler:
    def __init__(self, stdscr, current_page, page, selected_index, articles, filter_query=""):
        self.stdscr = stdscr
        self.current_page = current_page
        self.page = page
        self.selected_index = selected_index
        self.articles = articles
        self.filter_query = filter_query
    
    def open_link(self):
        cancelled = show_info_with_cancel(self.stdscr, "Press 'ESC' to cancel or wait to open the link.", "Opening Link", display_time=1)
        if not cancelled:
            webbrowser.open(self.articles[self.selected_index].link)
    
    def reset_filter(self):
        self.current_page = 1
        self.page = fetch_hacker_news(self.current_page)
        self.selected_index = 0
        self.filter_query = ""  # reset filter query

    def refresh_page(self):
        self.page = fetch_hacker_news(self.current_page)
        self.selected_index = 0
    
    def apply_filter(self):
        self.filter_query = show_filter_page(self.stdscr, self.filter_query)
        self.page = fetch_hacker_news(self.current_page)
    
    def show_help(self):
        show_help_page(self.stdscr)
    
    def handle_action(self, key):
        actions = {
            KEY_ENTER: self.open_link,
            10: self.open_link,  # Enter key (numeric value)
            ord(' '): self.reset_filter,
            ord('r'): self.refresh_page,
            ord('f'): self.apply_filter,
            ord('h'): self.show_help
        }
        
        # Execute the action if the key is in the dictionary
        action = actions.get(key)
        if action:
            action()
        
        return self.filter_query
