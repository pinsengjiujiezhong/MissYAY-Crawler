#coding=utf-8


import pymongo

client = pymongo.MongoClient('127.0.0.1')
mydb = client.testerhome
user = mydb.user
users = mydb.users

items = user.find({})
i = 1
for item in items:
    del item['_id']
    users.insert(item)
    i += 1


