import scrapy
import datetime
import re

class GitHubSpider(scrapy.Spider):
    name = 'luthfi'
    allowed_domains = ['github.com']
    start_urls = ['https://github.com/luthfizafir?tab=repositories']

    def parse(self, response):
        repositories = response.css('#user-repositories-list li')

        for repo in repositories:
            repo_url = response.urljoin(repo.css('h3 a::attr(href)').get())
            repo_name = repo.css('h3 a::text').get().strip()

            last_updated = repo.css('relative-time::attr(datetime)').get()
            if last_updated:
                last_updated = datetime.datetime.fromisoformat(
                    last_updated.replace('Z', '+00:00')
                ).strftime('%Y-%m-%d')

            repo_data = {
                'url': repo_url,
                'name': repo_name,
                'last_updated': last_updated
            }

            yield scrapy.Request(
                url=repo_url,
                callback=self.parse_repository_details,
                meta={'repo_data': repo_data}
            )

        #pagination
        next_page = response.css('a.next_page::attr(href)').get()
        if next_page:
            yield scrapy.Request(url=response.urljoin(next_page), callback=self.parse)

    def parse_repository_details(self, response):
        repo_data = response.meta['repo_data']

        #about
        about = response.css('p.f4.my-3::text').get()
        if about:
            repo_data['about'] = about.strip()
        else:
            repo_data['about'] = repo_data['name']

        #prog languages
        language_data = response.css('a[href*="search?l="] span::text').getall()
        languages = [language_data[i].strip() for i in range(0, len(language_data), 2)]
        repo_data['languages'] = languages if languages else ['None']

        #num of commit
        commits = None
        commit_texts = response.css('a[href*="/commits"] span::text').getall()
        for text in commit_texts:
            match = re.search(r'\d+', text.replace(',', ''))
            if match:
                commits = match.group(0)
                break

        repo_data['commits'] = commits if commits else '0'
        yield repo_data
