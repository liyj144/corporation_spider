# coding=utf-8
import pymongo
import redis

HOST = "139.196.7.26"
PORT = 27017
client = pymongo.MongoClient(HOST, PORT)
client.corporation.authenticate("corp", "corp")
corpDB = client.corporation

confRedis = redis.StrictRedis(
    host='139.196.7.26',
    port=6379,
    password="fuza54321",
    db=2
)
