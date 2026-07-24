from bs4 import BeautifulSoup
from urllib.parse import urlparse
from .article import Article


def parse_html(html: str) -> list[Article]:
    """
    Parse the HTML content to extract full Article models.

    :param html: HTML content from Hacker News
    :return: List of Article objects with title, link, domain, score, author, age, comments_count, etc.
    """
    soup = BeautifulSoup(html, 'html.parser')
    articles = []

    athings = soup.select('tr.athing')
    for athing in athings:
        item_id = athing.get('id', '')

        # Rank
        rank_elem = athing.select_one('span.rank')
        rank = rank_elem.get_text(strip=True).replace('\xa0', ' ') if rank_elem else ""

        # Title and Link
        title_a = athing.select_one('td.title > span.titleline > a')
        if not title_a:
            continue
        title = title_a.get_text(strip=True).replace('\xa0', ' ')
        link = title_a.get('href', '')
        if link.startswith('item?id='):
            link = f"https://news.ycombinator.com/{link}"

        # Domain
        domain_elem = athing.select_one('span.sitestr')
        if domain_elem:
            domain = domain_elem.get_text(strip=True)
        else:
            parsed = urlparse(link)
            domain = parsed.netloc or "news.ycombinator.com"

        # Subtext (sibling tr)
        subtext_tr = athing.find_next_sibling('tr')
        score = "0 points"
        author = "hn"
        age = ""
        comments_count = "0 comments"
        hn_link = f"https://news.ycombinator.com/item?id={item_id}" if item_id else link

        if subtext_tr:
            subtext_td = subtext_tr.select_one('td.subtext')
            if subtext_td:
                score_elem = subtext_td.select_one('span.score')
                if score_elem:
                    score = score_elem.get_text(strip=True).replace('\xa0', ' ')

                author_elem = subtext_td.select_one('a.hnuser')
                if author_elem:
                    author = author_elem.get_text(strip=True)

                age_elem = subtext_td.select_one('span.age')
                if age_elem:
                    age = age_elem.get_text(strip=True).replace('\xa0', ' ')

                comment_anchors = subtext_td.select('a[href^="item?id="]')
                for c_anchor in comment_anchors:
                    c_text = c_anchor.get_text(strip=True).replace('\xa0', ' ')
                    if 'comment' in c_text.lower() or 'discuss' in c_text.lower() or c_text.isdigit():
                        comments_count = c_text
                        hn_link = f"https://news.ycombinator.com/{c_anchor.get('href', '')}"
                        break
                    elif c_anchor == comment_anchors[-1]:
                        comments_count = c_text
                        hn_link = f"https://news.ycombinator.com/{c_anchor.get('href', '')}"

        articles.append(
            Article(
                title=title,
                link=link,
                rank=rank,
                domain=domain,
                score=score,
                author=author,
                age=age,
                comments_count=comments_count,
                hn_link=hn_link,
                item_id=item_id
            )
        )

    return articles
