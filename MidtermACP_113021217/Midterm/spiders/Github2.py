import scrapy
from datetime import datetime

class GithubSpider(scrapy.Spider):
    name = "Github2"
    allowed_domains = ["github.com"]
    start_urls = ["https://github.com/Zefanya211004?tab=repositories"]

    custom_settings = {
        'FEED_FORMAT': 'xml',
        'FEED_URI': 'github_repositories.xml',
        'FEED_EXPORT_ENCODING': 'utf-8',
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'ROBOTSTXT_OBEY': False,
        'DOWNLOAD_DELAY': 2,  # Be polite with delay
        'CONCURRENT_REQUESTS': 1,
    }

    def parse(self, response):
        self.logger.info(f"Processing profile page: {response.url}")
        
        # More reliable repository selector
        repos = response.css('li[itemprop="owns"]') or response.css('div.Box-row') or response.css('div[data-test-id="repository-list-item"]')
        
        if not repos:
            self.logger.error("No repositories found on the page!")
            return

        self.logger.info(f"Found {len(repos)} repositories")
        
        for repo in repos:
            item = {
                'url': response.urljoin(repo.css('a[itemprop="name codeRepository"]::attr(href)').get() or 
                                      repo.css('a[data-test-id="repository-link"]::attr(href)').get()),
                'last_updated': repo.css('relative-time::attr(datetime)').get(),
            }
            
            # Get repository name and about
            repo_name = (repo.css('a[itemprop="name codeRepository"]::text').get() or 
                        repo.css('a[data-test-id="repository-link"]::text').get() or "").strip()
            about = (repo.css('p[itemprop="description"]::text').get() or 
                    repo.css('p[data-test-id="repository-description"]::text').get() or repo_name)
            item['about'] = about.strip()

            self.logger.info(f"Processing repository: {repo_name}")
            
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
        self.logger.info(f"Processing repository page: {response.url}")
        
        # Check if repository is empty
        empty_repo = bool(response.css('div.BlankState'))
        
        if empty_repo:
            item.update({'languages': None, 'commits': None})
        else:
            # Improved language detection
            languages = response.css('li.d-inline a[data-ga-click*="language"] span::text').getall()
            if not languages:
                languages = response.css('a[href*="#language"] span::text').getall()
            item['languages'] = [lang.strip() for lang in languages] if languages else None
            
            # Improved commit count detection
            commits_text = response.css('a[href*="commits"] span::text').get()
            if not commits_text:
                commits_text = response.css('strong[data-test-id="commits"]::text').get()
            item['commits'] = commits_text.strip().replace(',', '') if commits_text else None
        
        yield item