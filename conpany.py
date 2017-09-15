#!/usr/bin/python
#-*- coding: utf-8 -*-
'''
Created on 2017-04-21 13:29:38

@author: Maxing
'''

import time
import json
import requests
import gevent
from utils.log4spider import get_service_logger
from gevent import monkey
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
monkey.patch_all()


logger = get_service_logger(name='spider_server_service')


'''从百度的接口查询失信'''


class ShixinBaidu(object):
    def __init__(self):
        global logger
        self.logger = logger
        self.prefix_url = 'https://sp0.baidu.com/8aQDcjqpAAV3otqbppnN2DJv/api.php'
        self.headers = {
            'Host': 'sp0.baidu.com',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'Accept': '*/*',
            'Referer': 'https://www.baidu.com/s?ie=utf-8&f=8&rsv_bp=0&rsv_idx=1&tn=baidu&wd=%E5%A4%B1%E4%BF%A1%E8%A2%AB%E6%89%A7%E8%A1%8C%E4%BA%BA&rsv_pq=f1736b4900060ca9&rsv_t=2b20CwKtuPOEyuBCXKMzaVK3c4MxZug8oVNXuFG83glpmlwfR9jkKJ59OR0&rqlang=cn&rsv_enter=1&rsv_sug3=2',
            'Accept-Encoding': 'gzip, deflate, sdch, br',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.6,en;q=0.4',
        }

    # 访问百度接口查询
    def _download(self, name, card_num='', start_record=''):
        # name: 姓名/企业名称
        # start_record: 翻页所需参数, 表示上一页最后一条记录序号
        # card_num: 身份证号/组织机构代码

        if len(card_num) == 18:
            card_num = card_num[:11] + '****' + card_num[-4:]
        elif len(card_num) == 15:
            card_num = card_num[:8] + '****' + card_num[-4:]
        else:
            card_num = ''

        payload = {
            'resource_id': '6899',
            'query': '失信被执行人名单',
            'cardNum': card_num,
            'iname': name,
            'areaName': '',
            'pn': start_record,         # 起始序号
            'rn': '50',                 # 该次查询获取多少条数据
            'ie': 'utf-8',
            'oe': 'utf-8',
            'format': 'json',
            't': '1492665543885',
            'cb': 'jQuery110206349114852395397_1492664725991',
            '_': '1492664725996',
        }

        retry_time = 0

        while retry_time <= 2:
            try:
                r = requests.get(url=self.prefix_url, headers=self.headers,
                                 params=payload, verify=False, allow_redirects=False)
                if r.status_code == 200:
                    return r.text
                else:
                    retry_time += 1
            except Exception as e:
                print e

    def extract_item(self, text, is_first_page):
        text = text.replace(
            '/**/jQuery110206349114852395397_1492664725991(', '').replace(');', '')
        baidu_items = json.loads(text)
        downloadTime = time.strftime(
            '%Y-%m-%d %H:%M:%S', time.localtime(time.time()))
        person_items = []
        company_items = []

        # 查询获取的总数据条数
        # 由于最多只能获取到2000条, 所以多余2000条按2000条处理
        # 多余50条需要翻页
        if not baidu_items or not baidu_items.get('data') or len(baidu_items['data']) == 0:
            if is_first_page:
                return person_items, company_items, 0
            else:
                return person_items, company_items

        disp_num = baidu_items['data'][0]['dispNum']
        if disp_num > 2000:
            disp_num = 2000

        for detail_json in baidu_items['data'][0]['result']:

            # 区分自然人和企业
            # partyTypeName: 0-自然人 1-企业
            partyTypeName = detail_json.get('partyTypeName')

            if partyTypeName == '1':
                # 企业和组织

                unit_item = {
                    'NAME': '',
                    'CODE': '',
                    'REPRESENTATIVE': '',
                    'EXECUTIVE_COURT': '',
                    'PROVINCE': '',
                    'EXECUTE_NUM': '',
                    'FILING_TIME': '',
                    'CASE_NUM': '',
                    'DEPARTMENT': '',
                    'INSTRUMENT_OBLIGATION': '',
                    'EXECUTION_PERFORMANCE': '',
                    'ACT_OF_DISHONESTY': '',
                    'RELEASE_TIME': '',
                    'DETAIL_LINK': '',
                    'COLLECT_TIME': '',
                }
                # 公司或组织名称
                unit_item['NAME'] = detail_json.get('iname').encode('utf8').strip().strip(
                    ',') if detail_json.get('iname') else ''

                # 组织机构代码
                unit_item['CODE'] = detail_json.get(
                    'cardNum').encode('utf8').strip() if detail_json.get('cardNum') else ''

                # 法定代表人或者负责人姓名
                unit_item['REPRESENTATIVE'] = detail_json.get('businessEntity').encode('utf8').strip().strip(
                    ',') if detail_json.get('businessEntity') else ''

                # 执行法院
                unit_item['EXECUTIVE_COURT'] = detail_json.get(
                    'courtName').encode('utf8').strip() if detail_json.get('courtName') else ''

                # 省份
                unit_item['PROVINCE'] = detail_json.get(
                    'areaName').encode('utf8').strip() if detail_json.get('areaName') else ''

                # 执行依据文号
                unit_item['EXECUTE_NUM'] = detail_json.get(
                    'gistId').encode('utf8').strip() if detail_json.get('gistId') else ''

                # 立案时间
                unit_item['FILING_TIME'] = detail_json.get(
                    'regDate').encode('utf8').strip() if detail_json.get('regDate') else ''

                # 案号
                unit_item['CASE_NUM'] = detail_json.get(
                    'caseCode').encode('utf8').strip() if detail_json.get('caseCode') else ''

                # 作出执行依据单位
                unit_item['DEPARTMENT'] = detail_json.get(
                    'gistUnit').encode('utf8').strip() if detail_json.get('gistUnit') else ''

                # 生效法律文书确定的义务
                unit_item['INSTRUMENT_OBLIGATION'] = detail_json.get(
                    'duty').encode('utf8').strip() if detail_json.get('duty') else ''

                # 被执行人的履行情况
                unit_item['EXECUTION_PERFORMANCE'] = detail_json.get(
                    'performance').encode('utf8').strip() if detail_json.get('performance') else ''

                # 失信被执行人行为具体情形
                unit_item['ACT_OF_DISHONESTY'] = detail_json.get('disruptTypeName').encode('utf8').strip(
                ) if detail_json.get('disruptTypeName') else ''

                # 发布日期
                unit_item['RELEASE_TIME'] = detail_json.get(
                    'publishDate').encode('utf8').strip() if detail_json.get('publishDate') else ''

                # 详细信息的页面
                # id信息是不变的, 验证码(pCode)和captchaId会变化
                doc_id = detail_json.get('loc').encode('utf8').split('detail?id=')[1]
                if len(doc_id) > 0:
                    unit_item[
                        'DETAIL_LINK'] = 'http://shixin.court.gov.cn/disDetailNew?id=%s&pCode=wstc&captchaId=7636b66df1b5442dadf0506a1da1ade0' % (doc_id)
                else:
                    unit_item['DETAIL_LINK'] = ''

                # 采集时间
                unit_item['COLLECT_TIME'] = downloadTime

                company_items.append(unit_item)

            if partyTypeName == '0':
                # 自然人

                person_item = {
                    'NAME': '',
                    'GENDER': '',
                    'AGE': '',
                    'ID_NUM': '',
                    'EXECUTIVE_COURT': '',
                    'PROVINCE': '',
                    'EXECUTE_NUM': '',
                    'FILING_TIME': '',
                    'CASE_NUM': '',
                    'DEPARTMENT': '',
                    'INSTRUMENT_OBLIGATION': '',
                    'EXECUTION_PERFORMANCE': '',
                    'ACT_OF_DISHONESTY': '',
                    'RELEASE_TIME': '',
                    'DETAIL_LINK': '',
                    'COLLECT_TIME': '',
                }

                # 被执行人姓名
                person_item['NAME'] = detail_json.get(
                    'iname').encode('utf8').strip().strip(',') if detail_json.get('iname') else ''

                # 性别
                person_item['GENDER'] = detail_json.get(
                    'sexy').encode('utf8').strip() if detail_json.get('sexy') else ''

                # 年龄
                person_item['AGE'] = str(detail_json.get(
                    'age')).encode('utf8').strip() if detail_json.get('age') else ''

                # 身份证号
                person_item['ID_NUM'] = detail_json.get(
                    'cardNum').encode('utf8').strip() if detail_json.get('cardNum') else ''

                # 执行法院
                person_item['EXECUTIVE_COURT'] = detail_json.get(
                    'courtName').encode('utf8').strip() if detail_json.get('courtName') else ''

                # 省份
                person_item['PROVINCE'] = detail_json.get(
                    'areaName').encode('utf8').strip() if detail_json.get('areaName') else ''

                # 执行依据文号
                person_item['EXECUTE_NUM'] = detail_json.get(
                    'gistId').encode('utf8').strip() if detail_json.get('gistId') else ''

                # 立案时间
                person_item['FILING_TIME'] = detail_json.get(
                    'regDate').encode('utf8').strip() if detail_json.get('regDate') else ''

                # 案号
                person_item['CASE_NUM'] = detail_json.get(
                    'caseCode').encode('utf8').strip() if detail_json.get('caseCode') else ''

                # 作出执行依据单位
                person_item['DEPARTMENT'] = detail_json.get(
                    'gistUnit').encode('utf8').strip() if detail_json.get('gistUnit') else ''

                # 生效法律文书确定的义务
                person_item['INSTRUMENT_OBLIGATION'] = detail_json.get(
                    'duty').encode('utf8').strip() if detail_json.get('duty') else ''

                # 被执行人的履行情况
                person_item['EXECUTION_PERFORMANCE'] = detail_json.get(
                    'performance').encode('utf8').strip() if detail_json.get('performance') else ''

                # 失信被执行人行为具体情形
                person_item['ACT_OF_DISHONESTY'] = detail_json.get('disruptTypeName').encode('utf8').strip(
                ) if detail_json.get('disruptTypeName') else ''

                # 发布时间
                person_item['RELEASE_TIME'] = detail_json.get(
                    'publishDate').encode('utf8').strip() if detail_json.get('publishDate') else ''

                # 详细页面的网址
                # id信息是不变的, 验证码(pCode)和captchaId会变化
                doc_id = detail_json.get('loc').encode('utf8').split('detail?id=')[1]
                if len(doc_id) > 0:
                    person_item[
                        'DETAIL_LINK'] = 'http://shixin.court.gov.cn/disDetailNew?id=%s&pCode=wstc&captchaId=7636b66df1b5442dadf0506a1da1ade0' % (doc_id)
                else:
                    person_item['DETAIL_LINK'] = ''

                # 采集时间
                person_item['COLLECT_TIME'] = downloadTime

                person_items.append(person_item)

        if is_first_page:
            return person_items, company_items, disp_num
        else:
            return person_items, company_items

    '''
    查询失信被执行人信息
    名字为必填, 身份证号/组织机构代码选填
    保存为文件
    '''

    def query_task(self, name, start_record, card_num):
        # name: 姓名/企业名称
        # start_record: 翻页所需参数, 实际为上一页最后一条数据的序号
        #               (如第2页开始参数为50, 第三页为100)
        # card_num: 身份证号/组织机构代码

        json_text = self._download(name, card_num, start_record)
        other_page_items_p, other_page_items_c = self.extract_item(
            json_text, False)
        return other_page_items_p, other_page_items_c

    def query_shixin(self, name, card_num=''):
        # name: 姓名/企业名称
        # card_num: 身份证号/组织机构代码

        text = self._download(name, card_num)
        shixin_items_p = []     # 个人
        shixin_items_c = []     # 企业

        first_page_items_p, first_page_items_c, disp_num = self.extract_item(text, True)

        if disp_num == 0:
            # print u'查询结果为0条。'
            self.logger.warning('No result found for shixin: {}, {}'.format(name, card_num))
        else:
            # 保存第一页
            if len(first_page_items_p) > 0:
                shixin_items_p += first_page_items_p
            if len(first_page_items_c) > 0:
                shixin_items_c += first_page_items_c

        if disp_num > 50:
            pages = int((disp_num + 49) / 50)
            query_num = 50
            # 其他页
            tasks = [gevent.spawn(
                self.query_task, name, query_num * (i + 1), card_num) for i in xrange(pages - 1)]
            gevent.joinall(tasks)

            for task in tasks:
                other_page_items_p, other_page_items_c = task.value
                if len(other_page_items_p) > 0:
                    shixin_items_p += other_page_items_p
                if len(other_page_items_c) > 0:
                    shixin_items_c += other_page_items_c

        self.logger.info('found {} companies and {} persons for shixin query: {}, {}'.format(len(shixin_items_c), len(shixin_items_p), name, card_num))
        return shixin_items_p, shixin_items_c
