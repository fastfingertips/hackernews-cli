from curses import KEY_RIGHT, KEY_LEFT, KEY_DOWN, KEY_UP
from utils.html.fetch_utils import fetch_hacker_news


class NavigationHandler:
    def __init__(self, current_page, page, selected_index, articles):
        self.current_page = current_page
        self.page = page
        self.selected_index = selected_index
        self.articles = articles
    
    def next_page(self):
        if self.current_page < self.page.total_pages:
            self.current_page += 1
            self.page = fetch_hacker_news(self.current_page)
            self.selected_index = 0
    
    def previous_page(self):
        if self.current_page > 1:
            self.current_page -= 1
            self.page = fetch_hacker_news(self.current_page)
            self.selected_index = 0
    
    def select_next_item(self):
        self.selected_index = min(self.selected_index + 1, len(self.articles) - 1)
    
    def select_previous_item(self):
        self.selected_index = max(self.selected_index - 1, 0)
    
    def handle_navigation(self, key):
        actions = {
            KEY_RIGHT: self.next_page,
            KEY_LEFT: self.previous_page,
            KEY_DOWN: self.select_next_item,
            KEY_UP: self.select_previous_item
        }
        
        # Execute the action if the key is in the dictionary
        action = actions.get(key)
        if action:
            action()
        
        return self.current_page, self.page, self.selected_index
