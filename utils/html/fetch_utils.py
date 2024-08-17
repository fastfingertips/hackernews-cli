import requests
from models.models import Article, Page
from utils.html.html_utils import parse_html


def fetch_html(url: str) -> str:
    """
    Fetch the HTML content from the specified URL.

    :param url: URL to fetch the HTML content from
    :return: Raw HTML content of the URL
    :raises requests.RequestException: If the HTTP request fails
    """
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def fetch_hacker_news(
        page: int,
        base_url: str = "https://news.ycombinator.com/news",
        items_per_page: int = 30,
        total_pages: int = 10) -> Page:
    """
    Fetch and parse a specific Hacker News page.

    :param page: Page number to fetch (1-based index)
    :param base_url: Base URL for fetching Hacker News pages
    :param items_per_page: Number of items per page (used for pagination estimation)
    :param total_pages: Total number of pages for pagination
    :return: A Page object containing articles and pagination info
    """
    url = f"{base_url}?p={page}"
    html = fetch_html(url)
    articles = [Article(title, link) for title, link in parse_html(html)]
    return Page(articles, page, total_pages)