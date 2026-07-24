"""Create the unified SQLite schema."""

from .saved_filters import BUILTIN_FILTERS


SCHEMA_VERSION = 4


def ensure_schema(connection):
    """Ensure the current application tables and indexes exist."""
    _create_tables(connection)
    _ensure_history_columns(connection)
    _seed_builtin_filters(connection)
    _create_indexes(connection)
    connection.execute(f"PRAGMA user_version = {SCHEMA_VERSION}")


def _create_tables(connection):
    _create_history_table(connection)
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS favorites (
            url TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            added_at TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS read_stories (
            url TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            read_at TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS saved_filters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE COLLATE NOCASE,
            query TEXT NOT NULL,
            is_builtin INTEGER NOT NULL DEFAULT 0,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
        """
    )
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS reading_list (
            url TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            added_at TEXT NOT NULL
        )
        """
    )


def _create_history_table(connection):
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            title TEXT NOT NULL,
            kind TEXT NOT NULL,
            visited_at TEXT NOT NULL,
            reverted_event_id INTEGER
        )
        """
    )


def _ensure_history_columns(connection):
    columns = {
        row[1]
        for row in connection.execute("PRAGMA table_info(history)")
    }
    if "reverted_event_id" not in columns:
        connection.execute(
            "ALTER TABLE history ADD COLUMN reverted_event_id INTEGER"
        )


def _seed_builtin_filters(connection):
    for name, query in BUILTIN_FILTERS:
        connection.execute(
            """
            INSERT OR IGNORE INTO saved_filters (
                name, query, is_builtin, created_at, updated_at
            )
            VALUES (?, ?, 1, CURRENT_TIMESTAMP, CURRENT_TIMESTAMP)
            """,
            (name, query),
        )


def _create_indexes(connection):
    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS history_visited_at_index
        ON history (visited_at DESC)
        """
    )
    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS history_reverted_event_index
        ON history (reverted_event_id)
        """
    )
    connection.execute(
        """
        CREATE INDEX IF NOT EXISTS history_url_index
        ON history (url)
        """
    )
