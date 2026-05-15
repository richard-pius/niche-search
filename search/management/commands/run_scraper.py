import requests
from bs4 import BeautifulSoup
from django.core.management.base import BaseCommand
from search.models import SearchResult

TARGET_URLS = [
    'https://news.ycombinator.com/',
    'https://dev.to/',
    'https://arstechnica.com/gadgets/',
    'https://en.wikipedia.org/wiki/Main_Page',   # ← NEW
]

class Command(BaseCommand):
    help = 'Scrape niche tech sites and save to database'

    def handle(self, *args, **options):
        self.stdout.write('Starting scraper...')
        for url in TARGET_URLS:
            try:
                resp = requests.get(url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                resp.raise_for_status()
                soup = BeautifulSoup(resp.text, 'html.parser')

                if 'ycombinator' in url:
                    items = soup.select('tr.athing')
                    for item in items[:5]:
                        title_elem = item.select_one('td.title a')
                        if not title_elem:
                            continue
                        title = title_elem.get_text()
                        link = title_elem.get('href')
                        if link.startswith('item?'):
                            link = 'https://news.ycombinator.com/' + link
                        subtext = item.find_next_sibling('tr')
                        desc = subtext.get_text()[:200] if subtext else ''
                        self.save_result(title, link, desc, 'Hacker News')

                elif 'dev.to' in url:
                    articles = soup.select('article.crayons-story')
                    for art in articles[:5]:
                        title_elem = art.select_one('h2 a')
                        if not title_elem:
                            continue
                        title = title_elem.get_text().strip()
                        link = 'https://dev.to' + title_elem['href']
                        desc_elem = art.select_one('p')
                        desc = desc_elem.get_text()[:200] if desc_elem else ''
                        self.save_result(title, link, desc, 'Dev.to')

                elif 'arstechnica' in url:
                    articles = soup.select('li.article')
                    for art in articles[:5]:
                        title_elem = art.select_one('header h2 a')
                        if not title_elem:
                            continue
                        title = title_elem.get_text().strip()
                        link = title_elem['href']
                        desc_elem = art.select_one('p.excerpt')
                        desc = desc_elem.get_text()[:200] if desc_elem else ''
                        self.save_result(title, link, desc, 'Ars Technica')
                
                elif 'wikipedia' in url:
                    # Scrape "Today's featured article" and a few "In the news" items
                    featured = soup.select_one('div#mp-tfa')
                    if featured:
                        title_elem = featured.select_one('b a, p a')   # link inside bold or paragraph
                        if title_elem:
                            title = title_elem.get_text().strip()
                            link = 'https://en.wikipedia.org' + title_elem['href']
                            desc = featured.get_text()[:200]
                            self.save_result(title, link, desc, 'Wikipedia')
                    # In the news (top stories)
                    news_items = soup.select('div#mp-itn ul li')
                    for item in news_items[:4]:
                        link_elem = item.select_one('a')
                        if link_elem:
                            title = link_elem.get_text().strip()
                            link = 'https://en.wikipedia.org' + link_elem['href']
                            desc = item.get_text()[:200]
                            self.save_result(title, link, desc, 'Wikipedia')


            except Exception as e:
                self.stderr.write(f'Error scraping {url}: {e}')

        self.stdout.write(self.style.SUCCESS('Scraping finished.'))

    def save_result(self, title, url, description, source):
        _, created = SearchResult.objects.get_or_create(
            url=url,
            defaults={'title': title, 'description': description, 'source_site': source}
        )
        if created:
            self.stdout.write(f'Added: {title}')
        else:
            self.stdout.write(f'Already exists: {title}')