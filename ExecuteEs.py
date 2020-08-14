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
es = Elasticsearch([{'host': '127.0.0.1', 'port': 9200}])
client = pymongo.MongoClient('127.0.0.1')
testerhome = client.testerhome

for key in flag.keys():
    print('当前执行的mongo库: %s'%key)
    mongokey = testerhome[key]
    items = mongokey.find({})
    for item in items:
        body = {"query": {"term": {flag[key]: item[flag[key]]}}}
        try:
            result = es.search(index='testerhome_%s'%key, doc_type=key, body=body)
            _id = result['hits']['hits'][0]['_id']
            es.delete(index='testerhome_%s'%key, doc_type=key, id=_id)
        except:
            pass
        del item['_id']
        res = es.index(index='testerhome_%s'%key, doc_type=key, body=item)

print(time.strftime('%Y-%M-%D %H:%M:%S', time.localtime(int(time.time()))) + '    es中数据已更新')
with open(r'flag.txt', 'r') as f:
    result = f.read()
result = eval(result)
result['mongoes'] = 'true'
result = json.dumps(result)
with open(r'flag.txt', 'w') as f:
    f.write(result)
