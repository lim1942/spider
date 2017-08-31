import json
import redis
import pymongo

def main():

    rediscli = redis.StrictRedis(host='192.168.61.146',port=6379,db=0)
    mongocli = pymongo.MongoClient(host='192.168.61.146',port=27017)

    db = mongocli['findlove']
    sheet = db['sz18_25']
    i=0
    while True:
        source,data = rediscli.blpop(["findlove:items"])
        print(data)
        data = data.decode('utf-8')
        print(data)
        item = json.loads(data)
        sheet.insert(item)
        i+=1
        print(i)

if __name__ == '__main__':
    main()