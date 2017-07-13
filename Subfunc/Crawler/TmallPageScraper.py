# __author__ = 'xjlin'
# -*- coding: utf-8 -*-
import os
import codecs
import csv
import time
import random 
import json

import requests

from Subfunc.Crawler import USER_AGENTS
from Work.log import Logger
logger = Logger('Tmall', 'DEBUG')
proxies = {}
proxies_pool = []


def proxy_changer():
    global proxies_pool
    global proxies
    if len(proxies_pool) == 0:
        try:
            re = requests.get(
                'http://tvp.daxiangdaili.com/ip/?tid=559959788048032&num=5&category=2&protocol=https&format=json')
            proxies_pool = json.loads(re.content)
        except Exception as e:
            logger.error('{}:{}'.format(e, re.content))
    proxy = proxies_pool.pop()
    url = 'http://{}:{}'.format(proxy['host'], proxy['port'])
    proxies = {
        'http': url,
        'https': url
    }
    logger.debug("change proxies to {}".format(url))


def get_web(url):
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

    logger.debug('Trying open {} with {}.'.format(url, proxies))
    r = requests.get(url=url, headers=headers, proxies=proxies)
    # logger.debug('{}: {}'.format(r.status_code, r.content))
    return r


def get_json(url):
    if proxies == {}:
        proxy_changer()

    # request for the HTML
    counter = 30
    while counter != 0:
        try:
            r = get_web(url)
            break
        except (requests.exceptions.ProxyError, requests.exceptions.ConnectionError):
            counter -= 1
            proxy_changer()

    if counter == 0:
        logger.error('{} {}'.format(url.encode('utf-8'), 'requests failed'))
        return
    else:
        logger.debug('Prase 1 passed.')

    flag = 2
    while flag != 0:
        try:
            js = json.loads(r.content)
            logger.debug('Prase 2 passed.')
            return js
        except ValueError:
            logger.traceback()
            flag -= 1
            if flag == 0:
                break
            else:
                proxy_changer()
                r = get_web(url)
    logger.error('{} {}'.format(url.encode('utf-8'), 'decode failed'))


def get_item(json_data):
    logger
    js = json_data['item']
    data_list = []
    for i in js:
        item = {}
        try:
            item['goodsID'] = i['item_id']
        except KeyError:
            item['goodsID'] = None

        try:
            item['goodsName'] = i['title'].encode('utf8')
        except KeyError:
            item['goodsName'] = None

        try:
            item['shopID'] = i['shop_id'].encode('utf8')
        except KeyError:
            item['shopID'] = None

        try:
            item['shopName'] = i['shop_name'].encode('utf8')
        except KeyError:
            item['shopName'] = None

        try:
            item['sales'] = i['sold'].encode('utf8')
        except KeyError:
            item['sales'] = None

        try:
            item['price'] = i['price'].encode('utf8')
        except KeyError:
            item['price'] = None

        try:
            item['comments'] = i['comment_num'].encode('utf8')
        except KeyError:
            item['comments'] = None
        data_list.append(item)
    return data_list


def write_csv(data_list, page, category_name):
    PATH = os.path.join(os.getcwd())
    PRESENT_TIME = str(time.strftime('%H-%M-%S', time.localtime(time.time())))
    PRESENT_DAY = str(time.strftime('%Y-%m-%d', time.localtime(time.time())))
    if data_list is None:
        return None

    # check or create a daily dictionary
    try:
        file_dict = os.path.join(PATH, 'Data', 'TmallData', '{}{}'.format('TmallData_', PRESENT_DAY))
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
    return


def parse(fake_url):
    try:
        logger.info(fake_url)
        url = fake_url.split('&*')[0]
        page = url.split('no=')[1]
        category_name = fake_url.split('*')[-1]
        json_data = get_json(url)
        data_list = get_item(json_data)
        write_csv(data_list, page, category_name)
        return 0
    except Exception:
        logger.error(logger.traceback())
        return 1
    

crawler = {
    'TMALL': parse
}
