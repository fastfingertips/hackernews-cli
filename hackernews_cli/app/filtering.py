from .filter_query import compare_number, parse_query


STATUS_FILTERS = {
    "visited",
    "unvisited",
    "fav",
    "unfav",
    "read",
    "unread",
    "later",
    "unlater",
}


def apply_filter(
        articles,
        filter_query: str,
        visited_urls=None,
        favorite_urls=None,
        read_urls=None,
        reading_list_urls=None):
    """
    Filter articles matching query across title, domain, or submitter author.
    """
    if not filter_query:
        return articles

    visited_urls = visited_urls or set()
    favorite_urls = favorite_urls or set()
    read_urls = read_urls or set()
    reading_list_urls = reading_list_urls or set()
    return [
        article for article in articles
        if _matches_terms(
            article,
            parse_query(filter_query),
            visited_urls,
            favorite_urls,
            read_urls,
            reading_list_urls,
        )
    ]


def _matches_terms(
        article,
        terms,
        visited_urls,
        favorite_urls,
        read_urls,
        reading_list_urls):
    return all(
        _matches_term(
            article,
            term,
            visited_urls,
            favorite_urls,
            read_urls,
            reading_list_urls,
        )
        for term in terms
    )


def _matches_term(
        article,
        term,
        visited_urls,
        favorite_urls,
        read_urls,
        reading_list_urls):
    fields = {
        None: lambda: _contains(
            term.value,
            article.title,
            article.domain,
            article.author,
        ),
        "title": lambda: term.value in article.title.lower(),
        "site": lambda: term.value in article.domain.lower(),
        "by": lambda: term.value in article.author.lower(),
        "points": lambda: compare_number(
            _number(article.score),
            term.value,
        ),
        "replies": lambda: compare_number(
            _number(article.comments_count),
            term.value,
        ),
        "is": lambda: _matches_status(
            article.link,
            term.value,
            visited_urls,
            favorite_urls,
            read_urls,
            reading_list_urls,
        ),
    }
    matcher = fields.get(term.field)
    matched = matcher() if matcher else False
    return not matched if term.negated else matched


def _matches_status(
        url,
        status,
        visited_urls,
        favorite_urls,
        read_urls,
        reading_list_urls):
    checks = {
        "visited": url in visited_urls,
        "unvisited": url not in visited_urls,
        "fav": url in favorite_urls,
        "unfav": url not in favorite_urls,
        "read": url in read_urls,
        "unread": url not in read_urls,
        "later": url in reading_list_urls,
        "unlater": url not in reading_list_urls,
    }
    return status in STATUS_FILTERS and checks[status]


def _contains(query, *values):
    return any(query in (value or "").lower() for value in values)


def _number(value):
    if not value:
        return 0
    token = str(value).split(maxsplit=1)[0]
    return int(token) if token.isdigit() else 0
