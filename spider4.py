import requests
from lxml import etree
import json
# import rk

def picHander(header,ssion):
    """验证码处理的函数，超时时间为55秒，请求验证
    码时必须带header，header中必须有reffer"""
    url = "http://www.dianhua.cn/auth/captcha.php"
    # 请求验证码的地址
    page_content = ssion.get(url,headers = header)
    # rc = rk.RClient('arsmarvin', 'delv20161212', '79357', 'ea46a92367e6490db6d61e491a884e8e')
    # im = page_content.content
    # return rc.rk_create(im, 5000)['Result']
    # pic_cookie = requests.utils.dict_from_cookiejar(page_content.cookies)
    with open('a.jpg','wb') as f:
        f.write(page_content.content)
    code = input('请输入验证码')
    return code

def page_hander(page):
    """解析页面获取字段的函数"""
    item = {}
    print('--------开始处理page--------')
    content = etree.HTML(page)
    Business_list = content.xpath("//div[@class='c_right_list']")
    for i in Business_list:
        item['tag'] = content.xpath("//div[@class='c_right_body']/div[@class='c_right_tag_box']/a[1]/text()")[
            0].strip()
            # tag字段
        if i.xpath("./dl/dt[2]/p[last()]/text()"):
            item['location'] = i.xpath("./dl/dt[2]/p[last()]/text()")[0].strip()
        else:
            item['location'] = ''
            # location字段，判断位置信息是不是在第二个p节点里
        item['name'] = ''.join(i.xpath("./dl/dt[1]/h5/a/text()")).strip().replace('\t', '').replace('\n','>')
            # name字段
        if i.xpath("./dl/dt[1]/div/p/text()") and i.xpath("./dl/dt[1]/div/p/span/text()"):
            item['telephone'] = (i.xpath("./dl/dt[1]/div/p/span/text()")[0] + ':' + i.xpath("./dl/dt[1]/div/p/text()")[0]).strip()
            # telephone字段
        if i.xpath("./dl/dt[1]/div[2]/text()"):
            item['addr'] = i.xpath("./dl/dt[1]/div[2]/text()")[0].strip()
        if i.xpath("./dl/dt[1]/div[2]/a/@href"):
            item['addr'] = i.xpath("./dl/dt[1]/div[2]/a/@href")[0]
            # addr字段，并判断是否为空
        write_item(item)  # 解析完成后调用写入函数
    print('--------处理完一页-------')

def write_item(item):
    """写入json的函数"""
    print('-----开始写入item----')
    content = json.dumps(item, ensure_ascii=False).encode('utf-8')
    # 二进制写入
    with open('business.json', 'ab') as f:
        f.write(content)
        f.write(b',')
        f.write(b'\n')
    print('---已经写入一个item----')

def main(url):
    header = {
        "Host":"www.dianhua.cn",
        "Connection":"keep-alive",
        "Upgrade-Insecure-Requests":"1",
        "User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36",
        "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        }
    ssion = requests.session()
    #创建一个可以保存cookie的对象
    response = ssion.get(url=url,headers=header)
    xml1 = etree.HTML(response.text)
    url_list = xml1.xpath("//div[@class='c_left']/dl[2]/dl/dd/a/@href")[1:-1]
    # 解析得到右侧边栏的区域链接列表，并舍去首尾
    if not url_list:
        # 如果没有右侧边栏
        page_hander(response.text)
        inner_url_list = xml1.xpath("//div[@class='page_box']/a/@href")[1:-1]
        for url in inner_url_list:
            # 再进行跟进
            fullurl = "http://www.dianhua.cn" + url
            print(fullurl)
            response = ssion.get(url=fullurl, headers=header)
            print(response.status_code)
            header['Referer'] = fullurl
            if response.status_code == 401:
                # 判断是否需要输入验证码
                pic_code = picHander(header, ssion)
                codeurl = "http://www.dianhua.cn/auth/code.php?code="
                fullcodeurl = codeurl + pic_code
                page = ssion.get(url=fullcodeurl, headers=header)
                while page.status_code == 401:
                    # 验证码输入错误继续输入
                    print('验证码输入有误')
                    pic_code = picHander(header, ssion)
                    codeurl = "http://www.dianhua.cn/auth/code.php?code="
                    fullcodeurl = codeurl + pic_code
                    page = ssion.get(url=fullcodeurl, headers=header)
                page_hander(page.text)
            else:
                page_hander(response.text)
    for url in url_list:
        fullurl = "http://www.dianhua.cn" + url
        response = ssion.get(url=fullurl,headers=header)
        # print(response.status_code)
        #响应的状态码
        header['Referer'] = fullurl
        # 在header中写入跳转的地址，否则请求的验证码无效code
        if response.status_code == 401:
            # 判读是否需要输入验证码
            pic_code = picHander(header,ssion)
            #调用验证码处理函数,并返回验证码
            codeurl = "http://www.dianhua.cn/auth/code.php?code="
            fullcodeurl = codeurl+pic_code
            page = ssion.get(url = fullcodeurl,headers=header)
            # 提交完验证码返回的页面
            while page.status_code == 401:
                # 验证码输入有误继续输入
                print('验证码输入有误')
                pic_code = picHander(header, ssion)
                codeurl = "http://www.dianhua.cn/auth/code.php?code="
                fullcodeurl = codeurl + pic_code
                page = ssion.get(url=fullcodeurl, headers=header)
            page_hander(page.text)
            xml2 = etree.HTML(page.text)
            inner_url_list = xml2.xpath("//div[@class='page_box']/a/@href")[1:-1]
            # 解析获得内部的页面列表
            for url in inner_url_list:
                # 再进行跟进
                fullurl = "http://www.dianhua.cn" + url
                print(fullurl)
                response = ssion.get(url=fullurl, headers=header)
                print(response.status_code)
                header['Referer'] = fullurl
                if response.status_code == 401:
                    # 判断是否需要输入验证码
                    pic_code = picHander(header, ssion)
                    codeurl = "http://www.dianhua.cn/auth/code.php?code="
                    fullcodeurl = codeurl + pic_code
                    page = ssion.get(url=fullcodeurl, headers=header)
                    while page.status_code == 401:
                        # 验证码输入错误继续输入
                        print('验证码输入有误')
                        pic_code = picHander(header, ssion)
                        codeurl = "http://www.dianhua.cn/auth/code.php?code="
                        fullcodeurl = codeurl + pic_code
                        page = ssion.get(url=fullcodeurl, headers=header)
                    page_hander(page.text)
                else:
                    page_hander(response.text)
        else:
            page_hander(response.text)
            xml2 = etree.HTML(response.text)
            inner_url_list = xml2.xpath("//div[@class='page_box']/a/@href")[1:-1]
            # 解析获得内部的页面列表
            for url in inner_url_list:
                # 再进行跟进
                fullurl = "http://www.dianhua.cn" + url
                print(fullurl)
                response = ssion.get(url=fullurl, headers=header)
                header['Referer'] = fullurl
                print(response.status_code)
                if response.status_code == 401:
                    # 判断是否需要输入验证码
                    pic_code = picHander(header, ssion)
                    codeurl = "http://www.dianhua.cn/auth/code.php?code="
                    fullcodeurl = codeurl + pic_code
                    page = ssion.get(url=fullcodeurl, headers=header)
                    while page.status_code == 401:
                        # 验证码错误继续输入
                        print('验证码输入有误')
                        pic_code = picHander(header, ssion)
                        codeurl = "http://www.dianhua.cn/auth/code.php?code="
                        fullcodeurl = codeurl + pic_code
                        page = ssion.get(url=fullcodeurl, headers=header)
                    page_hander(page.text)
                else:
                    page_hander(response.text)

# def getCateUrl(city_url,city):
#     response = requests.get(city_url)
#     xml = etree.HTML(response.text)
#     urllist = xml.xpath("//div[@class = 'm_z2']/ul/li[4]/div/ul/li/a/@href")
#     print('%s的url解析成功'%city)
#     return urllist

if __name__=="__main__":
    # city = input('请输入城市拼音')
    # city_url = 'http://www.dianhua.cn/' + city +'/life'
    # for url in getCateUrl(city_url,city):
    #     url = 'http://www.dianhua.cn' + url
    #     print(url)
    #     main(url)
    # url = 'http://www.dianhua.cn/beijing/c290'
    # main(url)#爬虫调度函数

    srart = input('输入y开始')
    if srart == 'y':
        page = requests.get("http://www.dianhua.cn/citylist")
        xml = etree.HTML(page.text)
        city_list = xml.xpath("//div[@class='city_letter_box']/dl/dd/a/@href")
        for city in city_list:
            url = "http://www.dianhua.cn" + city + "/c397"
            main(url)

