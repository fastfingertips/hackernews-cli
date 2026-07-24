class Article:
    """Represents an article with full Hacker News metadata."""

    def __init__(
        self,
        title: str,
        link: str,
        rank: str = "",
        domain: str = "",
        score: str = "0 points",
        author: str = "unknown",
        age: str = "",
        comments_count: str = "0 comments",
        hn_link: str = "",
        item_id: str = "",
        fetched_at: str = "",
    ):
        self.title = title
        self.link = link
        self.rank = rank
        self.domain = domain
        self.score = score
        self.author = author
        self.age = age
        self.comments_count = comments_count
        self.hn_link = hn_link
        self.item_id = item_id
        self.fetched_at = fetched_at

    def __repr__(self) -> str:
        return f"Article(title={self.title!r}, link={self.link!r}, score={self.score!r})"
