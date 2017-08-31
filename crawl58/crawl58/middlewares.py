# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from crawl58.settings import USER_AGENTS
import random
import requests
import base6

class RandomUserAgent(object):
    """User-Agent 下载中间件"""
    def process_request(self,request,spider):
        # 一定得是这个方法名
        user_agent = random.choice(USER_AGENTS)
        request.headers.setdefault('User-Agent',user_agent)

# class RandomProxy(object):
# 	"""随机的ip代理"""
#     def __init__(self):
#         #self.proxy_list = ["121.40.108.76:80", "121.8.243.51:8888","221.204.116.169:9797","112.95.205.29:8888","183.31.254.57:9797","221.204.116.211:9797"]
#         self.proxy_auth = "lim1942:wohenwuliao157"
#         self.proxy_api = "http://dps.kuaidaili.com/api/getdps/?orderid=958655825381063&num=50&ut=1&sep=3"
#         self.proxy_list = requests.get(self.proxy_api).text.split()

    # def process_request(self, request, spider):
    #     proxy = random.choice(self.proxy_list)
    #     base64_userpass = base64.b64encode(self.proxy_auth)
    #     #print proxy
    #     request.meta['proxy'] = "http://" + proxy
    #     #if self.proxy_auth != None:
    #     request.headers['Proxy-Authorization'] = "Basic " + base64_userpass