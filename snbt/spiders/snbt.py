import scrapy
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst
from datetime import datetime
from snbt.items import Article


class snbtSpider(scrapy.Spider):
    name = 'snbt'
    start_urls = ['https://www.snb-t.com/tools-services/news/']

    def parse(self, response):
        articles = response.xpath('//div[@class="elementor-post__text"][div]')
        for article in articles:
            link = article.xpath('.//a[@class="elementor-post__read-more"]/@href').get()
            date = article.xpath('.//span[@class="elementor-post-date"]/text()').get()
            if date:
                date = date.strip()
            yield response.follow(link, self.parse_article, cb_kwargs=dict(date=date))

        next_page = response.xpath('//a[@class="page-numbers next"]/@href').get()
        if next_page:
            yield response.follow(next_page, self.parse)

    def parse_article(self, response, date):
        if 'pdf' in response.url:
            return

        item = ItemLoader(Article())
        item.default_output_processor = TakeFirst()

        title = response.xpath('//h1/text()').get()
        if title:
            title = title.strip()

        content = response.xpath('//div[@data-widget_type="theme-post-content.default"]//text()').getall()
        content = [text for text in content if text.strip() and '{' not in text]
        content = "\n".join(content[1:]).strip()

        item.add_value('title', title)
        item.add_value('date', date)
        item.add_value('link', response.url)
        item.add_value('content', content)

        return item.load_item()
