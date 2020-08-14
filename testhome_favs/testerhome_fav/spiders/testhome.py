# -*- coding: utf-8 -*-
from scrapy import Spider, Request
import pymongo, time
from testerhome_fav.items import TesterhomeFavItem
import json
class TesthomeSpider(Spider):
    name = 'testhome'
    allowed_domains = ['testerhome.com']
    start_urls = ['http://testerhome.com/']
    start_url = 'https://testerhome.com/{uid}/favorites'

    def __init__(self):
        self.uidList = []

    def mongo_connect(self):
        client = pymongo.MongoClient('127.0.0.1')
        testerhome = client.testerhome
        follow = testerhome.follow
        uidList = []
        items = follow.find({})
        starttime = int(time.time())
        for item in items:
            if item['uid'] not in uidList:
                uidList.append(item['uid'])
            for followers in item['followers']:
                if followers['uid'] not in uidList:
                    uidList.append(followers['uid'])
            for following in item['following']:
                if following['uid'] not in uidList:
                    uidList.append(following['uid'])
        endtime = int(time.time())
        self.uidList = uidList


    def start_requests(self):
        self.mongo_connect()
        print('当前uid列表的长度: ', len(self.uidList))
        for uid in self.uidList:
            yield Request(self.start_url.format(uid=uid), self.parse_data, meta={'uid': uid, 'favs': []})


    def parse_data(self, response):
        favsItems = response.css('.node-topics.table .topic')
        uid = response.meta['uid']
        favs = response.meta['favs']
        for fav in favsItems:
            result = {}
            result['node'] = fav.css('.node::text').extract_first()
            result['nId'] = fav.css('.node::attr(href)').extract_first().replace('/topics/node', '')
            result['title'] = fav.css('.title>a::text').extract_first()
            result['topicsId'] = fav.css('.title>a::attr(href)').extract_first().replace('/topics/', '')
            favs.append(result)
        next_url = response.css('li.next>a::attr(href)').extract_first()
        if next_url:
            next_url = 'https://testerhome.com' + next_url
            yield Request(next_url, self.parse_data, meta={'uid': uid, 'favs': favs})
        else:
            item = TesterhomeFavItem()
            item['uid'] = uid
            item['favs'] = favs
            yield item

    def close(spider, reason):
        print('favs 执行完成')
        with open(r'../flag.txt', 'r') as f:
            result = f.read()
        result = eval(result)
        result['favs'] = 'true'
        result = json.dumps(result)
        with open(r'../flag.txt', 'w') as f:
            f.write(result)

