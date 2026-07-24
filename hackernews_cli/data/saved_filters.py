"""SQLite repository for reusable feed filters."""

from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone


BUILTIN_FILTERS = (
    ("Unread", "is:unread"),
    ("Popular unread", "is:unread points:>=100"),
    ("Unvisited discussions", "is:unvisited replies:>=20"),
    ("Favorites", "is:fav"),
    ("High signal", "points:>=300 replies:>=50"),
    ("Read later", "is:later"),
)


@dataclass(frozen=True)
class SavedFilter:
    id: int
    name: str
    query: str
    is_builtin: bool
    created_at: str
    updated_at: str


class SavedFilterRepository:
    """Persist built-in and user-created filter queries."""

    def __init__(self, database):
        self.database = database
        self.database_path = self.database.path
        self._lock = self.database.lock

    def list_entries(self):
        with self._lock, closing(self.database.connect()) as connection:
            rows = connection.execute(
                """
                SELECT id, name, query, is_builtin, created_at, updated_at
                FROM saved_filters
                ORDER BY is_builtin DESC, name COLLATE NOCASE
                """
            ).fetchall()
        return [
            SavedFilter(
                id=row[0],
                name=row[1],
                query=row[2],
                is_builtin=bool(row[3]),
                created_at=row[4],
                updated_at=row[5],
            )
            for row in rows
        ]

    def save(self, name, query):
        name = name.strip()
        query = query.strip()
        if not name or not query:
            return False

        timestamp = _utc_now()
        with self._lock, closing(self.database.connect()) as connection:
            with connection:
                cursor = connection.execute(
                    """
                    INSERT INTO saved_filters (
                        name, query, is_builtin, created_at, updated_at
                    )
                    VALUES (?, ?, 0, ?, ?)
                    ON CONFLICT(name) DO UPDATE SET
                        query = excluded.query,
                        updated_at = excluded.updated_at
                    WHERE saved_filters.is_builtin = 0
                    """,
                    (name, query, timestamp, timestamp),
                )
            return cursor.rowcount > 0

    def update_query(self, entry_id, query):
        query = query.strip()
        if not query:
            return False

        with self._lock, closing(self.database.connect()) as connection:
            with connection:
                cursor = connection.execute(
                    """
                    UPDATE saved_filters
                    SET query = ?, updated_at = ?
                    WHERE id = ? AND is_builtin = 0
                    """,
                    (query, _utc_now(), entry_id),
                )
            return cursor.rowcount > 0

    def remove(self, entry_id):
        with self._lock, closing(self.database.connect()) as connection:
            with connection:
                cursor = connection.execute(
                    """
                    DELETE FROM saved_filters
                    WHERE id = ? AND is_builtin = 0
                    """,
                    (entry_id,),
                )
            return cursor.rowcount > 0


def _utc_now():
    return datetime.now(timezone.utc).isoformat(timespec="microseconds")
