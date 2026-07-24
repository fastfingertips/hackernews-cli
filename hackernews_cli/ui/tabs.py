"""Shared top-level tab definitions and keyboard navigation."""

from dataclasses import dataclass

import curses

from ..hn.categories import CATEGORIES


@dataclass(frozen=True)
class Tab:
    id: str
    label: str
    compact_label: str


@dataclass(frozen=True)
class TabSwitch:
    target: str


TABS = tuple(
    Tab(category, category, category)
    for category in CATEGORIES
) + (
    Tab("favorites", "favorites", "fav"),
    Tab("later", "later", "later"),
    Tab("history", "history", "hist"),
    Tab("filters", "filters", "filters"),
    Tab("data", "data", "data"),
    Tab("about", "about", "about"),
    Tab("help", "help", "help"),
)
TAB_IDS = tuple(tab.id for tab in TABS)
TAB_BY_ID = {tab.id: tab for tab in TABS}
FEED_TAB_COUNT = len(CATEGORIES)

_ALIASES = {
    "local data": "data",
    "read later": "later",
    "saved filters": "filters",
}


def normalize_tab_id(value):
    normalized = value.casefold()
    return _ALIASES.get(normalized, normalized)


def adjacent_tab(current, step):
    current_id = normalize_tab_id(current)
    index = TAB_IDS.index(current_id)
    return TAB_IDS[(index + step) % len(TAB_IDS)]


def switch_for_key(current, key):
    if key == curses.KEY_LEFT:
        return TabSwitch(adjacent_tab(current, -1))
    if key == curses.KEY_RIGHT:
        return TabSwitch(adjacent_tab(current, 1))
    return None
