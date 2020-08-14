# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

from scrapy import Field, Item


class TesthomeUserItem(Item):
    # define the fields for your item here like:
    user = Field()
    uid = Field()
    img = Field()
    img_url = Field()
    uname = Field()
    date = Field()
    number = Field()
    company = Field()
    counts = Field()
    tagline = Field()
    post = Field()
    returncard = Field()
    social = Field()
    followers = Field()
    following = Field()
    stars = Field()
    profile = Field()
    location = Field()
    image_paths = Field()
    hot_topics = Field()
    recently = Field()
    introduce = Field()
    missList = Field()
