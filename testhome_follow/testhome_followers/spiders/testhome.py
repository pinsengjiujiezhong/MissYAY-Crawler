# -*- coding: utf-8 -*-
from scrapy import Spider, Request
import pymongo
import json
from testhome_followers.items import TesthomeFollowersItem

class TesthomeSpider(Spider):
    name = 'testhome'
    allowed_domains = ['testerhome.com']
    start_urls = ['http://testerhome.com/']
    start_followers = 'https://testerhome.com/{uid}/followers?page={page}'
    start_following = 'https://testerhome.com/{uid}/following?page={page}'


    def start_requests(self):
        client = pymongo.MongoClient('127.0.0.1')
        testerhome = client.testerhome
        community = testerhome.community
        items = community.find({})
        uidList = []
        for item in items:
            uid = item['uid']
            for comment in item['comments']:
                if 'quote_uid' in comment.keys():
                    comment_quote_uid = comment['quote_uid']
                    if comment_quote_uid not in uidList:
                        uidList.insert(0, comment_quote_uid)
                if 'uid' in comment.keys():
                    comment_uid = comment['uid']
                    if comment_uid not in uidList:
                        uidList.insert(0, comment_uid)
        print('当前用户列表的长度: ', len(uidList))
        for uid in uidList:
            yield Request(self.start_followers.format(uid=uid, page=1), self.parse_followers, meta={'followers': [], 'following': [], 'uid': uid})

    def parse_followers(self, response):
        item = TesthomeFollowersItem()
        followers = response.meta['followers']
        uid = response.meta['uid']
        following = response.meta['following']
        users = response.css('.panel-body div.user-card')
        for user in users:
            result = {}
            result['img'] = user.css('img.media-object::attr(src)').extract_first()
            result['uid'] = user.css('a.user-name::attr(href)').extract_first().replace('/', '')
            result['uname'] = user.css('a.user-name::text').extract_first()
            followers.append(result)
        next_url = response.css('li.next>a::attr(href)').extract_first()
        if next_url:
            url = 'https://testerhome.com' + next_url
            yield Request(url, self.parse_followers, meta={'followers': followers, 'following': [], 'uid': uid})
        else:
            url = self.start_following.format(uid=uid, page=1)
            yield Request(url, self.parse_followings, meta={'followers': followers, 'following': [], 'uid': uid})

    def parse_followings(self, response):
        item = TesthomeFollowersItem()
        followers = response.meta['followers']
        uid = response.meta['uid']
        following = response.meta['following']
        users = response.css('.panel-body div.user-card')
        for user in users:
            result = {}
            result['img'] = user.css('img.media-object::attr(src)').extract_first()
            result['uid'] = user.css('a.user-name::attr(href)').extract_first().replace('/', '')
            result['uname'] = user.css('a.user-name::text').extract_first()
            following.append(result)
        next_url = response.css('li.next>a::attr(href)').extract_first()
        if next_url:
            url = 'https://testerhome.com' + next_url
            yield Request(url, self.parse_followings, meta={'followers': followers, 'following': following, 'uid': uid})
        else:
            item['uid'] = uid
            item['followers'] = followers
            item['following'] = following
            yield item

    def close(spider, reason):
        print('follow 执行完成')
        with open(r'../flag.txt', 'r') as f:
            result = f.read()
        result = eval(result)
        result['follow'] = 'true'
        result = json.dumps(result)
        with open(r'../flag.txt', 'w') as f:
            f.write(result)