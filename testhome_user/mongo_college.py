#coding=utf-8
import pymongo
from elasticsearch import Elasticsearch

client = pymongo.MongoClient('127.0.0.1')
testerhome = client.testerhome
collegeMongo = testerhome.college
favs = testerhome.favs

es = Elasticsearch([{'host': '140.143.15.155', 'port': 9200}])

body = {
    'query': {
        'match_all': {}
    },
    'size': 1000
}
items = es.search(index='testerhome_college', doc_type='college', body=body)
colleges = [
    {
      'img_url': item['_source']['img_url'],
      'img': item['_source']['img'],
      'location': item['_source']['location'],
      'title': item['_source']['title'],
      'users': item['_source']['users'],
      'id': item['_source']['id'],
      'img_urls': item['_source']['img_urls'],
      'image_paths': item['_source']['image_paths'],
    } for item in items['hits']['hits']]


for college in colleges:
    collegeMongo.insert(college)