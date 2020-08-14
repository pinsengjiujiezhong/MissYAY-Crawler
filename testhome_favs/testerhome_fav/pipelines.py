# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy import Spider
import pymongo

class TesterhomeFavPipeline(object):
    def process_item(self, item, spider):
        return item


class MongoPipeline(Spider):

    def __init__(self, mongo_uri, mongo_db, mongo_key, mongo_key_new):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db
        self.mongo_key = mongo_key
        self.mongo_key_new = mongo_key_new

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE'),
            mongo_key=crawler.settings.get('MONGO_KEY'),
            mongo_key_new=crawler.settings.get('MONGO_KEY_NEW'),
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        self.db[self.mongo_key].insert(dict(item))
        # self.db[self.mongo_key_new].insert(dict(item))
