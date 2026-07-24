import curses
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

from hackernews_cli.app import ApplicationContext, FeedState
from hackernews_cli.app.input import InputController
from hackernews_cli.data import (
    Database,
    FavoriteRepository,
    HistoryRepository,
    ReadRepository,
    ReadingListRepository,
)
from hackernews_cli.hn import Article, Page


class InputDispatchTests(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        database = Database(Path(self.directory.name) / "test.sqlite3")
        self.page_service = Mock()
        self.context = ApplicationContext(
            page_service=self.page_service,
            history_repository=HistoryRepository(database),
            favorite_repository=FavoriteRepository(database),
            read_repository=ReadRepository(database),
            reading_list_repository=ReadingListRepository(database),
        )
        self.controller = InputController(self.context)
        self.articles = [
            Article("First", "https://example.com/first"),
            Article("Second", "https://example.com/second"),
        ]
        self.state = FeedState(
            Page(self.articles, current_page=2, total_pages=10, category="top")
        )

    def tearDown(self):
        self.directory.cleanup()

    def dispatch(
            self,
            key,
            state=None,
            articles=None,
            callback=None,
            loading_callback=None):
        state = state or self.state
        should_continue = self.controller.handle(
            None,
            key,
            state,
            articles or self.articles,
            callback,
            loading_callback,
        )
        return should_continue, state

    def test_navigation_updates_selection_without_running_an_action(self):
        _, state = self.dispatch(curses.KEY_DOWN)
        self.assertEqual(state.selected_index, 1)

    def test_category_switch_resets_all_related_state(self):
        ask_page = Page([], current_page=1, total_pages=10, category="ask")
        self.page_service.get_page.return_value = ask_page
        self.state.selected_index = 1
        self.state.filter_query = "python"

        _, state = self.dispatch(ord("3"))

        self.assertEqual(state.page, ask_page)
        self.assertEqual(state.selected_index, 0)
        self.assertEqual(state.filter_query, "")
        self.page_service.get_page.assert_called_once_with(
            1,
            category="ask",
            refresh=False,
        )

    def test_h_jumps_up_without_discarding_loaded_stories(self):
        articles = [
            Article(f"Story {index}", f"https://example.com/{index}")
            for index in range(40)
        ]
        page = Page(articles, 2, 10, "top", loaded_pages=(1, 2))
        state = FeedState(page, selected_index=35)

        _, state = self.dispatch(ord("h"), state, articles)

        self.assertEqual(state.page, page)
        self.assertEqual(state.selected_index, 5)

    def test_down_on_last_story_appends_next_prefetched_batch(self):
        next_page = Page([
            Article("Third", "https://example.com/third", item_id="3"),
            Article("Fourth", "https://example.com/fourth", item_id="4"),
        ], 2, 10, "top")
        first_page = Page(self.articles, 1, 10, "top")
        state = FeedState(first_page, selected_index=1)
        self.page_service.get_page.return_value = next_page

        _, state = self.dispatch(curses.KEY_DOWN, state)

        self.assertEqual(state.current_page, 2)
        self.assertEqual(len(state.page.articles), 4)
        self.assertEqual(state.selected_index, 2)

    def test_q_and_uppercase_q_stop_the_controller(self):
        self.assertFalse(self.dispatch(ord("q"))[0])
        self.assertFalse(self.dispatch(ord("Q"))[0])

    def test_uppercase_j_remains_navigation_for_caps_lock(self):
        _, state = self.dispatch(ord("J"))
        self.assertEqual(state.selected_index, 1)

    def test_u_fully_refreshes_current_category(self):
        refreshed_page = Page([], 1, 10, "top")
        self.page_service.refresh_category.return_value = refreshed_page
        self.state.selected_index = 1
        self.state.filter_query = "python"

        _, state = self.dispatch(ord("u"))

        self.assertEqual(state.page, refreshed_page)
        self.assertEqual(state.selected_index, 0)
        self.assertEqual(state.filter_query, "python")

    @patch("hackernews_cli.app.action_executor.show_data")
    def test_d_opens_local_data_screen(self, show_data):
        self.dispatch(ord("d"))
        show_data.assert_called_once()

    @patch("hackernews_cli.app.action_executor.show_about")
    def test_i_opens_about_screen(self, show_about):
        self.dispatch(ord("i"))
        show_about.assert_called_once()

    @patch("hackernews_cli.services.story.webbrowser.open")
    def test_opening_story_records_it_in_history(self, open_browser):
        self.dispatch(10)

        self.assertIn(
            self.articles[0].link,
            self.context.history_repository.visited_urls(),
        )
        open_browser.assert_called_once_with(self.articles[0].link)

    def test_f_toggles_selected_story_as_favorite(self):
        self.dispatch(ord("f"))
        self.assertIn(
            self.articles[0].link,
            self.context.favorite_repository.favorite_urls(),
        )
        self.assertEqual(
            self.context.history_repository.list_entries()[0].kind,
            "favorite_added",
        )

    def test_r_toggles_selected_story_read_state(self):
        self.dispatch(ord("r"))
        self.assertIn(
            self.articles[0].link,
            self.context.read_repository.read_urls(),
        )
        self.assertEqual(
            self.context.history_repository.list_entries()[0].kind,
            "read_marked",
        )

    def test_t_toggles_selected_story_in_read_later(self):
        self.dispatch(ord("t"))

        self.assertIn(
            self.articles[0].link,
            self.context.reading_list_repository.urls(),
        )
        self.assertEqual(
            self.context.history_repository.list_entries()[0].kind,
            "read_later_added",
        )

    @patch("hackernews_cli.app.action_executor.show_reading_list")
    def test_uppercase_t_opens_read_later_page(self, show_page):
        self.dispatch(ord("T"))

        show_page.assert_called_once_with(None, self.context)

    @patch(
        "hackernews_cli.app.action_executor.show_saved_filters",
        return_value="is:unread points:>=100",
    )
    def test_uppercase_s_applies_a_saved_filter(self, show_filters):
        self.context.saved_filter_repository = Mock()
        self.state.selected_index = 1

        self.dispatch(ord("S"))

        self.assertEqual(
            self.state.filter_query,
            "is:unread points:>=100",
        )
        self.assertEqual(self.state.selected_index, 0)
        show_filters.assert_called_once()

    def test_a_loads_every_available_page(self):
        next_articles = [
            Article("Third", "https://example.com/third"),
            Article("Fourth", "https://example.com/fourth"),
        ]
        first_page = Page(self.articles, 1, 2, "top")
        second_page = Page(next_articles, 2, 2, "top")
        state = FeedState(first_page)
        self.page_service.get_page.return_value = second_page
        loading_callback = Mock()

        self.dispatch(
            ord("a"),
            state,
            first_page.articles,
            loading_callback=loading_callback,
        )

        self.assertEqual(state.current_page, 2)
        self.assertEqual(len(state.page.articles), 4)
        self.page_service.get_page.assert_called_once()

    @patch(
        "hackernews_cli.app.action_executor.save_active_filter",
        return_value=("is:unread", True),
    )
    def test_lowercase_s_saves_and_activates_a_filter(self, save_filter):
        self.context.saved_filter_repository = Mock()
        self.state.selected_index = 1

        self.dispatch(ord("s"))

        self.assertEqual(self.state.filter_query, "is:unread")
        self.assertEqual(self.state.selected_index, 0)
        save_filter.assert_called_once()

    @patch("hackernews_cli.services.story.webbrowser.open")
    def test_bulk_open_skips_activity_and_loads_more_candidates(self, open_browser):
        scores = [999, 900, 800, 10, 20, 500, 300, 400, 100]
        articles = [
            Article(
                f"Story {index}",
                f"https://example.com/{index}",
                score=f"{scores[index]} points",
                item_id=str(index),
            )
            for index in range(9)
        ]
        first_page = Page(articles[:5], 1, 10, "top")
        second_page = Page(articles[5:], 2, 10, "top")
        state = FeedState(first_page)
        self.page_service.get_page.return_value = second_page
        callback = Mock()
        self.context.history_repository.add(articles[0].link, articles[0].title)
        self.context.favorite_repository.add(articles[1].link, articles[1].title)
        self.context.read_repository.mark_read(articles[2].link, articles[2].title)

        self.dispatch(ord("b"), state, first_page.articles, callback)

        self.assertEqual(
            [call.args[0] for call in open_browser.call_args_list],
            [articles[index].link for index in (5, 7, 6, 8, 4)],
        )
        self.assertEqual(state.current_page, 2)
        self.assertEqual(len(state.page.articles), 9)
        self.assertEqual(state.selected_index, 4)
        self.assertEqual(
            [call.args[0] for call in callback.call_args_list],
            [5, 7, 6, 8, 4],
        )


if __name__ == "__main__":
    unittest.main()
