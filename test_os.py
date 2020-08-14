#coding=utf-8
import pymongo
import os
import sys
import time
import json


def get_flag():
    with open(r'flag.txt', 'r') as f:
        result = f.read()
    flag = eval(result)
    return flag


flag_key = ['community', 'favs', 'follow', 'user', 'college', 'node']
i = 1
while True:
    print(time.strftime('%Y-%M-%D %H:%M:%S', time.localtime(int(time.time()))) + '     第%d次执行爬取任务'%i)
    for key in flag_key:
        os.chdir('./testhome_%s'%key)
        curr_dir = os.getcwd()
        print('当前爬取的路径: ',  curr_dir)
        os.system('scrapy crawl testhome')
        os.chdir('../')
        while True:
            flag = get_flag()
            if flag[key] == 'true':
                time.sleep(10)
                break
            time.sleep(5)
    print(time.strftime('%Y-%M-%D %H:%M:%S', time.localtime(int(time.time()))) + '     开始更新es中的数据')
    os.system('python3 ExecuteEs.py')
    while True:
        flag = get_flag()
        if flag['mongoes'] == 'true':
            with open(r'flag.txt', 'w') as f:
                flag_value = {"community": "false", "favs": "false", "follow": "false", "user": "false", "college": "false", "node": "false", "mongoes": "false"}
                result = json.dumps(flag_value)
                f.write(result)
            break
        time.sleep(10)
    i += 1
    time.sleep(60)
