# -*- coding: UTF-8 –*-
# @Anthor :'ben'
# @Created: 5/16/14
from scrapy.spider import Spider
from scrapy.selector import Selector
from scrapy.http import Request

from cheapdress_image.items import CheapWeddingDressDesigner
from cheapdress_image import settings
import os
import math
from urlparse import urljoin

Base_URL = "http://www.2013weddingdress.com/"

class CheapWeddingDressSpider(Spider):
    name = "2013weddingdress"
    allowed_domains = ["2013weddingdress.com"]
    start_urls = [
        "http://www.2013weddingdress.com/"
    ]

    rules = ()

    def parse(self, response):
        sel = Selector(response)
        categorys = sel.xpath("//ul[@id='shopindress_nav']/li[@class='nav-1 level-top']")
        for category in categorys:
            name = category.xpath('a/text()').extract()
            link = category.xpath('a/@href').extract()
            if not link or not name or name[0] != "Wedding Dresses":
                continue
            yield Request(link[0], callback=self.parse_category, meta={"category": name[0]})

    def parse_category(self, response):
        sel = Selector(response)
        items = sel.xpath("//div[@id='productListing']/table//td//div[@class='img']/a/@href").extract()
        for item in items:
            yield Request(item, callback=self.parse_item, meta=response.meta)

        pre_url = response.url.split('?')[0].split('-pg')[0]
        page_info = sel.xpath("//div[@id='productsListingTopNumber']/strong/text()").extract()
        if len(page_info) >= 3:
            total_page = int(math.ceil(int(page_info[2]) / 16.0))
            cur_page = int(page_info[1]) / 16
            if cur_page < total_page:
                yield Request(
                    '%s-pg-%s.html' % (pre_url.replace('.html', ''), cur_page + 1),
                    callback=self.parse_category,
                    meta=response.meta
                )

    def parse_item(self, response):
        sel = Selector(response)

        category = response.meta.get('category', '')
        url = response.url
        title = sel.xpath('//h1[@id="productName"]/text()').extract()[0].strip()
        regular_price = sel.xpath('//h2[@id="productPrices"]/span[@class="normalprice"]/text()').extract()
        regular_price = regular_price[0] if regular_price else 0
        special_price = sel.xpath('//h2[@id="productPrices"]/span[@class="productSpecialPrice"]/text()').extract()
        special_price = special_price[0] if special_price else 0
        desc = sel.xpath('//div[@id="productDescription"]/p//text()').extract()
        desc = ''.join(desc).encode('utf8')

        category_path = os.path.join(settings.IMAGES_STORE, category, title)
        if not os.path.exists(category_path):
            os.makedirs(category_path)

        with open(os.path.join(category_path, "desc.txt"), "w") as f:
            f.write("title: %s\n" % title)
            f.write("regular_price: %s\n" % regular_price)
            f.write("special_price: %s\n" % special_price)
            f.write("url: %s\n" % url)
            f.write("desc: %s\n" % desc)

        item = CheapWeddingDressDesigner()
        item["sub_path"] = os.path.join(category, title)
        img_urls = sel.xpath("//div[@id='productImage']//img/@src").extract()
        item["image_urls"] = map(lambda x: urljoin(Base_URL, x), img_urls)
        return item
