import scrapy

class GithubSpider(scrapy.Spider):
    name = "Github"
    allowed_domains = ["github.com"]
    start_urls = ["https://github.com/Zefanya211004?tab=repositories"]

    custom_settings = {
        'FEED_FORMAT': 'xml',
        'FEED_URI': 'github_repositories.xml',
        'FEED_EXPORT_ENCODING': 'utf-8',
        'ROBOTSTXT_OBEY': False, 
        'DOWNLOAD_DELAY': 2,
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    def parse(self, response):
        repos = response.css('li[itemprop="owns"]') or response.css('div.Box-row')
        
        if not repos:
            self.logger.error("No repositories found!")
            return
        
        for repo in repos:
            item = {
                'url': response.urljoin(repo.css('a[itemprop="name codeRepository"]::attr(href)').get()),
                'last_updated': repo.css('relative-time::attr(datetime)').get(),
            }
            
            repo_name = repo.css('a[itemprop="name codeRepository"]::text').get()
            item['repo_name'] = repo_name.strip() if repo_name else None
            
            about = repo.css('p[itemprop="description"]::text').get()
            item['about'] = about.strip() if about else repo_name
            
            if item['url']:
                yield scrapy.Request(
                    item['url'],
                    callback=self.parse_repo,
                    meta={'item': item},
                    headers={'Referer': response.url}
                )
            else:
                item.update({'languages': None, 'commits': None})
                yield item
        
    def parse_repo(self, response):
        item = response.meta['item']
        
        empty_repo = bool(response.css('div.BlankState'))
        
        if empty_repo:
            item.update({
                'languages': None,
                'commits': None
            })
        else:
            languages = response.css('li.d-inline a[data-ga-click*="language"] span::text').getall()
            item['languages'] = [lang.strip() for lang in languages] if languages else None
            
            commits_text = response.css('a[href*="commits"] span::text').get()
            if commits_text:
                item['commits'] = commits_text.strip().replace(',', '')
            else:
                commits_text = response.css('span.fgColor-default::text').get()
                item['commits'] = commits_text.strip().replace(',', '') if commits_text else None
        
        yield item
