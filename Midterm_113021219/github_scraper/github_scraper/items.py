import scrapy

class GithubRepoItem(scrapy.Item):
    url = scrapy.Field()
    name = scrapy.Field()
    about = scrapy.Field()
    last_updated = scrapy.Field()
    languages = scrapy.Field()
    commits = scrapy.Field()
    is_empty = scrapy.Field()
