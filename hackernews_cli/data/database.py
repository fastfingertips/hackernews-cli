"""Shared SQLite database connection factory."""

import sqlite3
from contextlib import closing
from pathlib import Path
from threading import RLock

from platformdirs import user_data_path

from .schema import ensure_schema


class Database:
    """Own the unified DB path, schema initialization, and shared lock."""

    def __init__(self, path=None):
        self.path = Path(path or self.default_path())
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.lock = RLock()
        self._initialize()

    @staticmethod
    def default_path():
        return user_data_path(
            "hackernews-cli",
            appauthor=False,
        ) / "hackernews-cli-data.sqlite3"

    def connect(self):
        return sqlite3.connect(self.path)

    def _initialize(self):
        with self.lock, closing(self.connect()) as connection:
            with connection:
                ensure_schema(connection)
