import atexit
from datetime import datetime, timezone

import httpx

from .. import __version__
from .article import Article
from .categories import CATEGORY_URLS, DEFAULT_CATEGORY
from .page import Page
from .parser import parse_html

HEADERS = {
    "User-Agent": f"hackernews-cli/{__version__}",
    "Accept": "text/html,application/xhtml+xml",
    "Accept-Language": "en-US,en;q=0.9",
}

_CLIENT = httpx.Client(
    headers=HEADERS,
    timeout=10,
    follow_redirects=True,
    http2=True,
)
atexit.register(_CLIENT.close)


def fetch_html(url: str) -> str:
    """
    Fetch HTML content from Hacker News URL with proper headers.
    """
    response = _CLIENT.get(url)
    response.raise_for_status()
    return response.text


def fetch_hacker_news(
        page: int = 1,
        category: str = DEFAULT_CATEGORY,
        total_pages: int = 10) -> Page:
    """
    Fetch and parse Hacker News page and category.
    """
    base_url = CATEGORY_URLS.get(
        category.lower(),
        CATEGORY_URLS[DEFAULT_CATEGORY],
    )
    url = f"{base_url}?p={page}"
    try:
        html = fetch_html(url)
        articles = parse_html(html)
    except Exception as e:
        articles = [Article(title=f"Error loading items: {e}", link="")]
    fetched_at = datetime.now(timezone.utc).isoformat(timespec="microseconds")
    for article in articles:
        article.fetched_at = fetched_at

    return Page(articles=articles, current_page=page, total_pages=total_pages, category=category)
