import unittest
from contextlib import redirect_stdout
from io import StringIO
from unittest.mock import patch

import main as entrypoint
from hackernews_cli import __version__
from hackernews_cli.hn.client import HEADERS


class VersionTests(unittest.TestCase):
    def test_release_version_is_shared_with_http_client(self):
        self.assertEqual(__version__, "1.0.0")
        self.assertEqual(
            HEADERS["User-Agent"],
            "hackernews-cli/1.0.0",
        )

    def test_version_flag_prints_without_starting_curses(self):
        output = StringIO()

        with patch.object(entrypoint.curses, "wrapper") as wrapper:
            with redirect_stdout(output), self.assertRaises(SystemExit):
                entrypoint.main(["--version"])

        self.assertEqual(output.getvalue().strip(), "hackernews-cli 1.0.0")
        wrapper.assert_not_called()


if __name__ == "__main__":
    unittest.main()
