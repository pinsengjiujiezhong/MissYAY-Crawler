#coding=utf-8
import pymongo
import time
from elasticsearch import Elasticsearch

es = Elasticsearch(hosts="140.143.15.155", port=9200)

client = pymongo.MongoClient('127.0.0.1')
mydb = client.testerhomes
community = mydb.community
fav = mydb.fav

items = community.find()
# for item in items:
#     del item['_id']
#     communitys.insert(item)
# 24363
# items = community.find()
# print(items.count())
#
i = 1
for item in items:
	if i > 10282:
		del item['_id']
		result = es.index(index="testerhome_community", doc_type="community", body=item)
	i += 1
# items = community.find()
# i = 1
# urlList = []
# for item in items:
# 	if item['url'] in urlList:
# 		community.delete_one({'url': item['url']})
# 	else:
# 		urlList.append(item['url'])
# 	i += 1
# 	print(i)
# body = {
#     "query": {
#         "term": {
#             "id": '24364'
#         }
#     }
# }
# result = es.indices.delete('testerhome_community')
# value = result
# print(value)





