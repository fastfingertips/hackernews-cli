class Article:
    """Represents an article with a title and a link."""
    
    def __init__(self, title: str, link: str):
        self.title = title
        self.link = link

    def __repr__(self) -> str:
        return f"Article(title={self.title!r}, link={self.link!r})"

class Page:
    """Represents a page containing articles and pagination info."""
    
    def __init__(self, articles: list[Article], current_page: int, total_pages: int):
        self.articles = articles
        self.current_page = current_page
        self.total_pages = total_pages

    def __repr__(self) -> str:
        return (f"Page(current_page={self.current_page}, "
                f"total_pages={self.total_pages}, "
                f"articles={self.articles!r})")