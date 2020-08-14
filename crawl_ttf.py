#coding=utf-8
import pymongo
from pyquery import PyQuery as pq
import requests

client = pymongo.MongoClient('127.0.0.1')
mydb = client.testerhomes
sites = mydb.sites


def request(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    else:
        return None

def parse_page(urlList):
    item = {}
    for url in urlList:
        html = request(url)
        doc = pq(html)
        if 'sites' in url:
            main = doc('div#homeland-site')
            item['sites'] = main.html()
        else:
            main = doc('div#main div.row:last-child')
            main = main.html()
            middle_items = doc('div.text-middle>a').items()
            uidList = []
            for middle in middle_items:
                uid = middle.text()
                main = main.replace('href="/%s"'%uid, 'href="/userinfo/%s"'%uid)
            main = main.replace('!md', '')
            main = main.replace('/uploads', '/images/uploads')
            main = main.replace('https://testerhome.com/system', '/images/system')
            main = main.replace('/github.svg', '/images/github.png')
            item['ttf'] = main
    sites.insert(item)


ttf_url = 'https://testerhome.com/github_statistics'
sites_url = 'https://testerhome.com/sites'
urlList = [ttf_url, sites_url]
parse_page(urlList)