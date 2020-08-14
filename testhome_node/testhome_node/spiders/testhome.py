# -*- coding: utf-8 -*-
from scrapy import Spider, Request
from testhome_node.items import TesthomeNodeItem
import json

class TesthomeSpider(Spider):
    name = 'testhome'
    allowed_domains = ['testerhome.com']
    start_urls = ['http://testerhome.com/']

    def start_requests(self):
        yield Request('https://testerhome.com/topics', self.parse_node)

    def parse_node(self, response):
        item = TesthomeNodeItem()
        nodes = response.css('.row div.node-list>.node')
        i = 0
        for node in nodes:
            i += 1
            item['id'] = i
            item['node'] = node.css('.media-left::text').extract_first()
            item['nodechild'] = []
            nodechilds = node.css('span.name>a')
            for nodechild in nodechilds:
                result = {}
                result['id'] = nodechild.css('a::attr(data-id)').extract_first()
                result['title'] = nodechild.css('a::attr(title)').extract_first()
                item['nodechild'].append(result)
            yield item

    def close(spider, reason):
        print('node 执行完成')
        with open(r'../flag.txt', 'r') as f:
            result = f.read()
        result = eval(result)
        result['user'] = 'true'
        result = json.dumps(result)
        with open(r'../flag.txt', 'w') as f:
            f.write(result)
