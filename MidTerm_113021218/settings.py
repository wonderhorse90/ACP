BOT_NAME = "github_scraper"

SPIDER_MODULES = ["github_scraper.spiders"]
NEWSPIDER_MODULE = "github_scraper.spiders"

ROBOTSTXT_OBEY = False

TWISTED_REACTOR = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
FEED_EXPORT_ENCODING = "utf-8"
