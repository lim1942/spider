# -*- coding: utf-8 -*-
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from crawl58.items import Crawl58Item
from scrapy.spiders import Rule
from scrapy_redis.spiders import RedisCrawlSpider


class FindloveSpider(RedisCrawlSpider):
    name = 'findlove'
    allowed_domains = ['jiaoyou.58.com']
    # start_urls = ['http://jiaoyou.58.com/sz/mm/18-24/']
    # 起始url

    redis_key = '58spider:start_urls'
    # 分布式时，master给slave分发任务时的key，代替start-url

    rules = (
        Rule(LinkExtractor(allow=r'/sz/mm/18-24/n/\d{13}/'), process_links='deal_links_1',callback='test',follow=True),
        # 继续跟进
        Rule(LinkExtractor(allow=r'/user/\d{14}/'),process_links='deal_links_2',callback='parse_item')
        # 不再继续递归跟进
    )

    def test(self,response):
        print(response.url)


    def deal_links_1(self,links):
    	"""处理rule提取的不规则的链接"""
        for link in links:
            if not link.url.startswith('http'):
                link.url='http://jiaoyou.58.com'+link.url
        print(link.url)
        return links

    def deal_page_2(self,links):
    	"""处理匹配的不规则的链接"""
        for link in links:
            if not link.url.startswith('http'):
                link.url='http://jiaoyou.58.com'+link.url
        return links

    def parse_item(self, response):
    	"""页面解析"""
        item = Crawl58Item()
        print('--------------------')
        print(response.url)
        print('--------------------')
        item['name'] = self.hand_name(response)
        item['age'] = self.hand_age(response)
        item['height'] = self.hand_height(response)
        item['star'] = self.hand_star(response)
        item['location'] = self.hand_location(response)
        item['content'] = self.hand_content(response)
        item['piclink'] = self.hand_piclink(response)
        item['source'] = '58findlove'
        item['url'] = response.url
        yield item

    def hand_name(self,response):
        result = response.xpath("//b[@id='nickid']/text()")
        if result:
            return result.extract()[0]

    def hand_age(self,response):
        result = response.xpath("//ul[@class='m_zl']/li[1]/span[2]/text()")
        if result:
            return result.extract()[0].split('：')[1]

    def hand_height(self,response):
        result = response.xpath("//ul[@class='m_zl']/li[1]/span[3]/text()")
        if result:
            return result.extract()[0].split('：')[1]

    def hand_star(self,response):
        result = response.xpath("//ul[@class='m_zl']/li[2]/span[2]/text()")
        if result:
            return result.extract()[0].split('：')[1]

    def hand_location(self,response):
        result = response.xpath("//ul[@class='m_zl']/li[2]/span[1]/text()")
        if result:
            return result.extract()[0].split('：')[1]

    def hand_content(self,response):
        result = response.xpath("//p[@class='m_yh']/text()")
        if result:
            return result.extract()[0]

    def hand_piclink(self,response):
        result = response.xpath("//div[@class='zy_img']//img/@src")
        if result:
            return result.extract()[0]


