#coding=utf-8
import pymongo


client = pymongo.MongoClient('127.0.0.1')
testerhome = client.testerhome
user = testerhome.user
favs = testerhome.favs

user_items = user.find({})
userList = []
for item in user_items:
    userList.append(item['uid'])
print(len(userList))

favs_items = favs.find({})
favsList = []
for item in favs_items:
    favsList.append(item['uid'])
print(len(favsList))

for uid in favsList:
    if uid not in userList:
        print(uid)