import unittest

from hackernews_cli.data.events import REVERSIBLE_EVENTS, VISIT_EVENTS
from hackernews_cli.hn.categories import (
    CATEGORIES,
    CATEGORY_SHORTCUTS,
    CATEGORY_URLS,
    DEFAULT_CATEGORY,
)


class DomainDefinitionTests(unittest.TestCase):
    def test_category_order_urls_and_shortcuts_share_one_definition(self):
        self.assertEqual(CATEGORIES, tuple(CATEGORY_URLS))
        self.assertEqual(tuple(CATEGORY_SHORTCUTS.values()), CATEGORIES)
        self.assertEqual(DEFAULT_CATEGORY, CATEGORIES[0])

    def test_visit_and_reversible_events_are_distinct(self):
        self.assertTrue(set(VISIT_EVENTS).isdisjoint(REVERSIBLE_EVENTS))


if __name__ == "__main__":
    unittest.main()
