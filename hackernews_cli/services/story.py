"""Story-level actions and persistence."""

import webbrowser

from ..data.events import OPEN_ARTICLE, OPEN_COMMENTS

class StoryService:
    def __init__(self, context, opener=None):
        self.context = context
        self.opener = opener or webbrowser.open

    @staticmethod
    def selected_article(articles, selected_index):
        if articles and 0 <= selected_index < len(articles):
            return articles[selected_index]
        return None

    def open_article(self, article, kind=OPEN_ARTICLE):
        if not article:
            return False
        url = article.hn_link if kind == OPEN_COMMENTS else article.link
        return self.open_url(url, article.title, kind)

    def open_url(self, url, title, kind=OPEN_ARTICLE):
        if not url:
            return False
        self.opener(url)
        self.context.history_repository.add(url, title, kind)
        return True
