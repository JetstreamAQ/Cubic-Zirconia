import scrapy
from urllib.parse import urljoin

class AmazonSpider(scrapy.Spider):
	name = "amazon"
	allowed_domains = ["www.amazon.com"]
	start_urls = [
		'https://www.amazon.com/s?k=computer&ref=nb_sb_noss_2',
		'https://www.amazon.com/s?k=graphics+card&ref=nb_sb_noss_1',
                'https://www.amazon.com/s?k=stick&ref=nb_sb_noss_2',
                'https://www.amazon.com/s?k=broom&ref=nb_sb_noss_2',
                'https://www.amazon.com/s?k=AIDS&ref=nb_sb_noss_2',
                'https://www.amazon.com/s?k=sand&ref=nb_sb_noss_2',
                'https://www.amazon.com/s?k=water&ref=nb_sb_noss_2',
                'https://www.amazon.com/s?k=drywall&ref=nb_sb_noss_1',
                'https://www.amazon.com/s?k=grill&ref=nb_sb_noss_2',
                'https://www.amazon.com/s?k=vegetable&ref=nb_sb_noss_1',
                'https://www.amazon.com/s?k=potato&ref=nb_sb_noss_2',
                'https://www.amazon.com/s?k=sword&ref=nb_sb_noss_2',
                'https://www.amazon.com/s?k=asbestos&ref=nb_sb_noss_2',
                'https://www.amazon.com/s?k=mesothelioma&ref=nb_sb_noss_2',
                'https://www.amazon.com/s?k=spaghetti&ref=nb_sb_noss',
                'https://www.amazon.com/s?k=rocks&ref=nb_sb_noss_1',
                'https://www.amazon.com/s?k=ram&ref=nb_sb_noss_1',
                'https://www.amazon.com/s?k=hdd&ref=nb_sb_noss',
                'https://www.amazon.com/s?k=ssd&ref=nb_sb_noss_2',
                'https://www.amazon.com/s?k=shovel&ref=nb_sb_noss_1',
                'https://www.amazon.com/s?k=dirt&ref=nb_sb_noss_1',
                'https://www.amazon.com/s?k=bike&ref=nb_sb_noss_1',
                'https://www.amazon.com/s?k=plane&ref=nb_sb_noss_2',
		'https://www.amazon.com/s?k=anime&ref=nb_sb_noss'
	]

	def parse(self, response):
		for selector in response.css('div[id*=mainResults]'):
			yield {
				'url': selector.css('a[class*="a-link-normal s-access"]::attr(href)').extract(),
			}
		
		urlPart = response.css('a[id=pagnNextLink]::attr(href)').extract()
		if not urlPart:
			urlPart = response.xpath('//li[starts-with(@class, "a-last")]/a/@href').extract()

		urlFull = urljoin('https://www.amazon.com', urlPart[0])
		yield scrapy.Request(url=urlFull, callback=self.parse_secondary)
		
	def parse_secondary(self, response):
		yield {
			'url': response.css('a[class="a-link-normal a-text-normal"]::attr(href)').extract(),
		}

		nextPart = response.xpath('//li[starts-with(@class, "a-last")]/a/@href').extract()
		if nextPart:
			urlFull = urljoin('https://www.amazon.com', nextPart[0])
			yield scrapy.Request(url=urlFull, callback=self.parse_secondary)
