# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class TesthomeWenItem(Item):
    # define the fields for your item here like:
    username = Field()
    uid = Field()
    id = Field()
    portrait = Field()
    url = Field()
    imgurls = Field()
    teamname = Field()
    teamuid = Field()
    flag = Field()
    awesome = Field()
    title = Field()
    desc = Field()
    stick = Field()
    time = Field()
    release_time = Field()
    recovery_time = Field()
    recovery_username = Field()
    recovery_uid = Field()
    admin_username = Field()
    admin_uid = Field()
    user = Field()
    hits = Field()
    hit = Field()
    content = Field()
    zan = Field()
    comments = Field()
    last_update_time = Field()
    image_paths = Field()