import scrapy


class Article(scrapy.Item):
    title = scrapy.Field()
    author = scrapy.Field()
    datetime = scrapy.Field()
    tags = scrapy.Field()
    categories = scrapy.Field()
    content = scrapy.Field()
    paths_to_img = scrapy.Field()


class VnexpressSpider(scrapy.Spider):
    name = "vnexpress"

    start_urls = ["https://vnexpress.net/"]

    base_url = "https://vnexpress.net"

    def parse(self, response, base_url=base_url):
        category_links = response.css('.parent a::attr(href)').getall()[2:]
        for category_link in category_links:
            if category_link.find('.') > 0 or category_link.find(':') > 0:
                continue
            category_urls_with_page_count = [base_url + category_link + "-p" + str(i) for i in range(1, 5000)]
            for category_url_with_page_count in category_urls_with_page_count:
                yield scrapy.Request(url=category_url_with_page_count, meta={
                    'dont_redirect': True,
                    'handle_httpstatus_list': [302]
                }, callback=self.parse_category_with_page_count)

    def parse_category_with_page_count(self, response):
        article_links = response.css('.item-news .title-news a::attr(href)').getall()
        for article_link in article_links:
            yield scrapy.Request(url=article_link, meta={
                'dont_redirect': True,
                'handle_httpstatus_list': [302]
            }, callback=self.parse_article)

    def parse_article(self, response):
        article = Article()

        article_type = response.css('meta[name="its_type"]::attr(content)').get()

        article["title"] = response.css('meta[name="its_title"]::attr(content)').get().replace('.', ' ')

        if article_type == 'text':
            if response.css('.author_mail strong::text').get() is None and response.css('.author strong::text').get() is not None:
                article["author"] = response.css('.author strong::text').get()
            elif response.css('.author_mail strong::text').get() is not None and response.css('.author strong::text').get() is None:
                article["author"] = response.css('.author_mail strong::text').get()
            elif len(response.css('.fck_detail p strong::text').getall()) > 0:
                article["author"] = response.css('.fck_detail p strong::text').getall()[-1]
            else:
                article["author"] = ''

            article["datetime"] = response.css('.date::text').get()

            content = response.xpath('.//p[@class="Normal"]//text()').getall()
            article["content"] = ' '.join([content[i].strip() for i in range(len(content)) if
                                           len(content[i].strip()) > 0 and content[i] != article["author"]])
        else:
            article["author"] = response.css('.author span::text').get()

            article["datetime"] = response.css('.time::text').get()

            article["content"] = response.css('.lead_detail::text').get().strip()

        article["tags"] = response.css('meta[name="its_tag"]::attr(content)').get().split(', ')

        article["categories"] = response.css('.breadcrumb a::text').getall()

        article["paths_to_img"] = response.css('.fig-picture img::attr(data-src)').getall()

        f = open(
            'E:\\Code\\Python\\Practices\\scraping\\scrapy\\amazon\\amazon\\spiders\\output\\vnexpress\\' + article[
                "title"] + '.txt',
            'w+')
        f.write(str(article))
