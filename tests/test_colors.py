import unittest
from unittest.mock import Mock, call, patch

from hackernews_cli.ui.terminal.colors import (
    DEFAULT_COLOR_PAIR,
    apply_default_background,
    init_colors,
)


class ColorTests(unittest.TestCase):
    @patch("hackernews_cli.ui.terminal.colors.curses.init_pair")
    @patch("hackernews_cli.ui.terminal.colors.curses.use_default_colors")
    @patch("hackernews_cli.ui.terminal.colors.curses.start_color")
    @patch("hackernews_cli.ui.terminal.colors.curses.has_colors", return_value=True)
    def test_palette_defines_terminal_default_background(
            self,
            _has_colors,
            _start_color,
            _use_default_colors,
            init_pair):
        init_colors()

        self.assertIn(
            call(DEFAULT_COLOR_PAIR, -1, -1),
            init_pair.call_args_list,
        )

    @patch(
        "hackernews_cli.ui.terminal.colors.curses.color_pair",
        return_value=512,
    )
    @patch("hackernews_cli.ui.terminal.colors.curses.has_colors", return_value=True)
    def test_default_background_is_applied_to_window(
            self,
            _has_colors,
            color_pair):
        window = Mock()

        apply_default_background(window)

        color_pair.assert_called_once_with(DEFAULT_COLOR_PAIR)
        window.bkgd.assert_called_once_with(" ", 512)


if __name__ == "__main__":
    unittest.main()
