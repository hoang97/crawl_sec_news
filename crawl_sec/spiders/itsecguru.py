import scrapy
import telegram

class ItsecguruSpider(scrapy.Spider):
    name = 'itsecguru'
    allowed_domains = ['www.itsecurityguru.org']
    start_urls = ['https://www.itsecurityguru.org/news']

    bot_token = '5538324444:AAF3O9TbuWophnrxNRfg93xvVNsd7PuBIus'
    bot = telegram.Bot(token=bot_token)

    def parse(self, response):
        articles = response.xpath('//article')
        print(self.chat_id)
        for article in articles:
            title = article.xpath('.//ancestor::node()[@class="jeg_post_title"]/a/text()').get()
            url = article.xpath('.//ancestor::node()[@class="jeg_post_title"]/a/@href').get()
            date = article.xpath('.//ancestor::node()[@class="jeg_meta_date"]/a/text()').get()
            yield {
                'title': title,
                'url': url,
                'date': date
            }