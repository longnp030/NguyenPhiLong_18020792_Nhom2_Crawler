import scrapy


class Product(scrapy.Item):
    name = scrapy.Field()
    price = scrapy.Field()
    description = scrapy.Field()
    path_to_img = scrapy.Field()
    tags = scrapy.Field()
    seller = scrapy.Field()


class RaovatSpider(scrapy.Spider):
    name = 'raovat'  # 300/m

    start_urls = ['https://raovat.vnexpress.net/', ]

    base_url = 'https://raovat.vnexpress.net'

    def parse(self, response):
        category_links = [link for link in response.css('a::attr(href)').getall() if 'http' in link]
        for category_link in category_links:
            yield scrapy.Request(url=category_link, callback=self.get_max_page_size)

    def get_max_page_size(self, response):
        #max_page_size = int(response.css('.pagination > .page-item a::text').getall()[-2])
        for i in range(1, 10):
            yield scrapy.Request(url=response.url+'?&page='+str(i), callback=self.parse_category_with_page_count)

    def parse_category_with_page_count(self, response):
        product_links = response.css('.product::attr(href)').getall()
        for product_link in product_links:
            yield scrapy.Request(url=self.base_url+product_link, callback=self.parse_product)

    def parse_product(self, response):
        product = Product()

        product["name"] = response.css('.page-title::text').get()

        product["price"] = response.css('.price::text').get()

        product["description"] = ' '.join([text.strip() for text in response.css('.paragraph::text').getall() if len(text.strip()) > 0])

        product["path_to_img"] = response.css('#light-gallery img::attr(src)').getall()

        product["tags"] = response.css('.tags a::text').getall()

        seller = {}

        seller_info = [info.strip() for info in response.xpath('.//ul[@class="contact"]//text()').getall() if len(info.strip()) > 0]

        try:
            seller["name"] = seller_info[0]
        except:
            seller["name"] = ''
        try:
            seller["date"] = seller_info[1]
        except:
            seller["date"] = ''
        try:
            seller["address"] = seller_info[2]
        except:
            seller["address"] = ''
        try:
            seller["phone"] = response.css('#profile-phone::attr(phone)').get()
        except:
            seller["phone"] = ''

        product["seller"] = seller

        f = open(
            'E:\\Code\\Python\\Practices\\scraping\\scrapy\\amazon\\amazon\\spiders\\output\\raovat\\' + product[
                "name"] + '.txt',
            'w+')
        f.write(str(product))
