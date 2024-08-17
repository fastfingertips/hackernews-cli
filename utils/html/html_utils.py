from bs4 import BeautifulSoup


def parse_html(html: str) -> list[tuple[str, str]]:
    """
    Parse the HTML content to extract article titles and links.

    :param html: HTML content to parse
    :return: List of tuples with the title and link of each article
    """
    soup = BeautifulSoup(html, 'html.parser')
    return [
        (a.get_text(strip=True), a.get('href', ''))
        for a in soup.select('tr.athing td.title > span.titleline > a')
    ]