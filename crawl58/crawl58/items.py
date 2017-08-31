# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class Crawl58Item(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    name = scrapy.Field()
    # 姓名
    age = scrapy.Field()
    # 年龄
    height = scrapy.Field()
    # 身高
    star = scrapy.Field()
    # 星座
    location = scrapy.Field()
    # 出没地点
    content = scrapy.Field()
    # 内心独白
    piclink = scrapy.Field()
    # 图片链接
    source = scrapy.Field()
    # 来源
    time = scrapy.Field()
    # 爬虫时间
    spidername = scrapy.Field()
    # 爬虫名
    url = scrapy.Field()
    # 个人主页



