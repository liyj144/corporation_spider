# coding=utf-8

"""
Created by yanjie on 15-7-13.
导出当前mongodb 中corp_id 到 redis 的key中
"""
from math import ceil
import pymongo
import redis

HOST = "127.0.0.1"
PORT = 27017
client = pymongo.MongoClient(HOST, PORT)
client.corporation.authenticate("corp", "corp")
corpDB = client.corporation

confRedis = redis.StrictRedis(
    host='127.0.0.1',
    port=6379,
    password="fuza54321",
    db=2
)

count = corpDB.corp.count()
print count
# 每次取100条
"""
page_len = 100
page_num = int(ceil(count / page_len))
for i in xrange(page_num):
    print "start to dump %d page ( %d pages all)" % (i, page_num)
    ar_corp_id = corpDB.corp.find({}, {"corp_id": "$corp_id"}).sort("_id").skip(i * page_len).limit(page_len)
    corp_id = [corp_id.get("corp_id") for corp_id in ar_corp_id]
    eval('confRedis.sadd("corp_id", \'%s\')' % "','".join(corp_id))
"""

