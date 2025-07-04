# web-news-scraping
Scrapers for news articles on different websites

## How to run?
`run.sh` USAGE
```
usage: SpiderAggregator [-h] [-w URL] [-s SPIDER]

Scraps websites.

options:
  -h, --help            show this help message and exit
  -w URL, --url URL     The URL of the website to run spider on.
  -s SPIDER, --spider SPIDER
                        Name of the spider. Should be similar to website name followed by _Spider.
```
- For each new website, in `run.sh` add a new line: `python aggregator.py -s "SPIDER_NAME' -w "URL"`
- Then run `bash run.sh` or `./run.sh` to run the scraper for each website.
