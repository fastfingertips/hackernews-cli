import unittest

from hackernews_cli.hn.parser import parse_html


SAMPLE_HTML = """
<table>
  <tr class="athing" id="123">
    <td><span class="rank">1.</span></td>
    <td class="title">
      <span class="titleline">
        <a href="https://example.com/story">A useful story</a>
        <span class="sitestr">example.com</span>
      </span>
    </td>
  </tr>
  <tr>
    <td class="subtext">
      <span class="score">42 points</span>
      <a class="hnuser">ada</a>
      <span class="age" title="2026-07-24T10:00:00 123">
        2 hours ago
      </span>
      <a href="item?id=123">12 comments</a>
    </td>
  </tr>
</table>
"""


class HtmlParserTests(unittest.TestCase):
    def test_parse_html_builds_complete_article(self):
        articles = parse_html(SAMPLE_HTML)

        self.assertEqual(len(articles), 1)
        article = articles[0]
        self.assertEqual(article.title, "A useful story")
        self.assertEqual(article.domain, "example.com")
        self.assertEqual(article.score, "42 points")
        self.assertEqual(article.author, "ada")
        self.assertEqual(article.comments_count, "12 comments")
        self.assertEqual(article.published_at, "2026-07-24T10:00:00")
        self.assertEqual(article.hn_link, "https://news.ycombinator.com/item?id=123")


if __name__ == "__main__":
    unittest.main()
