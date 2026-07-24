"""SQLite-backed user-controlled read-state repository."""

from contextlib import closing
from datetime import datetime, timezone

class ReadRepository:
    """Persist stories explicitly marked as read by the user."""

    def __init__(self, database):
        self.database = database
        self.database_path = self.database.path
        self._lock = self.database.lock
        self._read_dates = self._load_dates()

    def _connect(self):
        return self.database.connect()

    def _load_dates(self):
        with closing(self._connect()) as connection:
            rows = connection.execute(
                "SELECT url, read_at FROM read_stories"
            ).fetchall()
        return dict(rows)

    def toggle(self, url, title):
        if not url:
            return False
        if url in self.read_urls():
            self.mark_unread(url)
            return False
        self.mark_read(url, title)
        return True

    def mark_read(self, url, title):
        read_at = datetime.now(timezone.utc).isoformat(timespec="microseconds")
        with self._lock, closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    """
                    INSERT INTO read_stories (url, title, read_at)
                    VALUES (?, ?, ?)
                    ON CONFLICT(url) DO UPDATE SET
                        title = excluded.title,
                        read_at = excluded.read_at
                    """,
                    (url, title or url, read_at),
                )
            self._read_dates[url] = read_at

    def mark_unread(self, url):
        with self._lock, closing(self._connect()) as connection:
            with connection:
                connection.execute(
                    "DELETE FROM read_stories WHERE url = ?",
                    (url,),
                )
            self._read_dates.pop(url, None)

    def read_urls(self):
        with self._lock:
            return set(self._read_dates)

    def read_dates(self):
        with self._lock:
            return dict(self._read_dates)
