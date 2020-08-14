# -*- coding: utf-8 -*-
from scrapy import Request, Spider
from testhome_colleges.items import TesthomeCollegeItem
import re, time
import json

class TesthomeSpider(Spider):
    name = 'testhome'
    allowed_domains = ['testerhome.com']
    start_urls = ['http://testerhome.com/']
    start_url = 'https://testerhome.com/teams'

    def start_requests(self):
        yield Request(self.start_url, self.parse_page)

    def parse_page(self, response):
        colleges = response.css('div.media.user-card')
        for college in colleges:
            url = 'https://testerhome.com' + college.css('a.team-name::attr("href")').extract_first()
            yield Request(url, self.parse_data)

    def parse_data(self, response):
        item = {}
        item['img_url'] = response.css('div.media-left>.media-object::attr(src)').extract_first()
        if 'http' not in item['img_url']:
            item['img_url'] = 'https://testerhome.com' + item['img_url']
        item['img'] = item['img_url'].split('!')[0].replace('https://testerhome.com', '/image')
        item['location'] = response.xpath('//span[@class="location"]/text()').extract_first()
        item['title'] =response.xpath('//h1[@class="media-heading"]/text()').extract_first()
        item['id'] = response.request.url.split('/')[-1]
        url = response.request.url + '/people'
        item['users'] = []
        yield Request(url, self.parse_people, meta={'college_data': item})

    def parse_people(self, response):
        college_data = response.meta['college_data']
        userList = []
        peoples = response.css('tr.team-user')
        for people in peoples:
            item = {}
            item['img_url'] = people.css('.avatar>img::attr(src)').extract_first()
            if 'http' not in item['img_url']:
                item['img_url'] = 'https://testerhome.com' + item['img_url']
            item['img'] = item['img_url'].split('!')[0].replace('https://testerhome.com', '/image')
            item['uname'] = people.css('.name>a::text').extract_first()
            item['uid'] = people.css('.name>a::attr(href)').extract_first().replace('/', '')
            item['role'] = people.css('.role::text').extract_first()
            userList.append(item)
        college_data['users'].extend(userList)
        url = response.css('li.next>a::attr(href)').extract_first()
        print('next_url: ', url)
        if url:
            next_url = 'https://testerhome.com' + url
            yield Request(next_url, self.parse_people, meta={'college_data': college_data})
        else:
            college = TesthomeCollegeItem()
            college = college_data
            yield college

    def close(spider, reason):
        print('college 执行完成')
        with open(r'../flag.txt', 'r') as f:
            result = f.read()
        result = eval(result)
        result['college'] = 'true'
        result = json.dumps(result)
        with open(r'../flag.txt', 'w') as f:
            f.write(result)






