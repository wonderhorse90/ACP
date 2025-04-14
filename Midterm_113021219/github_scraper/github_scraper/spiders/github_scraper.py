import scrapy
import datetime
import re
from github_scraper.items import GithubRepoItem

class GitHubSpider(scrapy.Spider):
    name = 'github_spider'
    allowed_domains = ['github.com']
    start_urls = ['https://github.com/nayottama11?tab=repositories']

    def start_requests(self):
        print("Starting crawl with URL:", self.start_urls[0])  
        for url in self.start_urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        print("Parsing page:", response.url)  
        repositories = response.css('#user-repositories-list li')

        for repo in repositories:
            repo_url = response.urljoin(repo.css('h3 a::attr(href)').get())
            repo_name = repo.css('h3 a::text').get().strip()

            about = repo.css('p::text').get()
            print("About:", about)  
            if about:
                about = about.strip()

            last_updated = repo.css('relative-time::attr(datetime)').get()
            if last_updated:
                last_updated = datetime.datetime.fromisoformat(last_updated.replace('Z', '+00:00')).strftime('%Y-%m-%d')

            is_empty = 'This repository is empty.' in repo.get()

            if not about and not is_empty:
                about = repo_name

            repo_data = {
                'url': repo_url,
                'name': repo_name,
                'about': about,
                'last_updated': last_updated,
                'is_empty': is_empty
            }

            yield scrapy.Request(
                url=repo_url,
                callback=self.parse_repository_details,
                meta={'repo_data': repo_data}
            )

        next_page = response.css('a.next_page::attr(href)').get()
        if next_page:
            yield scrapy.Request(url=response.urljoin(next_page), callback=self.parse)

    def parse_repository_details(self, response):
        repo_data = response.meta['repo_data']
        is_empty = 'This repository is empty' in response.text
        repo_data['is_empty'] = is_empty

        if is_empty:
            repo_data['languages'] = None
            repo_data['commits'] = None
            yield repo_data
            return

        lang_data = response.css('a[href*="search?l="] span::text').getall()
        repo_data['languages'] = [lang.strip() for lang in lang_data if lang.strip()] or ['None']

        commits = None
        commit_texts = response.css('a[href*="commits"] span::text').getall()
        for text in commit_texts:
            match = re.search(r'\d+', text)
            if match:
                commits = match.group(0)
                break

        repo_data['commits'] = commits if commits else '0'
        yield repo_data
