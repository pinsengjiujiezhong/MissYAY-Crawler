# -*- coding: utf-8 -*-
import re, time
import scrapy
from scrapy import Spider
from scrapy.pipelines.images import ImagesPipeline
from scrapy.exceptions import DropItem
# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html
import pymongo


class TesthomeWenPipeline(object):
    def process_item(self, item, spider):
        if len(item['user']) == 1:
            item['username'] = item['user'][0].split('(')[0]
            item['uid'] = item['user'][0].split('(')[1].replace(')', '')
            item['recovery_username'] = ''
            item['recovery_uid'] = ''
            item['admin_username'] = ''
            item['admin_uid'] = ''
        if len(item['user']) == 2:
            item['username'] = item['user'][0].split('(')[0]
            item['uid'] = item['user'][0].split('(')[1].replace(')', '')
            item['recovery_username'] = item['user'][1].split('(')[0]
            item['recovery_uid'] = item['user'][1].split('(')[1].replace(')', '')
            item['admin_username'] = ''
            item['admin_uid'] = ''
        if len(item['user']) == 3:
            item['username'] = item['user'][0].split('(')[0]
            item['uid'] = item['user'][0].split('(')[1].replace(')', '')
            item['recovery_username'] = item['user'][1].split('(')[0]
            item['recovery_uid'] = item['user'][1].split('(')[1].replace(')', '')
            item['admin_username'] = item['user'][1].split('(')[0]
            item['admin_uid'] = item['user'][1].split('(')[1].replace(')', '')
        if len(item['time']) == 1:
            item['release_time'] = item['time'][0].replace('T', ' ').replace('+08:00', '')
            timeArray = time.strptime(item['release_time'], "%Y-%m-%d %H:%M:%S")
            item['release_time'] = item['last_update_time'] = int(time.mktime(timeArray))
            item['recovery_time'] = ''
        if len(item['time']) == 2:
            item['release_time'] = item['time'][0].replace('T', ' ').replace('+08:00', '')
            item['recovery_time'] = item['time'][1].replace('T', ' ').replace('+08:00', '')
            timeArray = time.strptime(item['release_time'], "%Y-%m-%d %H:%M:%S")
            item['release_time'] = int(time.mktime(timeArray))
            timeArray = time.strptime(item['recovery_time'], "%Y-%m-%d %H:%M:%S")
            item['recovery_time'] = item['last_update_time'] = int(time.mktime(timeArray))
        item['hit'] = re.findall('\d+', item['hits'][-1])[-1]
        if len(item['imgurls']) > 1:
            for url in item['imgurls']:
                if 'i.imgur.com' not in url:
                    oldurl = url
                    if '?' in url:
                        one = url.split('?')[0]
                    else:
                        one = url
                    if '!' in one:
                        two = one.split('!')[0]
                    else:
                        two = one
                    if '.' not in two:
                        seen_url = two + '.png'
                    else:
                        seen_url = two
                    seen_url = re.sub('(https|http).+?(\.com/|\.cn/|\.php/|\.net/|\.io/|\.org/|\.su/|\.top/|\.me/|\.info/|\.name/)', '/images/', seen_url)
                    if '/images' not in seen_url:
                        seen_url = '/images' + seen_url
                    item['content'] = item['content'].replace(oldurl, seen_url)
                else:
                    item['content'] = item['content'].replace(url, '/images/defalut')
        item['portrait'] = re.sub('https://testerhome.com', '/images', item['portrait']).split('!')[0]
        item['id'] = item['url'].split('/')[-1]
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
        images = []
        for img_url in item['imgurls']:
            if 'svg' in img_url:
                continue
            if 'uploads' in img_url and 'http' not in img_url:
                url = 'https://testerhome.com' + img_url.split('!')[0]
                images.append(url)
            else:
                images.append(img_url)
        for image in images:
            if 'i.imgur.com' not in image:
                yield scrapy.Request(image)

    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem("Item contains no images")
        item['image_paths'] = image_paths
        return item
        
    def file_path(self, request, response=None, info=None):
        url = request.url
        url = url.replace('*', '')
        if '?' in url:
            one = url.split('?')[0]
        else:
            one = url
        if '!' in one:
            two = one.split('!')[0]
        else:
            two = one
        if '.' not in two:
            seen_url = two + '.png'
        else:
            seen_url = two
        path = re.sub('(https|http).+?(\.com/|\.cn/|\.php/|\.net/|\.io/|\.org/|\.su/|\.top/|\.me/|\.info/|\.name/)', '/images/', seen_url)
        return path
