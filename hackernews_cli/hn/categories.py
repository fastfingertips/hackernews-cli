"""Supported Hacker News feeds and their keyboard shortcuts."""


CATEGORY_URLS = {
    "top": "https://news.ycombinator.com/news",
    "new": "https://news.ycombinator.com/newest",
    "ask": "https://news.ycombinator.com/ask",
    "show": "https://news.ycombinator.com/show",
    "jobs": "https://news.ycombinator.com/jobs",
}
CATEGORIES = tuple(CATEGORY_URLS)
DEFAULT_CATEGORY = CATEGORIES[0]
CATEGORY_SHORTCUTS = dict(zip(("1", "2", "3", "4", "5"), CATEGORIES))
