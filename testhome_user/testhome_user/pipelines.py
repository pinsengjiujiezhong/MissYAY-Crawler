# -*- coding: utf-8 -*-
import re, time
import pymongo
import scrapy
from scrapy import Spider
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html


class TesthomeUserPipeline(object):

    def process_item(self, item, spider):
        print('type: ', type(item['user']))
        print('len: ', len(item['user']))
        item['number'] = re.search('\d+', item['number'])[0]
        item['post'] = item['counts'][0]
        if 'http' not in item['img']:
            item['img'] = 'https://testerhome.com' + item['img']
        item['returncard'] = item['counts'][1]
        item['img_url'] = item['img'].replace('!lg', '')
        item['img'] = item['img'].replace('!lg', '').replace('https://testerhome.com', '/images')
        if '(' in item['user']:
            item['uid'] = item['user'].split('(')[0].strip()
            item['uname'] = item['user'].split('(')[1].replace(')', '')
        else:
            item['uid'] = item['uname'] = item['user'].strip()
        if item['tagline']:
            item['tagline'] = item['tagline'].strip()
        if item['company']:
            item['company'] = item['company'].replace('@', '').strip()
        topics = []
        for hot_topics in item['hot_topics']:
            topics_id = hot_topics.split('/')[-1]
            topics.append(topics_id)
        item['hot_topics'] = topics
        item['date'] = item['date'].replace('注册日期: ', '')
        recentlys = []
        for recently in item['recently']:
            recently_id = recently.split('/')[-1]
            recentlys.append(recently_id)
        item['recently'] = recentlys
        # if item['company']:
        #     print('company: ',  item['company'])
        #     item['company'] = re.search('>(.+?)@', item['company'])[0]
        # del item['user']
        # del item['counts']
        # del item['company']
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
        yield scrapy.Request(item['img_url'])

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        item['image_paths'] = image_paths
        return item

    def file_path(self, request, response=None, info=None):
        url = request.url
        path = url.replace('https://testerhome.com', '/images')
        return path
