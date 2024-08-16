class Article:
    def __init__(self, title, link):
        self.title = title
        self.link = link

class Page:
    def __init__(self, articles, current_page, total_pages):
        self.articles = articles
        self.current_page = current_page
        self.total_pages = total_pages
