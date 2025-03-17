import scrapy
import unicodedata
import re
from wiki.items import WikiItem

class wikispider(scrapy.Spider):
    name = 'wikispider'
    allowed_urls = ['https://en.wikipedia.org']
    start_urls = ['https://en.wikipedia.org/wiki/Garlic']
    page_count = 0  # Counter to track the number of crawled pages

    def parse(self, response):
        if self.page_count >= 2000:  # Stop if we have crawled 2000 pages
            return

        
        relevant_links = response.css('a::attr(href)')
        for link in relevant_links:
            url = link.get()
            if url and 'wiki' in url:
                # Create an absolute URL if it's a relative URL
                new_link = response.urljoin(url)
                if 'https://en.wikipedia.org' in new_link:
                    self.page_count += 1  # Increment the page count
                    yield response.follow(new_link, callback=self.parse_page)

    def parse_page(self, response):
        if self.page_count >= 2000:  # Stop if we have crawled 2000 pages
            return 0
        def clean(value):
            value = ' '.join(value)
            value = value.replace('\n', '')
            value = unicodedata.normalize("NFKD", value)
            value = re.sub(r' , ', ', ', value)
            value = re.sub(r' \( ', ' (', value)
            value = re.sub(r' \) ', ') ', value)
            value = re.sub(r' \)', ') ', value)
            value = re.sub(r'\[\d.*\]', ' ', value)
            value = re.sub(r' +', ' ', value)
            return value.strip()    

        wiki_item = WikiItem()
        
        wiki_item['url'] = response.url
        wiki_item['title'] = response.css('.mw-page-title-main::text').get()
        wiki_item['sample_text'] = clean(response.css('p::text').getall())
        
        yield wiki_item

        relevant_links = response.css('a::attr(href)')
        
        for link in relevant_links:
            url = link.get()
            if url and 'wiki' in url:
                new_link = response.urljoin(url)
                if 'https://en.wikipedia.org' in new_link:
                    if self.page_count >= 2000:  # Stop if we have crawled 2000 pages
                        return 0
                    yield response.follow(new_link, callback=self.parse_page)
