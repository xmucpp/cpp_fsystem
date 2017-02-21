# __author__ = 'xjlin'
# -*- coding: utf-8 -*-
import os
import codecs
import csv
import time
import random 
import json

import requests

from config import PRESENT_DAY, PATH
from Work.globalvar import USER_AGENTS
from Work.log import Logger
logger = Logger('Tmall', 'DEBUG')


def get_json(url):
    user_agent = random.choice(USER_AGENTS)
    headers = {
        ':host': 'list.tmall.com',
        ':method': 'GET',
        ':path': url,
        ':scheme': 'https',
        ':version': 'HTTP/1.1',
        'accept': 'text/html',
        'accept-encoding': 'gzip,deflate',
        'accept-language': 'zh-CN,zh;q=0.8',
        'cache-control': 'max-age=0',
        'referer': 'https://list.tmall.com',
        'user-agent': user_agent,
    }

    # request for the HTML
    try:
        r = requests.get(url, headers)
        if r.status_code == 302:
            logger.error('this server be banned by Tmall')
            time.sleep(30)
            raise
        else:
            return r.content
    except (requests.exceptions.ConnectionError, requests.exceptions.ReadTimeout):
        logger.error('{} {}'.format(url.encode('utf-8'), 'Connect Error'))
        raise


def get_item(json_data):
    js = json.loads(json_data)['item']
    data_list = []
    for i in js:
        item = {}
        try:
            item['goodsID'] = i['item_id']
        except KeyError:
            item['goodsID'] = None

        try:
            item['goodsName'] = i['title']
        except KeyError:
            item['goodsName'] = None

        try:
            item['shopID'] = i['shop_id']
        except KeyError:
            item['shopID'] = None

        try:
            item['shopName'] = i['shop_name']
        except KeyError:
            item['shopName'] = None

        try:
            item['sales'] = i['sold']
        except KeyError:
            item['sales'] = None

        try:
            item['price'] = i['price']
        except KeyError:
            item['price'] = None

        try:
            item['comments'] = i['comment_num']
        except KeyError:
            item['comments'] = None
        data_list.append(item)
    return data_list


def write_csv(data_list, page, category_name):
    PRESENT_TIME = str(time.strftime('%H-%M-%S', time.localtime(time.time())))
    if data_list is None:
        return None

    # check or create a daily dictionary
    try:
        file_dict = os.path.join(PATH, 'Data', '{}{}'.format('TmallData_', PRESENT_DAY))
    except TypeError:
        file_dict = ''.join(['../TmallData_', PRESENT_DAY])
    try:
        os.makedirs(file_dict)
    except OSError, e:
        if e.errno != 17:
            raise e

    # create a file and its name for a certain page

    file_name = ''.join(
        [file_dict, '/', 'tmallPrice', '_', PRESENT_DAY, '_', PRESENT_TIME, '_', category_name,
         '_', str(page)])

    with codecs.open(file_name, 'wb') as f:
        fieldnames = ['goodsID', 'goodsName', 'shopName', 'shopID', 'sales', 'price',
                      'comments', ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for data in data_list:
            data = {key: value for key, value in data.items() if key in fieldnames}
            writer.writerow(data)

    # return indicator
    return [itemid['goodsID'] for itemid in data_list]


def parse(fake_url):
    try:
        url = fake_url.split('&*')[0]
        page = url.split('no=')[1]
        category_name = fake_url.split('*')[-1]
        json_data = get_json(url)
        data_list = get_item(json_data)
        write_csv(data_list, page, category_name)
        return 0
    except Exception:
        return 1
    

if __name__ == '__main__':
    parse('https://list.tmall.com/m/search_items.htm?q=%CD%E0%D7%D3&page_no=1&*name*袜子')
