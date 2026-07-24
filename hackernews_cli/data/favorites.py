"""SQLite-backed favorite story repository."""

from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone

@dataclass(frozen=True)
class FavoriteEntry:
    url: str
    title: str
    added_at: str


class FavoriteRepository:
    """Persist and manage the user's favorite stories."""

    def __init__(self, database):
        self.database = database
        self.database_path = self.database.path
        self._lock = self.database.lock
        self._favorite_dates = self._load_dates()

    def _connect(self):
        return self.database.connect()

    def _load_dates(self):
        with closing(self._connect()) as connection:
            rows = connection.execute(
                "SELECT url, added_at FROM favorites"
            ).fetchall()
        return dict(rows)

    def toggle(self, url, title):
        if not url:
            return False
        if url in self.favorite_urls():
            self.remove(url)
            return False
        self.add(url, title)
        return True

    def add(self, url, title):
        added_at = datetime.now(timezone.utc).isoformat(timespec="microseconds")
        with self._lock, closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    INSERT INTO favorites (url, title, added_at)
                    VALUES (?, ?, ?)
                    ON CONFLICT(url) DO UPDATE SET
                        title = excluded.title,
                        added_at = excluded.added_at
                    """,
                    (url, title or url, added_at),
                )
            self._favorite_dates[url] = added_at

    def remove(self, url):
        with self._lock, closing(self._connect()) as connection:
            with connection:
                connection.execute("DELETE FROM favorites WHERE url = ?", (url,))
            self._favorite_dates.pop(url, None)

    def list_entries(self):
        with self._lock, closing(self._connect()) as connection:
            rows = connection.execute(
                """
                SELECT url, title, added_at
                FROM favorites
                ORDER BY added_at DESC
                """
            ).fetchall()
        return [FavoriteEntry(*row) for row in rows]

    def favorite_urls(self):
        with self._lock:
            return set(self._favorite_dates)

    def favorite_dates(self):
        with self._lock:
            return dict(self._favorite_dates)
