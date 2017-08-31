import redis
import pymysql
import json

def main():
    rediscli = redis.Redis(host='192.168.61.136',port=6379,db=0)
    print(22222222222222222)
    mysqlcli = pymysql.connect(host='192.168.61.136',user='python',passwd='helin4881245',db='findlove',port=3306)
    print('3333333333333333333333333333')
    i = 0
    # while True:
        i+=1
        source,data = rediscli.blpop(["findlove:items"])
        data = data.decode('utf-8')
        item = json.loads(data)
        print(item)
        cursor= mysqlcli.cursor()
        cursor.execute("insert into findlove (name,age,heiget,start,location,content,piclink,source,url) values (%s,%s,%s,%s,%s,%s,%s,%s,%s)"%(item['name'],item['age'],item['height'],item['star'],item['location'],item['content'],item['piclink'],item['source'],item['url']))
        mysqlcli.commit()
        cursor.close()
        print(i)

main()