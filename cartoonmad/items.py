# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class CartoonmadItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    imgurl = scrapy.Field()
    imgname = scrapy.Field()
    imgfolder = scrapy.Field()
    # 设置header
    imgheaders = scrapy.Field()
    pass


class ComicerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    imgurl = scrapy.Field()
    imgname = scrapy.Field()
    imgfolder = scrapy.Field()
    pass


class Dm5Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    imgurl = scrapy.Field()
    imgname = scrapy.Field()
    imgfolder = scrapy.Field()
    # 设置header
    imgheaders = scrapy.Field()
    imgproxy = scrapy.Field()
    pass


class ManhuaguiItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    imgurl = scrapy.Field()
    imgname = scrapy.Field()
    # 设置header
    imgheaders = scrapy.Field()
    imgfolder = scrapy.Field()
    pass
