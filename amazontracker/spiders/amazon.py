import scrapy
import re
from ..items import AmazontrackerItem
from ..loaders import ProductLoader

class AmazonSpider(scrapy.Spider):
    name = 'amazon'
    allowed_domains = ['amazon.com', 'm.media-amazon.com']
    start_urls = ['https://www.amazon.com/s?k=lego&ref=nb_sb_noss']
    # start_urls = ['https://www.amazon.com/LEGO-Star-Wars-Building-1771Piece/dp/B07Q2N1SJV', 'https://www.amazon.com/LEGO-Infinity-Gauntlet-Collectible-Building/dp/B08YP94QJN/']

    def start_requests(self):
        for url in self.start_urls[:]:
            yield scrapy.Request(url, callback=self.parse_detail)

    def parse(self, response):
        product_urls = response.css("div.a-section.a-spacing-none h2.a-spacing-none a.a-link-normal::attr(href)").getall() or response.css("div.a-row.a-spacing-mini div.a-row.a-spacing-none a.a-link-normal::attr(href)").getall() #or response.css("div.a-section.a-spacing-none span.rush-component a.a-link-normal::attr(href)").getall()
        for url in product_urls:
            if '/dp/' in url:
                product_url = "https://www.amazon.com" + "/".join(url.split("/")[:4])
                self.logger.info("Product url ==>> %s", product_url)
                yield scrapy.Request(product_url, callback=self.parse_detail)
        
        #follow Pagination_
        next_page_url = response.css("a.pagnNext::attr(href)").get() or response.css("li.a-last a::attr(href)").get()

        if next_page_url:
            full_url = "https://www.amazon.com/" + next_page_url
            #print("Full URL" , full_url)
            yield scrapy.Request(url=full_url, callback=self.parse)

    def parse_detail(self, response):
        self.logger.info("<< ============================= Parsing detail ================================== >>")
        # self.logger.info("Body:\n %s", response.body)
        loader = ProductLoader(item=AmazontrackerItem(), selector=response)
        loader.add_value('product_url', response.url)
        loader.add_css('product_name', 'h1.a-size-large span.a-size-large::text')
        loader.add_xpath('meta_category', '//*[@id="wayfinding-breadcrumbs_feature_div"]/ul//a/text()')
        loader.add_xpath('product_price', '//span[@id = "priceblock_ourprice"]/text()')
        loader.add_xpath('product_price', '//span[@class = "a-size-base a-color-price"]/text()')
        loader.add_xpath('product_price', '//span[@class = "olp-padding-right"]/span[@class = "a-color-price"]/text()')
        loader.add_css('brand_name', 'div.centerColAlign div.a-section a::text')
        loader.add_xpath('product_availability', '//*[@id="availability"]//span/text()')
        loader.add_xpath('product_attributes', '//*[@class="a-keyvalue prodDetTable"]/tr')
        loader.add_xpath('product_attributes', '//*[@id="detailBullets_feature_div"]/ul/li/span')
        loader.add_xpath('product_summary', '//div[@id = "feature-bullets"]/ul/li')
        loader.add_xpath('product_description', '//div[@id = "productDescription"]/p')
        loader.add_xpath('product_safety', '//span[@class = "cpsiaWarning"]/text()')
        loader.add_xpath('product_safety', '//div[@id = "productDescription"]/p[2]')
        loader.add_xpath('suppliers_list_url', '//*[@id="olp_feature_div"]/div[2]/span/a/@href')
        loader.add_value('image_urls', re.findall(r'large\"\:\"(.*?)\"', response.body.decode("utf-8"), re.S))
        loader.replace_value('image_urls', re.findall(r'hiRes\"\:\"(.*?)\"', response.body.decode("utf-8"), re.S))
        yield loader.load_item()
