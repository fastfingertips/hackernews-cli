"""SQLite-backed browsing history repository."""

from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Optional

from .events import OPEN_ARTICLE, VISIT_EVENTS


@dataclass(frozen=True)
class HistoryEntry:
    id: int
    url: str
    title: str
    kind: str
    visited_at: str
    reverted_event_id: Optional[int] = None


@dataclass(frozen=True)
class HistoryActivityStats:
    last_hour: int
    today: int
    this_week: int
    this_year: int


class HistoryRepository:
    """Persist the activity event log and its visit projection."""

    def __init__(self, database):
        self.database = database
        self.database_path = self.database.path
        self._lock = self.database.lock
        self._visited_dates = self._load_visited_dates()

    def _connect(self):
        return self.database.connect()

    def _load_visited_dates(self):
        with closing(self._connect()) as connection:
            rows = connection.execute(
                """
                SELECT url, MAX(visited_at)
                FROM history
                WHERE kind IN (?, ?, ?, ?, ?, ?)
                GROUP BY url
                """,
                VISIT_EVENTS,
            ).fetchall()
        return dict(rows)

    def add(
            self,
            url,
            title,
            kind=OPEN_ARTICLE,
            reverted_event_id=None):
        if not url:
            return None

        visited_at = datetime.now(timezone.utc).isoformat(timespec="microseconds")
        with self._lock, closing(self._connect()) as connection:
            with connection:
                cursor = connection.execute(
                    """
                    INSERT INTO history (
                        url,
                        title,
                        kind,
                        visited_at,
                        reverted_event_id
                    )
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        url,
                        title or url,
                        kind,
                        visited_at,
                        reverted_event_id,
                    ),
                )
            if kind in VISIT_EVENTS:
                self._visited_dates[url] = visited_at
            return cursor.lastrowid

    def list_entries(self, limit=500):
        with self._lock, closing(self._connect()) as connection:
            rows = connection.execute(
                """
                SELECT id, url, title, kind, visited_at, reverted_event_id
                FROM history
                ORDER BY visited_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()
        return [HistoryEntry(*row) for row in rows]

    def delete(self, entry_id):
        with self._lock, closing(self._connect()) as connection:
            with connection:
                row = connection.execute(
                    "SELECT url, kind FROM history WHERE id = ?",
                    (entry_id,),
                ).fetchone()
                connection.execute("DELETE FROM history WHERE id = ?", (entry_id,))
                if row and row[1] in VISIT_EVENTS:
                    remaining = connection.execute(
                        """
                        SELECT 1
                        FROM history
                        WHERE url = ? AND kind IN (?, ?, ?, ?, ?, ?)
                        LIMIT 1
                        """,
                        (row[0], *VISIT_EVENTS),
                    ).fetchone()
                    if not remaining:
                        self._visited_dates.pop(row[0], None)
                    else:
                        latest = connection.execute(
                            """
                            SELECT MAX(visited_at)
                            FROM history
                            WHERE url = ? AND kind IN (?, ?, ?, ?, ?, ?)
                            """,
                            (row[0], *VISIT_EVENTS),
                        ).fetchone()[0]
                        self._visited_dates[row[0]] = latest

    def is_reverted(self, entry_id):
        with self._lock, closing(self._connect()) as connection:
            row = connection.execute(
                """
                SELECT 1
                FROM history
                WHERE reverted_event_id = ?
                LIMIT 1
                """,
                (entry_id,),
            ).fetchone()
        return row is not None

    def clear(self):
        with self._lock, closing(self._connect()) as connection:
            with connection:
                connection.execute("DELETE FROM history")
            self._visited_dates.clear()

    def visited_urls(self):
        with self._lock:
            return set(self._visited_dates)

    def visited_dates(self):
        with self._lock:
            return dict(self._visited_dates)

    def activity_stats(self, now=None):
        """Count all visit events across useful local-time windows."""
        local_now = now or datetime.now().astimezone()
        if local_now.tzinfo is None:
            local_now = local_now.astimezone()

        day_start = local_now.replace(
            hour=0,
            minute=0,
            second=0,
            microsecond=0,
        )
        week_start = day_start - timedelta(days=day_start.weekday())
        year_start = day_start.replace(month=1, day=1)
        boundaries = (
            local_now - timedelta(hours=1),
            day_start,
            week_start,
            year_start,
        )
        utc_boundaries = tuple(
            boundary.astimezone(timezone.utc).isoformat()
            for boundary in boundaries
        )

        with self._lock, closing(self._connect()) as connection:
            row = connection.execute(
                """
                SELECT
                    COUNT(CASE WHEN julianday(visited_at) >= julianday(?) THEN 1 END),
                    COUNT(CASE WHEN julianday(visited_at) >= julianday(?) THEN 1 END),
                    COUNT(CASE WHEN julianday(visited_at) >= julianday(?) THEN 1 END),
                    COUNT(CASE WHEN julianday(visited_at) >= julianday(?) THEN 1 END)
                FROM history
                WHERE kind IN (?, ?, ?, ?, ?, ?)
                """,
                (*utc_boundaries, *VISIT_EVENTS),
            ).fetchone()
        return HistoryActivityStats(*row)
