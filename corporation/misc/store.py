# coding=utf-8
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
