"""Persist fetched stories and their feed membership."""

from contextlib import closing

from ..hn.article import Article


ARCHIVED_PAGE_LIMIT = 30


class StoryRepository:
    """Store live snapshots and recover stories missing from a later fetch."""

    def __init__(self, database):
        self.database = database

    def save_page(self, page):
        """Save one successful page and return its newly archived stories."""
        articles = [
            article
            for article in page.articles
            if article.item_id and article.link
        ]
        if not articles:
            return []

        fetched_at = articles[0].fetched_at
        item_ids = [article.item_id for article in articles]
        placeholders = ", ".join("?" for _ in item_ids)

        with self.database.lock, closing(
                self.database.connect()) as connection:
            with connection:
                connection.execute(
                    f"""
                    UPDATE feed_entries
                    SET is_current = 0
                    WHERE category = ?
                      AND page_number = ?
                      AND item_id NOT IN ({placeholders})
                    """,
                    (page.category, page.current_page, *item_ids),
                )
                for position, article in enumerate(articles):
                    self._upsert_story(connection, article, fetched_at)
                    self._upsert_feed_entry(
                        connection,
                        page.category,
                        page.current_page,
                        position,
                        article.item_id,
                        article.rank,
                        fetched_at,
                    )

        return self.archived_for_page(
            page.category,
            page.current_page,
            exclude_item_ids=set(item_ids),
        )

    def page(self, category, page_number):
        """Return the last saved page when the network is unavailable."""
        articles = self._entries(
            category,
            page_number,
            is_current=True,
        ) + self._entries(
            category,
            page_number,
            is_current=False,
            limit=ARCHIVED_PAGE_LIMIT,
        )
        for article in articles:
            article.is_cached = True
        return articles

    def archived_for_page(
            self,
            category,
            page_number,
            exclude_item_ids=None):
        return [
            article
            for article in self._entries(
                category,
                page_number,
                is_current=False,
                limit=ARCHIVED_PAGE_LIMIT,
            )
            if article.item_id not in (exclude_item_ids or set())
        ]

    def _entries(
            self,
            category,
            page_number,
            is_current,
            limit=None):
        limit_clause = "LIMIT ?" if limit is not None else ""
        parameters = [category, page_number, int(is_current)]
        if limit is not None:
            parameters.append(limit)
        with self.database.lock, closing(
                self.database.connect()) as connection:
            rows = connection.execute(
                f"""
                SELECT
                    story.item_id,
                    story.url,
                    story.title,
                    story.domain,
                    story.score,
                    story.author,
                    story.age,
                    story.published_at,
                    story.comments_count,
                    story.hn_url,
                    story.first_seen_at,
                    story.last_seen_at,
                    story.fetched_at,
                    entry.position,
                    entry.rank,
                    entry.is_current
                FROM feed_entries AS entry
                JOIN stories AS story ON story.item_id = entry.item_id
                WHERE entry.category = ?
                  AND entry.page_number = ?
                  AND entry.is_current = ?
                ORDER BY
                    CASE WHEN entry.is_current = 1
                        THEN entry.position END ASC,
                    entry.last_seen_at DESC
                {limit_clause}
                """,
                parameters,
            ).fetchall()
        return [self._article_from_row(row) for row in rows]

    @staticmethod
    def _upsert_story(connection, article, fetched_at):
        connection.execute(
            """
            INSERT INTO stories (
                item_id, url, title, domain, score, author, age,
                published_at, comments_count, hn_url, first_seen_at,
                last_seen_at, fetched_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(item_id) DO UPDATE SET
                url = excluded.url,
                title = excluded.title,
                domain = excluded.domain,
                score = excluded.score,
                author = excluded.author,
                age = excluded.age,
                published_at = excluded.published_at,
                comments_count = excluded.comments_count,
                hn_url = excluded.hn_url,
                last_seen_at = excluded.last_seen_at,
                fetched_at = excluded.fetched_at
            """,
            (
                article.item_id,
                article.link,
                article.title,
                article.domain,
                article.score,
                article.author,
                article.age,
                article.published_at,
                article.comments_count,
                article.hn_link,
                fetched_at,
                fetched_at,
                fetched_at,
            ),
        )

    @staticmethod
    def _upsert_feed_entry(
            connection,
            category,
            page_number,
            position,
            item_id,
            rank,
            fetched_at):
        connection.execute(
            """
            INSERT INTO feed_entries (
                category, item_id, page_number, position, rank, is_current,
                first_seen_at, last_seen_at
            )
            VALUES (?, ?, ?, ?, ?, 1, ?, ?)
            ON CONFLICT(category, item_id) DO UPDATE SET
                page_number = excluded.page_number,
                position = excluded.position,
                rank = excluded.rank,
                is_current = 1,
                last_seen_at = excluded.last_seen_at
            """,
            (
                category,
                item_id,
                page_number,
                position,
                rank,
                fetched_at,
                fetched_at,
            ),
        )

    @staticmethod
    def _article_from_row(row):
        return Article(
            item_id=row[0],
            link=row[1],
            title=row[2],
            domain=row[3],
            score=row[4],
            author=row[5],
            age=row[6],
            published_at=row[7],
            comments_count=row[8],
            hn_link=row[9],
            first_seen_at=row[10],
            last_seen_at=row[11],
            fetched_at=row[12],
            rank=row[14] or f"{row[13] + 1}.",
            is_cached=not bool(row[15]),
        )
