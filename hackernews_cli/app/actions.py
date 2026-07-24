"""Map keys to action methods without owning application behavior."""

from curses import KEY_ENTER, KEY_LEFT, KEY_RIGHT

from ..hn.categories import CATEGORY_SHORTCUTS
from .action_executor import ActionExecutor


class ActionHandler:
    HANDLED_KEYS = {
        KEY_ENTER,
        KEY_LEFT,
        KEY_RIGHT,
        10,
        ord("c"),
        ord(" "),
        ord("u"),
        ord("U"),
        ord("/"),
        ord("?"),
        ord("i"),
        ord("I"),
        ord("H"),
        ord("f"),
        ord("F"),
        ord("r"),
        ord("s"),
        ord("S"),
        ord("t"),
        ord("T"),
        ord("b"),
        ord("B"),
        ord("a"),
        ord("A"),
        ord("d"),
        ord("D"),
    } | {ord(key) for key in CATEGORY_SHORTCUTS}

    def __init__(
            self,
            stdscr,
            state,
            articles,
            context,
            selection_callback=None,
            loading_callback=None):
        self.executor = ActionExecutor(
            stdscr,
            state,
            articles,
            context,
            selection_callback,
            loading_callback,
        )

    def handle_action(self, key):
        actions = {
            KEY_ENTER: self.executor.open_link,
            KEY_LEFT: self.executor.previous_tab,
            KEY_RIGHT: self.executor.next_tab,
            10: self.executor.open_link,
            ord("c"): self.executor.open_comments,
            ord(" "): self.executor.reset_filter,
            ord("u"): self.executor.refresh_page,
            ord("U"): self.executor.refresh_page,
            ord("/"): self.executor.apply_filter,
            ord("?"): self.executor.show_help,
            ord("i"): self.executor.show_about,
            ord("I"): self.executor.show_about,
            ord("H"): self.executor.show_history,
            ord("f"): self.executor.toggle_favorite,
            ord("F"): self.executor.show_favorites,
            ord("r"): self.executor.toggle_read,
            ord("s"): self.executor.save_filter,
            ord("S"): self.executor.show_filters,
            ord("t"): self.executor.toggle_read_later,
            ord("T"): self.executor.show_reading_list,
            ord("b"): lambda: self.executor.bulk_open(5),
            ord("B"): lambda: self.executor.bulk_open(10),
            ord("a"): self.executor.load_all,
            ord("A"): self.executor.load_all,
            ord("d"): self.executor.show_data,
            ord("D"): self.executor.show_data,
        }
        actions.update({
            ord(key): lambda category=category: (
                self.executor.switch_category(category)
            )
            for key, category in CATEGORY_SHORTCUTS.items()
        })
        action = actions.get(key)
        if action:
            action()

    @classmethod
    def handles(cls, key):
        return key in cls.HANDLED_KEYS
