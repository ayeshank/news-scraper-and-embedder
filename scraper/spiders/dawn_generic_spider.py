"""
    Dawn Generic Blog Spider.
"""
import scrapy
import hashlib
from handler import SpiderFactory

@SpiderFactory.register('Dawn_Generic_Spider')
class Dawn_Generic_Spider(scrapy.Spider):
    name = "Dawn_Generic"

    def __init__(self, *args, **kwargs):
        self.category = kwargs.get('category', 'opinion')  # e.g. opinion, business, tech
        self.url = f"https://www.dawn.com/{self.category}"
        self.source = f"Dawn - {self.category.capitalize()}"
        super().__init__(*args, **kwargs)

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse_article(self, response, title):
        article_url = response.url
        date = (
            response.css("span.timestamp--date::text").get()
            or response.xpath("//span[contains(@class, 'timestamp--date')]/text()").get()
            or "Null"
        )
        content = response.css("div.story__content p::text").getall()
        content = ' '.join(p.strip().replace(',', '') for p in content) if content else "Null"
        checksum = hashlib.md5(f"{title}-{date}-{article_url}".encode("utf-8")).hexdigest()

        return {
            "title": title,
            "date": date.strip(),
            "hex": checksum,
            "article_url": article_url,
            "source": self.source,
            "article_content": content
        }

    def parse(self, response):
        articles = response.css("article.story")
        for article in articles:
            title = article.css("h2.story__title a::text").get()
            link = article.css("a::attr(href)").get()
            full_link = response.urljoin(link)
            #Only process /news/ articles
            if not full_link.startswith("https://www.dawn.com/news/"):
                continue
            full_link = response.urljoin(link)
            yield scrapy.Request(full_link, callback=self.parse_article, cb_kwargs={
                "title": title.strip()
            })
