import unittest

from hackernews_cli.ui.terminal.animation import selection_frames


class SelectionAnimationTests(unittest.TestCase):
    def test_short_move_visits_each_row(self):
        self.assertEqual(selection_frames(2, 5), [3, 4, 5])

    def test_long_move_has_bounded_frames_and_reaches_target(self):
        frames = selection_frames(0, 30)

        self.assertEqual(len(frames), 8)
        self.assertEqual(frames[-1], 30)
        self.assertEqual(frames, sorted(frames))

    def test_upward_move_reaches_target(self):
        frames = selection_frames(20, 3)

        self.assertEqual(frames[-1], 3)
        self.assertEqual(frames, sorted(frames, reverse=True))


if __name__ == "__main__":
    unittest.main()
