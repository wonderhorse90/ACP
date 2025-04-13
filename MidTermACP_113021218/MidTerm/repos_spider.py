import scrapy
from urllib.parse import urljoin


class ReposSpider(scrapy.Spider):
    name = "repos"
    start_urls = ['https://github.com/wonderhorse90?tab=repositories']

    def parse(self, response):
        repos = response.css('li[itemprop="owns"]')

        for repo in repos:
            repo_url = urljoin(response.url, repo.css('a[itemprop="name codeRepository"]::attr(href)').get())
            yield response.follow(repo_url, self.parse_repo)

    def parse_repo(self, response):
        url = response.url
        name = response.css('strong.mr-2.flex-self-stretch a::text').get().strip()
        about = response.css('p.f4.my-3::text').get()
        about = about.strip() if about else None

        # Check if repo is empty
        is_empty = response.css('div.Box.mt-3 h3::text').re_first(r"This repository is (.+?)") is not None

        if not about:
            about = name if not is_empty else None

        if is_empty:
            languages = None
            commits = None
        else:
            languages = response.css('li.d-inline a span::text').getall()
            commits = response.css('li.commits span.d-none::text').re_first(r'\d+')

        last_updated = response.css('relative-time::attr(datetime)').get()

        yield {
            'url': url,
            'about': about,
            'last_updated': last_updated,
            'languages': languages,
            'commits': commits
        }
