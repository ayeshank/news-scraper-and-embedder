"""
    Dawn Blog Spider.
"""
import scrapy
import hashlib
from handler import SpiderFactory

@SpiderFactory.register('Dawn_Pakistan_Spider')
class Dawn_Pakistan_Spider(scrapy.Spider):
    name = "Dawn_Pakistan"

    def __init__(self, *args, **kwargs):
        self.url = kwargs.get('url', 'https://www.dawn.com/pakistan')
        super().__init__(*args, **kwargs)

    def start_requests(self):
        yield scrapy.Request(url=self.url, callback=self.parse)

    def parse_article(self, response, title, date):
        article_url = response.url or "Null"
        content = response.css("div.story__content p::text").getall() or "Null"
        content = ' '.join(p.strip().replace(',', '') for p in content) or "Null"
        checksum = hashlib.md5(f"{title}-{date}-{article_url}".encode("utf-8")).hexdigest() or "Null"
        dateExtract = (
            response.css("span.timestamp--date::text").get()
            or response.xpath("//span[contains(@class, 'timestamp--date')]/text()").get()
            or "Null"
        )
        
        return {
            "title": title,
            "date": dateExtract.strip() if dateExtract else "Null",
            "hex": checksum,
            "article_url": article_url,
            "source": "Dawn",
            "article_content": content
        }

    def parse(self, response):
        articles = response.css("article.story")
        for article in articles:
            title = article.css("h2.story__title a::text").get() or "Null"
            link = response.urljoin(article.css("a::attr(href)").get()) or "Null"
            date = response.xpath("//span[contains(@class, 'timestamp--date')]/text()").get() or "Null"
            full_link = response.urljoin(link)
            #Only process /news/ articles
            if not full_link.startswith("https://www.dawn.com/news/"):
                continue
            yield scrapy.Request(link, callback=self.parse_article, cb_kwargs={
                "title": title.strip() if title else "Untitled",
                "date": date.strip()
            })
            
            
            
            
# import scrapy
# import hashlib
# from handler import SpiderFactory


# @SpiderFactory.register('Dawn_Pakistan_Spider')
# class Dawn_Pakistan_Spider(scrapy.Spider):
#     name = "Dawn_Pakistan"

#     def __init__(self, *args, **kwargs):
#         self.url = kwargs.get('url', 'https://www.dawn.com/pakistan')
#         super().__init__(*args, **kwargs)

#     def start_requests(self):
#         yield scrapy.Request(
#             url=self.url,
#             callback=self.parse,
#             meta={
#                 "playwright": True,
#                 "playwright_page_methods": [
#                     {
#                         "method": "evaluate",
#                         "args": ["window.scrollBy(0, document.body.scrollHeight)"]
#                     }
#                 ] * 3
#             }
#         )

#     def parse_article(self, response, title, date):
#         article_url = response.url
#         content = response.css("div.story__content p::text").getall()
#         content = ' '.join(p.strip().replace(',', '') for p in content if p.strip())
#         checksum = hashlib.md5(f"{title}-{date}-{article_url}".encode("utf-8")).hexdigest()
#         dateExtract = (
#             response.css("span.timestamp--date::text").get()
#             or response.xpath("//span[contains(@class, 'timestamp--date')]/text()").get()
#             or date
#         )

#         yield {
#             "title": title,
#             "date": dateExtract.strip(),
#             "hex": checksum,
#             "article_url": article_url,
#             "source": "Dawn",
#             "article_content": content
#         }

#     def parse(self, response):
#         articles = response.css("article.story")
#         for article in articles:
#             title = article.css("h2.story__title a::text").get()
#             link = article.css("a::attr(href)").get()
#             if not link or not link.startswith("/news/"):
#                 continue
#             full_link = response.urljoin(link)
#             yield scrapy.Request(
#                 full_link,
#                 callback=self.parse_article,
#                 cb_kwargs={"title": title.strip(), "date": "Unknown"},
#                 meta={
#                     "playwright": True,
#                     "playwright_page_methods": [
#                         {
#                             "method": "evaluate",
#                             "args": ["window.scrollBy(0, document.body.scrollHeight)"]
#                         }
#                     ] * 3
#                 }
#             )
  