# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import json
from datetime import datetime

class Crawl58Pipeline_1(object):
    def __init__(self):
        self.f=open('findlove.json','wb')
    def process_item(self, item, spider):
        content=json.dumps(dict(item),ensure_ascii=False).encode('utf-8')
        self.f.write(content)
        self.f.write(b'\n')
        return item

    def close_spider(self,spider):
        self.f.close()

class Crawl58Pipeline(object):
    def process_item(self,item,spider):
        item['time'] = datetime.utcnow()
        # 格林威治时间，距离中国 +8 时区
        item['spidername'] = spider.name
        # 爬虫名
        return item


