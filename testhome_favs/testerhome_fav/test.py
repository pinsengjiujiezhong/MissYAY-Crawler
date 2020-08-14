from elasticsearch import Elasticsearch

# es = Elasticsearch(hosts="127.0.0.1", port=9200)
# body = {
#     'query': {
#         'match': {
#             "comments.quote_uid": "Lihuazhang"
#         }
#     }
# }
# result = es.search(index="testerhome_community", doc_type="community", body=body)
# for item in result['hits']['hits']:
#     print(item['_source']['id'])

import pymongo
from elasticsearch import Elasticsearch
import json

client = pymongo.MongoClient('127.0.0.1')
testerhome = client.testerhome
node = testerhome.node
items = node.find({})
for item in items:
    print(item)

es = Elasticsearch([{'host':'127.0.0.1', 'port': 9200}])
body = {"query": {"term": {'node': '研发效能'}}}
try:
    result = es.search(index='testerhome_node' , doc_type=node, body=body)
    _id = result['hits']['hits'][0]['_id']
    es.delete(index='testerhome_node', doc_type='node', id=_id)
except:
    pass
del item['_id']
res = es.index(index='testerhome_node', doc_type='node', body=item)