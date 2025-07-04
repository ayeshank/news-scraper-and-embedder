"""
    Reuterspk Blog Spider.
"""
import scrapy
import hashlib
from handler import SpiderFactory

@SpiderFactory.register('Reuterspk_Spider')
class Reuterspk_Spider(scrapy.Spider):
    name = "ReutersPK"

    def __init__(self, *args, **kwargs):
        self.url = kwargs.get('url', 'https://www.reuters.com/world/pakistan/')
        super().__init__(*args, **kwargs)

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse_article(self, response, title, date):
        article_url = response.url
        content = response.css("div.article-body__content p::text").getall()
        if not content:
            content = response.css("div.ArticleBodyWrapper p::text").getall()
        content = ' '.join(p.strip().replace(',', '') for p in content)
        checksum = hashlib.md5(f"{title}-{date}-{article_url}".encode("utf-8")).hexdigest()

        return {
            "title": title,
            "date": date,
            "hex": checksum,
            "article_url": article_url,
            "source": "Reuters",
            "article_content": content
        }

    def parse(self, response):
        articles = response.css("article.story")
        for article in articles:
            link = article.css("a::attr(href)").get()
            full_link = response.urljoin(link)
            title = article.css("h3.story-title::text, h2::text").get()
            date = article.css("time::attr(datetime)").get() or "N/A"

            yield scrapy.Request(full_link, callback=self.parse_article, cb_kwargs={
                "title": title.strip() if title else "Untitled",
                "date": date.strip()
            })
