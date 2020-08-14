# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class TesthomeFollowersItem(Item):
    # define the fields for your item here like:
    uid = Field()
    followers = Field()
    following = Field()
    image_paths = Field()
    img_urls = Field()