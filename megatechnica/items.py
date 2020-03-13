# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class MegatechnicaItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    product_name = scrapy.Field()
    manufacturer = scrapy.Field()
    price = scrapy.Field()
    price_symbol = scrapy.Field()
    cat_list = scrapy.Field()
    category = scrapy.Field()
    sub_category = scrapy.Field()
    description = scrapy.Field()
    manufacturer_img = scrapy.Field()
    specifications = scrapy.Field()
    source_images = scrapy.Field()
    images = scrapy.Field()
    image_urls = scrapy.Field()
    url = scrapy.Field()

    # pass
