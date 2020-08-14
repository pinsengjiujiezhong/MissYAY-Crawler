# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import re, time
import scrapy
from scrapy import Spider
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
import pymongo
import re

class TesthomeFollowersPipeline(object):
    def process_item(self, item, spider):
        img_urls = []
        followersList = []
        followingList = []
        for followers in item['followers']:
            if 'http' in followers['img']:
                url = followers['img']
                followers['img'] = re.sub('(https|http).+?(\.com/|\.cn/|\.php/|\.net/|\.io/|\.org/|\.su/|\.top/|\.me/|\.info/|\.name/)', '/images/', followers['img'].split('!')[0])
            else:
                url = 'https://testerhome.com' + followers['img']
                followers['img'] = '/images' + followers['img'].split('!')[0]
            img_urls.append(url)
            followersList.append(followers)
        for following in item['following']:
            if 'http' in following['img']:
                url = following['img']
                following['img'] = re.sub('(https|http).+?(\.com/|\.cn/|\.php/|\.net/|\.io/|\.org/|\.su/|\.top/|\.me/|\.info/|\.name/)', '/images/', following['img'].split('!')[0])
            else:
                url = 'https://testerhome.com' + following['img']
                following['img'] = '/images' + following['img'].split('!')[0]
            img_urls.append(url)
            followingList.append(following)
        item['followers'] = followersList
        item['following'] = followingList
        item['img_urls'] = img_urls
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
        for img_url in item['img_urls']:
            yield scrapy.Request(img_url)

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        item['image_paths'] = image_paths
        return item

    def file_path(self, request, response=None, info=None):
        url = request.url.split('!')[0]
        path = re.sub('(https|http).+?(\.com/|\.cn/|\.php/|\.net/|\.io/|\.org/|\.su/|\.top/|\.me/|\.info/|\.name/)','/images/', url)
        return path
