# -*- coding: utf-8 -*-
import scrapy
from ..items import MegatechnicaItem
import os
import csv
import glob
from openpyxl import Workbook


class MegatechSpider(scrapy.Spider):
    name = 'megatech'
    allowed_domains = ['megatechnica.ge']
    start_urls = ['https://megatechnica.ge/ge/product', 'https://megatechnica.ge/en/sadenebi',
                  'https://megatechnica.ge/en/USB%20Flash%20drive']

    def start_requests(self):
        yield scrapy.Request(url=self.start_urls[1], callback=self.parse)

    def parse(self, response):
        for product in response.xpath('//li[@itemprop="itemListElement"]'):
            product_link = product.css("a.img_link::attr(href)").get()
            ab_link = response.urljoin(product_link)
            yield scrapy.Request(url=ab_link, callback=self.parse_page)

    def parse_page(self, response):
        items = MegatechnicaItem()
        url = response.url
        # name = response.css('div.detail>h2::text').extract()
        name = response.xpath('//div[@class="detail"]/h2[@itemprop="name"]/text()').extract()
        if name:
            name = self.rm_whilespace(name)
        manufacturer = response.css('div.detail span.manufacturer a span::text').extract()
        if manufacturer:
            manufacturer = self.rm_whilespace(manufacturer)
            manufacturer = manufacturer.strip()
        cat_list = response.css('div.subheader a>span.filter::text').extract()
        cat = ''
        sub_cat = ''
        if cat_list:
            if len(cat_list) == 2:
                cat = cat_list[1]
                sub_cat = 'NA'
            else:
                cat = cat_list[1]
                sub_cat = cat_list[2]

        # description = response.css('div.detail div.description::text').extract()
        # description = response.xpath('normalize-space(.//*[@class="description"])').extract()
        description = response.xpath(
            '//div[@class="detail"]/div[@class="description"]/descendant-or-self::*/text()').extract()
        if description:
            description = self.rm_whilespace(description)

        price = response.xpath('//div[@class="prices"]/span[@class="price"]/text()').extract()
        price_symbol = response.xpath('//div[@class="prices"]/span[@class="gel"]/text()').extract()
        if price:
            price = self.rm_whilespace(price)

        if price_symbol:
            price_symbol = self.rm_whilespace(price_symbol)

        relative_img_urls = response.xpath(
            '//div[@class="images"]/ul[contains(@class, "slider-for")]/li[contains(@data-fancybox, "images")]/@href').extract()

        images = response.xpath(
            '//div[@class="images"]/ul[contains(@class, "slider-for")]/li[contains(@data-fancybox, "images")]/@href').extract()
        if images:
            images = [nn_.replace('\n', '') for nn_ in images]
            images = [nn_.strip() for nn_ in images]
            images = [response.urljoin(nn_) for nn_ in images]
            images = filter(None, images)
            images = ', '.join(images)
            images = images

        manufacturer_img = response.xpath(
            '//div[@class="specifications"]/span[@class="manufacturer"]/@style').extract_first()

        if manufacturer_img:
            manufacturer_img = manufacturer_img.replace('background-image:url(', '')
            manufacturer_img = manufacturer_img.replace(');', '')
            manufacturer_img = response.urljoin(manufacturer_img)

        specifications = response.xpath('//div[@class="description"]/table/tbody/tr')
        spec = []
        for td in specifications:
            spec_head = td.xpath('td[1]//text()').extract()
            spec_value = td.xpath('td[2]//text()').extract()
            if spec_head:
                spec_head = self.rm_whilespace(spec_head)
            else:
                spec_head = 'NA'
            if spec_value:
                spec_value = self.rm_whilespace(spec_value)
            else:
                spec_value = 'NA'
            if spec_head:
                temp = str(spec_head) + ':' + str(spec_value)
                spec.append(temp)

        if spec:
            final_spec = '|'.join(spec)
        else:
            final_spec = response.xpath(
                '//div[@class="specifications"]/div[@class="description"]/descendant-or-self::*/text()').extract()
            final_spec = self.rm_whilespace(final_spec)

        items['product_name'] = name
        items['manufacturer'] = manufacturer
        items['price'] = price
        items['price_symbol'] = price_symbol
        items['cat_list'] = cat_list
        items['category'] = cat.strip()
        items['sub_category'] = sub_cat.strip()
        items['description'] = description
        items['manufacturer_img'] = manufacturer_img
        items['specifications'] = final_spec
        items['source_images'] = images
        # items['images'] = images
        items['image_urls'] = self.url_join(relative_img_urls, response)
        items['url'] = url

        yield items

    @staticmethod
    def rm_whilespace(query_term):
        if query_term:
            None_ = [nn_.replace('\n', '') for nn_ in query_term]
            None_ = [nn_.strip() for nn_ in None_]
            None_ = filter(None, None_)
            None_ = ' '.join(None_)
            ret_value = None_
            return ret_value
        return query_term

    def url_join(self, urls, response):
        joined_urls = []
        for url in urls:
            joined_urls.append(response.urljoin(url))

        return joined_urls

    def close(self, reason):
        csv_file = max(glob.iglob('*.csv'), key=os.path.getctime)

        wb = Workbook()
        ws = wb.active

        with open(csv_file, 'r', encoding='utf-8') as f:
            for row in csv.reader(f):
                ws.append(row)

        wb.save(csv_file.replace('.csv', '') + '.xlsx')
