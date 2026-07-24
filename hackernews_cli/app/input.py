"""Dispatch terminal keys without owning application behavior."""

from .actions import ActionHandler
from .navigation import NavigationHandler


class InputController:
    def __init__(self, context):
        self.context = context

    def handle(
            self,
            stdscr,
            key,
            state,
            articles,
            selection_callback=None,
            loading_callback=None):
        if key in (ord("q"), ord("Q")):
            return False

        if NavigationHandler.handles(key):
            NavigationHandler(
                state,
                articles,
                self.context,
                loading_callback,
            ).handle_navigation(key)
        elif ActionHandler.handles(key):
            ActionHandler(
                stdscr,
                state,
                articles,
                self.context,
                selection_callback,
                loading_callback,
            ).handle_action(key)
        return True
