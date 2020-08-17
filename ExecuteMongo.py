#coding=utf-8
import pymongo
from elasticsearch import Elasticsearch
import json
import time

flag_key = ['community', 'favs', 'follow', 'user', 'college', 'node']
flag = {
    'community': 'id',
    'favs': 'uid',
    'follow': 'uid',
    'user': 'uid',
    'college': 'id',
    'node': 'id',
}
es = Elasticsearch([{'host': '140.143.15.155', 'port': 9200}])
client = pymongo.MongoClient('127.0.0.1')
yunclient = pymongo.MongoClient('140.143.15.155')
testerhome = client.testerhomes
yuntesterhome = yunclient.testerhomes
for key in flag.keys():
    print('当前执行的mongo库: %s'%key)
    mongokey = testerhome[key]
    yunmongokey = yuntesterhome[key]
    items = mongokey.find({})
    for item in items:
        del item['_id']
        yunmongokey.insert(item)