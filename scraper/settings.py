# settings.py

# Enable Playwright handlers
DOWNLOAD_HANDLERS = {
    "http": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
    "https": "scrapy_playwright.handler.ScrapyPlaywrightDownloadHandler",
}

# Correct middleware path
DOWNLOADER_MIDDLEWARES = {
    'scrapy_playwright.middleware.ScrapyPlaywrightDownloadHandler': 543,
}

# Required for Windows + asyncio
TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"

# Playwright browser config
PLAYWRIGHT_BROWSER_TYPE = "chromium"
PLAYWRIGHT_LAUNCH_OPTIONS = {"headless": True}