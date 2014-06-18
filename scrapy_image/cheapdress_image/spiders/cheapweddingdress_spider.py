# -*- coding: UTF-8 –*-
# @Anthor :'ben'
# @Created: 5/16/14
from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http import Request

from cheapdress_image.items import CheapWeddingDressDesigner
from cheapdress_image import settings
import os


class CheapWeddingDressSpider(Spider):
    name = "meyiya"
    allowed_domains = ["cheapweddingdressdesigner.com"]
    start_urls = [
        "http://www.cheapweddingdressdesigner.com/"
    ]

    rules = ()

    def parse(self, response):
        sel = Selector(response)
        categorys = sel.xpath("//ul[@id='nav']/li")
        for category in categorys:
            name = category.xpath('a/span/text()').extract()
            if not name or name[0] not in ["Wedding Accessories", "Party Dresses"]:
                continue

            link = category.xpath('a/@href').extract()
            if not link:
                continue
            yield Request(link[0], callback=self.parse_category, meta={"category": name[0]})

    def parse_category(self, response):
        sel = Selector(response)
        items = sel.xpath("//ol").xpath("li[contains(@class, 'item')]/h5/a/@href").extract()
        for item in items:
            yield Request(item, callback=self.parse_item, meta=response.meta)

        pages = sel.xpath('//td[@class="pages"]')
        if pages:
            cur_page = pages[0].xpath('ol/li/span/text()').extract()
            if cur_page:
                cur_page = int(cur_page[0])
            page_lists = sel.xpath('//td[@class="pages"]')
            if page_lists:
                page_list = page_lists[0].xpath('ol/li/a/text()').extract()
                page_list = map(int, filter(None, page_list))
                for page in page_list:
                    if page > cur_page:
                        pre_url = response.url.split('?')[0]
                        yield Request('%s?p=%s' % (pre_url, page), callback=self.parse_category, meta=response.meta)

    def parse_item(self, response):
        sel = Selector(response)

        category = response.meta.get('category', '')
        url = response.url
        title = sel.xpath('//h3/text()').extract()[0].strip()
        special_price = sel.xpath('//div[@class="product-shop"]').xpath('span/span/text()').extract()
        if special_price:
            special_price = special_price[0].strip('R')
            regular_price = special_price
        else:
            regular_price = sel.xpath('//div[@class="product-shop"]').xpath('p[@class="old-price"]/span[@class="price"]/text()').extract()[0].strip().strip('R')
            special_price = sel.xpath('//div[@class="product-shop"]').xpath('p[@class="special-price"]/span[@class="price"]/text()').extract()[0].strip().strip('R')

        category_path = os.path.join(settings.IMAGES_STORE, category, title)
        if not os.path.exists(category_path):
            os.makedirs(category_path)

        with open(os.path.join(category_path, "desc.txt"), "w") as f:
            f.write("title: %s\n" % title)
            f.write("regular_price: %s\n" % regular_price)
            f.write("special_price: %s\n" % special_price)
            f.write("url: %s\n" % url)

        image_links = sel.xpath('//div[@class="more-views"]/ul/li/a/@onclick').re(r'popWin\(\'(.*)\/')
        for link in image_links:
            yield Request(link, callback=self.parse_images, meta={"sub_path": os.path.join(category, title)})

    def parse_images(self, response):
        sel = Selector(response)
        item = CheapWeddingDressDesigner()
        item["sub_path"] = response.meta.get('sub_path')
        item["image_urls"] = sel.xpath('//img/@src').extract()
        return item



