def apply_filter(articles, filter_query):
    return [s for s in articles if filter_query.lower() in s.title.lower()]