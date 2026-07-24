"""Inspect local databases and open their containing directory."""

import os
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class DatabaseInfo:
    name: str
    purpose: str
    path: Path
    size: int


class StorageService:
    def __init__(self, context):
        self.context = context

    def databases(self):
        path = Path(self.context.history_repository.database_path)
        return [DatabaseInfo(
            name=path.stem,
            purpose="History, fav, reads, later, saved filters",
            path=path,
            size=path.stat().st_size if path.exists() else 0,
        )]

    def directory(self):
        return self.databases()[0].path.parent

    def open_directory(self):
        directory = self.directory()
        directory.mkdir(parents=True, exist_ok=True)

        if sys.platform == "win32":
            os.startfile(str(directory))
        elif sys.platform == "darwin":
            self._launch("open", directory)
        else:
            self._launch("xdg-open", directory)
        return directory

    @staticmethod
    def _launch(command, directory):
        subprocess.Popen(
            [command, str(directory)],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
