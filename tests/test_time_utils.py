import unittest
from datetime import datetime, timedelta, timezone

from hackernews_cli.ui.time import full_relative_time, relative_time


class RelativeTimeTests(unittest.TestCase):
    def test_formats_full_local_date_followed_by_relative_age(self):
        now = datetime(2026, 7, 24, 14, 30, tzinfo=timezone.utc)
        local_timezone = timezone(timedelta(hours=3))

        self.assertEqual(
            full_relative_time(
                "2026-07-24T12:30:00+00:00",
                now=now,
                display_timezone=local_timezone,
            ),
            "2026-07-24 15:30:00 (2h ago)",
        )

    def test_full_time_normalizes_offsets_to_display_timezone(self):
        now = datetime(2026, 7, 24, 14, 30, tzinfo=timezone.utc)

        self.assertEqual(
            full_relative_time(
                "2026-07-24T15:30:00+03:00",
                now=now,
                display_timezone=timezone.utc,
            ),
            "2026-07-24 12:30:00 (2h ago)",
        )

    def setUp(self):
        self.now = datetime(2026, 7, 22, 12, 0, tzinfo=timezone.utc)

    def age(self, **delta):
        return (self.now - timedelta(**delta)).isoformat()

    def test_formats_compact_relative_units(self):
        cases = (
            (self.age(seconds=20), "just now"),
            (self.age(minutes=5), "5m ago"),
            (self.age(hours=3), "3h ago"),
            (self.age(days=4), "4d ago"),
            (self.age(days=14), "2w ago"),
            (self.age(days=90), "3mo ago"),
            (self.age(days=730), "2y ago"),
        )
        for value, expected in cases:
            with self.subTest(expected=expected):
                self.assertEqual(relative_time(value, now=self.now), expected)


if __name__ == "__main__":
    unittest.main()
