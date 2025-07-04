"""
    Aljazeera Blog Spider.
"""
import scrapy
import hashlib
from handler import SpiderFactory

@SpiderFactory.register('Aljazeera_Uscanada_Spider')
class Aljazeera_Uscanada_Spider(scrapy.Spider):
    name = "AlJazeera_Uscanada"

    def __init__(self, *args, **kwargs):
        self.url = kwargs.get('url', 'https://www.aljazeera.com/us-canada/')
        super().__init__(*args, **kwargs)

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse_article(self, response, title, date):
        article_url = response.url or "Null"
        titleExtract = response.css("header.article-header h1::text").get() or "Null"
        dateExtract = response.css("div.date-simple span[aria-hidden='true']::text").get() or "Null"
        paragraphs = response.css("div.wysiwyg p::text").getall() or "Null"
        content = ' '.join(p.strip().replace(',', '') for p in paragraphs) or "Null"
        checksum = hashlib.md5(f"{title}-{date}-{article_url}".encode("utf-8")).hexdigest() or "Null"

        return {
            "title": titleExtract,
            "date": dateExtract,
            "hex": checksum,
            "article_url": article_url,
            "source": "Al Jazeera",
            "article_content": content
        }

    def parse(self, response):
        articles = response.css("article")
        for article in articles:
            title = article.css("div.article-header h1::text").get() or "Null"
            link = response.urljoin(article.css("h3 a::attr(href)").get()) or "Null"
            date = article.css("time::attr(datetime)").get() or "Null"

            yield scrapy.Request(link, callback=self.parse_article, cb_kwargs={
                "title": title.strip(),
                "date": date.strip()
            })
