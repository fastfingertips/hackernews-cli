"""Rank and open untouched stories in batches."""

from ..data.events import OPEN_BULK


class BulkOpenService:
    def __init__(self, context, feed_service, story_service):
        self.context = context
        self.feed_service = feed_service
        self.story_service = story_service

    def execute(
            self,
            state,
            articles,
            limit,
            selection_callback=None):
        if not articles:
            return articles

        activity_urls = self.context.activity_urls()
        candidates = self._candidates(articles, activity_urls)

        while (
                len(candidates) < limit
                and self.feed_service.append_next(state)):
            articles = self.context.visible_articles(
                state.page,
                state.filter_query,
            )
            candidates = self._candidates(articles, activity_urls)

        for article in candidates[:limit]:
            self.story_service.open_url(
                article.link,
                article.title,
                OPEN_BULK,
            )
            activity_urls.add(article.link)
            state.selected_index = articles.index(article)
            if selection_callback:
                selection_callback(
                    state.selected_index,
                    articles,
                    state.page,
                )

        return articles

    @classmethod
    def _candidates(cls, articles, activity_urls):
        untouched = [
            article
            for article in articles
            if article.link and article.link not in activity_urls
        ]
        return sorted(
            untouched,
            key=lambda article: cls._score_value(article.score),
            reverse=True,
        )

    @staticmethod
    def _score_value(score):
        if not score:
            return 0
        token = str(score).split(maxsplit=1)[0]
        try:
            return int(token)
        except ValueError:
            return 0
