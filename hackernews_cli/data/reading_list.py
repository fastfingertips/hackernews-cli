"""SQLite-backed read-later repository."""

from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone


@dataclass(frozen=True)
class ReadingListEntry:
    url: str
    title: str
    added_at: str


class ReadingListRepository:
    """Persist stories intentionally deferred for later reading."""

    def __init__(self, database):
        self.database = database
        self.database_path = database.path
        self._lock = database.lock
        self._dates = self._load_dates()

    def _load_dates(self):
        with closing(self.database.connect()) as connection:
            return dict(connection.execute(
                "SELECT url, added_at FROM reading_list"
            ).fetchall())

    def toggle(self, url, title):
        if url in self.urls():
            self.remove(url)
            return False
        self.add(url, title)
        return True

    def add(self, url, title):
        if not url:
            return False
        added_at = datetime.now(timezone.utc).isoformat(timespec="microseconds")
        with self._lock, closing(self.database.connect()) as connection:
            with connection:
                connection.execute(
                    """
                    INSERT INTO reading_list (url, title, added_at)
                    VALUES (?, ?, ?)
                    ON CONFLICT(url) DO UPDATE SET
                        title = excluded.title,
                        added_at = excluded.added_at
                    """,
                    (url, title or url, added_at),
                )
            self._dates[url] = added_at
        return True

    def remove(self, url):
        with self._lock, closing(self.database.connect()) as connection:
            with connection:
                cursor = connection.execute(
                    "DELETE FROM reading_list WHERE url = ?",
                    (url,),
                )
            self._dates.pop(url, None)
        return cursor.rowcount > 0

    def list_entries(self):
        with self._lock, closing(self.database.connect()) as connection:
            rows = connection.execute(
                """
                SELECT url, title, added_at
                FROM reading_list
                ORDER BY added_at DESC
                """
            ).fetchall()
        return [ReadingListEntry(*row) for row in rows]

    def urls(self):
        with self._lock:
            return set(self._dates)

    def dates(self):
        with self._lock:
            return dict(self._dates)
