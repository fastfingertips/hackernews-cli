import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from hackernews_cli.app import ApplicationContext
from hackernews_cli.data import (
    Database,
    FavoriteRepository,
    HistoryRepository,
    ReadRepository,
    ReadingListRepository,
)
from hackernews_cli.services import StorageService
from hackernews_cli.ui.components.data_panel import draw_data
from hackernews_cli.ui.components.frame import PageFrame


class RecordingScreen:
    def __init__(self):
        self.writes = []

    def erase(self):
        pass

    def getmaxyx(self):
        return 20, 120

    def addstr(self, y, x, text, attr=0):
        self.writes.append((y, x, text, attr))

    def refresh(self):
        pass


class StorageTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        root = Path(self.directory.name)
        database = Database(root / "hackernews-cli-data.sqlite3")
        self.context = ApplicationContext(
            page_service=Mock(),
            history_repository=HistoryRepository(database),
            favorite_repository=FavoriteRepository(database),
            read_repository=ReadRepository(database),
            reading_list_repository=ReadingListRepository(database),
        )
        self.service = StorageService(self.context)

    def tearDown(self):
        self.directory.cleanup()

    def test_lists_all_local_databases_and_common_directory(self):
        databases = self.service.databases()

        self.assertEqual(
            [database.path.name for database in databases],
            ["hackernews-cli-data.sqlite3"],
        )
        self.assertEqual(self.service.directory(), Path(self.directory.name))

    @patch("hackernews_cli.services.storage.os.startfile", create=True)
    @patch("hackernews_cli.services.storage.sys.platform", "win32")
    def test_opens_database_directory_with_windows_file_manager(self, startfile):
        opened = self.service.open_directory()

        self.assertEqual(opened, Path(self.directory.name))
        startfile.assert_called_once_with(str(Path(self.directory.name)))

    @patch(
        "hackernews_cli.ui.components.footer.curses.has_colors",
        return_value=False,
    )
    @patch(
        "hackernews_cli.ui.components.header.curses.has_colors",
        return_value=False,
    )
    def test_data_panel_explains_location_and_security(
            self,
            _header_colors,
            _footer_colors):
        screen = RecordingScreen()

        draw_data(
            screen,
            PageFrame.from_screen(screen),
            self.service.directory(),
            self.service.databases(),
        )

        rendered = "".join(write[2] for write in screen.writes)
        self.assertIn(str(self.service.directory()), rendered)
        self.assertIn("SQLite", rendered)
        self.assertIn("sync: off", rendered)
        self.assertIn("encryption: no", rendered)
        self.assertIn("hackernews-cli-data.sqlite3", rendered)
        self.assertIn("saved filters", rendered)
