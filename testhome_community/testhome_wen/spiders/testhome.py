# -*- coding: utf-8 -*-
from scrapy import Request, Spider
from testhome_wen.items import TesthomeWenItem
import re, time
import json

class TesthomeSpider(Spider):
    name = 'testhome'
    allowed_domains = ['testerhome.com']
    start_urls = ['http://testerhome.com/']
    start_url = 'https://testerhome.com/topics?page={page}'

    def start_requests(self):
        for page in range(1, self.settings.get('MAX_PAGE')):
            yield Request(self.start_url.format(page=page), self.parse_list)

    def parse_list(self, response):
        topics = response.css('.item-list>.topic')
        # next_url = 'https://testerhome.com' + response.css('.pagination>.next>a::attr(href)').extract_first()
        # yield Request(next_url, self.parse_list)
        for topic in topics:
            params = {}
            params['portrait'] = topic.css('img.media-object::attr(src)').extract_first()
            params['flag'] = topic.css('.title a span.node::text').extract_first()
            params['title'] = topic.css('.title a::attr(title)').extract_first()
            params['thumb_tack'] = topic.css('i.fa-thumb-tack::attr(title)').extract_first()
            params['stick'] = topic.css('.fa-thumb-tack::attr(title)').extract_first()
            params['url'] = 'https://testerhome.com' + topic.css('.title a::attr(href)').extract_first()
            yield Request(params['url'], self.parse_content, meta={'params': params})

    def parse_content(self, response):
        params = response.meta['params']
        item = TesthomeWenItem()
        if 'http' not in params['portrait']:
            item['portrait'] = 'https://testerhome.com' + params['portrait']
        else:
            item['portrait'] = params['portrait']
        item['flag'] = params['flag']
        item['title'] = params['title']
        item['stick'] = params['stick']
        item['url'] = response.request.url
        item['time'] = response.css('div.topic-detail div.info abbr.timeago::attr(title)').extract()
        item['teamname'] = response.css('div.topic-detail div.info a.team-name::text').extract_first()
        item['teamuid'] = response.css('div.topic-detail div.info a.team-name::attr(href)').extract_first()
        if item['teamuid']:
            item['teamuid'] = item['teamuid'].replace('/', '')
        item['user'] = response.css('div.topic-detail div.info a.user-name::attr(title)').extract()
        awesome = response.xpath('//div[@class="label-awesome"]/text()').extract_first()
        if awesome:
            item['awesome'] = True
        else:
            item['awesome'] = False
        item['hits'] = response.css('div.info .hidden-mobile').extract()
        if len(item['hits']) < 2:
            item['hits'] = response.css('div.info').extract()
        item['content'] = response.css('div.topic-detail .panel-body').extract_first()
        item['imgurls'] = re.findall('<img.+?src="(.+?)".+?>', item['content'])
        item['imgurls'].append(item['portrait'])
        item['zan'] = response.css('div.panel-footer .likeable::attr(data-count)').extract_first()
        item['comments'] = []
        comments = response.css('.items>.reply')
        for comment in comments:
            result = {}
            result['comment_id'] = comment.css('.reply::attr(data-id)').extract_first()
            result['comment_floor'] = comment.css('div.reply>div::attr(data-floor)').extract_first()
            result['delete'] = comment.css('div.deleted::text').extract_first()
            if result['delete']:
                item['comments'].append(result)
                continue
            result['quote_user_portrait'] = comment.css('.reply-system img::attr(src)').extract_first()
            if result['quote_user_portrait']:
                if 'http' in result['quote_user_portrait']:
                    item['imgurls'].append(result['quote_user_portrait'])
                    result['quote_user_portrait'] = re.sub('https://testerhome.com', '/images', result['user_portrait']).split('!')[0]
                else:
                    item['imgurls'].append('https://testerhome.com' + result['quote_user_portrait'])
                    result['quote_user_portrait'] = '/images' + result['quote_user_portrait'].split('!')[0]
            result['quote_user_name'] = comment.css('.reply-system a.user-name::attr(title)').extract_first()
            if result['quote_user_name']:
                result['quote_uname'] = result['quote_user_name'].split('(')[0]
                result['quote_uid'] = result['quote_user_name'].split('(')[1].replace(')', '')
            result['quote_title'] = comment.css('.reply-system .topic>a::attr(title)').extract_first()
            result['quote_href'] = comment.css('.reply-system .topic>a::attr(href)').extract_first()
            quote_content = comment.xpath('//div[@id="reply-%s"]/text()'%result['comment_id']).extract()
            result['quote_content'] = ''.join(quote_content).strip()
            if result['quote_user_portrait']:
                item['comments'].append(result)
                continue
            result['user'] = comment.css('span.name>a::attr(title)').extract_first()
            if result['user']:
                result['username'] = result['user'].split('(')[0]
                result['uid'] = result['user'].split('(')[1].replace(')', '')
            else:
                result['username'] = ''
                result['uid'] = ''
            result['user_portrait'] = comment.css('.avatar img::attr(src)').extract_first()
            if 'http' in result['user_portrait']:
                item['imgurls'].append(result['user_portrait'])
                result['user_portrait'] = re.sub('https://testerhome.com', '/images', result['user_portrait']).split('!')[0]
            else:
                item['imgurls'].append('https://testerhome.com' + result['user_portrait'])
                result['user_portrait'] = '/images' + result['user_portrait'].split('!')[0]
            result['tier'] = comment.css('div>div::attr(data-floor)').extract_first()
            result['time'] = comment.css('abbr.timeago::attr(title)').extract_first()
            result['release_time'] = result['time'].replace('T', ' ').replace('+08:00', '')
            timeArray = time.strptime(result['release_time'], "%Y-%m-%d %H:%M:%S")
            result['date'] = int(time.mktime(timeArray))
            result['zan'] = comment.css('.likeable>span::text').extract_first()
            result['author'] = comment.css('.infos>.info>.reply_by_author::text').extract_first()
            result['content'] = comment.css('.markdown').extract_first()
            result['imgurls'] = re.findall('<img.+?src="(.+?)".+?>', result['content'])
            result['reply_id'] = comment.css('div.reply-to-block::attr(data-reply-to-id)').extract_first()
            for item_comment in item['comments']:
                if item_comment['comment_id'] == result['reply_id']:
                    result['reply_comment'] = {
                        'reply_id': result['comment_id'],
                        'reply_floor': result['comment_floor'],
                        'reply_username': result['username'],
                        'reply_uid': result['uid'],
                        'reply_portrait': result['user_portrait'],
                        'reply_content': result['content']
                    }
                    break
            for img in result['imgurls']:
                if 'http' not in img:
                    img = 'https://testerhome.com' + img
                item['imgurls'].append(img)
            for url in result['imgurls']:
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
                    result['content'] = result['content'].replace(oldurl, seen_url)
                else:
                    result['content'] = result['content'].replace(url, '/images/defalut')
                result['content'] = result['content'].replace('src="/images', 'src="/media/images')
            if not result['user']:
                result['admin_portrait'] = comment.css('img::attr(src)').extract_first()
                result['admin_user'] = comment.css('div>div>a:nth-child(1)::attr(title)').extract_first()
                if result['admin_user']:
                    result['admin_uid'] = result['admin_user'].split('(')[0]
                    result['admin_uname'] = result['admin_user'].split('(')[1].replace(')', '')
                result['admin_content'] = comment.css('div>a').extract()
                result['relevance_topic_title'] = comment.css('.topic>a::text').extract_first()
                result['relevance_topic_url'] = comment.css('.topic>a::attr(href)').extract_first()
            else:
                result['admin_portrait'] = ''
                result['admin_user'] = ''
                result['admin_content'] = ''
                result['relevance_topic_title'] = ''
                result['relevance_topic_url'] = ''
            result['author_only'] = comment.css('.author-only::text').extract_first()
            item['comments'].append(result)
        print(item)
        yield item

    def close(spider, reason):
        print('community 执行完成')
        with open(r'../flag.txt', 'r') as f:
            result = f.read()
        result = eval(result)
        print(result)
        print(type(result))
        result['community'] = 'true'
        print(result)
        result = json.dumps(result)
        with open(r'../flag.txt', 'w') as f:
            f.write(result)
