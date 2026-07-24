from .categories import DEFAULT_CATEGORY


class Page:
    """Represents a page containing articles and pagination info."""

    def __init__(
            self,
            articles: list,
            current_page: int,
            total_pages: int,
            category: str = DEFAULT_CATEGORY,
            loaded_pages=None):
        self.articles = articles
        self.current_page = current_page
        self.total_pages = total_pages
        self.category = category
        self.loaded_pages = tuple(loaded_pages or (current_page,))

    def append(self, next_page):
        """Return a new feed containing this page and a newly loaded page."""
        seen = {
            article.item_id or article.link
            for article in self.articles
            if article.item_id or article.link
        }
        articles = list(self.articles)

        for article in next_page.articles:
            identity = article.item_id or article.link
            if identity and identity in seen:
                continue
            articles.append(article)
            if identity:
                seen.add(identity)

        loaded_pages = tuple(dict.fromkeys(
            self.loaded_pages + next_page.loaded_pages
        ))
        return Page(
            articles=articles,
            current_page=max(loaded_pages),
            total_pages=max(self.total_pages, next_page.total_pages),
            category=self.category,
            loaded_pages=loaded_pages,
        )

    def __repr__(self) -> str:
        return (f"Page(current_page={self.current_page}, "
                f"total_pages={self.total_pages}, "
                f"category={self.category!r}, "
                f"loaded_pages={self.loaded_pages!r}, "
                f"articles={len(self.articles)})")
