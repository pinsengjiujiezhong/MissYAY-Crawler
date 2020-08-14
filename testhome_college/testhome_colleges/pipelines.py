# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
import re, time
import pymongo
import scrapy
from scrapy import Spider
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem

class TesthomeCollegesPipeline(object):
    def process_item(self, item, spider):
        item['img_urls'] = []
        item['img_urls'].append(item['img_url'])
        for user in item['users']:
            item['img_urls'].append(user['img_url'])
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


class MyImagesPipeline(ImagesPipeline):
    # 生成下载请求
    def get_media_requests(self, item, info):
        for url in item['img_urls']:
            yield scrapy.Request(url)

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        item['image_paths'] = image_paths
        return item

    def file_path(self, request, response=None, info=None):
        url = request.url
        path = url.replace('https://testerhome.com', '/media/images')
        return path