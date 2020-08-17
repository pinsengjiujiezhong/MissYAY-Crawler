# -*- coding: utf-8 -*-
from scrapy import Spider, Request
import pymongo
import time
from testhome_user.items import TesthomeUserItem
import os, json


class TesthomeSpider(Spider):
    name = 'testhome'
    allowed_domains = ['testerhome.com']
    start_urls = ['http://testerhome.com/']
    start_following_url = 'https://testerhome.com/{uid}/following'
    start_followers_url = 'https://testerhome.com/{uid}/followers'
    user_detail_url = 'https://testerhome.com/{uid}'
    start_uid = 'Lihuazhang'

    def __init__(self):
        self.uidList = []
        self.missList = []

    def mongo_connect(self):
        client = pymongo.MongoClient('127.0.0.1')
        testerhome = client.testerhomes
        follow = testerhome.follow
        college = testerhome.college
        uidList = []
        follow_items = follow.find({})
        starttime = int(time.time())
        for item in follow_items:
            if item['uid'] not in uidList:
                uidList.append(item['uid'])
            for followers in item['followers']:
                if followers['uid'] not in uidList:
                    uidList.append(followers['uid'])
            for following in item['following']:
                if following['uid'] not in uidList:
                    uidList.append(following['uid'])
        college_items = college.find({})
        for item in college_items:
            for user in item['users']:
                if user['uid'] not in uidList:
                    uidList.append(followers['uid'])
        endtime = int(time.time())
        self.uidList = uidList

    def mongo_miss(self):
        client = pymongo.MongoClient('127.0.0.1')
        testerhome = client.testerhomes
        user = testerhome.users
        favs = testerhome.favs
        user_items = user.find({})
        userList = []
        for item in user_items:
            userList.append(item['uid'])
        favs_items = favs.find({})
        favsList = []
        for item in favs_items:
            favsList.append(item['uid'])
        for uid in favsList:
            if uid not in userList:
                self.missList.append(uid)

    def start_requests(self): 
        self.mongo_connect()
        self.mongo_miss()
        print('uidListNum: ', len(self.uidList))
        print('missListNum: ', len(self.missList))
        for uid in self.uidList:
            yield Request(self.user_detail_url.format(uid=uid), self.parse_detail)
        # yield Request(self.start_following_url.format(uid=self.start_uid), self.parse_following_users)
        # yield Request(self.start_followers_url.format(uid=self.start_uid), self.parse_followers_users)

    def parse_following_users(self, response):
        followingCards = response.css('.panel-body>div.row div.user-card')
        for following in followingCards:
            following_uid = following.css('.media-heading>a.user-name::attr(href)').extract_first().replace('/', '')
            user_detail_url = 'https://testerhome.com/' + following_uid
            yield Request(user_detail_url, self.parse_detail)
            followers_url = self.start_followers_url.format(uid=following_uid)
            yield Request(followers_url, self.parse_followers_users)
            following_url = self.start_following_url.format(uid=following_uid)
            yield Request(following_url, self.parse_following_users)

    def parse_followers_users(self, response):
        followersCards = response.css('.panel-body>div.row div.user-card')
        for followers in followersCards:
            followers_uid = followers.css('.media-heading>a.user-name::attr(href)').extract_first().replace('/', '')
            user_detail_url = 'https://testerhome.com/' + followers_uid
            yield Request(user_detail_url, self.parse_detail)
            followers_url = self.start_followers_url.format(uid=followers_uid)
            yield Request(followers_url, self.parse_followers_users)
            following_url = self.start_following_url.format(uid=followers_uid)
            yield Request(following_url, self.parse_following_users)

    def parse_detail(self, response):
        item = TesthomeUserItem()
        item['user'] = response.xpath('//div[@class="media-body"]/div[1]/text()').extract_first().strip()
        item['img'] = response.css('div.image>img::attr(src)').extract_first().strip()
        item['number'] = response.css('.media .media-body>div.number::text').extract_first()
        item['company'] = response.xpath('//div[@class="media-body"]/div[@class="item company"]/text()').extract_first()
        item['tagline'] = response.xpath('//div[@class="tagline row"]/text()').extract_first()
        item['location'] = response.css('.media .media-body>div.company a::text').extract_first()
        item['date'] = response.css('.media div.number>span::text').extract_first()
        item['counts'] = response.css('.media .media-body>div.counts>span::text').extract()
        item['social'] = response.css('.media .media-body>div.social').extract_first()
        item['followers'] = response.css('div.follow-info>div.followers>a.counter::text').extract_first()
        item['following'] = response.css('div.follow-info>div.following>a.counter::text').extract_first()
        item['stars'] = response.css('div.follow-info>div.stars>a.counter::text').extract_first()
        item['profile'] = response.css('div.user-profile-fields').extract_first()
        item['hot_topics'] = response.css('#topics ul.list-group>li.list-group-item div.title>a:nth-child(2)::attr(href)').extract()
        item['recently'] = response.css('#replies ul.list-group>li.list-group-item div.title>a::attr(href)').extract()
        item['introduce'] = response.xpath('//div[@id="description"]/div/div/text()').extract_first()
        yield item

    def close(spider, reason):
        print('user 执行完成')
        with open(r'../flag.txt', 'r') as f:
            result = f.read()
        result = eval(result)
        result['user'] = 'true'
        result = json.dumps(result)
        with open(r'../flag.txt', 'w') as f:
            f.write(result)


